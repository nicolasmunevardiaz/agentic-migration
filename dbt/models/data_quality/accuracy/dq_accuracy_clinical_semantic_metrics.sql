{{ config(materialized='table') }}

with condition_checks as (
    select
        provider_slug,
        'conditions' as entity,
        'condition_source_code' as field_column,
        count(*) as total_rows,
        count(*) filter (where not source_code_matches_hint) as affected_rows,
        count(distinct condition_source_code) filter (
            where condition_source_code is not null
        ) as distinct_source_code_count,
        count(distinct condition_code_hint) filter (
            where condition_code_hint is not null
        ) as distinct_code_hint_count,
        'condition_source_code_is_primary_domain_hint_is_metadata' as resolution_hint,
        'managed_valid_code_with_domain_hint_mismatch' as managed_status
    from {{ ref('condition_fact') }}
    group by provider_slug
),

medication_checks as (
    select
        provider_slug,
        'medications' as entity,
        'medication_source_code' as field_column,
        count(*) as total_rows,
        count(*) filter (
            where medication_canonical_status <> 'complete'
        ) as affected_rows,
        count(distinct canonical_medication_code) filter (
            where canonical_medication_code is not null
        ) as distinct_source_code_count,
        null::bigint as distinct_code_hint_count,
        'medication_canonicalization_preserve_variants' as resolution_hint,
        case
            when count(*) filter (
                where medication_canonical_status = 'managed_description_match_code_conflict_preserved'
            ) > 0 then 'managed_description_match_code_conflict_preserved'
            when count(*) filter (
                where medication_canonical_status = 'managed_canonical_medication_code_with_variants'
            ) > 0 then 'managed_canonical_medication_code_with_variants'
            else 'complete'
        end as managed_status
    from {{ ref('dq_accuracy_medication_canonical_dimension') }}
    group by provider_slug
),

clinical_checks as (
    select * from condition_checks
    union all
    select * from medication_checks
)

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || field_column") }}
        as accuracy_clinical_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    affected_rows,
    distinct_source_code_count,
    distinct_code_hint_count,
    resolution_hint,
    case
        when affected_rows > 0 then managed_status
        else 'complete'
    end as accuracy_clinical_status
from clinical_checks
