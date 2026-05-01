{{ config(materialized='view') }}

with source_reference_fields as (
    select provider_slug, 'encounters' as entity, encounter_source_row_id as source_record_id,
        'member_reference' as field_column, member_reference as raw_reference,
        has_orphan_member_reference as has_unresolved_reference,
        'member_reference_normalization' as resolution_hint
    from {{ ref('encounter_fact') }}

    union all

    select provider_slug, 'conditions', condition_source_row_id,
        'member_reference', member_reference, has_orphan_member_reference,
        'member_reference_normalization'
    from {{ ref('condition_fact') }}

    union all

    select provider_slug, 'conditions', condition_source_row_id,
        'encounter_reference', encounter_reference, has_orphan_encounter_reference,
        'encounter_reference_audit_bridge'
    from {{ ref('condition_fact') }}

    union all

    select provider_slug, 'medications', medication_source_row_id,
        'member_reference', member_reference, has_orphan_member_reference,
        'member_reference_normalization'
    from {{ ref('medication_fact') }}

    union all

    select provider_slug, 'medications', medication_source_row_id,
        'encounter_reference', encounter_reference, has_orphan_encounter_reference,
        'encounter_reference_audit_bridge'
    from {{ ref('medication_fact') }}

    union all

    select provider_slug, 'medications', medication_source_row_id,
        'condition_reference', condition_reference, has_orphan_condition_reference,
        'condition_reference_audit_bridge'
    from {{ ref('medication_fact') }}

    union all

    select provider_slug, 'cost_records', cost_record_id,
        'member_reference', member_reference, has_orphan_member_reference,
        'member_reference_normalization'
    from {{ ref('cost_record_fact') }}

    union all

    select provider_slug, 'cost_records', cost_record_id,
        'encounter_reference', encounter_reference, has_orphan_encounter_reference,
        'encounter_reference_audit_bridge'
    from {{ ref('cost_record_fact') }}

    union all

    select provider_slug, 'cost_records', cost_record_id,
        'medication_reference', medication_reference, has_orphan_medication_reference,
        'medication_reference_audit_bridge'
    from {{ ref('cost_record_fact') }}
),

reference_fields as (
    select
        provider_slug,
        entity,
        source_record_id,
        field_column,
        {{ dq_trimmed_text("raw_reference") }} as raw_reference,
        has_unresolved_reference,
        resolution_hint
    from source_reference_fields
)

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || source_record_id || '|' || field_column") }}
        as reference_standardization_id,
    provider_slug,
    entity,
    source_record_id,
    field_column,
    raw_reference,
    {{ dq_reference_final_segment("raw_reference") }} as reference_final_segment,
    case
        when raw_reference is null then null
        else {{ dq_provider_scoped_reference_key("provider_slug", "raw_reference") }}
    end as provider_scoped_reference_key,
    has_unresolved_reference,
    resolution_hint,
    case
        when raw_reference is null then 'missing_reference'
        when has_unresolved_reference then 'reference_unresolved'
        else 'reference_resolved'
    end as reference_standardization_status
from reference_fields
