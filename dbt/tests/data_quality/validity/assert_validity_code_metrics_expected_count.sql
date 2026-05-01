select *
from (
    select count(*) as metric_count
    from {{ ref('dq_validity_code_metrics') }}
) as metrics
where metric_count <> 8
