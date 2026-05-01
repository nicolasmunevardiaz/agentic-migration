select *
from {{ ref('dq_uniqueness_coverage_period_metrics') }}
where duplicate_key_group_count > 0
  and uniqueness_metric_status <> 'managed_duplicate_key_survivor_applied'
