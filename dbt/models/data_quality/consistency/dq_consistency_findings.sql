{{ config(materialized='table') }}

select
    consistency_reference_metric_id as finding_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    unresolved_reference_rows as affected_rows,
    consistency_reference_status as finding_status,
    case
        when consistency_reference_status = 'contract_violation' then 'critical'
        when consistency_reference_status like 'managed_%' then 'medium'
        else 'low'
    end as severity,
    case
        when field_column = 'member_reference' then 'member_reference_normalization'
        when field_column = 'encounter_reference' then 'encounter_reference_audit_bridge'
        when field_column = 'condition_reference' then 'condition_reference_audit_bridge'
        when field_column = 'medication_reference' then 'medication_reference_audit_bridge'
        else 'reference_standardization'
    end as resolution_hint
from {{ ref('dq_consistency_reference_metrics') }}
where consistency_reference_status <> 'complete'

union all

select
    consistency_code_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    code_domain_drift_rows
        + raw_code_variant_code_rows
        + description_variant_code_rows
        + missing_code_rows as affected_rows,
    consistency_code_status,
    case
        when consistency_code_status = 'contract_violation' then 'critical'
        when consistency_code_status like 'managed_%' then 'medium'
        else 'medium'
    end as severity,
    case
        when consistency_code_status = 'managed_source_code_hint_domain_mismatch'
            then 'code_source_domain_mapping'
        else 'code_description_variant_dimensions'
    end as resolution_hint
from {{ ref('dq_consistency_code_metrics') }}
where consistency_code_status <> 'complete'

union all

select
    consistency_demographic_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    demographic_conflict_rows,
    consistency_demographic_status,
    'medium' as severity,
    'demographic_survivor_rules' as resolution_hint
from {{ ref('dq_consistency_demographic_metrics') }}
where consistency_demographic_status <> 'complete'
