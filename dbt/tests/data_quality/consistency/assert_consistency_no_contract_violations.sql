select *
from {{ ref('dq_consistency_contract_violations') }}
where affected_rows > 0
