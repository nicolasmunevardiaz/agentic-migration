with fact_counts as (
    select
        patient_provider_member_id,
        count(*) as fact_row_count,
        count(distinct medication_reference) as fact_medication_count
    from {{ ref('medication_fact') }}
    group by patient_provider_member_id
)

select
    summary.patient_provider_member_id,
    summary.medication_row_count,
    fact_counts.fact_row_count,
    summary.distinct_medication_count,
    fact_counts.fact_medication_count
from {{ ref('medication_member_summary') }} as summary
join fact_counts using (patient_provider_member_id)
where summary.medication_row_count <> fact_counts.fact_row_count
   or summary.distinct_medication_count <> fact_counts.fact_medication_count
