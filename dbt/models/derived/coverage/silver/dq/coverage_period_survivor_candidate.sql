{{ config(materialized='view') }}

with ranked as (
    select
        coverage_period_fact.*,
        {{ provider_scoped_hash(
            "provider_slug",
            "coalesce(patient_provider_member_id, 'UNKNOWN')"
            ~ " || '|' || coalesce(coverage_start_date::text, 'NULL')"
            ~ " || '|' || coalesce(coverage_end_date::text, 'NULL')"
            ~ " || '|' || coalesce(coverage_status, 'UNKNOWN')"
        ) }} as provider_member_plan_period_key,
        row_number() over (
            partition by
                provider_slug,
                patient_provider_member_id,
                coverage_start_date,
                coverage_end_date,
                coverage_status
            order by
                loaded_at desc nulls last,
                review_batch_id desc nulls last,
                source_row_id desc nulls last,
                coverage_source_row_id desc
        ) as survivor_rank,
        count(*) over (
            partition by
                provider_slug,
                patient_provider_member_id,
                coverage_start_date,
                coverage_end_date,
                coverage_status
        ) as survivor_group_row_count
    from {{ ref('coverage_period_fact') }} as coverage_period_fact
)

select
    *,
    survivor_rank = 1 as is_survivor,
    'latest_loaded_record_per_provider_member_period_status' as survivor_rule_id,
    case
        when survivor_group_row_count > 1 and survivor_rank = 1
            then 'survivor_selected'
        when survivor_group_row_count > 1
            then 'duplicate_retained_for_lineage'
        else 'not_duplicate'
    end as survivor_selection_status
from ranked
