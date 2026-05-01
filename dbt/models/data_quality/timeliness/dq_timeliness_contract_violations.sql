{{ config(materialized='view') }}

select
    timeliness_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    utc_without_approved_timezone_rows as affected_rows,
    'utc_without_temporal_authority' as violation_type,
    'provider_timezone_to_utc_mapping' as resolution_hint
from {{ ref('dq_timeliness_provider_field_metrics') }}
where utc_without_approved_timezone_rows > 0

union all

select
    {{ provider_scoped_hash("provider_slug", "'provider_timezone'") }} as timeliness_metric_id,
    provider_slug,
    'provider_timezone_contract' as entity,
    'provider_timezone' as field_column,
    1 as total_rows,
    1 as affected_rows,
    'timezone_approved_without_timezone_value' as violation_type,
    'provider_timezone_to_utc_mapping' as resolution_hint
from {{ ref('dq_provider_timezone_contract') }}
where timezone_status = 'timezone_approved'
  and provider_timezone is null
