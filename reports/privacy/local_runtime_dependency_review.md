# Local Runtime Dependency Review

plan_id: `04_local_runtime_and_contract_certification_plan`
provider: `all`
status: `python_dependencies_approved_for_local_import_only`

## HITL Approval

The user approved resuming Plan 04 after local package installation. This approval is interpreted narrowly as approval for the already-added Python packages in `pyproject.toml` and `uv.lock`: `pyspark`, `delta-spark`, and `openlineage-python`.

This approval does not authorize starting Colima, Docker services, Marquez, Databricks jobs, Terraform, bundles, cloud resources, production data usage, OpenLineage transport emission, Spark Declarative Pipeline execution, or Delta table writes.

## Approved Local Python Dependencies

| Dependency | Installed version | Approved purpose | Evidence | Remaining blocked action |
| --- | --- | --- | --- | --- |
| `pyspark` | `4.1.1` | Local import and Spark API availability check for future fixture validation. | `pyproject.toml`, `uv.lock`, import check in `reports/qa/local_runtime_certification.md` | Do not run Spark Declarative Pipelines or production-scale Spark jobs. |
| `delta-spark` | `4.2.0` | Local import check for future Delta Lake OSS table-shape validation. | `pyproject.toml`, `uv.lock`, import check in `reports/qa/local_runtime_certification.md` | Do not write Delta tables or claim Delta runtime certification. |
| `openlineage-python` | `1.46.0` | Local import check for future lineage event-shape validation. | `pyproject.toml`, `uv.lock`, import check in `reports/qa/local_runtime_certification.md` | Do not emit OpenLineage events to local, remote, Kafka, or cloud transports. |

## Local Tooling State

- Homebrew OpenJDK 17 is installed at `/opt/homebrew/opt/openjdk@17/bin/java`, but the default shell still needs `JAVA_HOME` and `PATH` configuration before plain `java -version` succeeds.
- Colima is installed but `colima status` reports not running.
- Docker CLI points at a Colima socket through local context or `DOCKER_HOST`, but container-backed validation remains blocked because service start approval was not granted.

## Candidate Dependencies

| Dependency | Purpose | Approval status | Blocked action |
| --- | --- | --- | --- |
| Spark Declarative Pipelines execution | Optional local run and dry-run capability. | `pending_human_approval` | Do not run Spark pipelines. |
| Delta Lake OSS table writes | Optional Delta table behavior for local Bronze/Silver tests. | `pending_human_approval` | Do not write Delta tables. |
| `openlineage-spark` | Optional Spark listener for local lineage event capture. | `pending_human_approval` | Do not install listener jars or emit Spark OpenLineage events. |
| `marquez` / Docker service | Optional local lineage backend/UI. | `pending_human_approval` | Do not start Docker services. |
| Databricks packages | Optional Databricks target-runtime validation tooling for later plans. | `pending_human_approval_for_plan_05_or_later` | Do not install Databricks Connect, run jobs, or deploy bundles in Plan 04. |

## Governance Notes

- `pyproject.toml` and `uv.lock` changed to add approved local Python packages.
- No Docker services, Databricks packages, cloud credentials, Terraform, bundle deployment, Marquez service, or production data are authorized.
- Any future dependency addition or service start must be reviewed by `privacy-governance-reviewer` and approved through HITL before execution.
