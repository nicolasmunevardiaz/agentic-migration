select
  'BQ-011' as question_id,
  provider_slug,
  medication_reference,
  count(*) as price_record_count,
  avg(cost_amount) as mean_unit_price,
  min(cost_amount) as min_unit_price,
  max(cost_amount) as max_unit_price
from {{ source('review', 'silver_cost_records') }}
where {{ active_batch_filter() }}
group by provider_slug, medication_reference
