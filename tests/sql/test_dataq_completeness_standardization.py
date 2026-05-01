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
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "qa" / "dataq_completeness_standardization_audit.jsonl"
PLAN_ID = "04_5_local_data_workbench_and_model_evolution_plan"
MODEL_SNAPSHOT = "V0_5"


class CompletenessAuditRecord(BaseModel):
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
    status: Literal["passed", "open", "managed", "failed"]
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


def _write_audit(rows: list[CompletenessAuditRecord]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(), sort_keys=True) + "\n")


def test_completeness_standardization_contract_on_full_dataset() -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    rows = _fetch(
        """
        select
            'DQM-' || lpad(
                row_number() over (order by provider_slug, entity, field_column)::text,
                3,
                '0'
            ) as check_id,
            provider_slug as provider,
            entity,
            field_column,
            total_rows,
            least(affected_rows, greatest(total_rows, affected_rows))::bigint as affected_rows,
            case
                when finding_status = 'contract_violation' then 'failed'
                when finding_status like 'managed_%' then 'managed'
                when finding_status like 'open_%' then 'open'
                else 'passed'
            end as status,
            severity,
            resolution_hint
        from data_quality.dq_completeness_findings
        order by provider_slug, entity, field_column
        """
    )
    audit_rows = [
        CompletenessAuditRecord(
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


def test_completeness_contract_metrics_are_materialized() -> None:
    rows = _fetch(
        """
        select
            (select count(*) from data_quality.dq_completeness_provider_entity_availability)
                as entity_metric_count,
            (select count(*) from data_quality.dq_completeness_field_metrics)
                as field_metric_count,
            (select count(*) from data_quality.dq_completeness_contract_violations)
                as contract_violation_count,
            (select count(*) from data_quality.dq_completeness_findings)
                as finding_count
        """
    )
    row = rows[0]

    assert row["entity_metric_count"] == 35
    assert row["field_metric_count"] == 50
    assert row["contract_violation_count"] == 0
    assert row["finding_count"] > 0


def test_pacific_shield_unavailable_entities_are_managed() -> None:
    rows = _fetch(
        """
        select entity, completeness_entity_status
        from data_quality.dq_completeness_provider_entity_availability
        where provider_slug = 'data_provider_5_pacific_shield_insurance'
          and entity in ('encounters', 'conditions', 'observations', 'medications', 'cost_records')
        """
    )

    assert len(rows) == 5
    assert {row["completeness_entity_status"] for row in rows} == {
        "managed_provider_not_applicable"
    }


def test_optional_observation_components_are_not_failures() -> None:
    rows = _fetch(
        """
        select distinct completeness_field_status
        from data_quality.dq_completeness_field_metrics
        where entity = 'observations'
          and missing_rows > 0
        """
    )

    assert {row["completeness_field_status"] for row in rows} == {
        "managed_optional_sparse"
    }


def test_missing_required_fields_preserve_null_without_inference() -> None:
    rows = _fetch(
        """
        select
            field_column,
            completeness_field_status,
            null_semantics_status,
            bool_or(coalesce(usable_for_sum, false)) as any_usable_for_sum,
            bool_or(coalesce(usable_for_temporal_analysis, false))
                as any_usable_for_temporal_analysis,
            bool_or(coalesce(usable_for_duration, false)) as any_usable_for_duration,
            count(*) as metric_count
        from data_quality.dq_completeness_field_metrics
        where missing_rows > 0
          and entity in ('cost_records', 'coverage_periods', 'encounters', 'medications')
        group by field_column, completeness_field_status, null_semantics_status
        order by field_column, completeness_field_status, null_semantics_status
        """
    )

    expected = {
        (
            "cost_amount",
            "managed_amount_not_provided",
            "null_preserved_amount_not_provided",
        ),
        (
            "cost_date",
            "managed_date_not_provided",
            "null_preserved_date_not_provided",
        ),
        (
            "coverage_end_date",
            "managed_coverage_boundary_not_provided",
            "null_preserved_coverage_boundary_not_provided",
        ),
        (
            "coverage_start_date",
            "managed_coverage_boundary_not_provided",
            "null_preserved_coverage_boundary_not_provided",
        ),
        (
            "encounter_datetime",
            "managed_event_datetime_not_provided",
            "null_preserved_event_datetime_not_provided",
        ),
        (
            "medication_datetime",
            "managed_event_datetime_not_provided",
            "null_preserved_event_datetime_not_provided",
        ),
    }

    assert {
        (
            row["field_column"],
            row["completeness_field_status"],
            row["null_semantics_status"],
        )
        for row in rows
    } == expected
    assert not any(row["any_usable_for_sum"] for row in rows)
    assert not any(row["any_usable_for_temporal_analysis"] for row in rows)
    assert not any(row["any_usable_for_duration"] for row in rows)
