select *
from (
    select count(*) as metric_count
    from {{ ref('dq_accuracy_financial_metrics') }}
) as metrics
where metric_count <> 4
