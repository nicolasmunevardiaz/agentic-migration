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
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "qa" / "dataq_timeliness_standardization_audit.jsonl"
PLAN_ID = "04_5_local_data_workbench_and_model_evolution_plan"
MODEL_SNAPSHOT = "V0_5"

EXPECTED_TEMPORAL_FIELDS = {
    ("coverage_periods", "coverage_end_date"),
    ("coverage_periods", "coverage_start_date"),
    ("cost_records", "cost_date"),
    ("encounters", "encounter_datetime"),
    ("medications", "medication_datetime"),
    ("observations", "observation_datetime"),
}


class TimelinessAuditRecord(BaseModel):
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
    status: Literal["passed", "failed", "open"]
    severity: Literal["critical", "high", "low"]
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


def _write_audit(rows: list[TimelinessAuditRecord]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(), sort_keys=True) + "\n")


def test_timeliness_standardization_contract_on_full_dataset() -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    rows = _fetch(
        """
        select
            'DQT-' || lpad(
                row_number() over (order by provider_slug, entity, field_column)::text,
                3,
                '0'
            )
                as check_id,
            provider_slug as provider,
            entity,
            field_column,
            total_rows,
            greatest(
                missing_source_value_rows
                , timezone_pending_rows
                , utc_without_approved_timezone_rows
            )::bigint as affected_rows,
            case
                when utc_without_approved_timezone_rows > 0 then 'failed'
                when missing_source_value_rows > 0 or timezone_pending_rows > 0 then 'open'
                else 'passed'
            end as status,
            case
                when utc_without_approved_timezone_rows > 0 then 'critical'
                when missing_source_value_rows = total_rows then 'critical'
                when missing_source_value_rows > 0 or timezone_pending_rows > 0 then 'high'
                else 'low'
            end as severity,
            case
                when utc_without_approved_timezone_rows > 0 then 'provider_timezone_to_utc_mapping'
                when missing_source_value_rows > 0 then 'approved_source_chronology_policy'
                when timezone_pending_rows > 0 then 'provider_timezone_to_utc_mapping'
                else 'none'
            end as resolution_hint
        from data_quality.dq_timeliness_provider_field_metrics
        order by provider_slug, entity, field_column
        """
    )
    audit_rows = [
        TimelinessAuditRecord(
            timestamp=timestamp,
            plan_id=PLAN_ID,
            model_snapshot=MODEL_SNAPSHOT,
            evidence_grain="provider_entity_field",
            **row,
        )
        for row in rows
    ]
    _write_audit(audit_rows)

    assert {(row.entity, row.field_column) for row in audit_rows} == EXPECTED_TEMPORAL_FIELDS
    assert all(row.total_rows > 0 for row in audit_rows)
    assert not [row for row in audit_rows if row.status == "failed"]
    assert [row for row in audit_rows if row.status == "open"]


def test_timeliness_utc_is_blocked_until_timezone_approval() -> None:
    rows = _fetch(
        """
        select
            count(*) filter (where provider_timezone is not null) as timezone_value_rows,
            count(*) filter (where timezone_status = 'timezone_approved') as approved_rows,
            count(*) filter (where timezone_status = 'offset_derived') as offset_derived_rows,
            count(*) filter (where utc_value is not null) as utc_value_rows,
            count(*) filter (
                where utc_value is not null
                  and timezone_status not in ('offset_derived', 'timezone_approved')
            ) as utc_without_temporal_authority_rows
        from data_quality.dq_standardized_temporal_fields
        """
    )
    row = rows[0]

    assert row["timezone_value_rows"] == 0
    assert row["approved_rows"] == 0
    assert row["offset_derived_rows"] > 0
    assert row["utc_value_rows"] == row["offset_derived_rows"]
    assert row["utc_without_temporal_authority_rows"] == 0


def test_timeliness_explicit_offsets_derive_utc_without_provider_timezone() -> None:
    rows = _fetch(
        """
        select
            count(*) as offset_rows,
            count(*) filter (where provider_timezone is not null) as provider_timezone_rows,
            count(*) filter (where utc_value is null) as missing_utc_rows,
            count(*) filter (where local_ntz_value is null) as missing_local_ntz_rows
        from data_quality.dq_standardized_temporal_fields
        where timezone_status = 'offset_derived'
        """
    )
    row = rows[0]

    assert row["offset_rows"] > 0
    assert row["provider_timezone_rows"] == 0
    assert row["missing_utc_rows"] == 0
    assert row["missing_local_ntz_rows"] == 0


def test_timeliness_metrics_cover_standardized_temporal_rows() -> None:
    rows = _fetch(
        """
        select
            (select count(*) from data_quality.dq_standardized_temporal_fields)
                as standardized_rows,
            (select sum(total_rows) from data_quality.dq_timeliness_provider_field_metrics)
                as metric_rows,
            (select count(*) from data_quality.dq_timeliness_contract_violations)
                as contract_violation_rows,
            (select count(*) from data_quality.dq_timeliness_findings)
                as finding_rows
        """
    )
    row = rows[0]

    assert row["standardized_rows"] == row["metric_rows"]
    assert row["contract_violation_rows"] == 0
    assert row["finding_rows"] > 0
