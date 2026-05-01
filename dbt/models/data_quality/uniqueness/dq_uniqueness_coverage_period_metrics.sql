{{ config(materialized='table') }}

with key_group_metrics as (
    select
        provider_slug,
        sum(period_key_row_count) as total_rows,
        count(*) as business_key_group_count,
        count(*) filter (where has_duplicate_period_key) as duplicate_key_group_count,
        coalesce(
            sum(period_key_row_count) filter (where has_duplicate_period_key),
            0
        ) as duplicate_key_rows,
        coalesce(
            sum(period_key_row_count - 1) filter (where has_duplicate_period_key),
            0
        ) as excess_duplicate_rows,
        max(period_key_row_count) as max_rows_per_business_key,
        sum(missing_required_lineage_rows) as missing_required_lineage_rows
    from {{ ref('dq_uniqueness_coverage_period_key_groups') }}
    group by provider_slug
),

survivor_metrics as (
    select
        provider_slug,
        count(*) as survivor_rows,
        count(distinct provider_member_plan_period_key) as survivor_distinct_keys,
        count(*) - count(distinct provider_member_plan_period_key)
            as survivor_duplicate_key_rows
    from {{ ref('coverage_period_survivor_fact') }}
    group by provider_slug
)

select
    {{ provider_scoped_hash("key_group_metrics.provider_slug", "'coverage_periods|provider_member_plan_period_key'") }}
        as uniqueness_metric_id,
    key_group_metrics.provider_slug,
    'coverage_periods' as entity,
    'provider_member_plan_period_key' as field_column,
    key_group_metrics.total_rows,
    key_group_metrics.business_key_group_count,
    key_group_metrics.duplicate_key_group_count,
    key_group_metrics.duplicate_key_rows,
    key_group_metrics.excess_duplicate_rows,
    key_group_metrics.max_rows_per_business_key,
    key_group_metrics.missing_required_lineage_rows,
    coalesce(survivor_metrics.survivor_rows, 0) as survivor_rows,
    coalesce(survivor_metrics.survivor_distinct_keys, 0) as survivor_distinct_keys,
    coalesce(survivor_metrics.survivor_duplicate_key_rows, 0)
        as survivor_duplicate_key_rows,
    'latest_loaded_record_per_provider_member_period_status' as survivor_rule_id,
    'deterministic_period_key_and_survivor_rule' as resolution_hint,
    case
        when key_group_metrics.missing_required_lineage_rows > 0
          or coalesce(survivor_metrics.survivor_duplicate_key_rows, 0) > 0
            then 'contract_violation'
        when key_group_metrics.duplicate_key_group_count > 0
            then 'managed_duplicate_key_survivor_applied'
        else 'complete'
    end as uniqueness_metric_status
from key_group_metrics
left join survivor_metrics
    on key_group_metrics.provider_slug = survivor_metrics.provider_slug
