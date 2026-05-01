{{ config(materialized='table') }}

with standardized_codes as (
    select
        provider_slug,
        entity,
        field_column,
        count(*) as total_rows,
        count(*) filter (where raw_code is null) as missing_code_rows,
        count(*) filter (where raw_code is not null) as present_code_rows,
        count(*) filter (where normalized_code_token is null and raw_code is not null)
            as missing_normalized_token_rows,
        count(*) filter (where has_code_domain_drift) as code_domain_drift_rows,
        count(distinct raw_code) filter (where raw_code is not null)
            as distinct_raw_code_count,
        count(distinct normalized_code_token) filter (
            where normalized_code_token is not null
        ) as distinct_normalized_code_token_count
    from {{ ref('dq_standardized_code_fields') }}
    group by provider_slug, entity, field_column
),

condition_domain_mapping as (
    select
        provider_slug,
        'conditions' as entity,
        'condition_source_code' as field_column,
        count(*) as mapping_rows,
        count(*) filter (
            where condition_code_consistency_status
                = 'managed_source_code_hint_domain_mismatch'
        ) as managed_domain_mismatch_rows
    from {{ ref('dq_condition_code_domain_mapping') }}
    group by provider_slug
),

medication_variants as (
    select
        provider_slug,
        'medications' as entity,
        'medication_source_code' as field_column,
        count(*) as normalized_code_rows,
        count(*) filter (where has_raw_code_variants) as raw_code_variant_code_rows,
        count(*) filter (where has_description_variants) as description_variant_code_rows,
        max(raw_code_variant_count) as max_raw_code_variant_count,
        max(description_variant_count) as max_description_variant_count,
        count(*) filter (
            where medication_code_consistency_status
                = 'managed_canonical_medication_code_with_variants'
        ) as managed_canonical_variant_rows,
        count(*) filter (
            where medication_code_consistency_status
                = 'managed_description_match_code_conflict_preserved'
        ) as managed_description_conflict_rows
    from {{ ref('dq_medication_code_consistency_bridge') }}
    group by provider_slug
)

select
    {{ provider_scoped_hash("standardized_codes.provider_slug", "standardized_codes.entity || '|' || standardized_codes.field_column") }}
        as consistency_code_metric_id,
    standardized_codes.provider_slug,
    standardized_codes.entity,
    standardized_codes.field_column,
    standardized_codes.total_rows,
    standardized_codes.missing_code_rows,
    standardized_codes.present_code_rows,
    standardized_codes.missing_normalized_token_rows,
    standardized_codes.code_domain_drift_rows,
    standardized_codes.distinct_raw_code_count,
    standardized_codes.distinct_normalized_code_token_count,
    coalesce(medication_variants.normalized_code_rows, 0) as normalized_code_rows,
    coalesce(medication_variants.raw_code_variant_code_rows, 0)
        as raw_code_variant_code_rows,
    coalesce(medication_variants.description_variant_code_rows, 0)
        as description_variant_code_rows,
    coalesce(medication_variants.max_raw_code_variant_count, 0)
        as max_raw_code_variant_count,
    coalesce(medication_variants.max_description_variant_count, 0)
        as max_description_variant_count,
    coalesce(condition_domain_mapping.managed_domain_mismatch_rows, 0)
        as managed_domain_mismatch_rows,
    coalesce(medication_variants.managed_canonical_variant_rows, 0)
        as managed_canonical_variant_rows,
    coalesce(medication_variants.managed_description_conflict_rows, 0)
        as managed_description_conflict_rows,
    case
        when standardized_codes.missing_normalized_token_rows > 0 then 'contract_violation'
        when coalesce(condition_domain_mapping.managed_domain_mismatch_rows, 0) > 0
            then 'managed_source_code_hint_domain_mismatch'
        when coalesce(medication_variants.managed_description_conflict_rows, 0) > 0
            then 'managed_description_match_code_conflict_preserved'
        when coalesce(medication_variants.managed_canonical_variant_rows, 0) > 0
          or coalesce(medication_variants.raw_code_variant_code_rows, 0) > 0
            then 'managed_canonical_medication_code_with_variants'
        when standardized_codes.missing_code_rows > 0 then 'managed_missing_code_preserved'
        else 'complete'
    end as consistency_code_status
from standardized_codes
left join condition_domain_mapping
    on standardized_codes.provider_slug = condition_domain_mapping.provider_slug
   and standardized_codes.entity = condition_domain_mapping.entity
   and standardized_codes.field_column = condition_domain_mapping.field_column
left join medication_variants
    on standardized_codes.provider_slug = medication_variants.provider_slug
   and standardized_codes.entity = medication_variants.entity
   and standardized_codes.field_column = medication_variants.field_column
