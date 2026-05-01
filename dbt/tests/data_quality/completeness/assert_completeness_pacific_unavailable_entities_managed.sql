select *
from {{ ref('dq_completeness_provider_entity_availability') }}
where provider_slug = 'data_provider_5_pacific_shield_insurance'
  and entity in ('encounters', 'conditions', 'observations', 'medications', 'cost_records')
  and completeness_entity_status <> 'managed_provider_not_applicable'
