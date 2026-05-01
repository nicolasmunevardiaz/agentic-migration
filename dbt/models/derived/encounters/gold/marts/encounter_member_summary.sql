{{ config(materialized='view') }}

with encounters as (
    select *
    from {{ ref('encounter_fact') }}
),

member_rollup as (
    select
        provider_slug,
        patient_provider_member_id,
        member_reference,
        count(*) as encounter_row_count,
        count(distinct encounter_reference) as distinct_encounter_count,
        count(distinct coverage_status) as encounter_coverage_status_count,
        count(distinct record_status) as encounter_record_status_count,
        count(*) filter (where coverage_status = 'COVERED') as covered_encounter_count,
        count(*) filter (where coverage_status = 'OUT_OF_COVERAGE') as out_of_coverage_encounter_count,
        count(*) filter (where coverage_status = 'UNINSURED') as uninsured_encounter_count,
        count(*) filter (where record_status = 'active') as active_record_count,
        count(*) filter (where record_status = 'inactive') as inactive_record_count,
        count(*) filter (where record_status = 'unknown') as unknown_record_count,
        count(*) filter (where has_missing_encounter_datetime) as missing_datetime_count,
        count(*) filter (where has_implausible_encounter_datetime) as implausible_datetime_count,
        count(*) filter (where has_orphan_member_reference) as orphan_member_reference_count,
        min(encounter_datetime) as first_encounter_datetime,
        max(encounter_datetime) as last_encounter_datetime
    from encounters
    group by provider_slug, patient_provider_member_id, member_reference
)

select
    provider_slug,
    patient_provider_member_id,
    member_reference,
    encounter_row_count,
    distinct_encounter_count,
    encounter_coverage_status_count,
    encounter_record_status_count,
    covered_encounter_count,
    out_of_coverage_encounter_count,
    uninsured_encounter_count,
    active_record_count,
    inactive_record_count,
    unknown_record_count,
    missing_datetime_count,
    implausible_datetime_count,
    orphan_member_reference_count,
    first_encounter_datetime,
    last_encounter_datetime,
    encounter_row_count > 1 as has_multiple_encounters,
    encounter_coverage_status_count > 1 as has_multiple_coverage_statuses,
    missing_datetime_count > 0 as has_missing_encounter_datetime,
    implausible_datetime_count > 0 as has_implausible_encounter_datetime,
    orphan_member_reference_count > 0 as has_orphan_member_reference
from member_rollup
