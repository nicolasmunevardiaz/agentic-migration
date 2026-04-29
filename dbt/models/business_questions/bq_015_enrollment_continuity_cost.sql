with coverage_summary as (
  select
    provider_slug,
    member_reference,
    count(*) as coverage_period_count
  from {{ source('review', 'silver_coverage_periods') }}
  where {{ active_batch_filter() }}
  group by provider_slug, member_reference
),
costs as (
  select *
  from {{ source('review', 'silver_cost_records') }}
  where {{ active_batch_filter() }}
)
select
  'BQ-015' as question_id,
  costs.provider_slug,
  case
    when coalesce(coverage_summary.coverage_period_count, 0) <= 1 then 'continuous_or_single_period'
    else 'multiple_periods_review_needed'
  end as enrollment_continuity_group,
  count(*) as cost_record_count,
  avg(costs.cost_amount) as mean_cost,
  sum(costs.cost_amount) as total_cost
from costs
left join coverage_summary
  on costs.provider_slug = coverage_summary.provider_slug
 and costs.member_reference = coverage_summary.member_reference
group by costs.provider_slug, enrollment_continuity_group
