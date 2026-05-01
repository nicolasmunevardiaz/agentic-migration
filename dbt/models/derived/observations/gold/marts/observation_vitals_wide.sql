{{ config(materialized='view') }}

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
    payload_type,
    payload_height_cm as height_cm,
    payload_height_unit as height_unit,
    payload_weight_kg as weight_kg,
    payload_weight_unit as weight_unit,
    payload_systolic_bp as systolic_bp,
    payload_diastolic_bp as diastolic_bp,
    payload_blood_pressure_unit as blood_pressure_unit,
    payload_pulse_lpm as pulse_lpm,
    payload_pulse_unit as pulse_unit,
    payload_temperature_c as temperature_c,
    payload_temperature_unit as temperature_unit,
    payload_bmi as bmi_payload,
    payload_bmi_unit as bmi_unit,
    recomputed_bmi,
    case
        when payload_bmi is not null and recomputed_bmi is not null
            then abs(payload_bmi - recomputed_bmi)
        else null
    end as bmi_payload_recomputed_abs_delta,
    has_payload_height,
    has_payload_weight,
    has_payload_bp_pair,
    has_payload_pulse,
    has_payload_temperature,
    has_payload_bmi,
    can_recompute_bmi,
    height_matches_silver,
    weight_matches_silver,
    systolic_matches_silver
from {{ ref('observation_payload_source_normalized') }}
