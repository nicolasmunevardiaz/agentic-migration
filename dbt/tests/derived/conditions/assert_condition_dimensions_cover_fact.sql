select fact.condition_provider_id
from {{ ref('condition_fact') }} as fact
left join {{ ref('condition_code_dimension') }} as code_dim
    on fact.condition_code_id = code_dim.condition_code_id
left join {{ ref('condition_record_status_dimension') }} as status_dim
    on fact.condition_record_status_id = status_dim.condition_record_status_id
where code_dim.condition_code_id is null
   or status_dim.condition_record_status_id is null
