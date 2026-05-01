{{ config(materialized='table') }}

select
    {{ provider_scoped_hash("provider_slug", "'observations|vital_components'") }}
        as accuracy_observation_metric_id,
    provider_slug,
    'observations' as entity,
    'vital_components' as field_column,
    count(*) as total_rows,
    count(*) filter (where height_matches_silver is false) as height_mismatch_rows,
    count(*) filter (where weight_matches_silver is false) as weight_mismatch_rows,
    count(*) filter (where systolic_matches_silver is false) as systolic_mismatch_rows,
    count(*) filter (
        where bmi_payload_recomputed_abs_delta > 0.1
    ) as bmi_recomputed_mismatch_rows,
    max(bmi_payload_recomputed_abs_delta) as max_bmi_payload_recomputed_abs_delta,
    count(*) filter (
        where height_matches_silver is false
           or weight_matches_silver is false
           or systolic_matches_silver is false
           or bmi_payload_recomputed_abs_delta > 0.1
    ) as affected_rows,
    'observation_computational_reconciliation' as resolution_hint,
    case
        when count(*) filter (
            where height_matches_silver is false
               or weight_matches_silver is false
               or systolic_matches_silver is false
               or bmi_payload_recomputed_abs_delta > 0.1
        ) > 0 then 'open_observation_computational_review'
        else 'complete'
    end as accuracy_observation_status
from {{ ref('observation_vitals_wide') }}
group by provider_slug
