# V0_5 Uniqueness Remediation Plan

Report id: `DATAQ_UNIQUENESS_REMEDIATION_V0_5_2026_04_30`
Plan id: `04_5_local_data_workbench_and_model_evolution_plan`
Model snapshot: `V0_5`
Scope: dbt contractual handling for duplicate business keys. No source rows are
dropped or merged.

## Contract Boundary

Uniqueness is handled as duplicate profiling and lineage preservation:

- deterministic business keys are emitted;
- duplicate business-key groups stay visible;
- required lineage columns are checked before any future survivor rule;
- duplicate rows are not dropped from the source-preserving fact;
- survivor ranks are emitted for downstream unique business-key reads;
- contract violations are reserved for missing lineage or identity failures.

## dbt Models

| Model | Purpose |
| --- | --- |
| `dq_uniqueness_coverage_period_key_groups` | Coverage-period business-key groups with row counts and lineage counts. |
| `dq_uniqueness_coverage_period_metrics` | Provider-level duplicate coverage-period metrics. |
| `dq_uniqueness_contract_violations` | Guardrail table that must remain empty before survivor logic. |
| `dq_uniqueness_findings` | Managed uniqueness findings ready for audit JSONL output. |
| `coverage_period_survivor_candidate` | Source-preserving survivor ranking over duplicate coverage business keys. |
| `coverage_period_survivor_fact` | One-row-per-business-key survivor view for downstream reads. |

## Managed Findings

Coverage-period business-key duplicates are managed for all five providers by
survivor rule `latest_loaded_record_per_provider_member_period_status`. This
layer confirms the duplicates remain visible in the source-preserving fact and
that the downstream survivor view is unique.

## QA

dbt tests are located under:

```text
dbt/tests/data_quality/uniqueness/
```

Python full-dataset audit is located at:

```text
tests/sql/test_dataq_uniqueness_standardization.py
```

The pytest audit writes:

```text
artifacts/qa/dataq_uniqueness_standardization_audit.jsonl
```

## Validation Results

Current local validation:

```text
dbt run --select path:models/data_quality/uniqueness
PASS=4 WARN=0 ERROR=0 SKIP=0 TOTAL=4

dbt run --select path:models/derived/coverage path:models/data_quality/uniqueness
PASS=10 WARN=0 ERROR=0 SKIP=0 TOTAL=10

dbt test --select path:models/data_quality/uniqueness path:tests/data_quality/uniqueness
PASS=22 WARN=0 ERROR=0 SKIP=0 TOTAL=22

dbt test --select path:models/derived/coverage path:models/data_quality/uniqueness path:tests/data_quality/uniqueness
PASS=74 WARN=0 ERROR=0 SKIP=0 TOTAL=74

pytest tests/sql/test_dataq_uniqueness_standardization.py
5 passed

pytest tests/sql/test_dataq_uniqueness_standardization.py tests/sql/test_coverage_derived_sql_outputs.py
8 passed
```

Current audit summary:

| Status | Severity | Finding count | Duplicate rows | Duplicate groups | Excess duplicate rows |
| --- | --- | ---: | ---: | ---: | ---: |
| `managed_duplicate_key_survivor_applied` | `high` | 1 | 21155 | 10117 | 11038 |
| `managed_duplicate_key_survivor_applied` | `medium` | 4 | 13668 | 6567 | 7101 |

Contract violations: `0`.

The duplicate rows remain visible in `derived.coverage_period_fact`; the data
quality layer does not hide or merge them.

## Survivor Rule

```text
rule_id: latest_loaded_record_per_provider_member_period_status
partition by:
  provider_slug,
  patient_provider_member_id,
  coverage_start_date,
  coverage_end_date,
  coverage_status
order by:
  loaded_at desc nulls last,
  review_batch_id desc nulls last,
  source_row_id desc nulls last,
  coverage_source_row_id desc
```

Survivor result:

```text
derived.coverage_period_fact row_count: 875760
derived.coverage_period_survivor_fact row_count: 857621
distinct survivor business keys: 857621
survivor duplicate business keys: 0
```

## Derived Identity Revalidation

Because uniqueness is critical, the full derived model was revalidated after
the coverage business-key layer was added.

Validation scope:

- all `unique` tests declared under `dbt/models/derived/**/schema.yml`;
- all `not_null` tests declared under `dbt/models/derived/**/schema.yml`;
- facts, dimensions, lookup tables, source-normalized tables, component tables,
  and member summaries.

Validation result:

```text
dbt test --select path:models/derived,test_name:unique
PASS=47 WARN=0 ERROR=0 SKIP=0 TOTAL=47

dbt test --select path:models/derived,test_name:not_null
PASS=145 WARN=0 ERROR=0 SKIP=0 TOTAL=145
```

Conclusion:

- no declared identity checksum/key in `derived` is duplicated;
- no declared identity/checksum/lineage-required field is null;
- lookup and dimension natural keys declared as unique are clean;
- the remaining uniqueness drift is not a checksum collision. It is a coverage
  period business-key duplicate managed by the survivor rule above.
