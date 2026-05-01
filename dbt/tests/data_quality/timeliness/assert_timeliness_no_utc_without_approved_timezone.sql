select *
from {{ ref('dq_timeliness_contract_violations') }}
where affected_rows > 0
