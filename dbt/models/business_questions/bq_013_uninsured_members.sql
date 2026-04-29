select
  'BQ-013' as question_id,
  provider_slug,
  count(*) as coverage_row_count,
  count(*) filter (where coverage_status = 'UNINSURED') as uninsured_row_count,
  count(*) filter (where coverage_status = 'UNKNOWN') as unknown_coverage_row_count
from {{ source('review', 'silver_coverage_periods') }}
where {{ active_batch_filter() }}
group by provider_slug
