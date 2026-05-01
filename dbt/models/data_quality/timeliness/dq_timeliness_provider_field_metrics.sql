{{ config(materialized='view') }}

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || field_column") }}
        as timeliness_metric_id,
    provider_slug,
    entity,
    field_column,
    temporal_role,
    count(*) as total_rows,
    count(*) filter (where parse_status = 'missing') as missing_source_value_rows,
    count(*) filter (where parse_status = 'parsed') as parsed_source_value_rows,
    count(*) filter (where timezone_status = 'timezone_pending') as timezone_pending_rows,
    count(*) filter (where timezone_status = 'offset_derived') as offset_derived_rows,
    count(*) filter (where timezone_status = 'timezone_approved') as timezone_approved_rows,
    count(*) filter (where local_ntz_value is not null) as local_ntz_value_rows,
    count(*) filter (where utc_value is not null) as utc_value_rows,
    count(*) filter (
        where utc_value is not null
          and timezone_status not in ('offset_derived', 'timezone_approved')
    ) as utc_without_approved_timezone_rows,
    min(raw_temporal_value) filter (where raw_temporal_value is not null) as min_raw_temporal_value,
    max(raw_temporal_value) filter (where raw_temporal_value is not null) as max_raw_temporal_value,
    case
        when count(*) filter (
            where utc_value is not null
              and timezone_status not in ('offset_derived', 'timezone_approved')
        ) > 0 then 'contract_violation'
        when count(*) filter (where parse_status = 'missing') > 0 then 'open_missing_temporal_value'
        when count(*) filter (where timezone_status = 'timezone_pending') > 0 then 'open_timezone_pending'
        else 'complete'
    end as timeliness_metric_status
from {{ ref('dq_standardized_temporal_fields') }}
group by provider_slug, entity, field_column, temporal_role
