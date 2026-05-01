{{ config(materialized='view') }}

with source_code_fields as (
    select
        provider_slug,
        'conditions' as entity,
        condition_source_row_id as source_record_id,
        'condition_source_code' as field_column,
        condition_source_code as raw_code,
        condition_code_hint as code_system_hint,
        condition_description as source_description,
        not source_code_matches_hint as has_code_domain_drift,
        'code_source_domain_mapping' as resolution_hint
    from {{ ref('condition_fact') }}

    union all

    select
        provider_slug,
        'medications' as entity,
        medication_source_row_id as source_record_id,
        'medication_source_code' as field_column,
        medication_source_code as raw_code,
        null::text as code_system_hint,
        medication_description as source_description,
        has_missing_medication_source_code as has_code_domain_drift,
        'code_description_variant_dimensions' as resolution_hint
    from {{ ref('medication_fact') }}
),

code_fields as (
    select
        provider_slug,
        entity,
        source_record_id,
        field_column,
        {{ dq_trimmed_text("raw_code") }} as source_raw_code,
        {{ dq_clean_wrapped_text("raw_code") }} as raw_code,
        {{ dq_clean_wrapped_text("code_system_hint") }} as code_system_hint,
        source_description,
        has_code_domain_drift,
        resolution_hint
    from source_code_fields
)

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || source_record_id || '|' || field_column") }}
        as code_standardization_id,
    provider_slug,
    entity,
    source_record_id,
    field_column,
    source_raw_code,
    raw_code,
    {{ dq_normalize_code_token("raw_code") }} as normalized_code_token,
    code_system_hint,
    source_description,
    has_code_domain_drift,
    resolution_hint,
    case
        when raw_code is null then 'missing_code'
        when has_code_domain_drift then 'review_code_domain'
        else 'normalized'
    end as code_standardization_status
from code_fields
