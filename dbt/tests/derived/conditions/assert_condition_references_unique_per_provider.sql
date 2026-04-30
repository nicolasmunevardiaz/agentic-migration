with duplicate_refs as (
    select
        provider_slug,
        condition_reference,
        count(*) as row_count
    from {{ ref('condition_fact') }}
    group by provider_slug, condition_reference
)

select *
from duplicate_refs
where row_count > 1
