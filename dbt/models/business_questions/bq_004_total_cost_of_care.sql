with costs as (
  select *
  from {{ source('review', 'silver_cost_records') }}
  where {{ active_batch_filter() }}
)
select
  'BQ-004' as question_id,
  provider_slug,
  member_reference,
  count(*) as cost_record_count,
  sum(cost_amount) as total_cost,
  avg(cost_amount) as mean_cost,
  percentile_cont(0.5) within group (order by cost_amount) as median_cost,
  percentile_cont(0.9) within group (order by cost_amount) as p90_cost
from costs
group by provider_slug, member_reference
