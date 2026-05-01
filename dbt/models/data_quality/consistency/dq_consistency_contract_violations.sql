{{ config(materialized='table') }}

select
    consistency_reference_metric_id as violation_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    key_without_raw_reference_rows + missing_final_segment_rows as affected_rows,
    case
        when key_without_raw_reference_rows > 0 then 'key_without_raw_reference'
        else 'missing_reference_final_segment'
    end as violation_type,
    'member_reference_normalization' as resolution_hint
from {{ ref('dq_consistency_reference_metrics') }}
where key_without_raw_reference_rows > 0
   or missing_final_segment_rows > 0

union all

select
    consistency_code_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    missing_normalized_token_rows as affected_rows,
    'missing_normalized_code_token' as violation_type,
    'code_description_variant_dimensions' as resolution_hint
from {{ ref('dq_consistency_code_metrics') }}
where missing_normalized_token_rows > 0
