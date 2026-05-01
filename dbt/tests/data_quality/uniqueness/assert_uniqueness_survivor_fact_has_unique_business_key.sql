select provider_member_plan_period_key
from {{ ref('coverage_period_survivor_fact') }}
group by provider_member_plan_period_key
having count(*) > 1
