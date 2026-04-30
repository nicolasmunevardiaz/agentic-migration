select
  'BQ-002' as question_id,
  provider_slug,
  coalesce(gender_code, 'unknown') as gender_code,
  count(*) as member_count
from {{ source('review', 'silver_members') }}
where {{ active_batch_filter() }}
group by provider_slug, coalesce(gender_code, 'unknown')
