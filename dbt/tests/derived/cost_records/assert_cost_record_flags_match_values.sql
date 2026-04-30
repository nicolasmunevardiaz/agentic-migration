select *
from {{ ref('cost_record_fact') }}
where has_missing_cost_amount != (source_cost_amount is null)
   or has_nonpositive_cost_amount != (source_cost_amount <= 0)
   or has_missing_cost_date != (cost_date is null)
   or has_implausible_cost_date != (
        cost_date < timestamp with time zone '1900-01-01 00:00:00+00'
        or cost_date > current_timestamp + interval '10 years'
   )
   or has_orphan_member_reference != (not has_patient_dimension_match)
   or has_orphan_encounter_reference != (not has_encounter_fact_match)
   or has_orphan_medication_reference != (not has_medication_fact_match)
