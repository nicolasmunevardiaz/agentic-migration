{{ config(materialized='view') }}

with medications as (
    select *
    from {{ ref('medication_fact') }}
),

member_rollup as (
    select
        provider_slug,
        patient_provider_member_id,
        member_reference,
        count(*) as medication_row_count,
        count(distinct medication_reference) as distinct_medication_count,
        count(distinct encounter_reference) as distinct_medication_encounter_count,
        count(distinct condition_reference) as distinct_medication_condition_count,
        count(distinct medication_code_id) as distinct_medication_code_count,
        count(*) filter (where record_status = 'active') as active_record_count,
        count(*) filter (where record_status = 'inactive') as inactive_record_count,
        count(*) filter (where record_status = 'unknown') as unknown_record_count,
        count(*) filter (where has_missing_medication_datetime) as missing_datetime_count,
        count(*) filter (where has_implausible_medication_datetime) as implausible_datetime_count,
        count(*) filter (where has_orphan_member_reference) as orphan_member_reference_count,
        count(*) filter (where has_orphan_encounter_reference) as orphan_encounter_reference_count,
        count(*) filter (where has_orphan_condition_reference) as orphan_condition_reference_count,
        min(medication_datetime) as first_medication_datetime,
        max(medication_datetime) as last_medication_datetime
    from medications
    group by provider_slug, patient_provider_member_id, member_reference
)

select
    provider_slug,
    patient_provider_member_id,
    member_reference,
    medication_row_count,
    distinct_medication_count,
    distinct_medication_encounter_count,
    distinct_medication_condition_count,
    distinct_medication_code_count,
    active_record_count,
    inactive_record_count,
    unknown_record_count,
    missing_datetime_count,
    implausible_datetime_count,
    orphan_member_reference_count,
    orphan_encounter_reference_count,
    orphan_condition_reference_count,
    first_medication_datetime,
    last_medication_datetime,
    medication_row_count > 1 as has_multiple_medications,
    missing_datetime_count > 0 as has_missing_medication_datetime,
    implausible_datetime_count > 0 as has_implausible_medication_datetime,
    orphan_member_reference_count > 0 as has_orphan_member_reference,
    orphan_encounter_reference_count > 0 as has_orphan_encounter_reference,
    orphan_condition_reference_count > 0 as has_orphan_condition_reference
from member_rollup
