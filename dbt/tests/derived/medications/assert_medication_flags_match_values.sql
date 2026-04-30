select *
from {{ ref('medication_fact') }}
where has_missing_medication_source_code <> (medication_source_code is null)
   or has_missing_medication_description <> (medication_description is null)
   or has_missing_medication_datetime <> (medication_datetime is null)
   or has_orphan_member_reference <> (not has_patient_dimension_match)
   or has_orphan_encounter_reference <> (not has_encounter_fact_match)
   or has_orphan_condition_reference <> (not has_condition_fact_match)
   or has_implausible_medication_datetime <> (
       medication_datetime < timestamp with time zone '1900-01-01 00:00:00+00'
       or medication_datetime > current_timestamp + interval '10 years'
   )
