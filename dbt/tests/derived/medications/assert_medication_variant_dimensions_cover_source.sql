with missing_code_variants as (
    select source.medication_source_row_id
    from {{ ref('medication_source_normalized') }} as source
    left join {{ ref('medication_code_variant_dimension') }} as code_variant
        on source.medication_code_id = code_variant.medication_code_id
       and source.medication_source_code_raw = code_variant.medication_source_code_raw
    where code_variant.medication_code_variant_id is null
),

missing_description_variants as (
    select source.medication_source_row_id
    from {{ ref('medication_source_normalized') }} as source
    left join {{ ref('medication_description_variant_dimension') }} as description_variant
        on source.medication_code_id = description_variant.medication_code_id
       and source.medication_description = description_variant.medication_description
    where description_variant.medication_description_variant_id is null
)

select 'missing_code_variant' as failure_reason, medication_source_row_id
from missing_code_variants

union all

select 'missing_description_variant' as failure_reason, medication_source_row_id
from missing_description_variants
