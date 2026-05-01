select *
from (
    select count(*) as metric_count
    from {{ ref('dq_uniqueness_coverage_period_metrics') }}
) as metrics
where metric_count <> 5
