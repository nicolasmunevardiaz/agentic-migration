{{ config(materialized='table') }}

with key_groups as (
    select
        provider_slug,
        'coverage_periods' as entity,
        'provider_member_plan_period_key' as field_column,
        {{ provider_scoped_hash(
            "provider_slug",
            "coalesce(patient_provider_member_id, 'UNKNOWN')"
            ~ " || '|' || coalesce(coverage_start_date::text, 'NULL')"
            ~ " || '|' || coalesce(coverage_end_date::text, 'NULL')"
            ~ " || '|' || coalesce(coverage_status, 'UNKNOWN')"
        ) }} as provider_member_plan_period_key,
        patient_provider_member_id,
        member_reference,
        coverage_start_date,
        coverage_end_date,
        coverage_status,
        count(*) as period_key_row_count,
        count(distinct coverage_period_id) as distinct_coverage_period_id_count,
        count(distinct coverage_source_row_id) as distinct_coverage_source_row_id_count,
        count(distinct source_row_id) as distinct_source_row_id_count,
        count(distinct source_lineage_ref) as distinct_source_lineage_ref_count,
        count(*) filter (
            where source_row_id is null
               or source_lineage_ref is null
               or coverage_source_row_id is null
        ) as missing_required_lineage_rows,
        min(source_lineage_ref) as sample_source_lineage_ref
    from {{ ref('coverage_period_fact') }}
    group by
        provider_slug,
        patient_provider_member_id,
        member_reference,
        coverage_start_date,
        coverage_end_date,
        coverage_status
)

select
    provider_member_plan_period_key as uniqueness_key_group_id,
    provider_slug,
    entity,
    field_column,
    provider_member_plan_period_key,
    patient_provider_member_id,
    member_reference,
    coverage_start_date,
    coverage_end_date,
    coverage_status,
    period_key_row_count,
    distinct_coverage_period_id_count,
    distinct_coverage_source_row_id_count,
    distinct_source_row_id_count,
    distinct_source_lineage_ref_count,
    missing_required_lineage_rows,
    sample_source_lineage_ref,
    period_key_row_count > 1 as has_duplicate_period_key,
    case
        when period_key_row_count > 1 and missing_required_lineage_rows > 0
            then 'contract_violation'
        when period_key_row_count > 1 then 'open_duplicate_key_pending_survivor_rule'
        else 'complete'
    end as uniqueness_key_group_status
from key_groups
