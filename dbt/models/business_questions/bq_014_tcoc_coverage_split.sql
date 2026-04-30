select
  'BQ-014' as question_id,
  encounters.provider_slug,
  coalesce(encounters.coverage_status, 'UNKNOWN') as encounter_coverage_status,
  count(distinct encounters.encounter_reference) as encounter_count,
  count(costs.cost_amount) as cost_record_count,
  sum(costs.cost_amount) as total_cost
from {{ source('review', 'silver_encounters') }} encounters
left join {{ source('review', 'silver_cost_records') }} costs
  on encounters.provider_slug = costs.provider_slug
 and encounters.member_reference = costs.member_reference
 and {{ active_batch_filter('costs') }}
where {{ active_batch_filter('encounters') }}
group by encounters.provider_slug, coalesce(encounters.coverage_status, 'UNKNOWN')
