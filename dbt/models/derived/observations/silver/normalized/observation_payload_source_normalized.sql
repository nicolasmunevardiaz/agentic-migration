{{ config(materialized='view') }}

with source_observations as (
    select
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        observation_reference,
        member_reference,
        encounter_reference,
        observation_datetime,
        observation_payload_raw,
        height_cm,
        weight_kg,
        systolic_bp,
        record_status,
        review_batch_id,
        loaded_at
    from {{ source('landing', 'observations') }}
    where {{ active_batch_filter() }}
),

extracted as (
    select
        {{ provider_scoped_hash('provider_slug', 'source_row_id') }} as observation_source_row_id,
        {{ provider_scoped_hash('provider_slug', 'observation_reference') }} as observation_provider_id,
        {{ provider_scoped_hash('provider_slug', 'member_reference') }} as patient_provider_member_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        observation_reference,
        member_reference,
        encounter_reference,
        observation_datetime,
        observation_payload_raw is not null as has_payload,
        observation_payload_raw #>> '{type}' as payload_type,
        nullif(observation_payload_raw #>> '{height,value}', '')::numeric as payload_height_cm,
        observation_payload_raw #>> '{height,u}' as payload_height_unit,
        nullif(observation_payload_raw #>> '{weight,value}', '')::numeric as payload_weight_kg,
        observation_payload_raw #>> '{weight,u}' as payload_weight_unit,
        nullif(observation_payload_raw #>> '{blood_pressure,systolic}', '')::numeric
            as payload_systolic_bp,
        nullif(observation_payload_raw #>> '{blood_pressure,diastolic}', '')::numeric
            as payload_diastolic_bp,
        observation_payload_raw #>> '{blood_pressure,u}' as payload_blood_pressure_unit,
        nullif(observation_payload_raw #>> '{pulse,value}', '')::numeric as payload_pulse_lpm,
        observation_payload_raw #>> '{pulse,u}' as payload_pulse_unit,
        nullif(observation_payload_raw #>> '{temperature,value}', '')::numeric
            as payload_temperature_c,
        observation_payload_raw #>> '{temperature,u}' as payload_temperature_unit,
        nullif(observation_payload_raw #>> '{imc,value}', '')::numeric as payload_bmi,
        observation_payload_raw #>> '{imc,u}' as payload_bmi_unit,
        height_cm,
        weight_kg,
        systolic_bp,
        record_status,
        review_batch_id,
        loaded_at
    from source_observations
),

profiled as (
    select
        *,
        payload_height_cm is not null as has_payload_height,
        payload_weight_kg is not null as has_payload_weight,
        payload_systolic_bp is not null and payload_diastolic_bp is not null as has_payload_bp_pair,
        payload_pulse_lpm is not null as has_payload_pulse,
        payload_temperature_c is not null as has_payload_temperature,
        payload_bmi is not null as has_payload_bmi,
        payload_height_cm is not null
            and payload_height_cm <> 0
            and payload_weight_kg is not null as can_recompute_bmi,
        case
            when payload_height_cm is not null
             and payload_weight_kg is not null
             and payload_height_cm <> 0
                then payload_weight_kg / ((payload_height_cm / 100.0) * (payload_height_cm / 100.0))
            else null
        end as recomputed_bmi,
        height_cm is not distinct from payload_height_cm as height_matches_silver,
        weight_kg is not distinct from payload_weight_kg as weight_matches_silver,
        systolic_bp is not distinct from payload_systolic_bp as systolic_matches_silver
    from extracted
)

select * from profiled
