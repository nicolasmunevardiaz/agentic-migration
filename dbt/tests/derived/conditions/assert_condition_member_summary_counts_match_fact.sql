with fact_counts as (
    select
        patient_provider_member_id,
        count(*) as fact_row_count,
        count(distinct condition_reference) as fact_condition_count
    from {{ ref('condition_fact') }}
    group by patient_provider_member_id
)

select
    summary.patient_provider_member_id,
    summary.condition_row_count,
    fact_counts.fact_row_count,
    summary.distinct_condition_count,
    fact_counts.fact_condition_count
from {{ ref('condition_member_summary') }} as summary
join fact_counts using (patient_provider_member_id)
where summary.condition_row_count <> fact_counts.fact_row_count
   or summary.distinct_condition_count <> fact_counts.fact_condition_count
