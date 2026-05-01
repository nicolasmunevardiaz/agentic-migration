{{ config(materialized='view') }}

with source_coverage as (
    select
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        member_reference,
        coverage_start_date,
        coverage_end_date,
        coverage_status,
        review_batch_id,
        loaded_at
    from {{ source('review', 'silver_coverage_periods') }}
    where {{ active_batch_filter() }}
),

normalized as (
    select
        {{ provider_scoped_hash('provider_slug', 'source_row_id') }} as coverage_source_row_id,
        {{ provider_scoped_hash('provider_slug', 'member_reference') }} as patient_provider_member_id,
        {{ provider_scoped_hash('provider_slug', "source_row_id || '|coverage_period'") }}
            as coverage_period_id,
        md5('coverage_status|' || coalesce(coverage_status, 'UNKNOWN')) as coverage_status_id,
        provider_slug,
        source_entity,
        source_row_id,
        source_lineage_ref,
        member_reference,
        coverage_start_date,
        coverage_end_date,
        coalesce(nullif(upper(trim(coverage_status)), ''), 'UNKNOWN') as coverage_status,
        review_batch_id,
        loaded_at,
        coverage_start_date is not null as has_coverage_start_date,
        coverage_end_date is not null as has_coverage_end_date,
        coverage_start_date is not null and coverage_end_date is null as is_open_ended_period,
        coverage_start_date is null and coverage_end_date is not null as is_end_date_only_period,
        coverage_start_date is null and coverage_end_date is null as is_undated_period,
        coverage_start_date is not null
            and coverage_end_date is not null
            and coverage_end_date < coverage_start_date as has_inverted_date_range,
        (
            coverage_start_date < date '1900-01-01'
            or coverage_end_date < date '1900-01-01'
            or coverage_start_date > current_date + interval '10 years'
            or coverage_end_date > current_date + interval '10 years'
        ) as has_implausible_coverage_date,
        case
            when coverage_start_date is not null
             and coverage_end_date is not null
             and coverage_end_date >= coverage_start_date
                then coverage_end_date - coverage_start_date + 1
            else null
        end as bounded_coverage_days
    from source_coverage
)

select * from normalized
