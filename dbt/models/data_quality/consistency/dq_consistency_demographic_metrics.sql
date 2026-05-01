{{ config(materialized='table') }}

select
    {{ provider_scoped_hash("provider_slug", "'patients|demographics'") }}
        as consistency_demographic_metric_id,
    provider_slug,
    'patients' as entity,
    'demographics' as field_column,
    count(*) as total_rows,
    count(*) filter (where has_gender_conflict) as gender_conflict_rows,
    count(*) filter (where has_birth_date_conflict) as birth_date_conflict_rows,
    count(*) filter (where has_demographic_conflict) as demographic_conflict_rows,
    count(*) filter (
        where demographic_survivor_status = 'managed_demographic_survivor_selected'
    ) as managed_demographic_survivor_rows,
    case
        when count(*) filter (
            where demographic_survivor_status = 'managed_demographic_survivor_selected'
        ) > 0 then 'managed_demographic_survivor_selected'
        else 'complete'
    end as consistency_demographic_status
from {{ ref('dq_patient_demographic_survivor') }}
group by provider_slug
