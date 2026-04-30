# Plan 04.5 V0_2 Repo Governance

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
| Dependency changes | Added approved local-only `dbt-postgres` and transitive `psycopg2-binary`. |
| Databricks impact | None; no jobs, bundles, Terraform, Unity Catalog targets, or Databricks packages. |
| Rollback | Redeploy previous complete snapshot `V0_1`; rollback dry-run artifact rendered. |

## Changed File Groups

- `metadata/model_specs/evolution/V0_2/`
- `dbt/`
- `src/handlers/local_model_evolution_workbench.py`
- `tests/specs/`, `tests/sql/`
- `docs/local_postgres_workbench_deploy.md`
- `metadata/runtime_specs/local/local_runtime_profile.yaml`
- `reports/privacy/`, `reports/qa/`, `reports/hitl/`
- `pyproject.toml`, `uv.lock`
- `logs/local_runtime/local_runtime_certification.md`

## Governance Result

PR creation is allowed because evidence is local-only, branch target is `main`, dependency approval is recorded, tests passed, rollback is defined, and no forbidden Databricks/Terraform/Docker/production action was introduced.
