{{ config(materialized='view') }}

with patient_rows as (
    select *
    from {{ ref('patient_source_normalized') }}
),

member_rollup as (
    select
        patient_provider_member_id,
        provider_slug,
        member_reference,
        min(review_batch_id) as review_batch_id,
        count(*) as source_row_count,
        count(distinct source_row_id) as distinct_source_row_count,
        count(distinct source_lineage_ref) as distinct_lineage_ref_count,
        count(*) filter (where is_active_record) as active_source_row_count,
        count(*) filter (where not is_active_record) as inactive_source_row_count,
        count(*) filter (where gender_code_normalized is not null) as gender_observed_row_count,
        count(distinct gender_code_normalized) filter (
            where gender_code_normalized is not null
        ) as distinct_gender_code_count,
        min(gender_code_normalized) filter (
            where gender_code_normalized is not null
        ) as min_gender_code,
        max(gender_code_normalized) filter (
            where gender_code_normalized is not null
        ) as max_gender_code,
        count(*) filter (where birth_date is not null) as birth_date_observed_row_count,
        count(distinct birth_date) filter (
            where birth_date is not null
        ) as distinct_birth_date_count,
        min(birth_date) filter (where birth_date is not null) as min_birth_date,
        max(birth_date) filter (where birth_date is not null) as max_birth_date,
        bool_or(birth_date_implausible) as has_implausible_birth_date
    from patient_rows
    group by patient_provider_member_id, provider_slug, member_reference
),

dimensioned as (
    select
        patient_provider_member_id,
        provider_slug,
        member_reference,
        review_batch_id,
        source_row_count,
        distinct_source_row_count,
        distinct_lineage_ref_count,
        active_source_row_count,
        inactive_source_row_count,
        active_source_row_count > 0 as has_active_source_row,
        inactive_source_row_count > 0 as has_inactive_source_row,
        gender_observed_row_count,
        distinct_gender_code_count,
        case
            when distinct_gender_code_count = 1 then min_gender_code
            else null
        end as normalized_gender_code,
        distinct_gender_code_count > 1 as has_gender_conflict,
        birth_date_observed_row_count,
        distinct_birth_date_count,
        case
            when distinct_birth_date_count = 1 and not has_implausible_birth_date then min_birth_date
            else null
        end as normalized_birth_date,
        distinct_birth_date_count > 1 as has_birth_date_conflict,
        has_implausible_birth_date,
        case
            when distinct_gender_code_count > 1 then 'conflicting_gender'
            when distinct_birth_date_count > 1 then 'conflicting_birth_date'
            when has_implausible_birth_date then 'implausible_birth_date'
            when member_reference is null then 'missing_member_reference'
            else 'usable_provider_scoped_dimension'
        end as patient_dimension_quality_status
    from member_rollup
)

select * from dimensioned
