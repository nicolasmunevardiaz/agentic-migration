select distinct fact.coverage_status_id
from {{ ref('coverage_period_fact') }} as fact
left join {{ ref('coverage_status_dimension') }} as dim
    on fact.coverage_status_id = dim.coverage_status_id
where dim.coverage_status_id is null
