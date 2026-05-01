select *
from {{ ref('dq_uniqueness_coverage_period_metrics') }}
where total_rows <> survivor_rows + excess_duplicate_rows
