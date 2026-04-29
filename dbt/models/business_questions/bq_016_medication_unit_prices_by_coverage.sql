select
  'BQ-016' as question_id,
  costs.provider_slug,
  coalesce(coverage.coverage_status, 'UNKNOWN') as coverage_status,
  costs.medication_reference,
  count(*) as price_record_count,
  avg(costs.cost_amount) as mean_unit_price
from {{ source('review', 'silver_cost_records') }} costs
left join {{ source('review', 'silver_coverage_periods') }} coverage
  on costs.provider_slug = coverage.provider_slug
 and costs.member_reference = coverage.member_reference
 and {{ active_batch_filter('coverage') }}
where {{ active_batch_filter('costs') }}
group by costs.provider_slug, coalesce(coverage.coverage_status, 'UNKNOWN'), costs.medication_reference
