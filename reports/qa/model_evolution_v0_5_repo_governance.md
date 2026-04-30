# Plan 04.5 V0_5 Repo Governance

plan_id: `04_5_local_data_workbench_and_model_evolution_plan`
provider: `all`
status: `allowed`
allowed_next_action: `create_pr`

## PR Evidence

| Field | Value |
| --- | --- |
| Base branch | `main` |
| Head branch | `agentops/04-5-model-evolution/all-providers` |
| Branch deletion plan | Delete local and remote head branch after PR merge or explicit human closure. |
| Skills used | `local-postgres-dbt-modeling-orchestrator`, `local-runtime-harness-planner`, `qa-evidence-reviewer`, `privacy-governance-reviewer`, `spec-test-generator`, `hitl-escalation-controller`, `repo-governance-auditor` |
| Dependency changes | None in V0_5. |
| Databricks impact | None; no jobs, bundles, Terraform, Unity Catalog targets, Docker services, or Databricks packages. |
| Rollback | Redeploy previous complete snapshot `V0_3`; rollback dry-run remains the declared rollback target. |
| Source data safety | Source data remains local-only under `data_500k`; no raw source data files are tracked. |

## Changed File Groups

- `dbt/models/derived/`
- `dbt/tests/derived/`
- `dbt/macros/`
- `metadata/model_specs/evolution/V0_5/`
- `reports/qa/model_evolution_v0_5_*.md`
- `tests/specs/test_model_specs.py`
- `tests/sql/test_*_derived_sql_outputs.py`
- `logs/local_runtime/local_runtime_certification.md`

## Validation

| Command | Result |
| --- | --- |
| `PGHOST=/tmp PGDATABASE=agentic_migration_local UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt compile --project-dir dbt --profiles-dir dbt --select path:models/derived` | passed |
| `PGHOST=/tmp PGDATABASE=agentic_migration_local UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt run --project-dir dbt --profiles-dir dbt --select path:models/derived` | passed, 32 views |
| `PGHOST=/tmp PGDATABASE=agentic_migration_local UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt test --project-dir dbt --profiles-dir dbt --select path:models/derived path:tests/derived` | passed, 247 tests |
| `PGHOST=/tmp PGDATABASE=agentic_migration_local UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt docs generate --project-dir dbt --profiles-dir dbt` | passed |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest` | passed, 237 tests |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs/test_model_specs.py tests/sql/test_medication_derived_sql_outputs.py tests/test_repository_governance.py` | passed, 26 tests |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync ruff check` | passed |

## Governance Result

PR creation is allowed because V0_5 is local-only, all derived dbt models are declarative,
business-question logic remains unchanged, rollback targets `V0_3`, raw `data_500k` files
are not tracked, and no forbidden Databricks, Terraform, Docker, production-serving, Gold,
clinical-interpretation, or financial-interpretation action was introduced.
