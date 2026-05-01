{{ config(materialized='view') }}

select
    condition_code_id,
    provider_slug,
    condition_source_code,
    condition_code_hint,
    min(condition_description) as representative_condition_description,
    count(*) as condition_row_count
from {{ ref('condition_source_normalized') }}
group by
    condition_code_id,
    provider_slug,
    condition_source_code,
    condition_code_hint
