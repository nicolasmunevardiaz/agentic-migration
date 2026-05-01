{{ config(materialized='view') }}

with coverage as (
    select *
    from {{ ref('coverage_period_fact') }}
),

member_rollup as (
    select
        provider_slug,
        patient_provider_member_id,
        member_reference,
        count(*) as coverage_period_row_count,
        count(distinct coverage_status) as coverage_status_count,
        count(*) filter (where coverage_status = 'COVERED') as covered_row_count,
        count(*) filter (where coverage_status = 'OUT_OF_COVERAGE') as out_of_coverage_row_count,
        count(*) filter (where is_undated_period) as undated_period_count,
        count(*) filter (where is_open_ended_period) as open_ended_period_count,
        count(*) filter (where is_end_date_only_period) as end_date_only_period_count,
        count(*) filter (where has_implausible_coverage_date) as implausible_date_count,
        count(*) filter (where has_duplicate_period_key) as duplicate_period_key_row_count,
        min(coverage_start_date) as earliest_coverage_start_date,
        max(coverage_start_date) as latest_coverage_start_date,
        min(coverage_end_date) as earliest_coverage_end_date,
        max(coverage_end_date) as latest_coverage_end_date
    from coverage
    group by provider_slug, patient_provider_member_id, member_reference
)

select
    provider_slug,
    patient_provider_member_id,
    member_reference,
    coverage_period_row_count,
    coverage_status_count,
    covered_row_count,
    out_of_coverage_row_count,
    undated_period_count,
    open_ended_period_count,
    end_date_only_period_count,
    implausible_date_count,
    duplicate_period_key_row_count,
    earliest_coverage_start_date,
    latest_coverage_start_date,
    earliest_coverage_end_date,
    latest_coverage_end_date,
    coverage_period_row_count > 1 as has_multiple_coverage_rows,
    coverage_status_count > 1 as has_multiple_coverage_statuses,
    covered_row_count > 0 as has_covered_status,
    out_of_coverage_row_count > 0 as has_out_of_coverage_status,
    implausible_date_count > 0 as has_implausible_coverage_date,
    duplicate_period_key_row_count > 0 as has_duplicate_period_keys
from member_rollup
