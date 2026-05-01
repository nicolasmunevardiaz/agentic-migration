{{ config(materialized='table') }}

select
    uniqueness_metric_id as violation_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    missing_required_lineage_rows as affected_rows,
    uniqueness_metric_status as violation_status,
    resolution_hint
from {{ ref('dq_uniqueness_coverage_period_metrics') }}
where uniqueness_metric_status = 'contract_violation'
