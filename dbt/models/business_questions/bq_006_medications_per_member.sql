select
  'BQ-006' as question_id,
  provider_slug,
  member_reference,
  count(distinct medication_reference) as distinct_medication_count,
  count(*) as medication_row_count
from {{ source('review', 'silver_medications') }}
where {{ active_batch_filter() }}
group by provider_slug, member_reference
