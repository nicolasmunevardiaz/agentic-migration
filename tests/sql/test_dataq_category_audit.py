from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, ConfigDict, Field, field_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "qa"
PLAN_ID = "04_5_local_data_workbench_and_model_evolution_plan"
MODEL_SNAPSHOT = "V0_5"


Category = Literal[
    "accuracy",
    "completeness",
    "consistency",
    "timeliness",
    "uniqueness",
    "validity",
]


class DataQualityFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    timestamp: str
    plan_id: str
    model_snapshot: str
    category: Category
    check_id: str
    provider: str
    entity: str
    field_column: str
    total_rows: int = Field(ge=0)
    affected_rows: int = Field(ge=0)
    severity: Literal["critical", "high", "medium", "low", "hitl"]
    status: Literal["passed", "failed"]
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


def _fetch_findings(sql: str) -> list[dict]:
    with _connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        return [dict(row) for row in cursor.fetchall()]


def _write_category_log(category: Category, rows: list[dict]) -> list[DataQualityFinding]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / f"dataq_{category}_audit.jsonl"
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    findings = [
        DataQualityFinding(
            timestamp=timestamp,
            plan_id=PLAN_ID,
            model_snapshot=MODEL_SNAPSHOT,
            category=category,
            status="failed" if int(row["affected_rows"]) > 0 else "passed",
            evidence_grain="provider_entity_field",
            **row,
        )
        for row in rows
    ]
    with path.open("w", encoding="utf-8") as handle:
        for finding in findings:
            handle.write(json.dumps(finding.model_dump(), sort_keys=True) + "\n")
    return findings


EXPECTED_FAILED_FINDING_COUNTS: dict[Category, int] = {
    "accuracy": 11,
    "completeness": 31,
    "consistency": 46,
    "timeliness": 10,
    "uniqueness": 5,
    "validity": 5,
}


def _assert_category_audit_matches_expected_findings(
    category: Category, sql: str
) -> None:
    findings = _write_category_log(category, _fetch_findings(sql))
    failed = [finding for finding in findings if finding.affected_rows > 0]
    assert findings, f"{category} data-quality audit produced no rows"
    assert len(failed) == EXPECTED_FAILED_FINDING_COUNTS[category], (
        f"{category} data-quality audit found {len(failed)} failing checks; "
        f"expected {EXPECTED_FAILED_FINDING_COUNTS[category]}. "
        f"See artifacts/qa/dataq_{category}_audit.jsonl"
    )


COMPLETENESS_SQL = """
with checks as (
    select provider_slug as provider, 'encounters' as entity,
        'encounter_datetime' as field_column,
        count(*)::bigint as total_rows,
        count(*) filter (where has_missing_encounter_datetime)::bigint as affected_rows,
        'critical' as severity,
        'approved_source_chronology_policy' as resolution_hint
    from derived.encounter_fact
    group by provider_slug
    union all
    select provider_slug, 'medications', 'medication_datetime',
        count(*)::bigint,
        count(*) filter (where has_missing_medication_datetime)::bigint,
        'critical',
        'approved_source_chronology_policy'
    from derived.medication_fact
    group by provider_slug
    union all
    select provider_slug, 'cost_records', 'cost_date',
        count(*)::bigint,
        count(*) filter (where has_missing_cost_date)::bigint,
        'critical',
        'approved_source_chronology_policy'
    from derived.cost_record_fact
    group by provider_slug
    union all
    select provider_slug, 'cost_records', 'cost_amount',
        count(*)::bigint,
        count(*) filter (where has_missing_cost_amount)::bigint,
        'medium',
        'amount_source_requiredness_policy'
    from derived.cost_record_fact
    group by provider_slug
    union all
    select provider_slug, 'coverage_periods', 'coverage_period_dates',
        count(*)::bigint,
        count(*) filter (where is_undated_period or is_end_date_only_period)::bigint,
        'critical',
        'coverage_period_state_model'
    from derived.coverage_period_fact
    group by provider_slug
    union all
    select provider_slug, 'observations', 'height_cm',
        count(*)::bigint,
        count(*) filter (where height_cm is null)::bigint,
        'high',
        'component_completeness_flags'
    from derived.observation_vitals_wide
    group by provider_slug
    union all
    select provider_slug, 'observations', 'weight_kg',
        count(*)::bigint,
        count(*) filter (where weight_kg is null)::bigint,
        'high',
        'component_completeness_flags'
    from derived.observation_vitals_wide
    group by provider_slug
    union all
    select provider_slug, 'observations', 'blood_pressure_pair',
        count(*)::bigint,
        count(*) filter (where systolic_bp is null or diastolic_bp is null)::bigint,
        'high',
        'component_completeness_flags'
    from derived.observation_vitals_wide
    group by provider_slug
    union all
    select provider_slug, 'observations', 'bmi_payload',
        count(*)::bigint,
        count(*) filter (where bmi_payload is null)::bigint,
        'high',
        'component_completeness_flags'
    from derived.observation_vitals_wide
    group by provider_slug
)
select
    'DQCAT-COMP-' || lpad(row_number() over (order by entity, field_column, provider)::text, 3, '0')
        as check_id,
    provider,
    entity,
    field_column,
    total_rows,
    affected_rows,
    severity,
    resolution_hint
from checks
order by entity, field_column, provider;
"""


UNIQUENESS_SQL = """
select
    'DQCAT-UNIQ-' || lpad(row_number() over (order by provider_slug)::text, 3, '0')
        as check_id,
    provider_slug as provider,
    'coverage_periods' as entity,
    'provider_member_plan_period_key' as field_column,
    count(*)::bigint as total_rows,
    count(*) filter (where has_duplicate_period_key)::bigint as affected_rows,
    'high' as severity,
    'deterministic_period_key_and_survivor_rule' as resolution_hint
from derived.coverage_period_fact
group by provider_slug
order by provider_slug;
"""


VALIDITY_SQL = """
with checks as (
    select provider_slug as provider, 'patients' as entity, 'birth_date' as field_column,
        count(*)::bigint as total_rows,
        count(*) filter (where has_implausible_birth_date)::bigint as affected_rows,
        'high' as severity,
        'date_bounds_parser_quarantine' as resolution_hint
    from derived.patient_dimension
    group by provider_slug
    union all
    select provider_slug, 'coverage_periods', 'coverage_start_date_or_end_date',
        count(*)::bigint,
        count(*) filter (where has_implausible_coverage_date or has_inverted_date_range)::bigint,
        'high',
        'date_bounds_parser_quarantine'
    from derived.coverage_period_fact
    group by provider_slug
    union all
    select provider_slug, 'conditions', 'condition_source_code',
        count(*)::bigint,
        count(*) filter (where not source_code_matches_hint)::bigint,
        'critical',
        'code_source_domain_mapping'
    from derived.condition_fact
    group by provider_slug
    union all
    select provider_slug, 'cost_records', 'cost_amount',
        count(*)::bigint,
        count(*) filter (where has_nonpositive_cost_amount)::bigint,
        'medium',
        'positive_numeric_amount_guardrail'
    from derived.cost_record_fact
    group by provider_slug
)
select
    'DQCAT-VAL-' || lpad(row_number() over (order by entity, field_column, provider)::text, 3, '0')
        as check_id,
    provider,
    entity,
    field_column,
    total_rows,
    affected_rows,
    severity,
    resolution_hint
from checks
order by entity, field_column, provider;
"""


CONSISTENCY_SQL = """
with checks as (
    select provider_slug as provider, 'patients' as entity, 'gender' as field_column,
        count(*)::bigint as total_rows,
        count(*) filter (where has_gender_conflict)::bigint as affected_rows,
        'medium' as severity,
        'demographic_survivor_rules' as resolution_hint
    from derived.patient_dimension
    group by provider_slug
    union all
    select provider_slug, 'patients', 'birth_date',
        count(*)::bigint,
        count(*) filter (where has_birth_date_conflict)::bigint,
        'high',
        'demographic_survivor_rules'
    from derived.patient_dimension
    group by provider_slug
    union all
    select provider_slug, 'encounters', 'member_reference',
        count(*)::bigint,
        count(*) filter (where has_orphan_member_reference)::bigint,
        'critical',
        'member_reference_normalization'
    from derived.encounter_fact
    group by provider_slug
    union all
    select provider_slug, 'conditions', 'member_reference',
        count(*)::bigint,
        count(*) filter (where has_orphan_member_reference)::bigint,
        'critical',
        'member_reference_normalization'
    from derived.condition_fact
    group by provider_slug
    union all
    select provider_slug, 'conditions', 'encounter_reference',
        count(*)::bigint,
        count(*) filter (where has_orphan_encounter_reference)::bigint,
        'critical',
        'encounter_reference_audit_bridge'
    from derived.condition_fact
    group by provider_slug
    union all
    select provider_slug, 'medications', 'member_reference',
        count(*)::bigint,
        count(*) filter (where has_orphan_member_reference)::bigint,
        'critical',
        'member_reference_normalization'
    from derived.medication_fact
    group by provider_slug
    union all
    select provider_slug, 'medications', 'encounter_reference',
        count(*)::bigint,
        count(*) filter (where has_orphan_encounter_reference)::bigint,
        'critical',
        'encounter_reference_audit_bridge'
    from derived.medication_fact
    group by provider_slug
    union all
    select provider_slug, 'medications', 'condition_reference',
        count(*)::bigint,
        count(*) filter (where has_orphan_condition_reference)::bigint,
        'critical',
        'condition_reference_audit_bridge'
    from derived.medication_fact
    group by provider_slug
    union all
    select provider_slug, 'cost_records', 'member_reference',
        count(*)::bigint,
        count(*) filter (where has_orphan_member_reference)::bigint,
        'critical',
        'member_reference_normalization'
    from derived.cost_record_fact
    group by provider_slug
    union all
    select provider_slug, 'cost_records', 'encounter_reference',
        count(*)::bigint,
        count(*) filter (where has_orphan_encounter_reference)::bigint,
        'critical',
        'encounter_reference_audit_bridge'
    from derived.cost_record_fact
    group by provider_slug
    union all
    select provider_slug, 'medications', 'medication_source_code',
        count(*)::bigint,
        count(*) filter (where has_raw_code_variants)::bigint,
        'medium',
        'code_description_variant_dimensions'
    from derived.medication_code_dimension
    group by provider_slug
    union all
    select provider_slug, 'medications', 'medication_description',
        count(*)::bigint,
        count(*) filter (where has_description_variants)::bigint,
        'medium',
        'code_description_variant_dimensions'
    from derived.medication_code_dimension
    group by provider_slug
)
select
    'DQCAT-CONS-' || lpad(row_number() over (order by entity, field_column, provider)::text, 3, '0')
        as check_id,
    provider,
    entity,
    field_column,
    total_rows,
    affected_rows,
    severity,
    resolution_hint
from checks
order by entity, field_column, provider;
"""


TIMELINESS_SQL = """
with checks as (
    select provider_slug as provider, 'encounters' as entity, 'encounter_datetime' as field_column,
        count(*)::bigint as total_rows,
        count(*) filter (where has_missing_encounter_datetime)::bigint as affected_rows,
        'critical' as severity,
        'provider_timezone_to_utc_mapping' as resolution_hint
    from derived.encounter_fact
    group by provider_slug
    union all
    select provider_slug, 'medications', 'medication_datetime',
        count(*)::bigint,
        count(*) filter (where has_missing_medication_datetime)::bigint,
        'critical',
        'provider_timezone_to_utc_mapping'
    from derived.medication_fact
    group by provider_slug
    union all
    select provider_slug, 'cost_records', 'cost_date',
        count(*)::bigint,
        count(*) filter (where has_missing_cost_date)::bigint,
        'critical',
        'provider_timezone_to_utc_mapping'
    from derived.cost_record_fact
    group by provider_slug
    union all
    select table_name as provider, 'derived_catalog' as entity, 'provider_timezone' as field_column,
        1::bigint as total_rows,
        1::bigint as affected_rows,
        'high' as severity,
        'provider_timezone_to_utc_mapping' as resolution_hint
    from information_schema.tables
    where table_schema = 'derived'
        and table_name in (
            'encounter_fact',
            'medication_fact',
            'cost_record_fact',
            'observation_vitals_wide'
        )
        and not exists (
            select 1
            from information_schema.columns c
            where c.table_schema = 'derived'
                and c.table_name = tables.table_name
                and c.column_name = 'provider_timezone'
        )
)
select
    'DQCAT-TIME-' || lpad(row_number() over (order by entity, field_column, provider)::text, 3, '0')
        as check_id,
    provider,
    entity,
    field_column,
    total_rows,
    affected_rows,
    severity,
    resolution_hint
from checks
order by entity, field_column, provider;
"""


ACCURACY_SQL = """
with checks as (
    select provider_slug as provider, 'medications' as entity,
        'medication_source_code' as field_column,
        count(*)::bigint as total_rows,
        count(*) filter (where has_raw_code_variants or has_description_variants)::bigint
            as affected_rows,
        'hitl' as severity,
        'clinical_semantic_review' as resolution_hint
    from derived.medication_code_dimension
    group by provider_slug
    union all
    select provider_slug, 'conditions', 'condition_source_code',
        count(*)::bigint,
        count(*) filter (where not source_code_matches_hint)::bigint,
        'hitl',
        'clinical_semantic_review'
    from derived.condition_fact
    group by provider_slug
    union all
    select provider_slug, 'cost_records', 'cost_amount_or_date',
        count(*)::bigint,
        count(*) filter (where has_missing_cost_amount or has_missing_cost_date)::bigint,
        'hitl',
        'financial_semantic_review'
    from derived.cost_record_fact
    group by provider_slug
)
select
    'DQCAT-ACC-' || lpad(row_number() over (order by entity, field_column, provider)::text, 3, '0')
        as check_id,
    provider,
    entity,
    field_column,
    total_rows,
    affected_rows,
    severity,
    resolution_hint
from checks
order by entity, field_column, provider;
"""


@pytest.mark.parametrize(
    ("category", "sql"),
    [
        ("completeness", COMPLETENESS_SQL),
        ("uniqueness", UNIQUENESS_SQL),
        ("validity", VALIDITY_SQL),
        ("consistency", CONSISTENCY_SQL),
        ("timeliness", TIMELINESS_SQL),
        ("accuracy", ACCURACY_SQL),
    ],
)
def test_dataq_category_audit_writes_expected_open_drift(
    category: Category, sql: str
) -> None:
    _assert_category_audit_matches_expected_findings(category, sql)
