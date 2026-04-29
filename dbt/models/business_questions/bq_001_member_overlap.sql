select
  'BQ-001' as question_id,
  provider_slug,
  count(*) as source_member_rows,
  count(distinct member_reference) as distinct_source_members,
  count(*) filter (where provider_slug = 'data_provider_5_pacific_shield_insurance') as payer_known_rows,
  count(*) filter (where provider_slug <> 'data_provider_5_pacific_shield_insurance') as provider_known_rows
from {{ source('review', 'silver_members') }}
where {{ active_batch_filter() }}
group by provider_slug
