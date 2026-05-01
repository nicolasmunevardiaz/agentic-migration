select *
from {{ ref('dq_accuracy_contract_violations') }}
