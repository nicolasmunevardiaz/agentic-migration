{{ config(materialized='table') }}

with patient_dates as (
    select
        provider_slug,
        'patients' as entity,
        patient_source_row_id as source_record_id,
        'birth_date' as field_column,
        birth_date as raw_date_value,
        case
            when birth_date_implausible then null::date
            else birth_date
        end as validated_date_value,
        birth_date_implausible as is_implausible_date,
        false as is_inverted_date_range,
        not birth_date_implausible as usable_for_temporal_analysis,
        'birth_date_validity_status' as status_field
    from {{ ref('patient_source_normalized') }}
    where birth_date is not null

    union all

    select
        provider_slug,
        'coverage_periods',
        coverage_period_id,
        'coverage_start_date',
        coverage_start_date,
        case
            when coverage_start_date < date '1900-01-01'
              or coverage_start_date > current_date + interval '1 year'
              or has_inverted_date_range then null::date
            else coverage_start_date
        end,
        coverage_start_date < date '1900-01-01'
          or coverage_start_date > current_date + interval '1 year',
        has_inverted_date_range,
        not (
            coverage_start_date < date '1900-01-01'
            or coverage_start_date > current_date + interval '1 year'
            or has_inverted_date_range
        ),
        'coverage_start_date_validity_status'
    from {{ ref('coverage_period_fact') }}
    where coverage_start_date is not null

    union all

    select
        provider_slug,
        'coverage_periods',
        coverage_period_id,
        'coverage_end_date',
        coverage_end_date,
        case
            when coverage_end_date < date '1900-01-01'
              or coverage_end_date > current_date + interval '1 year'
              or has_inverted_date_range then null::date
            else coverage_end_date
        end,
        coverage_end_date < date '1900-01-01'
          or coverage_end_date > current_date + interval '1 year',
        has_inverted_date_range,
        not (
            coverage_end_date < date '1900-01-01'
            or coverage_end_date > current_date + interval '1 year'
            or has_inverted_date_range
        ),
        'coverage_end_date_validity_status'
    from {{ ref('coverage_period_fact') }}
    where coverage_end_date is not null
)

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || source_record_id || '|' || field_column") }}
        as date_quarantine_id,
    provider_slug,
    entity,
    source_record_id,
    field_column,
    raw_date_value,
    validated_date_value,
    is_implausible_date,
    is_inverted_date_range,
    usable_for_temporal_analysis,
    case
        when entity = 'patients' and is_implausible_date
            then 'managed_implausible_birth_date_quarantined'
        when entity = 'coverage_periods' and (is_implausible_date or is_inverted_date_range)
            then 'managed_implausible_coverage_date_quarantined'
        else 'complete'
    end as date_validity_status,
    status_field
from patient_dates
