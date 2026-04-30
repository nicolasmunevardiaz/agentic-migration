{{ config(materialized='view') }}

with source_cost_records as (
    select
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        medication_reference,
        member_reference,
        encounter_reference,
        cost_amount,
        cost_date,
        record_status,
        review_batch_id,
        loaded_at
    from {{ source('review', 'silver_cost_records') }}
    where {{ active_batch_filter() }}
),

normalized as (
    select
        md5(
            'cost_record|'
            || coalesce(provider_slug, '')
            || '|'
            || coalesce(medication_reference, '')
            || '|'
            || coalesce(source_row_id, '')
        ) as cost_record_id,
        {{ provider_scoped_hash('provider_slug', 'source_row_id') }} as cost_source_row_id,
        {{ provider_scoped_hash('provider_slug', 'medication_reference') }} as medication_provider_id,
        {{ provider_scoped_hash('provider_slug', 'member_reference') }} as patient_provider_member_id,
        {{ provider_scoped_hash('provider_slug', 'encounter_reference') }} as encounter_provider_id,
        md5(
            'cost_record_status|'
            || coalesce(nullif(lower(trim(record_status)), ''), 'unknown')
        ) as cost_record_status_id,
        md5(
            'cost_amount_source|'
            || provider_slug
            || '|'
            || case
                when provider_slug = 'data_provider_1_aegis_care_network' then 'UNIT_COST'
                when provider_slug = 'data_provider_2_bluestone_health' then 'RX_UNIT_AMT'
                when provider_slug = 'data_provider_3_northcare_clinics' then 'MED_PRICE'
                when provider_slug = 'data_provider_4_valleybridge_medical' then 'LINE_PRICE'
                when provider_slug = 'data_provider_5_pacific_shield_insurance' then 'PAID_AMT'
                else 'UNKNOWN'
            end
        ) as cost_amount_source_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        medication_reference,
        member_reference,
        regexp_replace(member_reference, '^.*/', '') as member_reference_final_segment,
        encounter_reference,
        regexp_replace(encounter_reference, '^.*/', '') as encounter_reference_final_segment,
        case
            when provider_slug = 'data_provider_1_aegis_care_network' then 'UNIT_COST'
            when provider_slug = 'data_provider_2_bluestone_health' then 'RX_UNIT_AMT'
            when provider_slug = 'data_provider_3_northcare_clinics' then 'MED_PRICE'
            when provider_slug = 'data_provider_4_valleybridge_medical' then 'LINE_PRICE'
            when provider_slug = 'data_provider_5_pacific_shield_insurance' then 'PAID_AMT'
            else 'UNKNOWN'
        end as source_cost_amount_field_name,
        cost_amount as source_cost_amount,
        cost_date,
        date_trunc('month', cost_date)::date as cost_month,
        coalesce(nullif(lower(trim(record_status)), ''), 'unknown') as record_status,
        review_batch_id,
        loaded_at,
        cost_amount is null as has_missing_cost_amount,
        cost_amount <= 0 as has_nonpositive_cost_amount,
        cost_date is null as has_missing_cost_date,
        cost_date < timestamp with time zone '1900-01-01 00:00:00+00'
            or cost_date > current_timestamp + interval '10 years'
            as has_implausible_cost_date
    from source_cost_records
)

select * from normalized
