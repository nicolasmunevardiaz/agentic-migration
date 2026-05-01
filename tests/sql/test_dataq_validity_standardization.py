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
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "qa" / "dataq_validity_standardization_audit.jsonl"
PLAN_ID = "04_5_local_data_workbench_and_model_evolution_plan"
MODEL_SNAPSHOT = "V0_5"


class ValidityAuditRecord(BaseModel):
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
    status: Literal["passed", "managed", "open", "failed"]
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


def _write_audit(rows: list[ValidityAuditRecord]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(), sort_keys=True) + "\n")


def test_validity_standardization_contract_on_full_dataset() -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    rows = _fetch(
        """
        select
            'DQV-' || lpad(
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
                else 'open'
            end as status,
            severity,
            resolution_hint
        from data_quality.dq_validity_findings
        order by provider_slug, entity, field_column
        """
    )
    audit_rows = [
        ValidityAuditRecord(
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


def test_validity_metrics_are_materialized() -> None:
    rows = _fetch(
        """
        select
            (select count(*) from data_quality.dq_validity_date_metrics)
                as date_metric_count,
            (select count(*) from data_quality.dq_validity_code_metrics)
                as code_metric_count,
            (select count(*) from data_quality.dq_validity_amount_metrics)
                as amount_metric_count,
            (select count(*) from data_quality.dq_validity_domain_metrics)
                as domain_metric_count,
            (select count(*) from data_quality.dq_validity_contract_violations)
                as contract_violation_count,
            (select count(*) from data_quality.dq_validity_findings)
                as finding_count
        """
    )
    row = rows[0]

    assert row["date_metric_count"] == 22
    assert row["code_metric_count"] == 8
    assert row["amount_metric_count"] == 4
    assert row["domain_metric_count"] == 33
    assert row["contract_violation_count"] == 0
    assert row["finding_count"] > 0


def test_validity_domain_guardrails_are_clean() -> None:
    rows = _fetch(
        """
        select *
        from data_quality.dq_validity_domain_metrics
        where validity_domain_status <> 'complete'
        """
    )

    assert rows == []


def test_validity_preserves_known_open_failures() -> None:
    rows = _fetch(
        """
        select finding_status, count(*) as finding_count
        from data_quality.dq_validity_findings
        group by finding_status
        """
    )
    counts = {row["finding_status"]: row["finding_count"] for row in rows}

    assert counts.get("managed_split_provider_and_clinical_codes", 0) == 3
    assert counts.get("managed_implausible_date_quarantined", 0) == 2
    assert not any(status.startswith("open_") for status in counts)


def test_validity_condition_codes_are_split_and_cleaned() -> None:
    rows = _fetch(
        """
        select
            count(*) filter (
                where source_raw_code <> provider_condition_code_raw
            ) as cleaned_raw_code_rows,
            count(*) filter (
                where condition_code_domain_status = 'managed_split_provider_and_clinical_codes'
            ) as managed_split_rows,
            count(*) filter (
                where provider_condition_code_normalized is null
            ) as missing_provider_code_rows,
            count(*) filter (
                where clinical_code_system in ('snomed_ct', 'icd_9_cm', 'icd_10_cm')
            ) as classified_clinical_rows
        from data_quality.dq_validity_condition_code_domain_bridge
        """
    )
    row = rows[0]

    assert row["cleaned_raw_code_rows"] > 0
    assert row["managed_split_rows"] > 0
    assert row["missing_provider_code_rows"] == 0
    assert row["classified_clinical_rows"] > 0


def test_validity_implausible_dates_are_quarantined_to_validated_null() -> None:
    rows = _fetch(
        """
        select
            count(*) filter (
                where date_validity_status like 'managed_%'
            ) as managed_date_rows,
            count(*) filter (
                where date_validity_status like 'managed_%'
                  and validated_date_value is not null
            ) as managed_with_validated_value_rows,
            count(*) filter (
                where date_validity_status like 'managed_%'
                  and usable_for_temporal_analysis
            ) as managed_usable_rows
        from data_quality.dq_validity_date_quarantine
        """
    )
    row = rows[0]

    assert row["managed_date_rows"] > 0
    assert row["managed_with_validated_value_rows"] == 0
    assert row["managed_usable_rows"] == 0
