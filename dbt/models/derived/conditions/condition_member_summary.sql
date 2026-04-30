{{ config(materialized='view') }}

with conditions as (
    select *
    from {{ ref('condition_fact') }}
),

member_rollup as (
    select
        provider_slug,
        patient_provider_member_id,
        member_reference,
        count(*) as condition_row_count,
        count(distinct condition_reference) as distinct_condition_count,
        count(distinct encounter_reference) as distinct_condition_encounter_count,
        count(distinct condition_code_id) as distinct_condition_code_count,
        count(*) filter (where record_status = 'active') as active_record_count,
        count(*) filter (where record_status = 'inactive') as inactive_record_count,
        count(*) filter (where record_status = 'unknown') as unknown_record_count,
        count(*) filter (where has_orphan_member_reference) as orphan_member_reference_count,
        count(*) filter (where has_orphan_encounter_reference) as orphan_encounter_reference_count,
        count(*) filter (where source_code_matches_hint) as source_code_matches_hint_count
    from conditions
    group by provider_slug, patient_provider_member_id, member_reference
)

select
    provider_slug,
    patient_provider_member_id,
    member_reference,
    condition_row_count,
    distinct_condition_count,
    distinct_condition_encounter_count,
    distinct_condition_code_count,
    active_record_count,
    inactive_record_count,
    unknown_record_count,
    orphan_member_reference_count,
    orphan_encounter_reference_count,
    source_code_matches_hint_count,
    condition_row_count > 1 as has_multiple_conditions,
    orphan_member_reference_count > 0 as has_orphan_member_reference,
    orphan_encounter_reference_count > 0 as has_orphan_encounter_reference
from member_rollup
