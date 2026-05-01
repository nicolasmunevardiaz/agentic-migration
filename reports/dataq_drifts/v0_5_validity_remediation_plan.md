# V0_5 Validity Remediation Plan

Report id: `DATAQ_VALIDITY_REMEDIATION_V0_5_2026_04_30`
Plan id: `04_5_local_data_workbench_and_model_evolution_plan`
Model snapshot: `V0_5`
Scope: dbt contractual handling for validity drift. No source data is mutated.

## Contract Boundary

Validity is handled as neutral classification:

- raw values are preserved;
- standard tokens/domains are emitted when deterministic;
- dates outside approved neutral bounds are flagged, not imputed;
- nonpositive amounts are flagged, not replaced;
- unit and demographic domains are tested as guardrails;
- contract violations are reserved for failures in the dbt standardization layer itself.

## dbt Models

| Model | Purpose |
| --- | --- |
| `dq_validity_date_metrics` | Provider/entity/field invalid date-bound and inverted-range metrics. |
| `dq_validity_date_quarantine` | Raw date preservation, validated date output, quarantine flags, and temporal usability status. |
| `dq_validity_code_metrics` | Code token format, missing-code visibility, and managed source-code domain drift metrics. |
| `dq_validity_condition_code_domain_bridge` | Split provider condition code from clinical code hint/system without semantic replacement. |
| `dq_validity_amount_metrics` | Numeric parse and nonpositive amount guardrail metrics. |
| `dq_validity_domain_metrics` | Gender and observation unit domain guardrails. |
| `dq_validity_contract_violations` | Guardrail table that must remain empty for neutral validity handling. |
| `dq_validity_findings` | Managed/open validity findings ready for audit JSONL output. |

## Managed Findings

The validity layer now manages the previously open findings by contract:

- condition source-code/system hint mismatches are split into provider code and
  clinical hint fields;
- date values outside approved neutral bounds or inverted date ranges are
  quarantined to validated `null` values;
- nonpositive populated amounts if present in future loads;
- missing source codes where they overlap with completeness but still affect code-domain usability.

The layer does not repair or reinterpret source values. It preserves raw values,
emits validated/normalized fields, and exposes status/flag columns.

## QA

dbt tests are located under:

```text
dbt/tests/data_quality/validity/
```

Python full-dataset audit is located at:

```text
tests/sql/test_dataq_validity_standardization.py
```

The pytest audit writes:

```text
artifacts/qa/dataq_validity_standardization_audit.jsonl
```

## Validation Results

Current local validation:

```text
dbt run --select path:models/data_quality/standardization path:models/data_quality/validity
PASS=14 WARN=0 ERROR=0 SKIP=0 TOTAL=14

dbt test --select path:models/data_quality/validity path:tests/data_quality/validity
PASS=44 WARN=0 ERROR=0 SKIP=0 TOTAL=44

pytest tests/sql/test_dataq_validity_standardization.py
6 passed
```

Current audit summary:

| Status | Severity | Finding count | Affected rows |
| --- | --- | ---: | ---: |
| `managed_split_provider_and_clinical_codes` | `medium` | 3 | 611309 |
| `managed_implausible_date_quarantined` | `high` | 2 | 1662 |

Contract violations: `0`.

Domain guardrails for patient gender and observation units are complete.

No `open_*` validity findings remain.
