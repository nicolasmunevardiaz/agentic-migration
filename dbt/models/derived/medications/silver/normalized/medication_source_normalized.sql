{{ config(materialized='view') }}

with source_medications as (
    select
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        medication_reference,
        member_reference,
        encounter_reference,
        condition_reference,
        medication_source_code,
        medication_description,
        medication_datetime,
        record_status,
        review_batch_id,
        loaded_at
    from {{ source('landing', 'medications') }}
    where {{ active_batch_filter() }}
),

normalized as (
    select
        {{ provider_scoped_hash('provider_slug', 'source_row_id') }} as medication_source_row_id,
        {{ provider_scoped_hash('provider_slug', 'medication_reference') }} as medication_provider_id,
        {{ provider_scoped_hash('provider_slug', 'member_reference') }} as patient_provider_member_id,
        {{ provider_scoped_hash('provider_slug', 'encounter_reference') }} as encounter_provider_id,
        {{ provider_scoped_hash('provider_slug', 'condition_reference') }} as condition_provider_id,
        md5(
            'medication_code|'
            || provider_slug
            || '|'
            || coalesce(nullif(upper(trim(medication_source_code)), ''), 'UNKNOWN')
        ) as medication_code_id,
        md5(
            'medication_record_status|'
            || coalesce(nullif(lower(trim(record_status)), ''), 'unknown')
        ) as medication_record_status_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        medication_reference,
        member_reference,
        regexp_replace(member_reference, '^.*/', '') as member_reference_final_segment,
        encounter_reference,
        regexp_replace(encounter_reference, '^.*/', '') as encounter_reference_final_segment,
        condition_reference,
        regexp_replace(condition_reference, '^.*/', '') as condition_reference_final_segment,
        nullif(medication_source_code, '') as medication_source_code_raw,
        nullif(upper(trim(medication_source_code)), '') as medication_source_code,
        nullif(trim(medication_description), '') as medication_description,
        medication_datetime,
        coalesce(nullif(lower(trim(record_status)), ''), 'unknown') as record_status,
        review_batch_id,
        loaded_at,
        nullif(upper(trim(medication_source_code)), '') is null as has_missing_medication_source_code,
        nullif(trim(medication_description), '') is null as has_missing_medication_description,
        medication_datetime is null as has_missing_medication_datetime,
        medication_datetime < timestamp with time zone '1900-01-01 00:00:00+00'
            or medication_datetime > current_timestamp + interval '10 years'
            as has_implausible_medication_datetime
    from source_medications
)

select * from normalized
