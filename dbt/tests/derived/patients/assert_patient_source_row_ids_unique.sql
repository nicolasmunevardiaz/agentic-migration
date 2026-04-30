select patient_source_row_id
from {{ ref('patient_source_normalized') }}
group by patient_source_row_id
having count(*) > 1
