with coverage as (
  select *
  from {{ source('review', 'silver_coverage_periods') }}
  where {{ active_batch_filter() }}
)
select
  'BQ-012' as question_id,
  provider_slug,
  member_reference,
  count(*) as coverage_period_count,
  min(coverage_start_date) as first_coverage_start_date,
  max(coverage_end_date) as last_coverage_end_date,
  count(*) filter (where coverage_end_date is not null) as ended_period_count
from coverage
group by provider_slug, member_reference
