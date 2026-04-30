with missing_status_dimension as (
    select fact.cost_record_id
    from {{ ref('cost_record_fact') }} fact
    left join {{ ref('cost_record_status_dimension') }} dim
        on fact.cost_record_status_id = dim.cost_record_status_id
    where dim.cost_record_status_id is null
),

missing_amount_source_dimension as (
    select fact.cost_record_id
    from {{ ref('cost_record_fact') }} fact
    left join {{ ref('cost_amount_source_dimension') }} dim
        on fact.cost_amount_source_id = dim.cost_amount_source_id
    where dim.cost_amount_source_id is null
)

select 'missing_status_dimension' as failure_reason, cost_record_id
from missing_status_dimension

union all

select 'missing_amount_source_dimension' as failure_reason, cost_record_id
from missing_amount_source_dimension
