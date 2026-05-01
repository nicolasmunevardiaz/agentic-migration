{{ config(materialized='view') }}

select
    timeliness_metric_id as finding_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    missing_source_value_rows,
    timezone_pending_rows,
    utc_without_approved_timezone_rows,
    timeliness_metric_status as finding_status,
    case
        when utc_without_approved_timezone_rows > 0 then 'critical'
        when missing_source_value_rows = total_rows then 'critical'
        when missing_source_value_rows > 0 then 'high'
        when timezone_pending_rows > 0 then 'high'
        else 'low'
    end as severity,
    case
        when utc_without_approved_timezone_rows > 0 then 'provider_timezone_to_utc_mapping'
        when missing_source_value_rows > 0 then 'approved_source_chronology_policy'
        when timezone_pending_rows > 0 then 'provider_timezone_to_utc_mapping'
        else 'none'
    end as resolution_hint
from {{ ref('dq_timeliness_provider_field_metrics') }}
where timeliness_metric_status <> 'complete'
