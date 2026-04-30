with members as (
  select *
  from {{ source('review', 'silver_members') }}
  where {{ active_batch_filter() }}
)
select
  'BQ-003' as question_id,
  provider_slug,
  case
    when birth_date is null then 'missing_birth_date'
    when birth_date > current_date then 'invalid_future_birth_date'
    when age(current_date, birth_date) < interval '18 years' then '00_17'
    when age(current_date, birth_date) < interval '35 years' then '18_34'
    when age(current_date, birth_date) < interval '50 years' then '35_49'
    when age(current_date, birth_date) < interval '65 years' then '50_64'
    else '65_plus'
  end as age_band,
  count(*) as member_count
from members
group by provider_slug, age_band
