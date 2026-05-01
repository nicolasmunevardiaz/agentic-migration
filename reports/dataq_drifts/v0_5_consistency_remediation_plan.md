# V0_5 Consistency Remediation Plan

Plan id: `DATAQ_CONSISTENCY_REMEDIATION_V0_5_2026_04_30`
Category: Consistency
Contract: `metadata/model_specs/data_quality/contracts/consistency_contract.yaml`
Status: iteration 2 implemented; unresolved values remain visible as managed findings.

## Scope

This iteration implements the approved consistency contract directly. It does
not drop rows, infer missing references, merge patients across providers, or
reinterpret clinical meaning. It preserves raw references/codes, emits
provider-scoped bridge keys only when resolvable, and uses managed statuses plus
boolean flags for downstream control.

## Implemented dbt Models

| Model | Purpose |
| --- | --- |
| `data_quality.dq_consistency_reference_bridge` | Provider-scoped reference bridge preserving raw references, normalized keys, resolution ids, and boolean flags. |
| `data_quality.dq_consistency_reference_metrics` | Provider/entity/field reference metrics over standardized references. |
| `data_quality.dq_condition_code_domain_mapping` | Condition source-code/code-hint domain handling without replacing source clinical codes. |
| `data_quality.dq_medication_code_consistency_bridge` | Medication code variant bridge aligned with canonical medication rules while preserving variants. |
| `data_quality.dq_patient_demographic_survivor` | Provider-scoped demographic survivor surface without cross-provider patient merges. |
| `data_quality.dq_consistency_code_metrics` | Provider/entity/field code and medication semantic variant metrics. |
| `data_quality.dq_consistency_demographic_metrics` | Provider-level demographic conflict metrics. |
| `data_quality.dq_consistency_contract_violations` | Must stay empty; catches invalid neutral standardization behavior. |
| `data_quality.dq_consistency_findings` | Managed consistency findings by provider/entity/field. |

These Consistency models are materialized as local audit tables, not views, so
pytest and dbt tests do not repeatedly rescan the full derived layer.

## Contract Rules Implemented

- no provider-scoped reference key is emitted when raw reference is missing,
  blank, quoted blank, or `UNK_*`;
- every present raw reference must have a final segment;
- unresolved references are preserved as managed findings with
  `is_missing_reference`, `is_unknown_reference`, `is_unresolved_reference`, and
  `is_resolved_reference` flags;
- code tokens preserve raw code and expose neutral normalized token;
- demographic conflicts use a provider-scoped deterministic survivor and keep
  conflict/variant flags;
- condition source-code/code-hint domain mismatches are managed without
  replacing source codes;
- medication code/description variants are managed without dropping variants.

## QA

dbt:

```text
dbt run --select data_quality
dbt test --select path:models/data_quality/consistency path:tests/data_quality/consistency
```

pytest:

```text
tests/sql/test_dataq_consistency_standardization.py
```

Expected pytest behavior:

- pass structural contract checks;
- write `artifacts/qa/dataq_consistency_standardization_audit.jsonl`;
- assert that managed consistency findings exist and no open findings remain;
- assert there are zero consistency contract violations.

## Validation Results

Current local validation:

```text
dbt run --select path:models/data_quality/consistency
PASS=9 WARN=0 ERROR=0 SKIP=0 TOTAL=9

dbt test --select path:models/data_quality/consistency path:tests/data_quality/consistency
PASS=49 WARN=0 ERROR=0 SKIP=0 TOTAL=49

pytest tests/sql/test_dataq_consistency_standardization.py
7 passed
```

Audit output:

```text
artifacts/qa/dataq_consistency_standardization_audit.jsonl
rows: 44
status: {'managed': 44}
severity: {'medium': 44}
affected_sum: 3905338
```

Runtime note: the full consistency build took 7m16s because the reference
bridge materialized 11,780,760 provider-scoped reference rows. After
materializing the bridge and metrics tables, dbt tests completed in 4m03s and
pytest completed in 12.66s.

## Managed Findings

The contract implementation does not hide consistency issues. Findings are now
managed for:

- unresolved/missing/unknown member, encounter, condition, and medication
  references;
- condition source-code/code-hint domain mismatches;
- medication code and description variants;
- patient demographic conflicts with provider-scoped survivor selection.

Raw values remain preserved; managed status means downstream reads have explicit
flags and should not treat the drift as an unclassified discrepancy.
