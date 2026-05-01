{{ config(materialized='view') }}

with medications as (
    select *
    from {{ ref('medication_source_normalized') }}
),

patients as (
    select provider_slug, member_reference, patient_provider_member_id
    from {{ ref('patient_dimension') }}
),

encounters as (
    select provider_slug, encounter_reference, encounter_provider_id
    from {{ ref('encounter_fact') }}
),

conditions as (
    select provider_slug, condition_reference, condition_provider_id
    from {{ ref('condition_fact') }}
),

with_relationship_flags as (
    select
        medications.*,
        patients.patient_provider_member_id is not null as has_patient_dimension_match,
        encounters.encounter_provider_id is not null as has_encounter_fact_match,
        conditions.condition_provider_id is not null as has_condition_fact_match
    from medications
    left join patients
        on medications.provider_slug = patients.provider_slug
       and medications.member_reference = patients.member_reference
    left join encounters
        on medications.provider_slug = encounters.provider_slug
       and medications.encounter_reference = encounters.encounter_reference
    left join conditions
        on medications.provider_slug = conditions.provider_slug
       and medications.condition_reference = conditions.condition_reference
)

select
    medication_source_row_id,
    medication_provider_id,
    patient_provider_member_id,
    encounter_provider_id,
    condition_provider_id,
    medication_code_id,
    medication_record_status_id,
    provider_slug,
    source_entity,
    source_row_id,
    source_lineage_ref,
    medication_reference,
    member_reference,
    member_reference_final_segment,
    encounter_reference,
    encounter_reference_final_segment,
    condition_reference,
    condition_reference_final_segment,
    medication_source_code,
    medication_description,
    medication_datetime,
    date_trunc('month', medication_datetime)::date as medication_month,
    record_status,
    review_batch_id,
    loaded_at,
    has_missing_medication_source_code,
    has_missing_medication_description,
    has_missing_medication_datetime,
    has_implausible_medication_datetime,
    has_patient_dimension_match,
    has_encounter_fact_match,
    has_condition_fact_match,
    not has_patient_dimension_match as has_orphan_member_reference,
    not has_encounter_fact_match as has_orphan_encounter_reference,
    not has_condition_fact_match as has_orphan_condition_reference,
    case
        when has_missing_medication_source_code then 'review_missing_source_code'
        when has_missing_medication_description then 'review_missing_description'
        when has_implausible_medication_datetime then 'review_implausible_datetime'
        when has_missing_medication_datetime then 'review_missing_datetime'
        when not has_patient_dimension_match then 'review_orphan_member_reference'
        when not has_encounter_fact_match then 'review_orphan_encounter_reference'
        when not has_condition_fact_match then 'review_orphan_condition_reference'
        else 'complete'
    end as medication_quality_status
from with_relationship_flags
