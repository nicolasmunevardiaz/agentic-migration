with duplicate_refs as (
    select
        provider_slug,
        encounter_reference,
        count(*) as row_count
    from {{ ref('encounter_fact') }}
    group by provider_slug, encounter_reference
)

select *
from duplicate_refs
where row_count > 1
