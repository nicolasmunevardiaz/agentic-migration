select *
from {{ ref('condition_fact') }}
where has_missing_condition_source_code <> (condition_source_code is null)
   or has_missing_condition_code_hint <> (condition_code_hint is null)
   or has_missing_condition_description <> (condition_description is null)
   or has_orphan_member_reference <> (not has_patient_dimension_match)
   or has_orphan_encounter_reference <> (not has_encounter_fact_match)
   or source_code_matches_hint <> (
       condition_source_code is not null
       and condition_code_hint is not null
       and condition_source_code = condition_code_hint
   )
