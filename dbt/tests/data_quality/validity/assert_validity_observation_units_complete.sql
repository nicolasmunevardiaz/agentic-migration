select *
from {{ ref('dq_validity_domain_metrics') }}
where entity = 'observations'
  and validity_domain_status <> 'complete'
