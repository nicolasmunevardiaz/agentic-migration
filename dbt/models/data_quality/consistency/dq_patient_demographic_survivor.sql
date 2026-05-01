{{ config(materialized='table') }}

with gender_frequency as (
    select
        provider_slug,
        patient_provider_member_id,
        gender_code_normalized,
        count(*) as gender_value_row_count,
        max(loaded_at) as latest_loaded_at,
        max(source_row_id) as tie_breaker_source_row_id
    from {{ ref('patient_source_normalized') }}
    where gender_code_normalized is not null
    group by provider_slug, patient_provider_member_id, gender_code_normalized
),

ranked_gender as (
    select
        *,
        row_number() over (
            partition by provider_slug, patient_provider_member_id
            order by gender_value_row_count desc, latest_loaded_at desc nulls last,
                tie_breaker_source_row_id desc
        ) as survivor_rank
    from gender_frequency
),

birth_date_frequency as (
    select
        provider_slug,
        patient_provider_member_id,
        birth_date,
        count(*) as birth_date_value_row_count,
        max(loaded_at) as latest_loaded_at,
        max(source_row_id) as tie_breaker_source_row_id
    from {{ ref('patient_source_normalized') }}
    where birth_date is not null
      and not coalesce(birth_date_implausible, false)
    group by provider_slug, patient_provider_member_id, birth_date
),

ranked_birth_date as (
    select
        *,
        row_number() over (
            partition by provider_slug, patient_provider_member_id
            order by birth_date_value_row_count desc, latest_loaded_at desc nulls last,
                tie_breaker_source_row_id desc
        ) as survivor_rank
    from birth_date_frequency
)

select
    {{ provider_scoped_hash("patient_dimension.provider_slug", "patient_dimension.patient_provider_member_id || '|demographic_survivor'") }}
        as patient_demographic_survivor_id,
    patient_dimension.provider_slug,
    patient_dimension.patient_provider_member_id,
    ranked_gender.gender_code_normalized as survivor_gender_code,
    ranked_birth_date.birth_date as survivor_birth_date,
    patient_dimension.distinct_gender_code_count as gender_variant_count,
    patient_dimension.distinct_birth_date_count as birth_date_variant_count,
    patient_dimension.has_gender_conflict,
    patient_dimension.has_birth_date_conflict,
    patient_dimension.has_gender_conflict
        or patient_dimension.has_birth_date_conflict as has_demographic_conflict,
    'provider_scoped_frequency_latest_loaded_tiebreaker' as survivor_rule_id,
    ranked_gender.gender_value_row_count as survivor_gender_row_count,
    ranked_birth_date.birth_date_value_row_count as survivor_birth_date_row_count,
    case
        when patient_dimension.has_gender_conflict
          or patient_dimension.has_birth_date_conflict
            then 'managed_demographic_survivor_selected'
        else 'complete'
    end as demographic_survivor_status
from {{ ref('patient_dimension') }} as patient_dimension
left join ranked_gender
    on patient_dimension.provider_slug = ranked_gender.provider_slug
   and patient_dimension.patient_provider_member_id
       = ranked_gender.patient_provider_member_id
   and ranked_gender.survivor_rank = 1
left join ranked_birth_date
    on patient_dimension.provider_slug = ranked_birth_date.provider_slug
   and patient_dimension.patient_provider_member_id
       = ranked_birth_date.patient_provider_member_id
   and ranked_birth_date.survivor_rank = 1
