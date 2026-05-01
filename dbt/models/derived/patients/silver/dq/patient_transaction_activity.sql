{{ config(materialized='view') }}

with patients as (
    select
        patient_provider_member_id,
        provider_slug,
        member_reference,
        review_batch_id
    from {{ ref('patient_dimension') }}
),

coverage as (
    select provider_slug, member_reference, count(*) as coverage_rows
    from {{ source('review', 'silver_coverage_periods') }}
    where {{ active_batch_filter() }}
      and member_reference is not null
    group by provider_slug, member_reference
),

encounters as (
    select
        provider_slug,
        member_reference,
        count(*) as encounter_rows,
        min(encounter_datetime) as first_encounter_datetime,
        max(encounter_datetime) as last_encounter_datetime
    from {{ source('review', 'silver_encounters') }}
    where {{ active_batch_filter() }}
      and member_reference is not null
    group by provider_slug, member_reference
),

conditions as (
    select provider_slug, member_reference, count(*) as condition_rows
    from {{ source('review', 'silver_conditions') }}
    where {{ active_batch_filter() }}
      and member_reference is not null
    group by provider_slug, member_reference
),

medications as (
    select
        provider_slug,
        member_reference,
        count(*) as medication_rows,
        min(medication_datetime) as first_medication_datetime,
        max(medication_datetime) as last_medication_datetime
    from {{ source('review', 'silver_medications') }}
    where {{ active_batch_filter() }}
      and member_reference is not null
    group by provider_slug, member_reference
),

observations as (
    select
        provider_slug,
        member_reference,
        count(*) as observation_rows,
        count(*) filter (where observation_payload_raw is not null) as observation_payload_rows,
        min(observation_datetime) as first_observation_datetime,
        max(observation_datetime) as last_observation_datetime
    from {{ source('review', 'silver_observations') }}
    where {{ active_batch_filter() }}
      and member_reference is not null
    group by provider_slug, member_reference
),

costs as (
    select
        provider_slug,
        member_reference,
        count(*) as cost_rows,
        min(cost_date) as first_cost_date,
        max(cost_date) as last_cost_date
    from {{ source('review', 'silver_cost_records') }}
    where {{ active_batch_filter() }}
      and member_reference is not null
    group by provider_slug, member_reference
),

activity as (
    select
        patients.patient_provider_member_id,
        patients.provider_slug,
        patients.member_reference,
        patients.review_batch_id,
        coalesce(coverage.coverage_rows, 0) as coverage_rows,
        coalesce(encounters.encounter_rows, 0) as encounter_rows,
        coalesce(conditions.condition_rows, 0) as condition_rows,
        coalesce(medications.medication_rows, 0) as medication_rows,
        coalesce(observations.observation_rows, 0) as observation_rows,
        coalesce(observations.observation_payload_rows, 0) as observation_payload_rows,
        coalesce(costs.cost_rows, 0) as cost_rows,
        coalesce(encounters.encounter_rows, 0)
            + coalesce(conditions.condition_rows, 0)
            + coalesce(medications.medication_rows, 0)
            + coalesce(observations.observation_rows, 0)
            + coalesce(costs.cost_rows, 0) as transactional_row_count,
        coalesce(encounters.encounter_rows, 0)
            + coalesce(conditions.condition_rows, 0)
            + coalesce(medications.medication_rows, 0)
            + coalesce(observations.observation_rows, 0) as clinical_transaction_row_count,
        coalesce(costs.cost_rows, 0) as financial_transaction_row_count,
        coalesce(encounters.encounter_rows, 0)
            + coalesce(conditions.condition_rows, 0)
            + coalesce(medications.medication_rows, 0)
            + coalesce(observations.observation_rows, 0)
            + coalesce(costs.cost_rows, 0) > 0 as has_transactional_data,
        coalesce(encounters.encounter_rows, 0)
            + coalesce(conditions.condition_rows, 0)
            + coalesce(medications.medication_rows, 0)
            + coalesce(observations.observation_rows, 0) > 0 as has_clinical_transactional_data,
        coalesce(costs.cost_rows, 0) > 0 as has_financial_transactional_data,
        coalesce(observations.observation_payload_rows, 0) > 0 as has_observation_payload,
        least(
            encounters.first_encounter_datetime,
            medications.first_medication_datetime,
            observations.first_observation_datetime,
            costs.first_cost_date::timestamp with time zone
        ) as first_activity_datetime,
        greatest(
            encounters.last_encounter_datetime,
            medications.last_medication_datetime,
            observations.last_observation_datetime,
            costs.last_cost_date::timestamp with time zone
        ) as last_activity_datetime
    from patients
    left join coverage
      on patients.provider_slug = coverage.provider_slug
     and patients.member_reference = coverage.member_reference
    left join encounters
      on patients.provider_slug = encounters.provider_slug
     and patients.member_reference = encounters.member_reference
    left join conditions
      on patients.provider_slug = conditions.provider_slug
     and patients.member_reference = conditions.member_reference
    left join medications
      on patients.provider_slug = medications.provider_slug
     and patients.member_reference = medications.member_reference
    left join observations
      on patients.provider_slug = observations.provider_slug
     and patients.member_reference = observations.member_reference
    left join costs
      on patients.provider_slug = costs.provider_slug
     and patients.member_reference = costs.member_reference
)

select * from activity
