{{ config(materialized='view') }}

select
    cost_record_status_id,
    record_status,
    count(*) as cost_record_row_count
from {{ ref('cost_record_source_normalized') }}
group by cost_record_status_id, record_status
