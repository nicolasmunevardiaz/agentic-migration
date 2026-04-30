{{ config(materialized='view') }}

select
    patient_provider_member_id,
    provider_slug,
    member_reference,
    count(*) as cost_record_row_count,
    count(*) filter (where source_cost_amount is not null) as populated_amount_row_count,
    count(*) filter (where has_missing_cost_amount) as missing_amount_row_count,
    count(*) filter (where has_missing_cost_date) as missing_date_row_count,
    count(*) filter (where has_orphan_encounter_reference) as orphan_encounter_reference_row_count,
    count(*) filter (where has_orphan_medication_reference) as orphan_medication_reference_row_count,
    min(cost_date) as first_cost_date,
    max(cost_date) as last_cost_date
from {{ ref('cost_record_fact') }}
group by patient_provider_member_id, provider_slug, member_reference
