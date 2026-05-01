{{ config(materialized='view') }}

with cost_records as (
    select *
    from {{ ref('cost_record_source_normalized') }}
),

patients as (
    select provider_slug, member_reference, patient_provider_member_id
    from {{ ref('patient_dimension') }}
),

encounters as (
    select provider_slug, encounter_reference, encounter_provider_id
    from {{ ref('encounter_fact') }}
),

medications as (
    select provider_slug, medication_reference, medication_provider_id
    from {{ ref('medication_fact') }}
),

with_relationship_flags as (
    select
        cost_records.*,
        patients.patient_provider_member_id is not null as has_patient_dimension_match,
        encounters.encounter_provider_id is not null as has_encounter_fact_match,
        medications.medication_provider_id is not null as has_medication_fact_match
    from cost_records
    left join patients
        on cost_records.provider_slug = patients.provider_slug
       and cost_records.member_reference = patients.member_reference
    left join encounters
        on cost_records.provider_slug = encounters.provider_slug
       and cost_records.encounter_reference = encounters.encounter_reference
    left join medications
        on cost_records.provider_slug = medications.provider_slug
       and cost_records.medication_reference = medications.medication_reference
)

select
    cost_record_id,
    cost_source_row_id,
    medication_provider_id,
    patient_provider_member_id,
    encounter_provider_id,
    cost_record_status_id,
    cost_amount_source_id,
    provider_slug,
    source_entity,
    source_row_id,
    source_lineage_ref,
    medication_reference,
    member_reference,
    member_reference_final_segment,
    encounter_reference,
    encounter_reference_final_segment,
    source_cost_amount_field_name,
    source_cost_amount,
    cost_date,
    cost_month,
    record_status,
    review_batch_id,
    loaded_at,
    has_missing_cost_amount,
    has_nonpositive_cost_amount,
    has_missing_cost_date,
    has_implausible_cost_date,
    has_patient_dimension_match,
    has_encounter_fact_match,
    has_medication_fact_match,
    not has_patient_dimension_match as has_orphan_member_reference,
    not has_encounter_fact_match as has_orphan_encounter_reference,
    not has_medication_fact_match as has_orphan_medication_reference,
    case
        when has_missing_cost_amount then 'review_missing_amount'
        when has_nonpositive_cost_amount then 'review_nonpositive_amount'
        when has_implausible_cost_date then 'review_implausible_date'
        when has_missing_cost_date then 'review_missing_date'
        when not has_patient_dimension_match then 'review_orphan_member_reference'
        when not has_encounter_fact_match then 'review_orphan_encounter_reference'
        when not has_medication_fact_match then 'review_orphan_medication_reference'
        else 'complete'
    end as cost_record_quality_status
from with_relationship_flags
