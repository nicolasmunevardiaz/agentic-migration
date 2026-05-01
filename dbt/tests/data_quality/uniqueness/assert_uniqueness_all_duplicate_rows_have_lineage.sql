select *
from {{ ref('dq_uniqueness_coverage_period_key_groups') }}
where has_duplicate_period_key
  and missing_required_lineage_rows > 0
