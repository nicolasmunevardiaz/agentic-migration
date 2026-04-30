with source_counts as (
    select provider_slug, count(distinct patient_provider_member_id) as source_member_count
    from {{ ref('patient_source_normalized') }}
    group by provider_slug
),

dimension_counts as (
    select provider_slug, count(*) as dimension_member_count
    from {{ ref('patient_dimension') }}
    group by provider_slug
)

select
    coalesce(source_counts.provider_slug, dimension_counts.provider_slug) as provider_slug,
    source_counts.source_member_count,
    dimension_counts.dimension_member_count
from source_counts
full outer join dimension_counts using (provider_slug)
where coalesce(source_counts.source_member_count, -1)
   <> coalesce(dimension_counts.dimension_member_count, -1)
