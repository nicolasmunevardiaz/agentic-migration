{{ config(materialized='table') }}

with gender_checks as (
    select
        provider_slug,
        'patients' as entity,
        'gender' as field_column,
        count(*) as total_rows,
        count(*) filter (where gender_normalization_status = 'unexpected')
            as invalid_domain_rows,
        'gender_domain_standardization' as resolution_hint
    from {{ ref('patient_source_normalized') }}
    group by provider_slug
),

unit_checks as (
    select
        provider_slug,
        'observations' as entity,
        component_name as field_column,
        count(*) as total_rows,
        count(*) filter (
            where not (
                (component_name = 'height_cm' and component_unit = 'cm')
                or (component_name = 'weight_kg' and component_unit = 'kg')
                or (component_name in ('systolic_bp', 'diastolic_bp') and component_unit = 'mmHg')
                or (component_name = 'pulse_lpm' and component_unit = 'lpm')
                or (component_name = 'temperature_c' and component_unit = 'C')
                or (component_name = 'bmi' and component_unit = 'kg/m2')
            )
        ) as invalid_domain_rows,
        'observation_unit_domain_standardization' as resolution_hint
    from {{ ref('observation_vital_components') }}
    group by provider_slug, component_name
),

domain_checks as (
    select * from gender_checks
    union all
    select * from unit_checks
)

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || field_column") }}
        as validity_domain_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    invalid_domain_rows,
    invalid_domain_rows as affected_rows,
    resolution_hint,
    case
        when invalid_domain_rows > 0 and entity = 'observations'
            then 'open_unit_domain_failure'
        when invalid_domain_rows > 0 then 'open_domain_value_failure'
        else 'complete'
    end as validity_domain_status
from domain_checks
