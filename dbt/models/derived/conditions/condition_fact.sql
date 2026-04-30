{{ config(materialized='view') }}

with conditions as (
    select *
    from {{ ref('condition_source_normalized') }}
),

patients as (
    select provider_slug, member_reference, patient_provider_member_id
    from {{ ref('patient_dimension') }}
),

encounters as (
    select provider_slug, encounter_reference, encounter_provider_id
    from {{ ref('encounter_fact') }}
),

with_relationship_flags as (
    select
        conditions.*,
        patients.patient_provider_member_id is not null as has_patient_dimension_match,
        encounters.encounter_provider_id is not null as has_encounter_fact_match
    from conditions
    left join patients
        on conditions.provider_slug = patients.provider_slug
       and conditions.member_reference = patients.member_reference
    left join encounters
        on conditions.provider_slug = encounters.provider_slug
       and conditions.encounter_reference = encounters.encounter_reference
)

select
    condition_source_row_id,
    condition_provider_id,
    patient_provider_member_id,
    encounter_provider_id,
    condition_code_id,
    condition_record_status_id,
    provider_slug,
    source_entity,
    source_row_id,
    source_lineage_ref,
    condition_reference,
    member_reference,
    member_reference_final_segment,
    encounter_reference,
    encounter_reference_final_segment,
    condition_source_code,
    condition_code_hint,
    condition_description,
    record_status,
    review_batch_id,
    loaded_at,
    has_missing_condition_source_code,
    has_missing_condition_code_hint,
    has_missing_condition_description,
    source_code_matches_hint,
    has_patient_dimension_match,
    has_encounter_fact_match,
    not has_patient_dimension_match as has_orphan_member_reference,
    not has_encounter_fact_match as has_orphan_encounter_reference,
    case
        when has_missing_condition_source_code then 'review_missing_source_code'
        when has_missing_condition_code_hint then 'review_missing_code_hint'
        when has_missing_condition_description then 'review_missing_description'
        when not has_patient_dimension_match then 'review_orphan_member_reference'
        when not has_encounter_fact_match then 'review_orphan_encounter_reference'
        else 'complete'
    end as condition_quality_status
from with_relationship_flags
