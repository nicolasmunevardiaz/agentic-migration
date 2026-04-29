from __future__ import annotations

import argparse
import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_SPEC_PATH = Path("metadata/runtime_specs/local/local_postgres_workbench.yaml")
DEFAULT_OUTPUT_PATH = Path("artifacts/local_runtime/postgres/local_workbench_schema.sql")
TYPE_MAP = {
    "bigint": "bigint",
    "date": "date",
    "jsonb": "jsonb",
    "numeric": "numeric",
    "text": "text",
    "timestamp": "timestamp",
    "timestamptz": "timestamptz",
}
SILVER_TYPE_MAP = {
    "date": "date",
    "datetime": "timestamptz",
    "decimal": "numeric",
    "json_string": "jsonb",
    "string": "text",
}


class WorkbenchSpecError(ValueError):
    pass


@dataclass(frozen=True)
class Column:
    name: str
    data_type: str
    nullable: bool = True
    default: str | None = None


@dataclass(frozen=True)
class CheckConstraint:
    name: str
    expression: str


@dataclass(frozen=True)
class Index:
    name: str
    columns: tuple[str, ...]


@dataclass(frozen=True)
class Table:
    schema: str
    name: str
    columns: tuple[Column, ...]
    primary_key: tuple[str, ...] = ()
    checks: tuple[CheckConstraint, ...] = ()
    indexes: tuple[Index, ...] = ()

    @property
    def qualified_name(self) -> str:
        return f"{quote_identifier(self.schema)}.{quote_identifier(self.name)}"


def quote_identifier(value: str) -> str:
    if not value or not value.replace("_", "").isalnum() or value[0].isdigit():
        raise WorkbenchSpecError(f"Unsafe SQL identifier: {value}")
    return f'"{value}"'


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def load_yaml(path: Path) -> dict[str, Any]:
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        raise WorkbenchSpecError(f"YAML document must be a mapping: {path}")
    return content


def spec_checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def column_from_mapping(raw_column: dict[str, Any], type_map: dict[str, str]) -> Column:
    source_type = raw_column["type"]
    if source_type not in type_map:
        raise WorkbenchSpecError(f"Unsupported column type: {source_type}")
    return Column(
        name=raw_column["name"],
        data_type=type_map[source_type],
        nullable=bool(raw_column.get("nullable", True)),
        default=raw_column.get("default"),
    )


def table_from_mapping(raw_table: dict[str, Any]) -> Table:
    checks = tuple(
        CheckConstraint(name=item["name"], expression=item["expression"])
        for item in raw_table.get("checks", [])
    )
    indexes = tuple(
        Index(name=item["name"], columns=tuple(item["columns"]))
        for item in raw_table.get("indexes", [])
    )
    return Table(
        schema=raw_table["schema"],
        name=raw_table["name"],
        columns=tuple(
            column_from_mapping(column, TYPE_MAP)
            for column in raw_table["columns"]
        ),
        primary_key=tuple(raw_table.get("primary_key", [])),
        checks=checks,
        indexes=indexes,
    )


def silver_tables(spec: dict[str, Any], repo_root: Path) -> list[Table]:
    silver_config = spec["silver_review_tables"]
    silver_root = repo_root / silver_config["source_spec_root"]
    additional_columns = tuple(
        column_from_mapping(column, TYPE_MAP)
        for column in silver_config.get("additional_columns", [])
    )
    tables: list[Table] = []
    for silver_path in sorted(silver_root.glob("*.yaml")):
        silver_spec = load_yaml(silver_path)
        entity = silver_spec["entity"]
        columns = tuple(
            Column(
                name=column["name"],
                data_type=SILVER_TYPE_MAP[column["type"]],
                nullable=bool(column.get("nullable", True)),
            )
            for column in silver_spec["columns"]
        )
        tables.append(
            Table(
                schema=silver_config["schema"],
                name=f"{silver_config['table_prefix']}{entity}",
                columns=columns + additional_columns,
                indexes=(
                    Index(
                        name=f"idx_{silver_config['schema']}_{silver_config['table_prefix']}{entity}_lineage",
                        columns=("provider_slug", "source_entity", "source_row_id"),
                    ),
                ),
            )
        )
    return tables


def all_tables(spec: dict[str, Any], repo_root: Path) -> list[Table]:
    tables = [table_from_mapping(item) for item in spec["manual_tables"]]
    if spec["silver_review_tables"]["enabled"]:
        tables.extend(silver_tables(spec, repo_root))
    return tables


def render_column(column: Column) -> str:
    pieces = [quote_identifier(column.name), column.data_type]
    if not column.nullable:
        pieces.append("NOT NULL")
    if column.default:
        pieces.extend(["DEFAULT", column.default])
    return " ".join(pieces)


def render_create_table(table: Table) -> str:
    lines = [f"  {render_column(column)}" for column in table.columns]
    if table.primary_key:
        pk_columns = ", ".join(quote_identifier(column) for column in table.primary_key)
        constraint_name = quote_identifier("pk_" + table.schema + "_" + table.name)
        lines.append(
            f"  CONSTRAINT {constraint_name} PRIMARY KEY ({pk_columns})"
        )
    return f"CREATE TABLE IF NOT EXISTS {table.qualified_name} (\n" + ",\n".join(lines) + "\n);"


def render_add_columns(table: Table) -> list[str]:
    return [
        f"ALTER TABLE {table.qualified_name} ADD COLUMN IF NOT EXISTS {render_column(column)};"
        for column in table.columns
    ]


def render_primary_key(table: Table) -> str | None:
    if not table.primary_key:
        return None
    constraint_name = "pk_" + table.schema + "_" + table.name
    pk_columns = ", ".join(quote_identifier(column) for column in table.primary_key)
    return "\n".join(
        [
            "DO $$",
            "BEGIN",
            "  IF NOT EXISTS (",
            "    SELECT 1 FROM pg_constraint",
            f"    WHERE conname = {sql_literal(constraint_name)}",
            f"      AND conrelid = {sql_literal(table.schema + '.' + table.name)}::regclass",
            "  ) THEN",
            (
                f"    ALTER TABLE {table.qualified_name} "
                f"ADD CONSTRAINT {quote_identifier(constraint_name)} "
                f"PRIMARY KEY ({pk_columns});"
            ),
            "  END IF;",
            "END $$;",
        ]
    )


def render_check_constraint(table: Table, check: CheckConstraint) -> str:
    return "\n".join(
        [
            "DO $$",
            "BEGIN",
            "  IF NOT EXISTS (",
            "    SELECT 1 FROM pg_constraint",
            f"    WHERE conname = {sql_literal(check.name)}",
            f"      AND conrelid = {sql_literal(table.schema + '.' + table.name)}::regclass",
            "  ) THEN",
            (
                f"    ALTER TABLE {table.qualified_name} "
                f"ADD CONSTRAINT {quote_identifier(check.name)} "
                f"CHECK ({check.expression});"
            ),
            "  END IF;",
            "END $$;",
        ]
    )


def render_index(table: Table, index: Index) -> str:
    columns = ", ".join(quote_identifier(column) for column in index.columns)
    return (
        f"CREATE INDEX IF NOT EXISTS {quote_identifier(index.name)} "
        f"ON {table.qualified_name} ({columns});"
    )


def render_deploy_sql(spec_path: Path, repo_root: Path) -> str:
    spec = load_yaml(spec_path)
    checksum = spec_checksum(spec_path)
    tables = all_tables(spec, repo_root)
    lines = [
        "-- Generated by src.handlers.local_postgres_workbench_deploy",
        "-- Idempotent local PostgreSQL workbench deploy; review before applying.",
        "BEGIN;",
    ]
    for schema in spec["schemas"]:
        lines.append(f"CREATE SCHEMA IF NOT EXISTS {quote_identifier(schema['name'])};")
    for table in tables:
        lines.append(render_create_table(table))
        lines.extend(render_add_columns(table))
        primary_key = render_primary_key(table)
        if primary_key:
            lines.append(primary_key)
        lines.extend(render_check_constraint(table, check) for check in table.checks)
        lines.extend(render_index(table, index) for index in table.indexes)
    lines.extend(
        [
            (
                "INSERT INTO evidence.local_deploy_runs "
                "(deployment_id, plan_id, spec_path, spec_checksum, deploy_status, message)"
            ),
            "VALUES (",
            f"  {sql_literal('local-postgres-workbench-' + checksum[:12])},",
            f"  {sql_literal(spec['plan_id'])},",
            f"  {sql_literal(spec_path.as_posix())},",
            f"  {sql_literal(checksum)},",
            "  'applied',",
            "  'idempotent local PostgreSQL workbench schema deployed'",
            ")",
            "ON CONFLICT (deployment_id) DO UPDATE SET",
            "  deploy_status = EXCLUDED.deploy_status,",
            "  message = EXCLUDED.message,",
            "  deployed_at = now();",
            "COMMIT;",
        ]
    )
    return "\n".join(lines) + "\n"


def run_psql(database: str, sql_path: Path, psql_bin: str) -> None:
    subprocess.run(
        [psql_bin, "-v", "ON_ERROR_STOP=1", "-d", database, "-f", sql_path.as_posix()],
        check=True,
    )


def verify_deploy(database: str, spec_path: Path, repo_root: Path, psql_bin: str) -> None:
    spec = load_yaml(spec_path)
    expected_tables = sorted(
        f"{table.schema}.{table.name}"
        for table in all_tables(spec, repo_root)
    )
    values = ", ".join(sql_literal(value) for value in expected_tables)
    query = (
        "WITH expected(table_name) AS (VALUES "
        + ", ".join(f"({sql_literal(value)})" for value in expected_tables)
        + ") "
        "SELECT expected.table_name "
        "FROM expected "
        "LEFT JOIN information_schema.tables actual "
        "ON expected.table_name = actual.table_schema || '.' || actual.table_name "
        "WHERE actual.table_name IS NULL;"
    )
    _ = values
    result = subprocess.run(
        [psql_bin, "-v", "ON_ERROR_STOP=1", "-d", database, "-tAc", query],
        check=True,
        capture_output=True,
        text=True,
    )
    missing = [line for line in result.stdout.splitlines() if line.strip()]
    if missing:
        raise WorkbenchSpecError(f"Missing deployed tables: {missing}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render and optionally apply the local PostgreSQL workbench schema."
    )
    parser.add_argument("--spec", default=DEFAULT_SPEC_PATH.as_posix())
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH.as_posix())
    parser.add_argument("--database", default="")
    parser.add_argument("--psql-bin", default="psql")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    spec_path = Path(args.spec)
    output_path = Path(args.output)
    spec = load_yaml(spec_path)
    database = args.database or spec["database"]["default_database"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_deploy_sql(spec_path, repo_root), encoding="utf-8")
    print(f"wrote_sql={output_path.as_posix()}")
    if args.apply:
        run_psql(database=database, sql_path=output_path, psql_bin=args.psql_bin)
        print(f"applied_database={database}")
    if args.verify:
        verify_deploy(
            database=database,
            spec_path=spec_path,
            repo_root=repo_root,
            psql_bin=args.psql_bin,
        )
        print(f"verified_database={database}")
    if args.dry_run and not args.apply:
        print("dry_run=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
