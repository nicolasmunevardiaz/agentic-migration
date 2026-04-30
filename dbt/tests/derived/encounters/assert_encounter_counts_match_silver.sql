with silver_counts as (
    select provider_slug, count(*) as silver_rows
    from {{ source('review', 'silver_encounters') }}
    where {{ active_batch_filter() }}
    group by provider_slug
),

derived_counts as (
    select provider_slug, count(*) as derived_rows
    from {{ ref('encounter_fact') }}
    group by provider_slug
)

select
    coalesce(silver_counts.provider_slug, derived_counts.provider_slug) as provider_slug,
    silver_counts.silver_rows,
    derived_counts.derived_rows
from silver_counts
full outer join derived_counts using (provider_slug)
where coalesce(silver_counts.silver_rows, -1) <> coalesce(derived_counts.derived_rows, -1)
