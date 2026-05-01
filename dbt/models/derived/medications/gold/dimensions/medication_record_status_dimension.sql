{{ config(materialized='view') }}

select distinct
    medication_record_status_id,
    record_status,
    case
        when record_status = 'active' then true
        when record_status = 'inactive' then false
        else null
    end as indicates_active_record
from {{ ref('medication_source_normalized') }}
