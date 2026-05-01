{{ config(materialized='view') }}

select
    medication_code_id,
    provider_slug,
    medication_source_code,
    min(medication_description) as representative_medication_description,
    count(distinct medication_source_code_raw) as raw_code_variant_count,
    count(distinct medication_description) as description_variant_count,
    count(distinct medication_source_code_raw) > 1 as has_raw_code_variants,
    count(distinct medication_description) > 1 as has_description_variants,
    count(*) as medication_row_count
from {{ ref('medication_source_normalized') }}
group by
    medication_code_id,
    provider_slug,
    medication_source_code
