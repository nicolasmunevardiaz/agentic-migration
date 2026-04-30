{{ config(materialized='view') }}

with coverage as (
    select *
    from {{ ref('coverage_source_normalized') }}
),

with_duplicate_flags as (
    select
        *,
        count(*) over (
            partition by
                provider_slug,
                member_reference,
                coverage_start_date,
                coverage_end_date,
                coverage_status
        ) as duplicate_period_key_row_count
    from coverage
)

select
    coverage_period_id,
    coverage_source_row_id,
    patient_provider_member_id,
    coverage_status_id,
    provider_slug,
    source_entity,
    source_row_id,
    source_lineage_ref,
    member_reference,
    coverage_start_date,
    coverage_end_date,
    coverage_status,
    review_batch_id,
    loaded_at,
    has_coverage_start_date,
    has_coverage_end_date,
    is_open_ended_period,
    is_end_date_only_period,
    is_undated_period,
    has_inverted_date_range,
    has_implausible_coverage_date,
    duplicate_period_key_row_count > 1 as has_duplicate_period_key,
    duplicate_period_key_row_count,
    bounded_coverage_days,
    case
        when has_inverted_date_range then 'invalid_inverted_dates'
        when has_implausible_coverage_date then 'review_implausible_dates'
        when is_undated_period then 'review_missing_dates'
        when is_end_date_only_period then 'review_end_date_only'
        when is_open_ended_period then 'open_ended'
        else 'bounded'
    end as coverage_period_quality_status
from with_duplicate_flags
