# Local Runtime Certification

plan_id: `04_local_runtime_and_contract_certification_plan`
provider: `all`
status: `contract_defined_not_executed`
validation_state: `local_validated`
databricks_state: `not_databricks_certified`

## Summary

This report defines the initial local runtime certification evidence contract. It does not certify Databricks compatibility and does not install or execute Spark, Delta, OpenLineage, Marquez, Docker, Databricks packages, or cloud services.

## Interface Coverage

- Provider parser interface: defined in `metadata/runtime_specs/local/runtime_interface_contract.yaml`.
- Bronze writer interface: defined.
- Canonical mapper interface: defined.
- Silver writer interface: defined.
- Quarantine writer interface: defined.
- QA evidence writer interface: defined.
- Lineage emitter interface: defined.
- Runtime adapter interface: defined.

## Local Certification Boundary

Local certification may validate provider parser output, Bronze/Silver contract shape, canonical mapping, quarantine behavior, QA evidence shape, and lineage evidence shape. It must not claim Unity Catalog permissions, Databricks Runtime behavior, Lakeflow orchestration, Auto CDC, serverless behavior, cloud IAM, production performance, or exact Databricks event logs.

## Next Action

Use `local-runtime-harness-planner` in plan 04 to turn these contracts into executable local validation only after HITL approves any runtime dependencies.
