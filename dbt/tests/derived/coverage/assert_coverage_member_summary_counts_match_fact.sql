with fact_counts as (
    select
        patient_provider_member_id,
        count(*) as fact_row_count,
        count(distinct coverage_status) as fact_status_count
    from {{ ref('coverage_period_fact') }}
    group by patient_provider_member_id
)

select
    summary.patient_provider_member_id,
    summary.coverage_period_row_count,
    fact_counts.fact_row_count,
    summary.coverage_status_count,
    fact_counts.fact_status_count
from {{ ref('coverage_member_summary') }} as summary
join fact_counts using (patient_provider_member_id)
where summary.coverage_period_row_count <> fact_counts.fact_row_count
   or summary.coverage_status_count <> fact_counts.fact_status_count
