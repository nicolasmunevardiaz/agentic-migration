select
  'BQ-008' as question_id,
  provider_slug,
  coalesce(medication_source_code, medication_reference, 'unknown') as medication_code,
  max(medication_description) as medication_description,
  count(*) as source_row_count
from {{ source('review', 'silver_medications') }}
where {{ active_batch_filter() }}
group by provider_slug, coalesce(medication_source_code, medication_reference, 'unknown')
