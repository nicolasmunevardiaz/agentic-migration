select fact.medication_provider_id
from {{ ref('medication_fact') }} as fact
left join {{ ref('medication_code_dimension') }} as code_dim
    on fact.medication_code_id = code_dim.medication_code_id
left join {{ ref('medication_record_status_dimension') }} as status_dim
    on fact.medication_record_status_id = status_dim.medication_record_status_id
where code_dim.medication_code_id is null
   or status_dim.medication_record_status_id is null
