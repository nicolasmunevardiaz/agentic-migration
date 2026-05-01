{{ config(materialized='view') }}

with source_encounters as (
    select
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        encounter_reference,
        member_reference,
        encounter_datetime,
        coverage_status,
        record_status,
        review_batch_id,
        loaded_at
    from {{ source('landing', 'encounters') }}
    where {{ active_batch_filter() }}
),

normalized as (
    select
        {{ provider_scoped_hash('provider_slug', 'source_row_id') }} as encounter_source_row_id,
        {{ provider_scoped_hash('provider_slug', 'encounter_reference') }} as encounter_provider_id,
        {{ provider_scoped_hash('provider_slug', 'member_reference') }} as patient_provider_member_id,
        md5(
            'encounter_coverage_status|'
            || coalesce(nullif(upper(trim(coverage_status)), ''), 'UNKNOWN')
        ) as encounter_coverage_status_id,
        md5(
            'encounter_record_status|'
            || coalesce(nullif(lower(trim(record_status)), ''), 'unknown')
        ) as encounter_record_status_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        encounter_reference,
        member_reference,
        regexp_replace(member_reference, '^.*/', '') as member_reference_final_segment,
        encounter_datetime,
        coalesce(nullif(upper(trim(coverage_status)), ''), 'UNKNOWN') as coverage_status,
        coalesce(nullif(lower(trim(record_status)), ''), 'unknown') as record_status,
        review_batch_id,
        loaded_at,
        encounter_datetime is null as has_missing_encounter_datetime,
        encounter_datetime < timestamp with time zone '1900-01-01 00:00:00+00'
            or encounter_datetime > current_timestamp + interval '10 years'
            as has_implausible_encounter_datetime
    from source_encounters
)

select * from normalized
