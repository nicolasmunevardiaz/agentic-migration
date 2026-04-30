select *
from {{ ref('encounter_fact') }}
where has_missing_encounter_datetime <> (encounter_datetime is null)
   or has_orphan_member_reference <> (not has_patient_dimension_match)
   or has_implausible_encounter_datetime <> (
       encounter_datetime < timestamp with time zone '1900-01-01 00:00:00+00'
       or encounter_datetime > current_timestamp + interval '10 years'
   )
