{{ config(materialized='table') }}

select
    {{ provider_scoped_hash("provider_slug", "'cost_records|cost_amount_or_date'") }}
        as accuracy_financial_metric_id,
    provider_slug,
    'cost_records' as entity,
    'cost_amount_or_date' as field_column,
    count(*) as total_rows,
    count(*) filter (
        where has_missing_cost_amount or has_missing_cost_date
    ) as affected_rows,
    count(*) filter (where has_missing_cost_amount) as missing_amount_rows,
    count(*) filter (where has_missing_cost_date) as missing_date_rows,
    count(*) filter (where source_cost_amount is not null) as populated_amount_rows,
    source_cost_amount_field_name,
    min(source_cost_amount) filter (where source_cost_amount is not null)
        as min_source_cost_amount,
    percentile_cont(0.5) within group (
        order by source_cost_amount
    ) filter (where source_cost_amount is not null) as median_source_cost_amount,
    max(source_cost_amount) filter (where source_cost_amount is not null)
        as max_source_cost_amount,
    'financial_amount_date_preserve_nulls_and_provider_semantics' as resolution_hint,
    case
        when count(*) filter (
            where has_missing_cost_amount or has_missing_cost_date
        ) > 0 then 'managed_financial_semantics_preserved'
        else 'complete'
    end as accuracy_financial_status
from {{ ref('cost_record_fact') }}
group by provider_slug, source_cost_amount_field_name
