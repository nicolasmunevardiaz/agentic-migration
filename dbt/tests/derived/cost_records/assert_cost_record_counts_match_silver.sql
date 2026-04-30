with silver_counts as (
    select count(*) as row_count
    from {{ source('review', 'silver_cost_records') }}
    where {{ active_batch_filter() }}
),

source_counts as (
    select count(*) as row_count
    from {{ ref('cost_record_source_normalized') }}
),

fact_counts as (
    select count(*) as row_count
    from {{ ref('cost_record_fact') }}
)

select 'source_normalized_count_mismatch' as failure_reason
from silver_counts, source_counts
where silver_counts.row_count != source_counts.row_count

union all

select 'fact_count_mismatch' as failure_reason
from silver_counts, fact_counts
where silver_counts.row_count != fact_counts.row_count
