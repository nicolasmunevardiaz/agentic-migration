select fact.encounter_provider_id
from {{ ref('encounter_fact') }} as fact
left join {{ ref('encounter_coverage_status_dimension') }} as coverage_dim
    on fact.encounter_coverage_status_id = coverage_dim.encounter_coverage_status_id
left join {{ ref('encounter_record_status_dimension') }} as record_dim
    on fact.encounter_record_status_id = record_dim.encounter_record_status_id
where coverage_dim.encounter_coverage_status_id is null
   or record_dim.encounter_record_status_id is null
