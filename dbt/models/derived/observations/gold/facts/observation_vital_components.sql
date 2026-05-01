{{ config(materialized='view') }}

with observations as (
    select *
    from {{ ref('observation_payload_source_normalized') }}
),

components as (
    select
        observation_source_row_id,
        observation_provider_id,
        patient_provider_member_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        observation_reference,
        member_reference,
        encounter_reference,
        observation_datetime,
        review_batch_id,
        'height_cm' as component_name,
        payload_height_cm as component_value,
        payload_height_unit as component_unit,
        '{height,value}' as payload_value_path,
        '{height,u}' as payload_unit_path
    from observations
    where payload_height_cm is not null

    union all

    select
        observation_source_row_id,
        observation_provider_id,
        patient_provider_member_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        observation_reference,
        member_reference,
        encounter_reference,
        observation_datetime,
        review_batch_id,
        'weight_kg',
        payload_weight_kg,
        payload_weight_unit,
        '{weight,value}',
        '{weight,u}'
    from observations
    where payload_weight_kg is not null

    union all

    select
        observation_source_row_id,
        observation_provider_id,
        patient_provider_member_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        observation_reference,
        member_reference,
        encounter_reference,
        observation_datetime,
        review_batch_id,
        'systolic_bp',
        payload_systolic_bp,
        payload_blood_pressure_unit,
        '{blood_pressure,systolic}',
        '{blood_pressure,u}'
    from observations
    where payload_systolic_bp is not null

    union all

    select
        observation_source_row_id,
        observation_provider_id,
        patient_provider_member_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        observation_reference,
        member_reference,
        encounter_reference,
        observation_datetime,
        review_batch_id,
        'diastolic_bp',
        payload_diastolic_bp,
        payload_blood_pressure_unit,
        '{blood_pressure,diastolic}',
        '{blood_pressure,u}'
    from observations
    where payload_diastolic_bp is not null

    union all

    select
        observation_source_row_id,
        observation_provider_id,
        patient_provider_member_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        observation_reference,
        member_reference,
        encounter_reference,
        observation_datetime,
        review_batch_id,
        'pulse_lpm',
        payload_pulse_lpm,
        payload_pulse_unit,
        '{pulse,value}',
        '{pulse,u}'
    from observations
    where payload_pulse_lpm is not null

    union all

    select
        observation_source_row_id,
        observation_provider_id,
        patient_provider_member_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        observation_reference,
        member_reference,
        encounter_reference,
        observation_datetime,
        review_batch_id,
        'temperature_c',
        payload_temperature_c,
        payload_temperature_unit,
        '{temperature,value}',
        '{temperature,u}'
    from observations
    where payload_temperature_c is not null

    union all

    select
        observation_source_row_id,
        observation_provider_id,
        patient_provider_member_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        observation_reference,
        member_reference,
        encounter_reference,
        observation_datetime,
        review_batch_id,
        'bmi',
        payload_bmi,
        payload_bmi_unit,
        '{imc,value}',
        '{imc,u}'
    from observations
    where payload_bmi is not null
),

with_ids as (
    select
        {{ provider_scoped_hash('provider_slug', "source_row_id || '|' || component_name") }}
            as observation_component_id,
        *
    from components
)

select * from with_ids
