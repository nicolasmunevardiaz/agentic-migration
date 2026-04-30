select *
from {{ ref('observation_vital_components') }}
where component_value < 0
