{{ config(materialized='table') }}

with date_checks as (
    select
        provider_slug,
        'patients' as entity,
        'birth_date' as field_column,
        count(*) as total_rows,
        count(*) filter (where has_implausible_birth_date) as invalid_date_rows,
        0::bigint as inverted_date_range_rows,
        'date_bounds_parser_quarantine' as resolution_hint
    from {{ ref('patient_dimension') }}
    group by provider_slug

    union all

    select
        provider_slug,
        'coverage_periods',
        'coverage_start_date_or_end_date',
        count(*),
        count(*) filter (where has_implausible_coverage_date),
        count(*) filter (where has_inverted_date_range),
        'date_bounds_parser_quarantine'
    from {{ ref('coverage_period_fact') }}
    group by provider_slug

    union all

    select
        provider_slug,
        'encounters',
        'encounter_datetime',
        count(*),
        count(*) filter (where has_implausible_encounter_datetime),
        0::bigint,
        'date_bounds_parser_quarantine'
    from {{ ref('encounter_fact') }}
    group by provider_slug

    union all

    select
        provider_slug,
        'medications',
        'medication_datetime',
        count(*),
        count(*) filter (where has_implausible_medication_datetime),
        0::bigint,
        'date_bounds_parser_quarantine'
    from {{ ref('medication_fact') }}
    group by provider_slug

    union all

    select
        provider_slug,
        'cost_records',
        'cost_date',
        count(*),
        count(*) filter (where has_implausible_cost_date),
        0::bigint,
        'date_bounds_parser_quarantine'
    from {{ ref('cost_record_fact') }}
    group by provider_slug
)

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || field_column") }}
        as validity_date_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    invalid_date_rows,
    inverted_date_range_rows,
    invalid_date_rows + inverted_date_range_rows as affected_rows,
    resolution_hint,
    case
        when invalid_date_rows + inverted_date_range_rows > 0
            then 'managed_implausible_date_quarantined'
        else 'complete'
    end as validity_date_status
from date_checks
