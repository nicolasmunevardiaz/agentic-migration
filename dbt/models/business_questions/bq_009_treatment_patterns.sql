select
  'BQ-009' as question_id,
  provider_slug,
  coalesce(condition_reference, 'missing_condition_reference') as condition_reference,
  coalesce(medication_source_code, medication_reference, 'unknown_medication') as medication_code,
  count(*) as medication_condition_rows,
  count(distinct member_reference) as member_count
from {{ source('review', 'silver_medications') }}
where {{ active_batch_filter() }}
group by
  provider_slug,
  coalesce(condition_reference, 'missing_condition_reference'),
  coalesce(medication_source_code, medication_reference, 'unknown_medication')
