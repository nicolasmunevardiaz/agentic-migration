{{ config(materialized='table') }}

select
    validity_date_metric_id as finding_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    affected_rows,
    validity_date_status as finding_status,
    'high' as severity,
    resolution_hint
from {{ ref('dq_validity_date_metrics') }}
where validity_date_status <> 'complete'

union all

select
    validity_code_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    affected_rows,
    validity_code_status,
    case
        when validity_code_status = 'contract_violation' then 'critical'
        when validity_code_status = 'open_code_domain_drift' then 'critical'
        else 'medium'
    end as severity,
    resolution_hint
from {{ ref('dq_validity_code_metrics') }}
where validity_code_status <> 'complete'

union all

select
    validity_amount_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    affected_rows,
    validity_amount_status,
    case
        when validity_amount_status = 'contract_violation' then 'critical'
        else 'medium'
    end as severity,
    resolution_hint
from {{ ref('dq_validity_amount_metrics') }}
where validity_amount_status <> 'complete'

union all

select
    validity_domain_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    affected_rows,
    validity_domain_status,
    case
        when validity_domain_status = 'open_unit_domain_failure' then 'high'
        else 'medium'
    end as severity,
    resolution_hint
from {{ ref('dq_validity_domain_metrics') }}
where validity_domain_status <> 'complete'
