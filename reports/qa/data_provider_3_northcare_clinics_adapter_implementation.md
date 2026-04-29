# NorthCare Clinics Adapter Implementation QA Evidence

plan_id: `03_adapter_implementation_and_ci_plan`
provider: `data_provider_3_northcare_clinics`
status: `local_validation_passed`

## Scope

- Runtime-neutral shared adapter utilities under `src/common/`.
- NorthCare handler under `src/handlers/northcare_adapter.py`.
- NorthCare parser reuse under `src/adapters/northcare_clinics.py`.
- Synthetic NorthCare fixtures under `tests/fixtures/northcare/`.
- Adapter and spec tests under `tests/adapters/` and `tests/specs/`.

## Canonical Metadata Gate

- `metadata/model_specs/**` is treated as the primary canonical metadata for Bronze/Silver behavior.
- NorthCare provider specs are used only for source dialect, parser profile, row key `EXPORT_ID`, and source fields.
- No Silver columns are derived directly from provider spec `canonical_name` values when model specs define canonical column names.
- DRIFT-007 approves NorthCare X12-style segment envelopes for canonical planning.
- DRIFT-015 makes all Bronze/Silver ingestion fields nullable and defers schema-required compliance to later QA/certification.

## Test Families

- Unit data tests: parser compatibility, malformed envelope rejection, missing HDR rejection, missing row-key rejection, unsupported parser-family rejection, and element-count mismatch handling.
- Integration tests: handler emits Bronze and provider-filtered Silver rows from fixture files.
- Local data integration tests: handler runs against all 10 files per entity under `data_500k/data_provider_3_northcare_clinics/year=2025/<entity>/` when the ignored local dataset is present.
- Local data failure evidence includes provider, entity, source file, checksum, error type, decision, and message.
- Local data audit logs: generated under `artifacts/qa/data_500k_adapter_load_audit.jsonl` and summarized by `artifacts/qa/data_500k_adapter_load_audit.md`.
- Data quality tests: invalid ingestion decimal and malformed optional observation payload warn without quarantining.
- Schema tests: NorthCare canonical mappings reference existing provider fields.
- Regression tests: direct identifier provider fields are not promoted as Silver column names.
- QA evidence tests: adapter evidence avoids raw sensitive values.

## Focused Local Results

| Command | Result |
| --- | --- |
| `uv run --no-sync pytest tests/adapters/test_northcare_clinics_parser.py tests/adapters/test_northcare_adapter_runtime.py tests/specs/test_northcare_adapter_contract.py` | passed, 31 tests |

## Full Local Results

| Command | Result |
| --- | --- |
| `uv run --no-sync pytest tests/specs` | passed, 39 tests |
| `uv run --no-sync pytest tests/adapters` | passed, 112 tests |
| `uv run --no-sync python -m src.handlers.data_500k_adapter_audit` | passed, 150 data_500k file audit records, 0 failures, 0 skips |
| `uv run --no-sync pytest` | passed, 165 tests |
| `uv run --no-sync ruff check` | passed |

## Risks And Boundaries

- Local runtime certification remains out of scope for Plan 03.
- Databricks execution, Terraform, cloud resources, and production data remain out of scope.
- No new dependency was added or installed.
