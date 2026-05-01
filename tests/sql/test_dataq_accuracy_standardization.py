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
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "qa" / "dataq_accuracy_standardization_audit.jsonl"
PLAN_ID = "04_5_local_data_workbench_and_model_evolution_plan"
MODEL_SNAPSHOT = "V0_5"


class AccuracyAuditRecord(BaseModel):
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
    status: Literal["passed", "managed", "hitl_required", "open", "failed"]
    severity: Literal["critical", "high", "medium", "low", "hitl"]
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


def _write_audit(rows: list[AccuracyAuditRecord]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(), sort_keys=True) + "\n")


def test_accuracy_standardization_contract_on_full_dataset() -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    rows = _fetch(
        """
        select
            'DQA-' || lpad(
                row_number() over (order by provider_slug, entity, field_column)::text,
                3,
                '0'
            ) as check_id,
            provider_slug as provider,
            entity,
            field_column,
            total_rows,
            affected_rows,
            case
                when finding_status = 'contract_violation' then 'failed'
                when finding_status like 'managed_%' then 'managed'
                when finding_status like 'hitl_required_%' then 'hitl_required'
                else 'open'
            end as status,
            severity,
            resolution_hint
        from data_quality.dq_accuracy_findings
        order by provider_slug, entity, field_column
        """
    )
    audit_rows = [
        AccuracyAuditRecord(
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
    assert len(audit_rows) == 11
    assert {row.status for row in audit_rows} == {"managed"}
    assert {row.severity for row in audit_rows} == {"medium"}


def test_accuracy_metrics_are_materialized() -> None:
    rows = _fetch(
        """
        select
            (select count(*) from data_quality.dq_accuracy_clinical_semantic_metrics)
                as clinical_metric_count,
            (select count(*) from data_quality.dq_accuracy_financial_metrics)
                as financial_metric_count,
            (select count(*) from data_quality.dq_accuracy_observation_reconciliation_metrics)
                as observation_metric_count,
            (select count(*) from data_quality.dq_accuracy_medication_canonical_dimension)
                as medication_canonical_count,
            (select count(*) from data_quality.dq_accuracy_contract_violations)
                as contract_violation_count,
            (select count(*) from data_quality.dq_accuracy_findings)
                as finding_count
        """
    )
    row = rows[0]

    assert row["clinical_metric_count"] == 8
    assert row["financial_metric_count"] == 4
    assert row["observation_metric_count"] == 4
    assert row["medication_canonical_count"] == 700
    assert row["contract_violation_count"] == 0
    assert row["finding_count"] == 11


def test_accuracy_observation_reconciliation_is_clean() -> None:
    rows = _fetch(
        """
        select
            coalesce(sum(affected_rows), 0) as affected_rows,
            max(max_bmi_payload_recomputed_abs_delta) as max_bmi_delta
        from data_quality.dq_accuracy_observation_reconciliation_metrics
        """
    )

    assert rows[0]["affected_rows"] == 0
    assert rows[0]["max_bmi_delta"] <= 0.1


def test_accuracy_does_not_apply_forbidden_semantic_remediation() -> None:
    rows = _fetch(
        """
        select
            (
                select count(*)
                from data_quality.dq_accuracy_contract_violations
            ) as contract_violation_count,
            (
                select count(*)
                from data_quality.dq_accuracy_findings
                where finding_status like 'hitl_required_%'
            ) as hitl_finding_count,
            (
                select count(*)
                from data_quality.dq_accuracy_findings
                where finding_status like 'managed_%'
            ) as managed_finding_count
        """
    )

    assert rows[0]["contract_violation_count"] == 0
    assert rows[0]["hitl_finding_count"] == 0
    assert rows[0]["managed_finding_count"] == 11
