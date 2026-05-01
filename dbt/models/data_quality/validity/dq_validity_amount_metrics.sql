{{ config(materialized='table') }}

with amount_checks as (
    select
        provider_slug,
        entity,
        field_column,
        count(*) as total_rows,
        count(*) filter (
            where raw_amount is not null
              and numeric_amount is null
        ) as failed_numeric_parse_rows,
        count(*) filter (where has_nonpositive_cost_amount) as nonpositive_amount_rows,
        min(resolution_hint) as resolution_hint
    from {{ ref('dq_standardized_amount_fields') }}
    group by provider_slug, entity, field_column
)

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || field_column") }}
        as validity_amount_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    failed_numeric_parse_rows,
    nonpositive_amount_rows,
    failed_numeric_parse_rows + nonpositive_amount_rows as affected_rows,
    resolution_hint,
    case
        when failed_numeric_parse_rows > 0 then 'contract_violation'
        when nonpositive_amount_rows > 0 then 'open_nonpositive_amount'
        else 'complete'
    end as validity_amount_status
from amount_checks
