with fact_counts as (
    select
        patient_provider_member_id,
        count(*) as cost_record_row_count,
        count(*) filter (where source_cost_amount is not null) as populated_amount_row_count,
        count(*) filter (where has_missing_cost_amount) as missing_amount_row_count,
        count(*) filter (where has_missing_cost_date) as missing_date_row_count,
        count(*) filter (where has_orphan_encounter_reference) as orphan_encounter_reference_row_count,
        count(*) filter (where has_orphan_medication_reference) as orphan_medication_reference_row_count
    from {{ ref('cost_record_fact') }}
    group by patient_provider_member_id
),

summary_counts as (
    select
        patient_provider_member_id,
        cost_record_row_count,
        populated_amount_row_count,
        missing_amount_row_count,
        missing_date_row_count,
        orphan_encounter_reference_row_count,
        orphan_medication_reference_row_count
    from {{ ref('cost_record_member_summary') }}
)

select fact_counts.patient_provider_member_id
from fact_counts
full outer join summary_counts
    on fact_counts.patient_provider_member_id = summary_counts.patient_provider_member_id
where fact_counts.cost_record_row_count is distinct from summary_counts.cost_record_row_count
   or fact_counts.populated_amount_row_count is distinct from summary_counts.populated_amount_row_count
   or fact_counts.missing_amount_row_count is distinct from summary_counts.missing_amount_row_count
   or fact_counts.missing_date_row_count is distinct from summary_counts.missing_date_row_count
   or fact_counts.orphan_encounter_reference_row_count is distinct from summary_counts.orphan_encounter_reference_row_count
   or fact_counts.orphan_medication_reference_row_count is distinct from summary_counts.orphan_medication_reference_row_count
