{{ config(materialized='table') }}

with reference_rows as (
    select
        reference_standardization_id,
        provider_slug,
        entity,
        source_record_id,
        field_column,
        raw_reference,
        reference_final_segment,
        provider_scoped_reference_key,
        resolution_hint
    from {{ ref('dq_standardized_reference_fields') }}
),

patient_targets as (
    select distinct provider_slug, patient_provider_member_id
    from {{ ref('patient_dimension') }}
),

encounter_targets as (
    select distinct provider_slug, encounter_provider_id
    from {{ ref('encounter_fact') }}
),

condition_targets as (
    select distinct provider_slug, condition_provider_id
    from {{ ref('condition_fact') }}
),

medication_targets as (
    select distinct provider_slug, medication_provider_id
    from {{ ref('medication_fact') }}
),

resolved as (
    select
        reference_rows.*,
        patient_targets.patient_provider_member_id as resolved_patient_provider_member_id,
        encounter_targets.encounter_provider_id as resolved_encounter_provider_id,
        condition_targets.condition_provider_id as resolved_condition_provider_id,
        medication_targets.medication_provider_id as resolved_medication_provider_id
    from reference_rows
    left join patient_targets
        on reference_rows.field_column = 'member_reference'
       and reference_rows.provider_slug = patient_targets.provider_slug
       and reference_rows.provider_scoped_reference_key = patient_targets.patient_provider_member_id
    left join encounter_targets
        on reference_rows.field_column = 'encounter_reference'
       and reference_rows.provider_slug = encounter_targets.provider_slug
       and reference_rows.provider_scoped_reference_key = encounter_targets.encounter_provider_id
    left join condition_targets
        on reference_rows.field_column = 'condition_reference'
       and reference_rows.provider_slug = condition_targets.provider_slug
       and reference_rows.provider_scoped_reference_key = condition_targets.condition_provider_id
    left join medication_targets
        on reference_rows.field_column = 'medication_reference'
       and reference_rows.provider_slug = medication_targets.provider_slug
       and reference_rows.provider_scoped_reference_key = medication_targets.medication_provider_id
),

classified as (
    select
        *,
        case
            when field_column = 'member_reference' then 'patient'
            when field_column = 'encounter_reference' then 'encounter'
            when field_column = 'condition_reference' then 'condition'
            when field_column = 'medication_reference' then 'medication'
            else 'unknown'
        end as expected_reference_target,
        raw_reference is null
            or btrim(raw_reference) in ('', '""', '" "')
            as is_missing_reference,
        upper(btrim(coalesce(raw_reference, ''))) like 'UNK_%'
            as is_unknown_reference
    from resolved
)

select
    reference_standardization_id as consistency_reference_bridge_id,
    provider_slug,
    entity,
    source_record_id,
    field_column,
    expected_reference_target,
    raw_reference,
    reference_final_segment,
    case
        when is_missing_reference or is_unknown_reference then null
        else provider_scoped_reference_key
    end as normalized_reference_key,
    resolved_patient_provider_member_id,
    resolved_encounter_provider_id,
    resolved_condition_provider_id,
    resolved_medication_provider_id,
    is_missing_reference,
    is_unknown_reference,
    case
        when field_column = 'member_reference'
            then resolved_patient_provider_member_id is not null
        when field_column = 'encounter_reference'
            then resolved_encounter_provider_id is not null
        when field_column = 'condition_reference'
            then resolved_condition_provider_id is not null
        when field_column = 'medication_reference'
            then resolved_medication_provider_id is not null
        else false
    end as is_resolved_reference,
    not (
        case
            when field_column = 'member_reference'
                then resolved_patient_provider_member_id is not null
            when field_column = 'encounter_reference'
                then resolved_encounter_provider_id is not null
            when field_column = 'condition_reference'
                then resolved_condition_provider_id is not null
            when field_column = 'medication_reference'
                then resolved_medication_provider_id is not null
            else false
        end
    ) as is_unresolved_reference,
    case
        when is_missing_reference then 'missing_reference'
        when is_unknown_reference then 'unknown_reference'
        when field_column = 'member_reference'
         and resolved_patient_provider_member_id is not null then 'resolved'
        when field_column = 'encounter_reference'
         and resolved_encounter_provider_id is not null then 'resolved'
        when field_column = 'condition_reference'
         and resolved_condition_provider_id is not null then 'resolved'
        when field_column = 'medication_reference'
         and resolved_medication_provider_id is not null then 'resolved'
        else 'unresolved_reference'
    end as reference_resolution_status,
    case
        when is_missing_reference then 'managed_missing_reference_preserved'
        when is_unknown_reference then 'managed_unknown_reference_preserved'
        when field_column = 'member_reference'
         and resolved_patient_provider_member_id is not null then 'complete'
        when field_column = 'encounter_reference'
         and resolved_encounter_provider_id is not null then 'complete'
        when field_column = 'condition_reference'
         and resolved_condition_provider_id is not null then 'complete'
        when field_column = 'medication_reference'
         and resolved_medication_provider_id is not null then 'complete'
        else 'managed_unresolved_reference_preserved'
    end as consistency_reference_management_status,
    resolution_hint
from classified
