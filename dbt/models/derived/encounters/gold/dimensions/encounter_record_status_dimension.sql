{{ config(materialized='view') }}

select distinct
    encounter_record_status_id,
    record_status,
    case
        when record_status = 'active' then true
        when record_status = 'inactive' then false
        else null
    end as indicates_active_record
from {{ ref('encounter_source_normalized') }}
