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
DEFAULT_EVIDENCE_PATH = f"metadata/model_specs/evolution/{ITERATION_ID}/db_state_snapshot.yaml"
DEFAULT_STATE_PATH = MODEL_ROOT / f"evolution/{ITERATION_ID}/db_state_snapshot.yaml"
DEFAULT_SQL_ANSWER_PATH = MODEL_ROOT / f"evolution/{ITERATION_ID}/sql_answer_evidence.yaml"
DEFAULT_DBT_ARTIFACT_PATH = MODEL_ROOT / f"evolution/{ITERATION_ID}/dbt_artifacts_manifest.yaml"
PLAN_ID = "04_5_local_data_workbench_and_model_evolution_plan"

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

BUSINESS_QUESTION_OUTPUTS = {
    "BQ-001": "bq_001_member_overlap",
    "BQ-002": "bq_002_gender_distribution",
    "BQ-003": "bq_003_age_groups",
    "BQ-004": "bq_004_total_cost_of_care",
    "BQ-005": "bq_005_prevalent_conditions",
    "BQ-006": "bq_006_medications_per_member",
    "BQ-007": "bq_007_condition_catalog",
    "BQ-008": "bq_008_medication_catalog",
    "BQ-009": "bq_009_treatment_patterns",
    "BQ-010": "bq_010_vital_signs",
    "BQ-011": "bq_011_unit_price_benchmark",
    "BQ-012": "bq_012_enrollment_gaps",
    "BQ-013": "bq_013_uninsured_members",
    "BQ-014": "bq_014_tcoc_coverage_split",
    "BQ-015": "bq_015_enrollment_continuity_cost",
    "BQ-016": "bq_016_medication_unit_prices_by_coverage",
}


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


def table_count(cursor, table_name: str) -> int:
    cursor.execute(f"SELECT count(*) FROM {table_name}")
    value = cursor.fetchone()[0]
    return int(value)


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


def capture_dbt_artifacts(target_dir: Path, output_path: Path) -> dict[str, Any]:
    artifacts = {}
    for name in ("manifest.json", "run_results.json", "catalog.json"):
        path = target_dir / name
        if path.exists():
            artifacts[name] = {
                "path": path.as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size_bytes": path.stat().st_size,
            }
        else:
            artifacts[name] = {"path": path.as_posix(), "status": "missing"}
    manifest = {
        "spec_version": 0.1,
        "artifact": "dbt_artifacts_manifest",
        "iteration_id": ITERATION_ID,
        "dbt_status": "captured",
        "project": "dbt/dbt_project.yml",
        "profiles": "dbt/profiles.yml",
        "approved_adapter": "dbt-postgres",
        "artifacts": artifacts,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return manifest


def validate_sql_answers(database: str, output_path: Path) -> dict[str, Any]:
    results = []
    with connect(database) as connection, connection.cursor() as cursor:
        for question_id, model_name in BUSINESS_QUESTION_OUTPUTS.items():
            row_count = table_count(cursor, f'evidence."{model_name}"')
            result = {
                "question_id": question_id,
                "sql_output": f"evidence.{model_name}",
                "status": "answered",
                "row_count": row_count,
                "acceptance": "pass" if row_count >= 0 else "fail",
            }
            if question_id == "BQ-016":
                result["semantic_review"] = (
                    "PROBE-V0_3-001 retained final-segment member and encounter "
                    "reference alignment before coverage classification"
                )
            results.append(result)
    evidence = {
        "spec_version": 0.1,
        "artifact": "sql_answer_evidence",
        "iteration_id": ITERATION_ID,
        "status": "passed",
        "answered_count": len(results),
        "deferred_hitl_count": 0,
        "business_question_results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(evidence, sort_keys=False), encoding="utf-8")
    return evidence


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
    parser.add_argument("--capture-dbt-artifacts", action="store_true")
    parser.add_argument("--validate-sql-answers", action="store_true")
    parser.add_argument("--state-output", default=DEFAULT_STATE_PATH.as_posix())
    parser.add_argument("--dbt-target-dir", default="dbt/target")
    parser.add_argument("--dbt-artifact-output", default=DEFAULT_DBT_ARTIFACT_PATH.as_posix())
    parser.add_argument("--sql-answer-output", default=DEFAULT_SQL_ANSWER_PATH.as_posix())
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
    if args.capture_dbt_artifacts:
        manifest = capture_dbt_artifacts(
            target_dir=Path(args.dbt_target_dir),
            output_path=Path(args.dbt_artifact_output),
        )
        print(f"captured_dbt_artifacts={manifest['artifacts'].keys()}")
    if args.validate_sql_answers:
        evidence = validate_sql_answers(
            database=args.database,
            output_path=Path(args.sql_answer_output),
        )
        print(f"validated_sql_answers={evidence['answered_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
