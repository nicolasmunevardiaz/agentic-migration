{{ config(materialized='table') }}

with field_checks as (
    select
        provider_slug,
        'cost_records' as entity,
        'cost_amount' as field_column,
        count(*) as total_rows,
        count(*) filter (where amount_standardization_status = 'missing_amount')
            as missing_rows,
        'approved_null_semantics' as requiredness_status,
        'amount_source_requiredness_policy' as resolution_hint
    from {{ ref('dq_standardized_amount_fields') }}
    group by provider_slug

    union all

    select
        provider_slug,
        entity,
        field_column,
        total_rows,
        missing_source_value_rows as missing_rows,
        'approved_null_semantics' as requiredness_status,
        'approved_source_chronology_policy' as resolution_hint
    from {{ ref('dq_timeliness_provider_field_metrics') }}
    where field_column in (
        'encounter_datetime',
        'medication_datetime',
        'cost_date',
        'coverage_start_date',
        'coverage_end_date'
    )

    union all

    select
        provider_slug,
        'observations' as entity,
        'height_cm' as field_column,
        count(*) as total_rows,
        count(*) filter (where height_cm is null) as missing_rows,
        'optional' as requiredness_status,
        'component_completeness_flags' as resolution_hint
    from {{ ref('observation_vitals_wide') }}
    group by provider_slug

    union all

    select
        provider_slug,
        'observations',
        'weight_kg',
        count(*),
        count(*) filter (where weight_kg is null),
        'optional',
        'component_completeness_flags'
    from {{ ref('observation_vitals_wide') }}
    group by provider_slug

    union all

    select
        provider_slug,
        'observations',
        'blood_pressure_pair',
        count(*),
        count(*) filter (where systolic_bp is null or diastolic_bp is null),
        'optional',
        'component_completeness_flags'
    from {{ ref('observation_vitals_wide') }}
    group by provider_slug

    union all

    select
        provider_slug,
        'observations',
        'pulse_lpm',
        count(*),
        count(*) filter (where pulse_lpm is null),
        'optional',
        'component_completeness_flags'
    from {{ ref('observation_vitals_wide') }}
    group by provider_slug

    union all

    select
        provider_slug,
        'observations',
        'temperature_c',
        count(*),
        count(*) filter (where temperature_c is null),
        'optional',
        'component_completeness_flags'
    from {{ ref('observation_vitals_wide') }}
    group by provider_slug

    union all

    select
        provider_slug,
        'observations',
        'bmi_payload',
        count(*),
        count(*) filter (where bmi_payload is null),
        'optional',
        'component_completeness_flags'
    from {{ ref('observation_vitals_wide') }}
    group by provider_slug
)

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || field_column") }}
        as completeness_field_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    missing_rows,
    total_rows - missing_rows as populated_rows,
    requiredness_status,
    resolution_hint,
    case
        when missing_rows = 0 then 'complete'
        when requiredness_status = 'optional' then 'managed_optional_sparse'
        when entity = 'cost_records' and field_column = 'cost_amount'
            then 'managed_amount_not_provided'
        when entity = 'cost_records' and field_column = 'cost_date'
            then 'managed_date_not_provided'
        when field_column in ('encounter_datetime', 'medication_datetime')
            then 'managed_event_datetime_not_provided'
        when entity = 'coverage_periods'
            and field_column in ('coverage_start_date', 'coverage_end_date')
            then 'managed_coverage_boundary_not_provided'
        else 'contract_violation'
    end as completeness_field_status,
    case
        when missing_rows = 0 then 'not_applicable_populated'
        when requiredness_status = 'optional' then 'optional_component_not_provided'
        when entity = 'cost_records' and field_column = 'cost_amount'
            then 'null_preserved_amount_not_provided'
        when entity = 'cost_records' and field_column = 'cost_date'
            then 'null_preserved_date_not_provided'
        when field_column in ('encounter_datetime', 'medication_datetime')
            then 'null_preserved_event_datetime_not_provided'
        when entity = 'coverage_periods'
            and field_column in ('coverage_start_date', 'coverage_end_date')
            then 'null_preserved_coverage_boundary_not_provided'
        else 'unknown_requiredness_status'
    end as null_semantics_status,
    case
        when missing_rows = 0 then true
        when entity = 'cost_records' and field_column = 'cost_amount' then false
        else null
    end as usable_for_sum,
    case
        when missing_rows = 0 then true
        when field_column in (
            'cost_date',
            'encounter_datetime',
            'medication_datetime',
            'coverage_start_date',
            'coverage_end_date'
        ) then false
        else null
    end as usable_for_temporal_analysis,
    case
        when missing_rows = 0 then true
        when entity = 'coverage_periods'
            and field_column in ('coverage_start_date', 'coverage_end_date')
            then false
        else null
    end as usable_for_duration,
    case
        when missing_rows = 0 then 'use_source_value'
        when requiredness_status = 'optional' then 'preserve_null_optional_component'
        when entity = 'cost_records' and field_column = 'cost_amount'
            then 'preserve_null_do_not_convert_to_zero'
        when field_column in (
            'cost_date',
            'encounter_datetime',
            'medication_datetime',
            'coverage_start_date',
            'coverage_end_date'
        ) then 'preserve_null_do_not_infer_from_related_entities'
        else 'contract_violation'
    end as safe_downstream_value_policy
from field_checks
