{{ config(materialized='view') }}

select
    cost_amount_source_id,
    provider_slug,
    source_cost_amount_field_name,
    'medication_financial_source_amount' as source_amount_role,
    count(*) as cost_record_row_count,
    count(*) filter (where source_cost_amount is not null) as populated_amount_row_count,
    count(*) filter (where has_missing_cost_amount) as missing_amount_row_count
from {{ ref('cost_record_source_normalized') }}
group by
    cost_amount_source_id,
    provider_slug,
    source_cost_amount_field_name
