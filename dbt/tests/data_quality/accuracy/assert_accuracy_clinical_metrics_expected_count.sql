select *
from (
    select count(*) as metric_count
    from {{ ref('dq_accuracy_clinical_semantic_metrics') }}
) as metrics
where metric_count <> 8
