select count(*) as metric_count
from {{ ref('dq_completeness_field_metrics') }}
having count(*) <> 50
