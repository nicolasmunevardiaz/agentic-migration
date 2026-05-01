from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, ConfigDict, Field, field_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "qa" / "dataq_consistency_standardization_audit.jsonl"
PLAN_ID = "04_5_local_data_workbench_and_model_evolution_plan"
MODEL_SNAPSHOT = "V0_5"

EXPECTED_REFERENCE_FIELDS = {
    ("conditions", "encounter_reference"),
    ("conditions", "member_reference"),
    ("cost_records", "encounter_reference"),
    ("cost_records", "medication_reference"),
    ("cost_records", "member_reference"),
    ("encounters", "member_reference"),
    ("medications", "condition_reference"),
    ("medications", "encounter_reference"),
    ("medications", "member_reference"),
}

EXPECTED_CODE_FIELDS = {
    ("conditions", "condition_source_code"),
    ("medications", "medication_source_code"),
}


class ConsistencyAuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    timestamp: str
    plan_id: str
    model_snapshot: str
    check_id: str
    provider: str
    entity: str
    field_column: str
    total_rows: int = Field(ge=0)
    affected_rows: int = Field(ge=0)
    status: Literal["passed", "failed", "open", "managed"]
    severity: Literal["critical", "high", "medium", "low"]
    evidence_grain: Literal["provider_entity_field"]
    resolution_hint: str

    @field_validator("timestamp")
    @classmethod
    def timestamp_is_iso(cls, value: str) -> str:
        datetime.fromisoformat(value)
        return value


def _connection():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "/tmp"),
        dbname=os.environ.get("PGDATABASE", "agentic_migration_local"),
        user=os.environ.get("PGUSER"),
    )


def _fetch(sql: str) -> list[dict]:
    with _connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        return [dict(row) for row in cursor.fetchall()]


def _write_audit(rows: list[ConsistencyAuditRecord]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(), sort_keys=True) + "\n")


def test_consistency_standardization_contract_on_full_dataset() -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    rows = _fetch(
        """
        select
            'DQC-' || lpad(
                row_number() over (order by provider_slug, entity, field_column)::text,
                3,
                '0'
            ) as check_id,
            provider_slug as provider,
            entity,
            field_column,
            total_rows,
            least(affected_rows, total_rows)::bigint as affected_rows,
            case
                when finding_status = 'contract_violation' then 'failed'
                when finding_status like 'managed_%' then 'managed'
                when finding_status like 'open_%' then 'open'
                else 'passed'
            end as status,
            severity,
            resolution_hint
        from data_quality.dq_consistency_findings
        order by provider_slug, entity, field_column
        """
    )
    audit_rows = [
        ConsistencyAuditRecord(
            timestamp=timestamp,
            plan_id=PLAN_ID,
            model_snapshot=MODEL_SNAPSHOT,
            evidence_grain="provider_entity_field",
            **row,
        )
        for row in rows
    ]
    _write_audit(audit_rows)

    assert not [row for row in audit_rows if row.status == "failed"]
    assert not [row for row in audit_rows if row.status == "open"]
    assert [row for row in audit_rows if row.status == "managed"]
    assert all(row.affected_rows <= row.total_rows for row in audit_rows)


def test_consistency_metrics_cover_standardized_rows() -> None:
    rows = _fetch(
        """
        select
            (select count(*) from data_quality.dq_consistency_reference_metrics)
                as reference_metric_count,
            (select count(*) from data_quality.dq_consistency_code_metrics)
                as code_metric_count,
            (select count(*) from data_quality.dq_consistency_demographic_metrics)
                as demographic_metric_count,
            (select count(*) from data_quality.dq_consistency_contract_violations)
                as contract_violation_rows,
            (select count(*) from data_quality.dq_consistency_findings)
                as finding_rows
        """
    )
    row = rows[0]

    assert row["reference_metric_count"] == 36
    assert row["code_metric_count"] == 8
    assert row["demographic_metric_count"] == 5
    assert row["contract_violation_rows"] == 0
    assert row["finding_rows"] > 0


def test_consistency_expected_fields_are_profiled() -> None:
    reference_rows = _fetch(
        """
        select distinct entity, field_column
        from data_quality.dq_consistency_reference_metrics
        """
    )
    code_rows = _fetch(
        """
        select distinct entity, field_column
        from data_quality.dq_consistency_code_metrics
        """
    )

    assert {(row["entity"], row["field_column"]) for row in reference_rows} == (
        EXPECTED_REFERENCE_FIELDS
    )
    assert {(row["entity"], row["field_column"]) for row in code_rows} == EXPECTED_CODE_FIELDS


def test_consistency_reference_key_contract() -> None:
    rows = _fetch(
        """
        select
            (select count(*) from data_quality.dq_consistency_contract_violations)
                as contract_violation_rows,
            (
                select coalesce(sum(unresolved_reference_rows), 0)
                from data_quality.dq_consistency_reference_metrics
            ) as unresolved_reference_rows
        """
    )
    row = rows[0]

    assert row["contract_violation_rows"] == 0
    assert row["unresolved_reference_rows"] > 0


def test_consistency_reference_bridge_preserves_unresolved_flags() -> None:
    rows = _fetch(
        """
        select
            reference_resolution_status,
            consistency_reference_management_status,
            bool_or(is_unresolved_reference) as has_unresolved_flag,
            bool_or(is_missing_reference) as has_missing_flag,
            bool_or(is_unknown_reference) as has_unknown_flag,
            count(*) as row_count
        from data_quality.dq_consistency_reference_bridge
        where is_unresolved_reference
        group by reference_resolution_status, consistency_reference_management_status
        order by reference_resolution_status, consistency_reference_management_status
        """
    )

    statuses = {
        (
            row["reference_resolution_status"],
            row["consistency_reference_management_status"],
        )
        for row in rows
    }

    assert ("missing_reference", "managed_missing_reference_preserved") in statuses
    assert ("unknown_reference", "managed_unknown_reference_preserved") in statuses
    assert ("unresolved_reference", "managed_unresolved_reference_preserved") in statuses
    assert all(row["has_unresolved_flag"] for row in rows)


def test_consistency_demographic_survivor_is_provider_scoped() -> None:
    rows = _fetch(
        """
        select
            count(*) as survivor_rows,
            count(*) filter (
                where demographic_survivor_status = 'managed_demographic_survivor_selected'
            ) as managed_survivor_rows,
            count(distinct provider_slug || '|' || patient_provider_member_id)
                as provider_scoped_patient_keys
        from data_quality.dq_patient_demographic_survivor
        """
    )
    row = rows[0]

    assert row["survivor_rows"] == row["provider_scoped_patient_keys"]
    assert row["managed_survivor_rows"] > 0


def test_consistency_code_variants_are_managed_without_source_replacement() -> None:
    rows = _fetch(
        """
        select
            (
                select count(*)
                from data_quality.dq_condition_code_domain_mapping
                where condition_code_consistency_status
                    = 'managed_source_code_hint_domain_mismatch'
            ) as managed_condition_domain_rows,
            (
                select count(*)
                from data_quality.dq_medication_code_consistency_bridge
                where medication_code_consistency_status like 'managed_%'
            ) as managed_medication_variant_rows,
            (
                select count(*)
                from data_quality.dq_consistency_findings
                where finding_status like 'open_%'
            ) as open_finding_rows
        """
    )
    row = rows[0]

    assert row["managed_condition_domain_rows"] > 0
    assert row["managed_medication_variant_rows"] > 0
    assert row["open_finding_rows"] == 0
