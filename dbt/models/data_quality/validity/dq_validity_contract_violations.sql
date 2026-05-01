{{ config(materialized='table') }}

select
    validity_code_metric_id as violation_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    failed_tokenization_rows + invalid_token_format_rows as affected_rows,
    validity_code_status as violation_status,
    resolution_hint
from {{ ref('dq_validity_code_metrics') }}
where validity_code_status = 'contract_violation'

union all

select
    validity_amount_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    failed_numeric_parse_rows,
    validity_amount_status,
    resolution_hint
from {{ ref('dq_validity_amount_metrics') }}
where validity_amount_status = 'contract_violation'
