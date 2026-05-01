{{ config(materialized='view') }}

with providers as (
    select distinct provider_slug
    from {{ ref('patient_dimension') }}
)

select
    provider_slug,
    null::text as provider_timezone,
    'timezone_pending' as timezone_status,
    'temporal_contract_requires_ianna_timezone_before_utc_derivation' as resolution_hint
from providers
