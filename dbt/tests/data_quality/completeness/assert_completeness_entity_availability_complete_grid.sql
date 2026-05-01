select provider_slug, count(*) as entity_count
from {{ ref('dq_completeness_provider_entity_availability') }}
group by provider_slug
having count(*) <> 7
