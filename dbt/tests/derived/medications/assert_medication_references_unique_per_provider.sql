with duplicate_refs as (
    select
        provider_slug,
        medication_reference,
        count(*) as row_count
    from {{ ref('medication_fact') }}
    group by provider_slug, medication_reference
)

select *
from duplicate_refs
where row_count > 1
