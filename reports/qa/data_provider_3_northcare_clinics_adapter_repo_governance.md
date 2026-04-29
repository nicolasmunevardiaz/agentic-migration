# NorthCare Clinics Adapter Repository Governance Review

plan_id: `03_adapter_implementation_and_ci_plan`
provider: `data_provider_3_northcare_clinics`
status: `allowed`
allowed_next_action: `create_pr`

## Branch And Scope

- Branch: `agentops/03-adapter-implementation/northcare-clinics`.
- Target base branch: `main`.
- Temporary branch deletion plan: delete local and remote branch after PR approval and merge or explicit closure.
- Scope: NorthCare Plan 03 adapter implementation, reusable local data_500k audit registration, runtime-neutral handler, adapter contract tests, synthetic fixture/runtime tests, and evidence only.

## Evidence

- Adapter code: `src/handlers/northcare_adapter.py`
- Parser reuse: `src/adapters/northcare_clinics.py`
- Fixtures: `tests/fixtures/northcare/`
- Tests: `tests/adapters/test_northcare_adapter_runtime.py`, `tests/adapters/test_northcare_clinics_parser.py`, `tests/specs/test_northcare_adapter_contract.py`
- Local data audit: `src/handlers/data_500k_adapter_audit.py`, `tests/adapters/test_data_500k_adapter_audit.py`, `reports/qa/data_500k_adapter_load_audit.md`
- QA evidence: `reports/qa/data_provider_3_northcare_clinics_adapter_implementation.md`
- Privacy evidence: `reports/privacy/data_provider_3_northcare_clinics_adapter_implementation.md`
- Trace log: `logs/adapter_implementation/data_provider_3_northcare_clinics.md`

## Local QA

| Command | Result |
| --- | --- |
| `uv run --no-sync pytest tests/specs` | passed, 39 tests |
| `uv run --no-sync pytest tests/adapters` | passed, 112 tests |
| `uv run --no-sync python -m src.handlers.data_500k_adapter_audit` | passed, 150 data_500k file audit records, 0 failures, 0 skips |
| `uv run --no-sync pytest` | passed, 165 tests |
| `uv run --no-sync ruff check` | passed |

## Governance Findings

- Dependency safety: pass; no package or lockfile changes.
- Source data safety: pass; no `data_500k/` files are tracked or copied.
- Secrets safety: pass; no secret, token, or local credential changes.
- Databricks/Terraform guardrails: pass; no Databricks, Terraform, cloud, or production-impacting action.
- HITL: pass for PR creation because Plan 02 decisions DRIFT-001 through DRIFT-015 govern the canonical mappings used by this adapter.

## Rollback

Revert the scoped branch changes; no external runtime, dependency, Databricks, Terraform, or cloud state was modified.
