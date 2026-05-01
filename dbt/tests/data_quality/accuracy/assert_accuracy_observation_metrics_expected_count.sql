select *
from (
    select count(*) as metric_count
    from {{ ref('dq_accuracy_observation_reconciliation_metrics') }}
) as metrics
where metric_count <> 4
