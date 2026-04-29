# Local Runtime Repo Governance

plan_id: `04_local_runtime_and_contract_certification_plan`
provider: `all`
status: `ready_for_pr`
allowed_next_action: `create_pr`

## Scope

- Base branch: `main`
- Head branch: `agentops/04-local-runtime-certification/all`
- Branch deletion plan: delete the temporary head branch locally and remotely after PR approval and merge or explicit human closure.
- Skills used: `local-runtime-harness-planner`, `adapter-contract-reviewer`, `qa-evidence-reviewer`, `privacy-governance-reviewer`, `spec-test-generator`, `repo-governance-auditor`.

## Changed Files

- `docs/local_runtime_macos_requirements.md`
- `metadata/runtime_specs/local/local_runtime_profile.yaml`
- `metadata/runtime_specs/local/runtime_interface_contract.yaml`
- `reports/privacy/local_runtime_dependency_review.md`
- `reports/qa/local_runtime_certification.md`
- `reports/qa/local_runtime_repo_governance.md`
- `tests/specs/test_local_runtime_specs.py`
- `logs/local_runtime/local_runtime_certification.md`
- `pyproject.toml`
- `uv.lock`

## Evidence

| Evidence | Status |
| --- | --- |
| Local dependency review | `reports/privacy/local_runtime_dependency_review.md` records approved import-only packages and blocked service/runtime actions. |
| Runtime profile and interface contract | `metadata/runtime_specs/local/` defines local-only scope, profile separation, dependency evidence, and all eight runtime-neutral interfaces. |
| Local runtime QA | `reports/qa/local_runtime_certification.md` records dependency checks, adapter audit, test results, and certification boundary. |
| `data_500k` adapter audit | `artifacts/qa/data_500k_adapter_load_audit.jsonl` and `.md` show 250 Plan 04 records, all passed, no failures, no skips. |

## Validation

| Command | Result |
| --- | --- |
| `git diff --check` | passed |
| `/opt/homebrew/opt/openjdk@17/bin/java -version` | passed, OpenJDK `17.0.19` |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -c "import pyspark; import delta; import openlineage.client; print(pyspark.__version__)"` | passed, PySpark `4.1.1` |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.data_500k_adapter_audit --plan-id 04_local_runtime_and_contract_certification_plan` | passed, 250 records |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs` | passed, 46 tests |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/adapters` | passed, 143 tests |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/test_repository_governance.py` | passed, 14 tests |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync ruff check` | passed |

## Governance Findings

- Dependency risk status: approved for local import/spec-shape validation only; no runtime service or cloud execution approval is granted.
- HITL status: user approved the already-added Python packages `pyspark`, `delta-spark`, and `openlineage-python`; Marquez, Docker service start, OpenLineage emission, Spark pipeline execution, Delta writes, Databricks packages, Terraform, bundles, cloud resources, and production data remain blocked.
- Databricks impact: none executed; Plan 04 remains `not_databricks_certified`.
- Secrets and local data: no `data_500k/` files are tracked; runtime evidence remains in ignored `artifacts/qa/`.
- Rollback notes: revert this PR to remove Plan 04 dependency additions, runtime spec/report updates, and validation tests; no cloud or service cleanup is required.
