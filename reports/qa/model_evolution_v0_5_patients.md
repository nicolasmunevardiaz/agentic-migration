# Plan 04.5 Model Evolution V0_5 Patients QA

plan_id: `04_5_local_data_workbench_and_model_evolution_plan`
provider: `all`
status: `passed`
scope: `patients only`
rollback_snapshot: `V0_3`

## Summary

V0_5 creates the first table-by-table derived normalization layer for patients. The implementation uses `review.silver_members` as the source, keeps all source rows in `derived.patient_source_normalized`, collapses provider-scoped members into `derived.patient_dimension`, and adds transaction-presence rollups in `derived.patient_transaction_activity`.

No enterprise identity resolution is performed. Conflicting gender and birth-date evidence remains visible as flags instead of being silently resolved.

## Derived Outputs

| Output | Rows | Grain |
| --- | ---: | --- |
| `derived.patient_source_normalized` | 875760 | one provider patient source row |
| `derived.patient_dimension` | 479813 | one provider-scoped `member_reference` |
| `derived.patient_transaction_activity` | 479813 | one provider-scoped member activity rollup |

## QA Evidence

| Command | Result |
| --- | --- |
| `dbt compile --select path:models/derived/patients` | passed |
| `dbt run --select path:models/derived/patients` | passed, 3 views |
| `dbt test --select path:models/derived/patients path:tests/derived/patients` | passed, 21 tests |
| `dbt docs generate` | passed |
| `pytest tests/specs/test_model_specs.py tests/sql/test_patient_derived_sql_outputs.py` | passed, 12 tests |
| `pytest` | passed, 219 tests |
| `ruff check dbt tests/specs/test_model_specs.py tests/sql/test_patient_derived_sql_outputs.py` | passed |
| rollback dry-run to `V0_3` | passed |

## Provider Notes

- Aegis, BlueStone, NorthCare, and ValleyBridge have patient rows plus clinical/financial transaction activity.
- Pacific Shield has patient and coverage rows but no linked clinical/cost transaction rows in the current Silver V0_3 load; V0_5 records this as `has_transactional_data = false`, not as a clinical conclusion.
- Gender conflicts: 9704 provider-scoped members.
- Birth-date conflicts: 9957 provider-scoped members.
- Implausible birth date flags: 92 provider-scoped members.

## Decision

Patient derived normalization is safe to promote as local dbt views. Continue one table at a time; do not resolve demographic conflicts or cross-provider identity without HITL approval.
