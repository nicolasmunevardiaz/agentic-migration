{{ config(materialized='view') }}

with source_members as (
    select
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        member_reference,
        gender_code,
        birth_date,
        record_status,
        review_batch_id,
        loaded_at
    from {{ source('review', 'silver_members') }}
    where {{ active_batch_filter() }}
),

normalized as (
    select
        {{ provider_scoped_hash('provider_slug', 'source_row_id') }} as patient_source_row_id,
        {{ provider_scoped_hash('provider_slug', 'member_reference') }} as patient_provider_member_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        member_reference,
        gender_code as gender_code_raw,
        {{ normalize_gender_code('gender_code') }} as gender_code_normalized,
        case
            when {{ normalize_gender_code('gender_code') }} in ('F', 'M') then 'accepted'
            when {{ normalize_gender_code('gender_code') }} is null then 'missing'
            else 'unexpected'
        end as gender_normalization_status,
        birth_date,
        case
            when birth_date is null then false
            when birth_date < date '1900-01-01' then true
            when birth_date > current_date then true
            else false
        end as birth_date_implausible,
        record_status,
        case when record_status = 'active' then true else false end as is_active_record,
        review_batch_id,
        loaded_at
    from source_members
)

select * from normalized
