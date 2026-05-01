{{ config(materialized='view') }}

select
    md5(
        'medication_code_variant|'
        || provider_slug
        || '|'
        || coalesce(medication_source_code, 'UNKNOWN')
        || '|'
        || coalesce(medication_source_code_raw, 'UNKNOWN')
    ) as medication_code_variant_id,
    medication_code_id,
    provider_slug,
    medication_source_code,
    medication_source_code_raw,
    medication_source_code_raw is distinct from medication_source_code as differs_from_normalized_code,
    count(*) as medication_row_count
from {{ ref('medication_source_normalized') }}
group by
    medication_code_id,
    provider_slug,
    medication_source_code,
    medication_source_code_raw
