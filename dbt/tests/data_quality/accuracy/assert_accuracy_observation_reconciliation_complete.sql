select *
from {{ ref('dq_accuracy_observation_reconciliation_metrics') }}
where accuracy_observation_status <> 'complete'
