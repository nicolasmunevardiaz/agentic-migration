from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from glob import glob
from pathlib import Path
from typing import Any

import psycopg2
import yaml
from psycopg2.extras import execute_batch

from src.handlers.aegis_adapter import run_aegis_adapter_for_file
from src.handlers.bluestone_adapter import run_bluestone_adapter_for_file
from src.handlers.northcare_adapter import run_northcare_adapter_for_file
from src.handlers.pacific_shield_adapter import run_pacific_shield_adapter_for_file
from src.handlers.valleybridge_adapter import run_valleybridge_adapter_for_file

REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = REPO_ROOT / "metadata/model_specs"
SILVER_ROOT = MODEL_ROOT / "silver"
DEFAULT_DATABASE = "agentic_migration_local"
ITERATION_ID = "V0_3"
DEFAULT_BATCH_ID = "plan-04-5-v0-3-data-500k"
DEFAULT_EVIDENCE_PATH = "reports/qa/local_postgres_landing_load.md"
DEFAULT_STATE_PATH = REPO_ROOT / "artifacts/qa/local_postgres_landing_state_snapshot.yaml"
PLAN_ID = "04_local_runtime_and_contract_certification_plan"

AdapterRunner = Callable[..., Any]


@dataclass(frozen=True)
class ProviderDataSet:
    provider_slug: str
    provider_spec_root: Path
    runner: AdapterRunner
    entities: tuple[str, ...] = (
        "patients",
        "encounters",
        "conditions",
        "medications",
        "observations",
    )


PROVIDER_DATASETS = (
    ProviderDataSet(
        provider_slug="data_provider_1_aegis_care_network",
        provider_spec_root=REPO_ROOT / "metadata/provider_specs/data_provider_1_aegis_care_network",
        runner=run_aegis_adapter_for_file,
    ),
    ProviderDataSet(
        provider_slug="data_provider_2_bluestone_health",
        provider_spec_root=REPO_ROOT / "metadata/provider_specs/data_provider_2_bluestone_health",
        runner=run_bluestone_adapter_for_file,
    ),
    ProviderDataSet(
        provider_slug="data_provider_3_northcare_clinics",
        provider_spec_root=REPO_ROOT / "metadata/provider_specs/data_provider_3_northcare_clinics",
        runner=run_northcare_adapter_for_file,
    ),
    ProviderDataSet(
        provider_slug="data_provider_4_valleybridge_medical",
        provider_spec_root=REPO_ROOT
        / "metadata/provider_specs/data_provider_4_valleybridge_medical",
        runner=run_valleybridge_adapter_for_file,
    ),
    ProviderDataSet(
        provider_slug="data_provider_5_pacific_shield_insurance",
        provider_spec_root=REPO_ROOT
        / "metadata/provider_specs/data_provider_5_pacific_shield_insurance",
        runner=run_pacific_shield_adapter_for_file,
    ),
)

def load_yaml(path: Path) -> dict[str, Any]:
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        raise ValueError(f"YAML document must be a mapping: {path}")
    return content


def silver_columns() -> dict[str, list[str]]:
    columns: dict[str, list[str]] = {}
    for path in sorted(SILVER_ROOT.glob("*.yaml")):
        spec = load_yaml(path)
        columns[spec["entity"]] = [column["name"] for column in spec["columns"]]
    return columns


def connect(database: str):
    return psycopg2.connect(dbname=database)


def sql_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return value


def source_files_for_entity(provider: ProviderDataSet, entity: str) -> list[Path]:
    provider_spec = load_yaml(provider.provider_spec_root / f"{entity}.yaml")
    files: list[Path] = []
    for pattern in provider_spec["source"]["expected_file_patterns"]:
        if not pattern.startswith("data_500k/"):
            raise ValueError(
                f"Plan 04.5 V0_3 may only load data_500k source files: {pattern}"
            )
        files.extend(Path(path) for path in glob((REPO_ROOT / pattern).as_posix()))
    return sorted(set(files))


def collect_data_500k_rows(batch_id: str) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int]]:
    rows_by_entity: dict[str, list[dict[str, Any]]] = {}
    source_counts: dict[str, int] = {}
    for provider in PROVIDER_DATASETS:
        for source_entity in provider.entities:
            source_counts[f"{provider.provider_slug}.{source_entity}"] = 0
            for source_file in source_files_for_entity(provider, source_entity):
                result = provider.runner(
                    entity=source_entity,
                    source_file=source_file,
                    ingestion_run_id=batch_id,
                    provider_spec_root=provider.provider_spec_root,
                    model_root=MODEL_ROOT,
                    evidence_path=DEFAULT_EVIDENCE_PATH,
                )
                source_counts[f"{provider.provider_slug}.{source_entity}"] += len(
                    result.bronze_records
                )
                for silver_entity, rows in result.silver_rows.items():
                    for row in rows:
                        loaded_row = dict(row)
                        loaded_row["review_batch_id"] = batch_id
                        rows_by_entity.setdefault(silver_entity, []).append(loaded_row)
    return rows_by_entity, source_counts


def load_data_500k_rows(database: str, batch_id: str) -> dict[str, Any]:
    columns_by_entity = silver_columns()
    rows_by_entity, source_counts = collect_data_500k_rows(batch_id=batch_id)
    with connect(database) as connection, connection.cursor() as cursor:
        for entity in sorted(columns_by_entity):
            cursor.execute(
                f'DELETE FROM landing."{entity}" WHERE review_batch_id = %s',
                (batch_id,),
            )
        for entity, rows in sorted(rows_by_entity.items()):
            insert_columns = columns_by_entity[entity] + ["review_batch_id"]
            placeholders = ", ".join(["%s"] * len(insert_columns))
            quoted_columns = ", ".join(f'"{column}"' for column in insert_columns)
            sql = (
                f'INSERT INTO landing."{entity}" '
                f"({quoted_columns}) VALUES ({placeholders})"
            )
            execute_batch(
                cursor,
                sql,
                [tuple(sql_value(row.get(column)) for column in insert_columns) for row in rows],
                page_size=1000,
            )
    return {
        "batch_id": batch_id,
        "source_record_count": sum(source_counts.values()),
        "source_checksum": checksum_data_500k_contract(),
        "evidence_path": DEFAULT_EVIDENCE_PATH,
        "landing_row_counts": {
            entity: len(rows) for entity, rows in sorted(rows_by_entity.items())
        },
        "source_counts": source_counts,
    }


def checksum_data_500k_contract() -> str:
    digest = hashlib.sha256()
    for provider in PROVIDER_DATASETS:
        for entity in provider.entities:
            digest.update(provider.provider_slug.encode("utf-8"))
            digest.update(entity.encode("utf-8"))
            for source_file in source_files_for_entity(provider, entity):
                digest.update(source_file.relative_to(REPO_ROOT).as_posix().encode("utf-8"))
                digest.update(hashlib.sha256(source_file.read_bytes()).hexdigest().encode("utf-8"))
    return digest.hexdigest()


def capture_state(database: str, batch_id: str, output_path: Path) -> dict[str, Any]:
    columns_by_entity = silver_columns()
    state: dict[str, Any] = {
        "spec_version": 0.1,
        "artifact": "local_postgres_state_snapshot",
        "iteration_id": ITERATION_ID,
        "status": "captured",
        "database": database,
        "review_batch_id": batch_id,
        "privacy_rule": "No raw PHI or PII values are stored in this snapshot.",
        "schemas": ["landing"],
        "row_counts": {},
        "null_rate_checks": {},
        "duplicate_key_checks": {},
        "orphan_relationship_checks": {},
        "failed_cast_checks": [],
        "nested_payload_checks": [],
        "entity_mismatch_checks": [],
    }
    with connect(database) as connection, connection.cursor() as cursor:
        for entity, columns in sorted(columns_by_entity.items()):
            table = f'landing."{entity}"'
            cursor.execute(
                f"SELECT count(*) FROM {table} WHERE review_batch_id = %s",
                (batch_id,),
            )
            state["row_counts"][f"landing.{entity}"] = int(cursor.fetchone()[0])
            state["null_rate_checks"][entity] = {}
            for column in columns:
                cursor.execute(
                    f"""
                    SELECT count(*) FILTER (WHERE "{column}" IS NULL), count(*)
                    FROM {table}
                    WHERE review_batch_id = %s
                    """,
                    (batch_id,),
                )
                null_count, total_count = cursor.fetchone()
                rate = 0 if int(total_count) == 0 else float(null_count) / float(total_count)
                state["null_rate_checks"][entity][column] = {
                    "null_count": int(null_count),
                    "total_count": int(total_count),
                    "null_rate": round(rate, 6),
                }
            cursor.execute(
                f"""
                SELECT count(*) FROM (
                  SELECT provider_slug, source_entity, source_row_id, count(*)
                  FROM {table}
                  WHERE review_batch_id = %s
                  GROUP BY provider_slug, source_entity, source_row_id
                  HAVING count(*) > 1
                ) duplicates
                """,
                (batch_id,),
            )
            state["duplicate_key_checks"][entity] = int(cursor.fetchone()[0])
        state["orphan_relationship_checks"] = {
            "conditions_without_member": orphan_count(
                cursor, "conditions", "member_reference", batch_id
            ),
            "encounters_without_member": orphan_count(
                cursor, "encounters", "member_reference", batch_id
            ),
            "medications_without_member": orphan_count(
                cursor, "medications", "member_reference", batch_id
            ),
            "observations_without_member": orphan_count(
                cursor, "observations", "member_reference", batch_id
            ),
        }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")
    return state


def orphan_count(cursor, entity: str, column: str, batch_id: str) -> int:
    cursor.execute(
        f"""
        SELECT count(*)
        FROM landing."{entity}" child
        LEFT JOIN landing.members members
          ON child.provider_slug = members.provider_slug
         AND child."{column}" = members.member_reference
         AND members.review_batch_id = %s
        WHERE child.review_batch_id = %s
          AND child."{column}" IS NOT NULL
          AND members.member_reference IS NULL
        """,
        (batch_id, batch_id),
    )
    return int(cursor.fetchone()[0])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Operate Plan 04.5 local model workbench.")
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument("--batch-id", default=DEFAULT_BATCH_ID)
    parser.add_argument(
        "--load-data-500k",
        action="store_true",
        help="Load all provider files matched by data_500k provider spec patterns.",
    )
    parser.add_argument(
        "--load-fixtures",
        action="store_true",
        help="Deprecated compatibility alias for --load-data-500k; fixtures are not loaded.",
    )
    parser.add_argument("--capture-state", action="store_true")
    parser.add_argument("--state-output", default=DEFAULT_STATE_PATH.as_posix())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.load_data_500k or args.load_fixtures:
        result = load_data_500k_rows(database=args.database, batch_id=args.batch_id)
        print(f"loaded_batch={result['batch_id']} landing_rows={result['landing_row_counts']}")
    if args.capture_state:
        state = capture_state(
            database=args.database,
            batch_id=args.batch_id,
            output_path=Path(args.state_output),
        )
        print(f"captured_state={args.state_output} row_counts={state['row_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
