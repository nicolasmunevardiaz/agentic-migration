select
  'BQ-010' as question_id,
  provider_slug,
  count(*) as observation_count,
  avg(height_cm) as avg_height_cm,
  avg(weight_kg) as avg_weight_kg,
  avg(systolic_bp) as avg_systolic_bp,
  count(*) filter (where height_cm is null) as missing_height_count,
  count(*) filter (where weight_kg is null) as missing_weight_count,
  count(*) filter (where systolic_bp is null) as missing_systolic_count
from {{ source('review', 'silver_observations') }}
where {{ active_batch_filter() }}
group by provider_slug
