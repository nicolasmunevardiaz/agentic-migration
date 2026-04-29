# Aegis Care Network Adapter Repository Governance Review

plan_id: `03_adapter_implementation_and_ci_plan`
provider: `data_provider_1_aegis_care_network`
status: `allowed`
allowed_next_action: `create_pr`

## Branch And Scope

- Branch: `agentops/03-adapter-implementation/aegis`.
- Target base branch: `main`.
- Temporary branch deletion plan: delete local and remote branch after PR approval and merge or explicit closure.
- Scope: Aegis Plan 03 adapter implementation, runtime-neutral shared utilities, handler, synthetic fixtures, tests, and evidence only.
- Existing unrelated local change: `docs/agentic_rollout.md` remains uncommitted and must not be included in the adapter PR.

## Evidence

- Adapter code: `src/adapters/aegis_care_network.py`
- Shared runtime utilities: `src/common/adapter_runtime.py`
- Handler: `src/handlers/aegis_adapter.py`
- Fixtures: `tests/fixtures/aegis/`
- Tests: `tests/adapters/test_aegis_adapter_runtime.py`, `tests/adapters/test_aegis_care_network_parser.py`, `tests/specs/test_aegis_adapter_contract.py`
- QA evidence: `reports/qa/data_provider_1_aegis_care_network_adapter_implementation.md`
- Privacy evidence: `reports/privacy/data_provider_1_aegis_care_network_adapter_implementation.md`
- Trace log: `logs/adapter_implementation/data_provider_1_aegis_care_network.md`

## Local QA

| Command | Result |
| --- | --- |
| `uv run --no-sync pytest tests/specs` | passed, 34 tests |
| `uv run --no-sync pytest tests/adapters` | passed, 78 tests |
| `uv run --no-sync pytest` | passed, 126 tests |
| `uv run --no-sync ruff check` | passed |

## Governance Findings

- Dependency safety: pass; no package or lockfile changes.
- Source data safety: pass; no `data_500k/` files are tracked or copied.
- Secrets safety: pass; no secret, token, or local credential changes.
- Databricks/Terraform guardrails: pass; no Databricks, Terraform, cloud, or production-impacting action.
- HITL: pass for Plan 03 PR creation because Plan 02 applied canonical decisions govern only the recorded Bronze/Silver mappings.

## Rollback

Revert the scoped branch changes; no external runtime, dependency, Databricks, Terraform, or cloud state was modified.
