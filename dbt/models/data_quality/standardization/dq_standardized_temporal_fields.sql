{{ config(materialized='view') }}

with temporal_fields as (
    select
        provider_slug,
        'encounters' as entity,
        encounter_source_row_id as source_record_id,
        'encounter_datetime' as field_column,
        encounter_datetime::text as raw_temporal_value,
        encounter_datetime is not null as has_source_temporal_value,
        'business_timestamp' as temporal_role,
        'approved_source_chronology_policy' as resolution_hint
    from {{ ref('encounter_fact') }}

    union all

    select
        provider_slug,
        'medications' as entity,
        medication_source_row_id as source_record_id,
        'medication_datetime' as field_column,
        medication_datetime::text as raw_temporal_value,
        medication_datetime is not null as has_source_temporal_value,
        'business_timestamp' as temporal_role,
        'approved_source_chronology_policy' as resolution_hint
    from {{ ref('medication_fact') }}

    union all

    select
        provider_slug,
        'cost_records' as entity,
        cost_record_id as source_record_id,
        'cost_date' as field_column,
        cost_date::text as raw_temporal_value,
        cost_date is not null as has_source_temporal_value,
        'business_timestamp' as temporal_role,
        'approved_source_chronology_policy' as resolution_hint
    from {{ ref('cost_record_fact') }}

    union all

    select
        provider_slug,
        'coverage_periods' as entity,
        coverage_period_id as source_record_id,
        'coverage_start_date' as field_column,
        coverage_start_date::text as raw_temporal_value,
        coverage_start_date is not null as has_source_temporal_value,
        'business_date' as temporal_role,
        'coverage_period_state_model' as resolution_hint
    from {{ ref('coverage_period_fact') }}

    union all

    select
        provider_slug,
        'coverage_periods' as entity,
        coverage_period_id as source_record_id,
        'coverage_end_date' as field_column,
        coverage_end_date::text as raw_temporal_value,
        coverage_end_date is not null as has_source_temporal_value,
        'business_date' as temporal_role,
        'coverage_period_state_model' as resolution_hint
    from {{ ref('coverage_period_fact') }}

    union all

    select
        provider_slug,
        'observations' as entity,
        observation_source_row_id as source_record_id,
        'observation_datetime' as field_column,
        observation_datetime::text as raw_temporal_value,
        observation_datetime is not null as has_source_temporal_value,
        'business_timestamp' as temporal_role,
        'provider_timezone_to_utc_mapping' as resolution_hint
    from {{ ref('observation_vitals_wide') }}
),

timezone_contract as (
    select *
    from {{ ref('dq_provider_timezone_contract') }}
),

standardized as (
    select
        {{ provider_scoped_hash("temporal_fields.provider_slug", "temporal_fields.entity || '|' || temporal_fields.source_record_id || '|' || temporal_fields.field_column") }}
            as temporal_standardization_id,
        temporal_fields.provider_slug,
        temporal_fields.entity,
        temporal_fields.source_record_id,
        temporal_fields.field_column,
        temporal_fields.temporal_role,
        temporal_fields.raw_temporal_value,
        {{ dq_temporal_has_explicit_offset("temporal_fields.raw_temporal_value") }}
            as has_explicit_offset,
        timezone_contract.provider_timezone,
        {{ dq_parse_status("temporal_fields.raw_temporal_value") }} as parse_status,
        temporal_fields.resolution_hint
    from temporal_fields
    left join timezone_contract
        on temporal_fields.provider_slug = timezone_contract.provider_slug
)

select
    temporal_standardization_id,
    provider_slug,
    entity,
    source_record_id,
    field_column,
    temporal_role,
    raw_temporal_value,
    case
        when parse_status = 'missing' then null::timestamp without time zone
        when has_explicit_offset then raw_temporal_value::timestamp without time zone
        when provider_timezone is not null then raw_temporal_value::timestamp without time zone
        else null::timestamp without time zone
    end as local_ntz_value,
    provider_timezone,
    case
        when parse_status = 'missing' then null::timestamp with time zone
        when has_explicit_offset then raw_temporal_value::timestamp with time zone
        when provider_timezone is not null
            then raw_temporal_value::timestamp without time zone at time zone provider_timezone
        else null::timestamp with time zone
    end as utc_value,
    parse_status,
    case
        when parse_status = 'missing' then 'timezone_pending'
        when has_explicit_offset then 'offset_derived'
        when provider_timezone is not null then 'timezone_approved'
        else 'timezone_pending'
    end as timezone_status,
    has_explicit_offset,
    resolution_hint,
    case
        when parse_status = 'missing' then 'missing_source_temporal_value'
        when has_explicit_offset then 'standardized_from_source_offset'
        when provider_timezone is null then 'timezone_pending'
        else 'standardized'
    end as temporal_standardization_status
from standardized
