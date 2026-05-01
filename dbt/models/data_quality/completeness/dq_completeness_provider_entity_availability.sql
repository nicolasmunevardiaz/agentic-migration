{{ config(materialized='table') }}

with providers as (
    select distinct provider_slug
    from {{ ref('patient_dimension') }}
),

entities as (
    select *
    from (
        values
            ('patients'),
            ('coverage_periods'),
            ('encounters'),
            ('conditions'),
            ('observations'),
            ('medications'),
            ('cost_records')
    ) as entity_list(entity)
),

provider_entities as (
    select
        providers.provider_slug,
        entities.entity
    from providers
    cross join entities
),

entity_counts as (
    select provider_slug, 'patients' as entity, count(*) as row_count
    from {{ ref('patient_dimension') }}
    group by provider_slug

    union all

    select provider_slug, 'coverage_periods', count(*)
    from {{ ref('coverage_period_fact') }}
    group by provider_slug

    union all

    select provider_slug, 'encounters', count(*)
    from {{ ref('encounter_fact') }}
    group by provider_slug

    union all

    select provider_slug, 'conditions', count(*)
    from {{ ref('condition_fact') }}
    group by provider_slug

    union all

    select provider_slug, 'observations', count(*)
    from {{ ref('observation_vitals_wide') }}
    group by provider_slug

    union all

    select provider_slug, 'medications', count(*)
    from {{ ref('medication_fact') }}
    group by provider_slug

    union all

    select provider_slug, 'cost_records', count(*)
    from {{ ref('cost_record_fact') }}
    group by provider_slug
),

classified as (
    select
        provider_entities.provider_slug,
        provider_entities.entity,
        coalesce(entity_counts.row_count, 0) as row_count,
        case
            when provider_entities.provider_slug = 'data_provider_5_pacific_shield_insurance'
             and provider_entities.entity in (
                'encounters',
                'conditions',
                'observations',
                'medications',
                'cost_records'
             ) then false
            else true
        end as is_required_entity
    from provider_entities
    left join entity_counts
        on provider_entities.provider_slug = entity_counts.provider_slug
       and provider_entities.entity = entity_counts.entity
)

select
    {{ provider_scoped_hash("provider_slug", "entity") }} as completeness_entity_availability_id,
    provider_slug,
    entity,
    row_count,
    is_required_entity,
    case
        when not is_required_entity then 'managed_provider_not_applicable'
        when row_count = 0 then 'open_required_entity_missing'
        else 'complete'
    end as completeness_entity_status,
    case
        when not is_required_entity then 'provider_entity_availability_contract'
        when row_count = 0 then 'provider_entity_requiredness_contract'
        else 'none'
    end as resolution_hint
from classified
