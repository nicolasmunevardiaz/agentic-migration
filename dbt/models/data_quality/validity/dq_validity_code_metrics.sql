{{ config(materialized='table') }}

with standardized_checks as (
    select
        provider_slug,
        entity,
        field_column,
        count(*) as total_rows,
        count(*) filter (where raw_code is null) as missing_code_rows,
        count(*) filter (
            where raw_code is not null
              and normalized_code_token is null
        ) as failed_tokenization_rows,
        count(*) filter (
            where normalized_code_token is not null
              and normalized_code_token !~ '^[A-Z0-9]+(_[A-Z0-9]+)*$'
        ) as invalid_token_format_rows,
        count(*) filter (where has_code_domain_drift) as code_domain_drift_rows,
        count(distinct normalized_code_token) filter (
            where normalized_code_token is not null
        ) as distinct_normalized_token_count,
        min(resolution_hint) as resolution_hint
    from {{ ref('dq_standardized_code_fields') }}
    group by provider_slug, entity, field_column
),

condition_domain_checks as (
    select
        provider_slug,
        'conditions' as entity,
        'condition_source_code' as field_column,
        count(*) filter (
            where condition_code_domain_status = 'managed_split_provider_and_clinical_codes'
        ) as managed_code_domain_drift_rows,
        count(*) filter (
            where condition_code_domain_status = 'open_unresolved_clinical_code_pattern'
        ) as unresolved_clinical_code_pattern_rows
    from {{ ref('dq_validity_condition_code_domain_bridge') }}
    group by provider_slug
),

code_checks as (
    select
        standardized_checks.*,
        coalesce(condition_domain_checks.managed_code_domain_drift_rows, 0)
            as managed_code_domain_drift_rows,
        coalesce(condition_domain_checks.unresolved_clinical_code_pattern_rows, 0)
            as unresolved_clinical_code_pattern_rows
    from standardized_checks
    left join condition_domain_checks
        on standardized_checks.provider_slug = condition_domain_checks.provider_slug
       and standardized_checks.entity = condition_domain_checks.entity
       and standardized_checks.field_column = condition_domain_checks.field_column
)

select
    {{ provider_scoped_hash("provider_slug", "entity || '|' || field_column") }}
        as validity_code_metric_id,
    provider_slug,
    entity,
    field_column,
    total_rows,
    missing_code_rows,
    failed_tokenization_rows,
    invalid_token_format_rows,
    code_domain_drift_rows,
    managed_code_domain_drift_rows,
    unresolved_clinical_code_pattern_rows,
    distinct_normalized_token_count,
    failed_tokenization_rows + invalid_token_format_rows + code_domain_drift_rows
        + missing_code_rows as affected_rows,
    resolution_hint,
    case
        when failed_tokenization_rows > 0 or invalid_token_format_rows > 0
            then 'contract_violation'
        when unresolved_clinical_code_pattern_rows > 0
            then 'open_unresolved_clinical_code_pattern'
        when code_domain_drift_rows > 0
            then 'managed_split_provider_and_clinical_codes'
        when missing_code_rows > 0 then 'open_missing_code'
        else 'complete'
    end as validity_code_status
from code_checks
