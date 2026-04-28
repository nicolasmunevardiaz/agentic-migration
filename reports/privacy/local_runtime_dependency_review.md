# Local Runtime Dependency Review

plan_id: `04_local_runtime_and_contract_certification_plan`
provider: `all`
status: `dependencies_blocked_pending_hitl`

## Candidate Dependencies

| Dependency | Purpose | Approval status | Blocked action |
| --- | --- | --- | --- |
| `pyspark[pipelines]` | Optional Spark Declarative Pipelines local run and dry-run capability. | `pending_human_approval` | Do not install or run Spark pipelines. |
| `delta-spark` | Optional Delta Lake OSS table behavior for local Bronze/Silver tests. | `pending_human_approval` | Do not install or write Delta tables. |
| `openlineage-spark` | Optional Spark listener for local lineage event capture. | `pending_human_approval` | Do not install or emit OpenLineage events. |
| `marquez` / Docker service | Optional local lineage backend/UI. | `pending_human_approval` | Do not start Docker services. |

## Governance Notes

- No `pyproject.toml` or lockfile changes are made by this plan update.
- No Docker services, Databricks packages, cloud credentials, Terraform, or bundle deployment are authorized.
- Any future dependency addition must be reviewed by `privacy-governance-reviewer` and approved through HITL before installation.
