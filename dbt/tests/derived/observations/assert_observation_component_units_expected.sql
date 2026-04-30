select *
from {{ ref('observation_vital_components') }}
where (component_name = 'height_cm' and component_unit <> 'cm')
   or (component_name = 'weight_kg' and component_unit <> 'kg')
   or (component_name in ('systolic_bp', 'diastolic_bp') and component_unit <> 'mmHg')
   or (component_name = 'pulse_lpm' and component_unit <> 'lpm')
   or (component_name = 'temperature_c' and component_unit <> 'C')
   or (component_name = 'bmi' and component_unit <> 'kg/m2')
