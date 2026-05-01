{{ config(materialized='table') }}

select
    medication_code_id as medication_code_consistency_bridge_id,
    provider_slug,
    medication_source_code,
    medication_source_code as canonical_medication_code,
    representative_medication_description as canonical_medication_description,
    raw_code_variant_count,
    description_variant_count,
    has_raw_code_variants,
    has_description_variants,
    medication_row_count,
    case
        when has_description_variants then 'description_conflict_preserved'
        when has_raw_code_variants then 'same_normalized_code_canonicalized'
        else 'not_applicable_no_variants'
    end as canonical_rule_id,
    case
        when has_description_variants
            then 'managed_description_match_code_conflict_preserved'
        when has_raw_code_variants
            then 'managed_canonical_medication_code_with_variants'
        else 'complete'
    end as medication_code_consistency_status
from {{ ref('medication_code_dimension') }}
