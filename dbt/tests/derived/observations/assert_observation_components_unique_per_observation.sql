select observation_source_row_id, component_name
from {{ ref('observation_vital_components') }}
group by observation_source_row_id, component_name
having count(*) > 1
