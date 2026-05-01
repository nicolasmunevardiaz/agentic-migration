select *
from {{ ref('dq_validity_contract_violations') }}
