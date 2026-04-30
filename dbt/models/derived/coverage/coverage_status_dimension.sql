{{ config(materialized='view') }}

select distinct
    md5('coverage_status|' || coalesce(coverage_status, 'UNKNOWN')) as coverage_status_id,
    coalesce(coverage_status, 'UNKNOWN') as coverage_status,
    lower(coalesce(coverage_status, 'UNKNOWN')) as coverage_status_label,
    case
        when coverage_status = 'COVERED' then true
        when coverage_status = 'OUT_OF_COVERAGE' then false
        else null
    end as indicates_covered
from {{ ref('coverage_source_normalized') }}
