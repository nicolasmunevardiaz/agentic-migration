with source_counts as (
    select
        medication_code_id,
        provider_slug,
        medication_source_code,
        count(distinct medication_source_code_raw) as raw_code_variant_count,
        count(distinct medication_description) as description_variant_count
    from {{ ref('medication_source_normalized') }}
    group by medication_code_id, provider_slug, medication_source_code
),

dimension_counts as (
    select
        medication_code_id,
        provider_slug,
        medication_source_code,
        raw_code_variant_count,
        description_variant_count
    from {{ ref('medication_code_dimension') }}
)

select
    source_counts.provider_slug,
    source_counts.medication_source_code
from source_counts
join dimension_counts
    using (medication_code_id, provider_slug, medication_source_code)
where source_counts.raw_code_variant_count != dimension_counts.raw_code_variant_count
   or source_counts.description_variant_count != dimension_counts.description_variant_count
