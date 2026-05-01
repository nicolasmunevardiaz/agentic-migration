select *
from {{ ref('dq_accuracy_findings') }}
where finding_status like 'hitl_required_%'
