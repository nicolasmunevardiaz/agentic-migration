# Aegis Care Network Adapter Implementation QA Evidence

plan_id: `03_adapter_implementation_and_ci_plan`
provider: `data_provider_1_aegis_care_network`
status: `local_validation_passed`

## Scope

- Runtime-neutral shared adapter utilities under `src/common/`.
- Aegis handler under `src/handlers/`.
- Aegis parser compatibility under `src/adapters/aegis_care_network.py`.
- Synthetic Aegis fixtures under `tests/fixtures/aegis/`.
- Adapter and spec tests under `tests/adapters/` and `tests/specs/`.

## Canonical Metadata Gate

- `metadata/model_specs/**` is treated as the primary canonical metadata for Bronze/Silver behavior.
- Aegis provider specs are used only for source dialect, parser profile, row keys, and source fields.
- Plan 01 HITL/provider readiness blockers are reconciled by Plan 02 applied runbook decisions DRIFT-001 through DRIFT-005 and DRIFT-012 through DRIFT-014 for the exact canonical mappings in `metadata/model_specs/**`.
- No Silver columns are derived directly from provider spec `canonical_name` values when model specs define a different canonical column name.

## Test Families

- Unit data tests: parser compatibility, malformed JSON rejection, missing row-key rejection, and wrong resource type rejection.
- Integration tests: handler emits Bronze and provider-filtered Silver rows from fixture files.
- Local sample integration tests: handler runs against `data_500k/data_provider_1_aegis_care_network/year=2025/<entity>/<entity>_001.json` when the ignored local dataset is present.
- Data quality tests: invalid required decimal quarantines `cost_records.cost_amount`.
- Schema tests: Aegis canonical mappings reference existing provider fields.
- Regression tests: direct identifier provider fields are not promoted as Silver column names.
- QA evidence tests: malformed optional observation payload emits warnings without raw sensitive values.

## Focused Local Results

| Command | Result |
| --- | --- |
| `uv run --no-sync pytest tests/adapters/test_aegis_care_network_parser.py tests/adapters/test_aegis_adapter_runtime.py tests/specs/test_aegis_adapter_contract.py` | passed, 27 tests |
| `uv run --no-sync ruff check src/common/adapter_runtime.py src/handlers/aegis_adapter.py tests/adapters/test_aegis_care_network_parser.py tests/adapters/test_aegis_adapter_runtime.py tests/specs/test_aegis_adapter_contract.py` | passed |

## Full Local Results

| Command | Result |
| --- | --- |
| `uv run --no-sync pytest tests/specs` | passed, 34 tests |
| `uv run --no-sync pytest tests/adapters` | passed, 78 tests |
| `uv run --no-sync pytest` | passed, 126 tests |
| `uv run --no-sync ruff check` | passed |

## Risks And Boundaries

- Local runtime certification remains out of scope for Plan 03.
- Databricks execution, Terraform, cloud resources, and production data remain out of scope.
- No new dependency was added or installed.
