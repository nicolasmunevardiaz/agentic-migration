{{ config(materialized='table') }}

with description_conflicts as (
    select
        provider_slug,
        lower(trim(medication_description)) as normalized_description,
        count(distinct medication_source_code) as distinct_code_count
    from {{ ref('medication_fact') }}
    where medication_description is not null
      and medication_source_code is not null
    group by provider_slug, lower(trim(medication_description))
),

canonical as (
    select
        medication_code_dimension.provider_slug,
        medication_code_dimension.medication_code_id as canonical_medication_id,
        medication_code_dimension.medication_source_code as canonical_medication_code,
        medication_code_dimension.representative_medication_description
            as canonical_medication_description,
        medication_code_dimension.raw_code_variant_count,
        medication_code_dimension.description_variant_count,
        medication_code_dimension.medication_row_count,
        medication_code_dimension.has_raw_code_variants,
        medication_code_dimension.has_description_variants,
        coalesce(description_conflicts.distinct_code_count, 1)
            as description_distinct_code_count
    from {{ ref('medication_code_dimension') }} as medication_code_dimension
    left join description_conflicts
        on medication_code_dimension.provider_slug = description_conflicts.provider_slug
       and lower(trim(medication_code_dimension.representative_medication_description))
           = description_conflicts.normalized_description
)

select
    canonical_medication_id,
    provider_slug,
    canonical_medication_code,
    canonical_medication_description,
    raw_code_variant_count,
    description_variant_count,
    description_distinct_code_count,
    medication_row_count,
    case
        when description_distinct_code_count > 1
            then 'medication_same_description_different_code_preserve_conflict'
        when has_raw_code_variants or has_description_variants
            then 'medication_same_normalized_code_canonicalizes_with_variants'
        else 'medication_no_accuracy_variant'
    end as canonical_rule_id,
    case
        when description_distinct_code_count > 1
            then 'managed_description_match_code_conflict_preserved'
        when has_raw_code_variants or has_description_variants
            then 'managed_canonical_medication_code_with_variants'
        else 'complete'
    end as medication_canonical_status
from canonical
