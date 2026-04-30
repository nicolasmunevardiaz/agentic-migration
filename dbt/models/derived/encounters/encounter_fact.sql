{{ config(materialized='view') }}

with encounters as (
    select *
    from {{ ref('encounter_source_normalized') }}
),

patients as (
    select
        provider_slug,
        member_reference,
        patient_provider_member_id
    from {{ ref('patient_dimension') }}
),

with_patient_link as (
    select
        encounters.*,
        patients.patient_provider_member_id is not null as has_patient_dimension_match
    from encounters
    left join patients
        on encounters.provider_slug = patients.provider_slug
       and encounters.member_reference = patients.member_reference
)

select
    encounter_source_row_id,
    encounter_provider_id,
    patient_provider_member_id,
    encounter_coverage_status_id,
    encounter_record_status_id,
    provider_slug,
    source_entity,
    source_row_id,
    source_lineage_ref,
    encounter_reference,
    member_reference,
    member_reference_final_segment,
    encounter_datetime,
    date_trunc('month', encounter_datetime)::date as encounter_month,
    coverage_status,
    record_status,
    review_batch_id,
    loaded_at,
    has_missing_encounter_datetime,
    has_implausible_encounter_datetime,
    has_patient_dimension_match,
    not has_patient_dimension_match as has_orphan_member_reference,
    case
        when has_implausible_encounter_datetime then 'review_implausible_datetime'
        when has_missing_encounter_datetime then 'review_missing_datetime'
        when not has_patient_dimension_match then 'review_orphan_member_reference'
        else 'complete'
    end as encounter_quality_status
from with_patient_link
