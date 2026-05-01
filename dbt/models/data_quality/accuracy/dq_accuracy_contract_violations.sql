{{ config(materialized='table') }}

select
    null::text as violation_id,
    null::text as provider_slug,
    null::text as entity,
    null::text as field_column,
    0::bigint as total_rows,
    0::bigint as affected_rows,
    null::text as violation_status,
    null::text as resolution_hint
where false
