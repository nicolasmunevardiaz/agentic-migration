# V0_5 Data Quality Contract And Standardization Audit

Report id: `DATAQ_CONTRACT_STANDARDIZATION_V0_5_2026_04_30`
Scope: contracts, dbt neutral standardization models, and category-specific
remediation boundaries. No drift is remediated by this artifact.

## What Changed

Contracts were added under:

```text
metadata/model_specs/data_quality/contracts/
```

dbt neutral standardization models were added under:

```text
dbt/models/data_quality/standardization/
```

The dbt project now routes `models/data_quality` into the `data_quality` schema.

## Contracts Created

| Contract | Main decision boundary |
| --- | --- |
| `accuracy_contract.yaml` | SQL may profile accuracy issues and apply approved preservation/canonicalization rules; semantic correction still requires HITL. |
| `completeness_contract.yaml` | Required vs optional fields must be provider/entity/field-specific. |
| `consistency_contract.yaml` | References and semantic variants are normalized neutrally before survivor rules. |
| `temporal_contract.yaml` | UTC derivation requires approved provider IANA timezone. |
| `validity_contract.yaml` | Format/domain failures are flagged or quarantined only after accepted rules. |
| `uniqueness_contract.yaml` | Duplicate rows require lineage-preserving survivor/merge rules. |

## Standard dbt Models Created

| Model | Purpose |
| --- | --- |
| `dq_provider_timezone_contract` | Provider timezone placeholder; all providers remain `timezone_pending` until approved. |
| `dq_standardized_temporal_fields` | Neutral surface for raw temporal value, local NTZ placeholder, provider timezone, UTC placeholder, parse status, and timezone status. |
| `dq_standardized_reference_fields` | Neutral surface for raw reference, final segment, provider-scoped reference key, and resolution status. |
| `dq_standardized_code_fields` | Neutral surface for raw code, normalized code token, code-system hint, description, and domain status. |
| `dq_standardized_amount_fields` | Neutral surface for raw amount, numeric amount, amount source field, and parse/status flags. |
| `dq_standardization_issue_register` | Unified open issue register produced from neutral standardization surfaces. |
| `dq_timeliness_provider_field_metrics` | Provider/entity/field temporal metrics over the neutral temporal surface. |
| `dq_timeliness_contract_violations` | Guardrail view that must remain empty; flags UTC values without approved timezone. |
| `dq_timeliness_findings` | Open timeliness findings for missing chronology and pending timezone approval. |
| `dq_consistency_reference_bridge` | Provider-scoped reference bridge preserving raw references and boolean resolution flags. |
| `dq_consistency_reference_metrics` | Provider/entity/field reference metrics over standardized references. |
| `dq_condition_code_domain_mapping` | Condition source-code/code-hint domain mapping without source-code replacement. |
| `dq_medication_code_consistency_bridge` | Medication code variant bridge preserving raw variants and canonical status. |
| `dq_patient_demographic_survivor` | Provider-scoped demographic survivor surface without cross-provider patient merges. |
| `dq_consistency_code_metrics` | Provider/entity/field code and medication semantic variant metrics. |
| `dq_consistency_demographic_metrics` | Provider-level demographic conflict metrics. |
| `dq_consistency_contract_violations` | Guardrail view that must remain empty for neutral consistency standardization. |
| `dq_consistency_findings` | Managed consistency findings without dropping, inferring, or cross-provider merging. |
| `dq_completeness_provider_entity_availability` | Provider/entity availability classified by completeness contract. |
| `dq_completeness_field_metrics` | Provider/entity/field missingness classified by requiredness. |
| `dq_completeness_contract_violations` | Guardrail table that must remain empty for completeness contract handling. |
| `dq_completeness_findings` | Managed completeness findings without filling, inferring, or imputing source values. |
| `dq_validity_date_metrics` | Provider/entity/field date-bound and inverted-range validity metrics. |
| `dq_validity_code_metrics` | Code token format and source-code domain drift metrics. |
| `dq_validity_amount_metrics` | Numeric parse and nonpositive amount guardrail metrics. |
| `dq_validity_domain_metrics` | Gender and observation unit domain guardrails. |
| `dq_validity_contract_violations` | Guardrail table that must remain empty for neutral validity handling. |
| `dq_validity_findings` | Open validity findings without source mutation or semantic correction. |
| `dq_uniqueness_coverage_period_key_groups` | Coverage-period business-key groups with row counts and lineage counts. |
| `dq_uniqueness_coverage_period_metrics` | Provider-level duplicate coverage-period metrics. |
| `dq_uniqueness_contract_violations` | Guardrail table that must remain empty before survivor logic. |
| `dq_uniqueness_findings` | Open uniqueness findings without dropping or merging rows. |
| `coverage_period_survivor_candidate` | Source-preserving coverage survivor ranking over duplicate business keys. |
| `coverage_period_survivor_fact` | One-row-per-provider/member/date/status survivor view for downstream reads. |
| `dq_accuracy_clinical_semantic_metrics` | Clinical semantic accuracy metrics for conditions and medications. |
| `dq_accuracy_medication_canonical_dimension` | Approved canonical medication columns for normalized-code equivalence with raw variants preserved. |
| `dq_accuracy_financial_metrics` | Financial amount/date accuracy metrics with source distribution evidence and preservation status. |
| `dq_accuracy_observation_reconciliation_metrics` | Deterministic observation payload-vs-derived reconciliation metrics. |
| `dq_accuracy_contract_violations` | Guardrail table that must remain empty when dbt follows approved contract rules. |
| `dq_accuracy_findings` | Managed accuracy findings by provider/entity/field plus any future HITL-required findings. |

## Category-Specific Changes

### Accuracy

Change: contracts now block semantic correction unless an approved contract rule
or HITL approves clinical or financial meaning.

dbt behavior: source values are preserved. Approved accuracy rules emit
canonical medication columns, preserve financial amount/date/source-field
semantics, and convert source-code/hint mismatches into managed findings.

### Completeness

Change: completeness is governed by requiredness and provider/entity
availability. Pacific Shield clinical/cost absence is treated as availability
until the provider contract changes.

dbt behavior: neutral models expose missing status; no imputation is introduced.

### Consistency

Change: references and semantic variants now have standard raw/final/key/status
surfaces.

dbt behavior: `dq_standardized_reference_fields` creates provider-scoped
reference keys and keeps unresolved references visible.

### Timeliness

Change: timestamps now have a neutral standard contract before LTZ/UTC
normalization.

dbt behavior: `dq_standardized_temporal_fields` emits raw temporal values and
explicitly sets UTC/local neutral fields to null until provider timezones are
approved.

### Uniqueness

Change: duplicate coverage keys require lineage-preserving survivor rules.

dbt behavior: no duplicate rows are dropped in the standardization layer.

### Validity

Change: code/date/amount format rules are explicit and separate from semantic
correction.

dbt behavior: `dq_standardized_code_fields` normalizes code tokens while
preserving raw codes and review status.

## Validity Iteration 1

Validity is now handled directly from the approved contract without mutating
source data.

Implemented in this iteration:

- source code cleanup trims outer whitespace and wrapping quotes before
  standard token emission;
- provider condition codes stay separate from clinical code hints;
- clinical code hints are classified by approved patterns for SNOMED CT,
  ICD-9-CM, and ICD-10-CM;
- implausible patient birth dates and coverage boundary dates preserve raw
  values but expose validated `null` values with usability flags;
- no provider code is replaced by a clinical code, and no invalid date is
  imputed.

Managed by contract:

- `managed_split_provider_and_clinical_codes`: 3 findings, 611309 rows;
- `managed_implausible_date_quarantined`: 2 findings, 1662 rows.

Validation result:

```text
dbt run --select path:models/data_quality/standardization path:models/data_quality/validity
PASS=14 WARN=0 ERROR=0 SKIP=0 TOTAL=14

dbt test --select path:models/data_quality/validity path:tests/data_quality/validity
PASS=44 WARN=0 ERROR=0 SKIP=0 TOTAL=44

pytest tests/sql/test_dataq_validity_standardization.py
6 passed
```

Current validity open findings: `0`.

## QA Added

Macro behavior test:

```text
dbt/tests/data_quality/standardization/assert_dataq_standardization_macros.sql
```

Contract tests:

```text
tests/specs/test_dataq_contracts.py
```

Existing report-contract tests remain in:

```text
tests/specs/test_dataq_drift_reports.py
```

Existing exhaustive category audit remains in:

```text
tests/sql/test_dataq_category_audit.py
```

## Expected Behavior

The new data-quality standardization models should compile and run, but they
are expected to expose open issues. They are not expected to make
`dataq_*_audit.jsonl` pass yet.

The next remediation iteration should choose one category, convert approved
contract rules into dbt transformations/tests, and update the JSONL audit only
after the category-specific evidence changes.

## Validation Results

Baseline local validation when the neutral data-quality scaffold was created:

```text
pytest tests/specs/test_dataq_contracts.py tests/specs/test_dataq_drift_reports.py
10 passed

dbt parse
pass

dbt compile --select data_quality
pass

dbt run --select data_quality
PASS=6 WARN=0 ERROR=0 SKIP=0 TOTAL=6

dbt test --select data_quality
PASS=28 WARN=0 ERROR=0 SKIP=0 TOTAL=28
```

Runtime note: `dbt test --select data_quality` took 26 minutes and 28 seconds
because the standardization models are PostgreSQL views over the full local
dataset. This is acceptable for local certification, but future CI should
materialize category audit metrics.

## Timeliness Iteration 1

Timeliness is the first category selected for remediation because it provides a
neutral time contract for later Validity, Completeness, Consistency, and
Accuracy work.

Implemented in this iteration:

- Provider timezone registry is explicit and pending for all providers.
- UTC derivation is blocked until provider timezone approval.
- Temporal metrics are aggregated by provider/entity/field.
- Contract violations are separated from open findings.
- A dedicated pytest writes `artifacts/qa/dataq_timeliness_standardization_audit.jsonl`.

Still open by contract:

- no provider has an approved IANA timezone;
- missing business chronology remains unresolved for affected provider/entity/field slices;
- UTC values are intentionally null until timezone approval exists.

## Consistency Iteration 1

Consistency is implemented directly from the approved contract with no HITL
dependency because this iteration preserves raw values, does not infer missing
references, and does not reinterpret clinical meaning.

Implemented in this iteration:

- provider-scoped reference keys are emitted only when raw references are
  present and not blank/quoted blank/`UNK_*`;
- unresolved references stay visible as managed findings with boolean flags;
- code tokens are normalized while raw codes are preserved;
- demographic conflicts use a provider-scoped deterministic survivor without
  cross-provider patient merging;
- condition code/hint domain mismatches are managed without replacing source
  codes;
- medication code/description variants are managed without dropping variants;
- `artifacts/qa/dataq_consistency_standardization_audit.jsonl` is generated by pytest.

Managed by contract:

- missing, unknown, and unresolved references are preserved with
  `is_missing_reference`, `is_unknown_reference`, `is_unresolved_reference`, and
  `is_resolved_reference`;
- patient demographic conflicts are provider scoped and survivor-selected by
  frequency/latest-loaded/tie-breaker rules;
- source-code/hint mismatches and medication variants are managed but not
  semantically recoded.

Validation result:

```text
dbt run --select path:models/data_quality/consistency
PASS=9 WARN=0 ERROR=0 SKIP=0 TOTAL=9

dbt test --select path:models/data_quality/consistency path:tests/data_quality/consistency
PASS=49 WARN=0 ERROR=0 SKIP=0 TOTAL=49

pytest tests/sql/test_dataq_consistency_standardization.py
7 passed
```

## Completeness Iteration 1

Completeness is implemented directly from the approved contract. Missing data
is not filled or inferred; it is classified as managed with explicit null
semantics and downstream usability flags.

Implemented in this iteration:

- Pacific Shield clinical/cost absence is managed as provider-not-applicable;
- optional observation component sparsity is managed as optional;
- missing chronology preserves null and emits temporal unusable flags;
- missing cost amount preserves null and emits `usable_for_sum = false`;
- missing coverage boundaries preserve null and emit temporal/duration unusable
  flags;
- `artifacts/qa/dataq_completeness_standardization_audit.jsonl` is generated by pytest.

Validation result:

```text
dbt run --select path:models/data_quality/completeness
PASS=4 WARN=0 ERROR=0 SKIP=0 TOTAL=4

dbt test --select path:models/data_quality/completeness path:tests/data_quality/completeness
PASS=26 WARN=0 ERROR=0 SKIP=0 TOTAL=26

pytest tests/sql/test_dataq_completeness_standardization.py
5 passed
```

## Validity Iteration 1

Validity is implemented directly from the contract. Values are not corrected;
dbt classifies format, bounds, token, amount, and domain issues so downstream
queries can avoid unclassified discrepancies.

Implemented in this iteration:

- date-bound and inverted-range metrics for patients, coverage, encounters,
  medications, and cost records;
- code token/domain metrics for conditions and medications;
- amount parse/nonpositive guardrails for cost records;
- patient gender and observation unit domain guardrails;
- `artifacts/qa/dataq_validity_standardization_audit.jsonl` is generated by pytest.

Still open by contract:

- condition source-code/system hint mismatches remain open until code-domain
  mapping rules are approved;
- Northcare date-bound failures remain open pending quarantine or source
  correction rules.

Validation result:

```text
dbt run --select path:models/data_quality/validity
PASS=6 WARN=0 ERROR=0 SKIP=0 TOTAL=6

dbt test --select path:models/data_quality/validity path:tests/data_quality/validity
PASS=34 WARN=0 ERROR=0 SKIP=0 TOTAL=34

pytest tests/sql/test_dataq_validity_standardization.py
4 passed
```

## Uniqueness Iteration 1

Uniqueness is implemented directly from the contract. Duplicate business keys
are profiled and kept visible; the coverage survivor rule exposes a unique
downstream view without dropping source-preserving rows.

Implemented in this iteration:

- coverage-period business-key groups using provider, member, start date, end
  date, and coverage status;
- coverage-period survivor candidates ranked by latest loaded record, review
  batch, source row id, and coverage source row id;
- coverage-period survivor fact with one row per provider/member/date/status
  business key;
- provider-level duplicate metrics for all five providers;
- lineage guardrails for source row id, source lineage ref, and coverage source
  row id;
- `artifacts/qa/dataq_uniqueness_standardization_audit.jsonl` is generated by pytest.

Managed by contract:

- coverage-period duplicate business keys are managed by
  `latest_loaded_record_per_provider_member_period_status`.

Validation result:

```text
dbt run --select path:models/data_quality/uniqueness
PASS=4 WARN=0 ERROR=0 SKIP=0 TOTAL=4

dbt test --select path:models/data_quality/uniqueness path:tests/data_quality/uniqueness
PASS=22 WARN=0 ERROR=0 SKIP=0 TOTAL=22

pytest tests/sql/test_dataq_uniqueness_standardization.py
5 passed

dbt test --select path:models/derived/coverage path:models/data_quality/uniqueness path:tests/data_quality/uniqueness
PASS=74 WARN=0 ERROR=0 SKIP=0 TOTAL=74

pytest tests/sql/test_dataq_uniqueness_standardization.py tests/sql/test_coverage_derived_sql_outputs.py
8 passed
```

## Accuracy Iteration 1

Accuracy is implemented directly from the approved contract rules. dbt does not
overwrite clinical or financial source values and does not impute amount or date
values.

Implemented in this iteration:

- condition code/source hint semantic review metrics;
- medication canonical dimension for same-normalized-code equivalence with raw
  code/description variants preserved;
- medication same-description/different-code conflict preservation;
- cost amount/date financial semantic review metrics with source distribution
  evidence;
- observation payload reconciliation metrics for height, weight, systolic blood
  pressure, and BMI recomputation;
- `artifacts/qa/dataq_accuracy_standardization_audit.jsonl` is generated by pytest.

Managed by contract:

- condition source code is primary and condition code hint is metadata;
- medication normalized-code variants canonicalize into new canonical columns;
- different medication codes with the same description remain separate and are
  flagged as preserved conflicts;
- missing cost amount/date remains null and source-field semantics are
  provider-preserved;
- BMI payload/recomputed delta <= 0.1 is accepted.

Still HITL-required by contract:

- any future attempt to reinterpret clinical code meaning beyond the approved
  source-code/hint rule;
- any future attempt to infer payment conclusion, impute financial values, or
  equate source amount fields across providers.

Validation result:

```text
dbt run --select path:models/data_quality/accuracy
PASS=6 WARN=0 ERROR=0 SKIP=0 TOTAL=6

dbt test --select path:models/data_quality/accuracy path:tests/data_quality/accuracy
PASS=36 WARN=0 ERROR=0 SKIP=0 TOTAL=36

pytest tests/sql/test_dataq_accuracy_standardization.py
4 passed
```
