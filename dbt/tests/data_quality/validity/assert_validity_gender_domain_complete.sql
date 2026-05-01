select *
from {{ ref('dq_validity_domain_metrics') }}
where entity = 'patients'
  and field_column = 'gender'
  and validity_domain_status <> 'complete'
