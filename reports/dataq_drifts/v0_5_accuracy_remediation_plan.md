# V0_5 Accuracy Remediation Plan

Report id: `DATAQ_ACCURACY_REMEDIATION_V0_5_2026_04_30`
Plan id: `04_5_local_data_workbench_and_model_evolution_plan`
Model snapshot: `V0_5`
Scope: dbt contractual handling for accuracy drift using approved neutral
canonicalization and preservation rules. No source clinical or financial value
is overwritten by dbt.

## Contract Boundary

Accuracy is profile-only unless an approved contract rule or HITL-approved
semantic rule exists:

- condition source codes remain primary and code hints are treated as metadata;
- medication raw code/description variants are preserved while canonical
  medication columns are emitted for normalized-code equivalence;
- same-description/different-code medication conflicts are preserved and
  surfaced as managed conflicts;
- financial amount/date fields are preserved, not imputed;
- provider/source-field financial semantics are not treated as globally
  equivalent;
- observation payload reconciliation is deterministic and does not replace
  observed vitals;
- contract violations are reserved for forbidden semantic remediation or lost
  evidence.

## dbt Models

| Model | Purpose |
| --- | --- |
| `dq_accuracy_clinical_semantic_metrics` | Clinical code/description semantic review metrics for conditions and medications. |
| `dq_accuracy_medication_canonical_dimension` | Canonical medication columns for approved normalized-code equivalence with raw variants preserved. |
| `dq_accuracy_financial_metrics` | Cost amount/date semantic review metrics with source amount distribution evidence. |
| `dq_accuracy_observation_reconciliation_metrics` | Deterministic observation payload-vs-derived reconciliation metrics. |
| `dq_accuracy_contract_violations` | Guardrail table that must remain empty when dbt follows approved contract rules. |
| `dq_accuracy_findings` | Managed accuracy findings by provider/entity/field plus any future HITL-required findings. |

## Expected Findings

Accuracy findings are now managed by explicit contract rules:

- `managed_valid_code_with_domain_hint_mismatch` for condition source-code vs
  hint mismatches, because the source code is primary and the hint is metadata;
- `managed_canonical_medication_code_with_variants` for same normalized
  medication code with raw variants preserved;
- `managed_description_match_code_conflict_preserved` for same normalized
  medication description across distinct codes, with codes kept separate;
- `managed_financial_semantics_preserved` for missing cost amount/date and
  provider/source-field financial semantics, with no imputation.

Observation reconciliation is expected to be clean because payload-derived
height, weight, systolic blood pressure, and recomputed BMI match the current
neutral thresholds.

## QA

dbt tests are located under:

```text
dbt/tests/data_quality/accuracy/
```

Python full-dataset audit is located at:

```text
tests/sql/test_dataq_accuracy_standardization.py
```

The pytest audit writes:

```text
artifacts/qa/dataq_accuracy_standardization_audit.jsonl
```

## Validation Results

Current local validation:

```text
dbt run --select path:models/data_quality/accuracy
PASS=6 WARN=0 ERROR=0 SKIP=0 TOTAL=6

dbt test --select path:models/data_quality/accuracy path:tests/data_quality/accuracy
PASS=36 WARN=0 ERROR=0 SKIP=0 TOTAL=36

pytest tests/sql/test_dataq_accuracy_standardization.py
4 passed
```

Current audit summary:

| Status | Severity | Finding count | Affected rows |
| --- | --- | ---: | ---: |
| `managed_valid_code_with_domain_hint_mismatch` | `medium` | 3 | 611309 |
| `managed_description_match_code_conflict_preserved` | `medium` | 4 | 700 |
| `managed_financial_semantics_preserved` | `medium` | 4 | 726946 |

Observation reconciliation:

```text
status: complete
provider metrics: 4
affected rows: 0
max BMI payload/recomputed delta: 0.05
```

Contract violations: `0`.

HITL-required findings after approved contract rules: `0`.

Medication canonical dimension status:

| Status | Rows |
| --- | ---: |
| `managed_canonical_medication_code_with_variants` | 140 |
| `managed_description_match_code_conflict_preserved` | 560 |
