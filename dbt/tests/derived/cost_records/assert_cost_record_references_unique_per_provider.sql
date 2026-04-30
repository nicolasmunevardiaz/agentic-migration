select provider_slug, medication_reference, source_row_id, count(*) as duplicate_count
from {{ ref('cost_record_source_normalized') }}
group by provider_slug, medication_reference, source_row_id
having count(*) > 1
