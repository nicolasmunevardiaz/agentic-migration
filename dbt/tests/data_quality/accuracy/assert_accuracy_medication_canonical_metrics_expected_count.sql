select *
from (
    select count(*) as metric_count
    from {{ ref('dq_accuracy_medication_canonical_dimension') }}
) as metrics
where metric_count <> 700
