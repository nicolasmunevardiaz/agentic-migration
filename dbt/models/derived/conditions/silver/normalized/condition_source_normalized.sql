{{ config(materialized='view') }}

with source_conditions as (
    select
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        condition_reference,
        member_reference,
        encounter_reference,
        condition_source_code,
        condition_code_hint,
        condition_description,
        record_status,
        review_batch_id,
        loaded_at
    from {{ source('review', 'silver_conditions') }}
    where {{ active_batch_filter() }}
),

normalized as (
    select
        {{ provider_scoped_hash('provider_slug', 'source_row_id') }} as condition_source_row_id,
        {{ provider_scoped_hash('provider_slug', 'condition_reference') }} as condition_provider_id,
        {{ provider_scoped_hash('provider_slug', 'member_reference') }} as patient_provider_member_id,
        {{ provider_scoped_hash('provider_slug', 'encounter_reference') }} as encounter_provider_id,
        md5(
            'condition_code|'
            || provider_slug
            || '|'
            || coalesce(nullif(upper(trim(condition_source_code)), ''), 'UNKNOWN')
            || '|'
            || coalesce(nullif(upper(trim(condition_code_hint)), ''), 'UNKNOWN')
        ) as condition_code_id,
        md5(
            'condition_record_status|'
            || coalesce(nullif(lower(trim(record_status)), ''), 'unknown')
        ) as condition_record_status_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        condition_reference,
        member_reference,
        regexp_replace(member_reference, '^.*/', '') as member_reference_final_segment,
        encounter_reference,
        regexp_replace(encounter_reference, '^.*/', '') as encounter_reference_final_segment,
        nullif(upper(trim(condition_source_code)), '') as condition_source_code,
        nullif(upper(trim(condition_code_hint)), '') as condition_code_hint,
        nullif(trim(condition_description), '') as condition_description,
        coalesce(nullif(lower(trim(record_status)), ''), 'unknown') as record_status,
        review_batch_id,
        loaded_at,
        nullif(upper(trim(condition_source_code)), '') is null as has_missing_condition_source_code,
        nullif(upper(trim(condition_code_hint)), '') is null as has_missing_condition_code_hint,
        nullif(trim(condition_description), '') is null as has_missing_condition_description,
        nullif(upper(trim(condition_source_code)), '') is not null
            and nullif(upper(trim(condition_code_hint)), '') is not null
            and nullif(upper(trim(condition_source_code)), '')
                = nullif(upper(trim(condition_code_hint)), '')
            as source_code_matches_hint
    from source_conditions
)

select * from normalized
