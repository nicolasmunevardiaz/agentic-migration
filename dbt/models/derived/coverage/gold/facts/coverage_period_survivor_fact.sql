{{ config(materialized='view') }}

select *
from {{ ref('coverage_period_survivor_candidate') }}
where is_survivor
