{{ config(materialized='view') }}

select
    md5(
        'medication_description_variant|'
        || provider_slug
        || '|'
        || coalesce(medication_source_code, 'UNKNOWN')
        || '|'
        || coalesce(medication_description, 'UNKNOWN')
    ) as medication_description_variant_id,
    medication_code_id,
    provider_slug,
    medication_source_code,
    medication_description,
    count(*) as medication_row_count
from {{ ref('medication_source_normalized') }}
group by
    medication_code_id,
    provider_slug,
    medication_source_code,
    medication_description
