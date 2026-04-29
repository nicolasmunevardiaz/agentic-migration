select
  'BQ-007' as question_id,
  provider_slug,
  coalesce(condition_source_code, condition_code_hint, 'unknown') as condition_code,
  max(condition_description) as condition_description,
  count(*) as source_row_count
from {{ source('review', 'silver_conditions') }}
where {{ active_batch_filter() }}
group by provider_slug, coalesce(condition_source_code, condition_code_hint, 'unknown')
