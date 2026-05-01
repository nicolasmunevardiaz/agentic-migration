{{ config(materialized='view') }}

select
    temporal_standardization_id as issue_id,
    provider_slug,
    entity,
    field_column,
    'timeliness' as category,
    temporal_standardization_status as issue_status,
    resolution_hint
from {{ ref('dq_standardized_temporal_fields') }}
where temporal_standardization_status in (
    'missing_source_temporal_value',
    'timezone_pending'
)

union all

select
    reference_standardization_id,
    provider_slug,
    entity,
    field_column,
    'consistency' as category,
    reference_standardization_status,
    resolution_hint
from {{ ref('dq_standardized_reference_fields') }}
where reference_standardization_status <> 'reference_resolved'

union all

select
    code_standardization_id,
    provider_slug,
    entity,
    field_column,
    'validity' as category,
    code_standardization_status,
    resolution_hint
from {{ ref('dq_standardized_code_fields') }}
where code_standardization_status <> 'normalized'

union all

select
    amount_standardization_id,
    provider_slug,
    entity,
    field_column,
    'accuracy' as category,
    amount_standardization_status,
    resolution_hint
from {{ ref('dq_standardized_amount_fields') }}
where amount_standardization_status <> 'parsed_numeric_amount'
