{{ config(materialized='table') }}

select
    completeness_entity_availability_id as finding_id,
    provider_slug,
    entity,
    'entity_presence' as field_column,
    row_count as total_rows,
    case
        when completeness_entity_status = 'managed_provider_not_applicable' then 0
        when completeness_entity_status = 'open_required_entity_missing' then 1
        else 0
    end as affected_rows,
    completeness_entity_status as finding_status,
    case
        when completeness_entity_status = 'open_required_entity_missing' then 'critical'
        when completeness_entity_status = 'managed_provider_not_applicable' then 'low'
        else 'low'
    end as severity,
    resolution_hint
from {{ ref('dq_completeness_provider_entity_availability') }}
where completeness_entity_status <> 'complete'

union all

select
    completeness_field_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    missing_rows,
    completeness_field_status,
    case
        when completeness_field_status = 'open_pending_source_validation'
         and missing_rows = total_rows then 'critical'
        when completeness_field_status = 'open_pending_source_validation' then 'high'
        when completeness_field_status = 'open_pending_financial_contract' then 'medium'
        when completeness_field_status = 'managed_amount_not_provided' then 'medium'
        when completeness_field_status = 'managed_date_not_provided'
         and missing_rows = total_rows then 'critical'
        when completeness_field_status = 'managed_event_datetime_not_provided'
         and missing_rows = total_rows then 'critical'
        when completeness_field_status = 'managed_coverage_boundary_not_provided'
         and missing_rows = total_rows then 'critical'
        when completeness_field_status in (
            'managed_date_not_provided',
            'managed_event_datetime_not_provided',
            'managed_coverage_boundary_not_provided'
        ) then 'high'
        when completeness_field_status = 'managed_optional_sparse' then 'low'
        else 'low'
    end as severity,
    resolution_hint
from {{ ref('dq_completeness_field_metrics') }}
where completeness_field_status <> 'complete'
