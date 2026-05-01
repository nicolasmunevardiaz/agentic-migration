{{ config(materialized='table') }}

select
    uniqueness_metric_id as finding_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    duplicate_key_rows as affected_rows,
    uniqueness_metric_status as finding_status,
    case
        when uniqueness_metric_status = 'contract_violation' then 'critical'
        when excess_duplicate_rows > 10000 then 'high'
        else 'medium'
    end as severity,
    duplicate_key_group_count,
    excess_duplicate_rows,
    max_rows_per_business_key,
    missing_required_lineage_rows,
    survivor_rows,
    survivor_distinct_keys,
    survivor_duplicate_key_rows,
    survivor_rule_id,
    resolution_hint
from {{ ref('dq_uniqueness_coverage_period_metrics') }}
where uniqueness_metric_status <> 'complete'
