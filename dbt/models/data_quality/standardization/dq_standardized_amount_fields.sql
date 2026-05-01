{{ config(materialized='view') }}

select
    {{ provider_scoped_hash("provider_slug", "cost_record_id || '|cost_amount'") }}
        as amount_standardization_id,
    provider_slug,
    'cost_records' as entity,
    cost_record_id as source_record_id,
    'cost_amount' as field_column,
    source_cost_amount::text as raw_amount,
    source_cost_amount as numeric_amount,
    source_cost_amount_field_name as amount_source_field,
    has_missing_cost_amount,
    has_nonpositive_cost_amount,
    'amount_source_requiredness_policy' as resolution_hint,
    case
        when has_missing_cost_amount then 'missing_amount'
        when has_nonpositive_cost_amount then 'nonpositive_amount'
        else 'parsed_numeric_amount'
    end as amount_standardization_status
from {{ ref('cost_record_fact') }}
