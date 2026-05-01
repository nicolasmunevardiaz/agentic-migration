{{ config(materialized='table') }}

select
    {{ provider_scoped_hash("provider_slug", "condition_source_code || '|' || coalesce(condition_code_hint, '')") }}
        as condition_code_domain_mapping_id,
    provider_slug,
    condition_source_code,
    condition_code_hint,
    min(condition_description) as representative_condition_description,
    count(*) as condition_row_count,
    count(*) filter (where source_code_matches_hint) as matching_hint_rows,
    count(*) filter (where not source_code_matches_hint) as domain_hint_mismatch_rows,
    'source_code_primary' as source_code_domain_role,
    'metadata_hint' as hint_code_domain_role,
    case
        when count(*) filter (where condition_source_code is null) > 0
            then 'missing_source_code'
        when count(*) filter (where condition_code_hint is null) > 0
            then 'missing_code_hint'
        when count(*) filter (where not source_code_matches_hint) > 0
            then 'managed_source_code_hint_domain_mismatch'
        else 'complete'
    end as condition_code_consistency_status
from {{ ref('condition_fact') }}
group by provider_slug, condition_source_code, condition_code_hint
