{{ config(materialized='table') }}

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || field_column") }}
        as consistency_reference_metric_id,
    provider_slug,
    entity,
    field_column,
    count(*) as total_rows,
    count(*) filter (where is_missing_reference) as missing_reference_rows,
    count(*) filter (where is_unknown_reference) as unknown_reference_rows,
    count(*) filter (where raw_reference is not null) as present_reference_rows,
    count(*) filter (where is_unresolved_reference) as unresolved_reference_rows,
    count(*) filter (where is_resolved_reference) as resolved_reference_rows,
    count(distinct reference_final_segment) filter (
        where reference_final_segment is not null
    ) as distinct_reference_final_segment_count,
    count(distinct normalized_reference_key) filter (
        where normalized_reference_key is not null
    ) as distinct_provider_scoped_reference_key_count,
    count(*) filter (
        where (is_missing_reference or is_unknown_reference)
          and normalized_reference_key is not null
    ) as key_without_raw_reference_rows,
    count(*) filter (
        where not is_missing_reference
          and not is_unknown_reference
          and raw_reference is not null
          and reference_final_segment is null
    ) as missing_final_segment_rows,
    case
        when count(*) filter (
            where (is_missing_reference or is_unknown_reference)
              and normalized_reference_key is not null
        ) > 0 then 'contract_violation'
        when count(*) filter (
            where not is_missing_reference
              and not is_unknown_reference
              and raw_reference is not null
              and reference_final_segment is null
        ) > 0 then 'contract_violation'
        when count(*) filter (
            where consistency_reference_management_status
                = 'managed_unresolved_reference_preserved'
        ) > 0 then 'managed_unresolved_reference_preserved'
        when count(*) filter (
            where consistency_reference_management_status
                = 'managed_unknown_reference_preserved'
        ) > 0 then 'managed_unknown_reference_preserved'
        when count(*) filter (
            where consistency_reference_management_status
                = 'managed_missing_reference_preserved'
        ) > 0 then 'managed_missing_reference_preserved'
        else 'complete'
    end as consistency_reference_status
from {{ ref('dq_consistency_reference_bridge') }}
group by provider_slug, entity, field_column
