{{ config(materialized='table') }}

with condition_codes as (
    select *
    from {{ ref('dq_standardized_code_fields') }}
    where entity = 'conditions'
      and field_column = 'condition_source_code'
),

classified as (
    select
        code_standardization_id,
        provider_slug,
        source_record_id,
        source_raw_code,
        raw_code as provider_condition_code_raw,
        normalized_code_token as provider_condition_code_normalized,
        code_system_hint as clinical_code_raw,
        {{ dq_normalize_code_token("code_system_hint") }} as clinical_code_normalized,
        source_description,
        has_code_domain_drift,
        case
            when code_system_hint is null then 'missing'
            when code_system_hint ~ '^[0-9]{6,}$' then 'snomed_ct'
            when code_system_hint ~ '^[A-TV-Z][0-9][A-Z0-9](\\.[A-Z0-9]+)?$' then 'icd_10_cm'
            when code_system_hint ~ '^[0-9]{3}(\\.[0-9]+)?$' then 'icd_9_cm'
            else 'unknown'
        end as clinical_code_system,
        case
            when code_system_hint is null then 'missing_clinical_code_hint'
            when code_system_hint ~ '^[0-9]{6,}$'
              or code_system_hint ~ '^[A-TV-Z][0-9][A-Z0-9](\\.[A-Z0-9]+)?$'
              or code_system_hint ~ '^[0-9]{3}(\\.[0-9]+)?$'
                then 'classified_by_contract_pattern'
            else 'unresolved_pattern'
        end as clinical_code_system_inference_status
    from condition_codes
)

select
    code_standardization_id as condition_code_domain_bridge_id,
    provider_slug,
    source_record_id,
    source_raw_code,
    provider_condition_code_raw,
    provider_condition_code_normalized,
    clinical_code_raw,
    clinical_code_normalized,
    clinical_code_system,
    clinical_code_system_inference_status,
    source_description,
    has_code_domain_drift,
    case
        when has_code_domain_drift then 'managed_split_provider_and_clinical_codes'
        else 'complete'
    end as condition_code_domain_status
from classified
