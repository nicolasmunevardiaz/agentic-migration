select *
from {{ ref('coverage_period_fact') }}
where has_inverted_date_range
