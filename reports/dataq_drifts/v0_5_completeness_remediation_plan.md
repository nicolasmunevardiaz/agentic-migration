# V0_5 Completeness Remediation Plan

Plan id: `DATAQ_COMPLETENESS_REMEDIATION_V0_5_2026_04_30`
Category: Completeness
Contract: `metadata/model_specs/data_quality/contracts/completeness_contract.yaml`
Status: iteration 2 implemented; no source values are filled, inferred, or imputed.

## Scope

This iteration implements the completeness contract directly in dbt. It
classifies missingness and availability without changing source data.

## Implemented dbt Models

| Model | Purpose |
| --- | --- |
| `data_quality.dq_completeness_provider_entity_availability` | Provider/entity availability grid classified by contract. |
| `data_quality.dq_completeness_field_metrics` | Provider/entity/field missingness classified by requiredness. |
| `data_quality.dq_completeness_contract_violations` | Must stay empty; catches required entity gaps or unknown requiredness. |
| `data_quality.dq_completeness_findings` | Managed completeness findings by provider/entity/field. |

These models are materialized as local audit tables so pytest and dbt tests do
not repeatedly rescan the full derived layer.

## Contract Rules Implemented

- Pacific Shield clinical and cost entity absence is managed as
  `managed_provider_not_applicable`.
- Optional observation components are managed as `managed_optional_sparse`.
- Missing chronology is managed as null-preserved and unusable for temporal
  analysis until source-provided values exist.
- Missing cost amount is managed as null-preserved and unusable for sum
  aggregation; empty amount is not converted to zero.
- Missing coverage start/end boundaries are managed as null-preserved and
  unusable for point-in-time/duration analysis when the required boundary is
  absent.
- No values are imputed or inferred.

## QA

dbt:

```text
dbt run --select path:models/data_quality/completeness
dbt test --select path:models/data_quality/completeness path:tests/data_quality/completeness
```

pytest:

```text
tests/sql/test_dataq_completeness_standardization.py
```

Expected pytest behavior:

- pass structural contract checks;
- write `artifacts/qa/dataq_completeness_standardization_audit.jsonl`;
- assert that no contract violations exist;
- assert that managed findings remain visible and no open/failed completeness
  findings remain after approved null semantics.

## Validation Results

Current local validation:

```text
dbt run --select path:models/data_quality/completeness
PASS=4 WARN=0 ERROR=0 SKIP=0 TOTAL=4

dbt test --select path:models/data_quality/completeness path:tests/data_quality/completeness
PASS=26 WARN=0 ERROR=0 SKIP=0 TOTAL=26

pytest tests/sql/test_dataq_completeness_standardization.py
5 passed
```

Audit output:

```text
artifacts/qa/dataq_completeness_standardization_audit.jsonl
rows: 49
status: {'managed': 49}
severity: {'medium': 4, 'critical': 10, 'low': 29, 'high': 6}
affected_sum: 3268402
```

Interpretation:

- `managed` means the missingness is handled by contract and should not be
  interpreted as a downstream discrepancy.
- Missing required values are still null in source-preserving outputs, but now
  have explicit `null_semantics_status`, `usable_for_sum`,
  `usable_for_temporal_analysis`, `usable_for_duration`, and
  `safe_downstream_value_policy` metadata.
- `failed` is reserved for contract violations; none were emitted.
