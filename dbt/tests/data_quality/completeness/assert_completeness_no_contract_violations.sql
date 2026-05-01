select *
from {{ ref('dq_completeness_contract_violations') }}
where affected_rows > 0
