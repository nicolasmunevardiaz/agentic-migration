{{ config(materialized='table') }}

select
    accuracy_clinical_metric_id as finding_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    affected_rows,
    accuracy_clinical_status as finding_status,
    case
        when accuracy_clinical_status like 'hitl_required_%' then 'hitl'
        else 'medium'
    end as severity,
    resolution_hint
from {{ ref('dq_accuracy_clinical_semantic_metrics') }}
where accuracy_clinical_status <> 'complete'

union all

select
    accuracy_financial_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    affected_rows,
    accuracy_financial_status,
    case
        when accuracy_financial_status like 'hitl_required_%' then 'hitl'
        else 'medium'
    end as severity,
    resolution_hint
from {{ ref('dq_accuracy_financial_metrics') }}
where accuracy_financial_status <> 'complete'

union all

select
    accuracy_observation_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    affected_rows,
    accuracy_observation_status,
    'high' as severity,
    resolution_hint
from {{ ref('dq_accuracy_observation_reconciliation_metrics') }}
where accuracy_observation_status <> 'complete'
