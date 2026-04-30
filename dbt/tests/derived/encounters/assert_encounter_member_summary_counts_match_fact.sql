with fact_counts as (
    select
        patient_provider_member_id,
        count(*) as fact_row_count,
        count(distinct encounter_reference) as fact_encounter_count
    from {{ ref('encounter_fact') }}
    group by patient_provider_member_id
)

select
    summary.patient_provider_member_id,
    summary.encounter_row_count,
    fact_counts.fact_row_count,
    summary.distinct_encounter_count,
    fact_counts.fact_encounter_count
from {{ ref('encounter_member_summary') }} as summary
join fact_counts using (patient_provider_member_id)
where summary.encounter_row_count <> fact_counts.fact_row_count
   or summary.distinct_encounter_count <> fact_counts.fact_encounter_count
