select *
from {{ ref('dq_completeness_field_metrics') }}
where entity = 'observations'
  and field_column in (
    'height_cm',
    'weight_kg',
    'blood_pressure_pair',
    'pulse_lpm',
    'temperature_c',
    'bmi_payload'
  )
  and missing_rows > 0
  and completeness_field_status <> 'managed_optional_sparse'
