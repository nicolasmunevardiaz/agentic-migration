select *
from {{ ref('observation_vitals_wide') }}
where has_payload_height <> (height_cm is not null)
   or has_payload_weight <> (weight_kg is not null)
   or has_payload_bp_pair <> (systolic_bp is not null and diastolic_bp is not null)
   or has_payload_pulse <> (pulse_lpm is not null)
   or has_payload_temperature <> (temperature_c is not null)
   or has_payload_bmi <> (bmi_payload is not null)
   or can_recompute_bmi <> (height_cm is not null and height_cm <> 0 and weight_kg is not null)
