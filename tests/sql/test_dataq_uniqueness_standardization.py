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
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "qa" / "dataq_uniqueness_standardization_audit.jsonl"
PLAN_ID = "04_5_local_data_workbench_and_model_evolution_plan"
MODEL_SNAPSHOT = "V0_5"


class UniquenessAuditRecord(BaseModel):
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
    duplicate_key_group_count: int = Field(ge=0)
    excess_duplicate_rows: int = Field(ge=0)
    max_rows_per_business_key: int = Field(ge=0)
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


def _write_audit(rows: list[UniquenessAuditRecord]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(), sort_keys=True) + "\n")


def test_uniqueness_standardization_contract_on_full_dataset() -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    rows = _fetch(
        """
        select
            'DQU-' || lpad(
                row_number() over (order by provider_slug, entity, field_column)::text,
                3,
                '0'
            ) as check_id,
            provider_slug as provider,
            entity,
            field_column,
            total_rows,
            affected_rows,
            duplicate_key_group_count,
            excess_duplicate_rows,
            max_rows_per_business_key,
            case
                when finding_status = 'contract_violation' then 'failed'
                when finding_status like 'managed_%' then 'managed'
                else 'open'
            end as status,
            severity,
            resolution_hint
        from data_quality.dq_uniqueness_findings
        order by provider_slug, entity, field_column
        """
    )
    audit_rows = [
        UniquenessAuditRecord(
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
    assert {row.status for row in audit_rows} == {"managed"}
    assert len(audit_rows) == 5
    assert sum(row.affected_rows for row in audit_rows) == 34823


def test_uniqueness_metrics_are_materialized() -> None:
    rows = _fetch(
        """
        select
            (select count(*) from data_quality.dq_uniqueness_coverage_period_metrics)
                as metric_count,
            (select count(*) from data_quality.dq_uniqueness_contract_violations)
                as contract_violation_count,
            (select count(*) from data_quality.dq_uniqueness_findings)
                as finding_count,
            (
                select coalesce(sum(duplicate_key_rows), 0)
                from data_quality.dq_uniqueness_coverage_period_metrics
            ) as duplicate_key_rows
        """
    )
    row = rows[0]

    assert row["metric_count"] == 5
    assert row["contract_violation_count"] == 0
    assert row["finding_count"] == 5
    assert row["duplicate_key_rows"] == 34823


def test_uniqueness_duplicate_groups_preserve_required_lineage() -> None:
    rows = _fetch(
        """
        select count(*) as missing_lineage_duplicate_group_count
        from data_quality.dq_uniqueness_coverage_period_key_groups
        where has_duplicate_period_key
          and missing_required_lineage_rows > 0
        """
    )

    assert rows[0]["missing_lineage_duplicate_group_count"] == 0


def test_uniqueness_does_not_hide_duplicate_rows() -> None:
    rows = _fetch(
        """
        select
            (
                select count(*)
                from derived.coverage_period_fact
                where has_duplicate_period_key
            ) as fact_duplicate_rows,
            (
                select coalesce(sum(duplicate_key_rows), 0)
                from data_quality.dq_uniqueness_coverage_period_metrics
            ) as metric_duplicate_rows
        """
    )

    assert rows[0]["fact_duplicate_rows"] == rows[0]["metric_duplicate_rows"]


def test_uniqueness_survivor_view_has_one_row_per_business_key() -> None:
    rows = _fetch(
        """
        select count(*) as duplicate_survivor_key_count
        from (
            select provider_member_plan_period_key
            from derived.coverage_period_survivor_fact
            group by provider_member_plan_period_key
            having count(*) > 1
        ) as duplicate_keys
        """
    )

    assert rows[0]["duplicate_survivor_key_count"] == 0
