with standardized as (
    select count(*) as row_count
    from {{ ref('dq_standardized_temporal_fields') }}
),

metrics as (
    select sum(total_rows) as row_count
    from {{ ref('dq_timeliness_provider_field_metrics') }}
)

select
    standardized.row_count as standardized_row_count,
    metrics.row_count as metric_row_count
from standardized
cross join metrics
where standardized.row_count <> metrics.row_count
