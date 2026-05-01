{{ config(materialized='table') }}

select
    completeness_entity_availability_id as violation_id,
    provider_slug,
    entity,
    'entity_presence' as field_column,
    row_count as total_rows,
    1 as affected_rows,
    'required_entity_missing' as violation_type,
    resolution_hint
from {{ ref('dq_completeness_provider_entity_availability') }}
where completeness_entity_status = 'open_required_entity_missing'

union all

select
    completeness_field_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    missing_rows,
    'unknown_requiredness_status' as violation_type,
    resolution_hint
from {{ ref('dq_completeness_field_metrics') }}
where completeness_field_status = 'contract_violation'
