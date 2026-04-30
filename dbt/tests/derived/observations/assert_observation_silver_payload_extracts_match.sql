select *
from {{ ref('observation_payload_source_normalized') }}
where not height_matches_silver
   or not weight_matches_silver
   or not systolic_matches_silver
