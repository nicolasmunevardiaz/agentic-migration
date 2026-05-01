{{ config(materialized='view') }}

select distinct
    encounter_coverage_status_id,
    coverage_status,
    lower(coverage_status) as coverage_status_label,
    case
        when coverage_status = 'COVERED' then true
        when coverage_status in ('OUT_OF_COVERAGE', 'UNINSURED') then false
        else null
    end as indicates_covered
from {{ ref('encounter_source_normalized') }}
