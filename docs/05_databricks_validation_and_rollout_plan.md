# Databricks Validation And Rollout Plan

## Goal

Prepare approved Databricks and Unity Catalog validation for Raw/Bronze to Silver migration outputs after local runtime certification and any required Plan 04.5 local model evolution gates are complete. This plan defines how reviewed specs, adapter artifacts, local certification evidence, QA evidence, model-evolution evidence, and governance controls become a Databricks-ready validation package.

This plan is Databricks-oriented but the project architecture remains cloud agnostic. Databricks, Unity Catalog, Lakeflow, and Databricks Asset Bundles are one governed target implementation, not the source of modeling truth. Provider specs, Bronze/Silver contracts, local runtime contracts, model-evolution snapshots, QA contracts, Terraform modules, and CI/CD workflow definitions must be designed so the same control plane can be mapped to another approved cloud target later.

This plan covers Databricks validation and rollout planning only. It must not discover provider behavior, design the canonical model, build the local runtime harness, apply Terraform, deploy bundles, create cloud resources, run production jobs, promote beyond the approved local model-evolution scope, or execute full-volume data without explicit Human in the Loop approval.

## Cloud-Agnostic Architecture Requirement

Plan 05 must separate portable architecture from Databricks-specific binding:

- Portable contracts: provider specs, Bronze/Silver model specs, business-question registry versions, runtime-neutral interfaces, QA evidence contracts, lineage requirements, and model-evolution snapshots.
- Portable orchestration intent: declarative Spark pipeline definitions, data quality expectations, dependency graph, rollback, rerun behavior, and CI/CD gates.
- Target bindings: Databricks workspace, Unity Catalog catalog/schema/table names, governed storage locations, Lakeflow/DLT job configuration, Databricks Asset Bundles, cloud IAM, and environment secrets.
- Infrastructure binding: Terraform modules and variables must expose cloud/provider-specific values without hardcoding them into model specs or adapter code.

Databricks deployment specs must reference portable contracts by path and version. They must not redefine provider semantics, canonical model semantics, business-question logic, or local model-evolution decisions.

## Required Skills

Use `databricks-rollout-planner` as the primary rollout planning skill. Use `qa-evidence-reviewer` to validate evidence contracts, QA decisions, rerun behavior, and failure handling. Use `privacy-governance-reviewer` to review PII/PHI, permissions, Unity Catalog targets, secrets, and approval requirements.

## Definition Of Ready

Provider specs, canonical model specs, adapter readiness report, generated adapter artifacts, local runtime specs, local runtime certification report, Plan 04.5 model-evolution evidence or HITL-approved deferral, spec tests, adapter tests, QA evidence contract, and privacy review findings are available. GitHub CI has passed local/static validation. Human approval exists for Databricks validation execution.

The deployment strategy must identify which pieces are cloud-agnostic and which pieces are Databricks/AWS/Azure/GCP bindings. Terraform planning is allowed only as reviewable specs or modules; `terraform apply` remains blocked until explicit HITL approval.

## Inputs

Read model specs, local runtime specs, model-evolution snapshots, deployment templates, adapter readiness output, QA evidence expectations, local certification evidence, privacy review output, Unity Catalog target assumptions, Databricks environment constraints, Terraform/IaC assumptions, CI/CD workflow assumptions, and the Technical PRD. Use Databricks as the runtime for representative data validation only after local certification, local model-evolution gates, GitHub CI, and human approval.

## Filesystem Contract

Follow `docs/agentops_filesystem_conventions.md`. Do not create private agent folders or alternative output roots. Databricks deployment specs must land under `metadata/deployment_specs/databricks/`, portable deployment abstractions or cloud-agnostic CI/CD mappings under approved `metadata/deployment_specs/` subtrees when created, QA evidence plans under `reports/qa/`, privacy and governance findings under `reports/privacy/`, HITL approval records under `reports/hitl/`, deployment validation tests under `tests/specs/`, and local runtime outputs under `artifacts/`.

## Trace Logging

Append concise technical entries to `logs/databricks_rollout/rollout_readiness.md`. Use `provider=all` for platform-level rollout readiness and use a provider slug only when the event concerns provider-specific validation. Logs are append-only: do not purge, delete, reorder, or rewrite entries. Keep each note under one sentence and link to deployment specs, QA evidence, or HITL approvals.

## Expected Outputs

Create Databricks deployment specs under `metadata/deployment_specs/databricks/*.yaml`, a Databricks validation plan, a QA evidence contract, a Unity Catalog governance checklist, a cloud-agnostic CI/CD mapping note, a Terraform readiness note, and a HITL approval record. Deployment specs may reference Databricks Asset Bundles, Lakeflow/DLT, dlt-meta, workflows, jobs, governed storage locations, quarantine outputs, manifests, and QA evidence tables, but execution remains approval-gated.

Deployment specs must consume the runtime-neutral contracts certified by Plan 04 and any approved Plan 04.5 model-evolution evidence instead of redefining provider, canonical, Silver, Gold-candidate, or business-question semantics.

## Declarative Spark And Pipeline Contract

Spark Declarative Pipelines, Lakeflow Declarative Pipelines, DLT, and dlt-meta are implementation options for declarative Spark execution. Their specs must be generated from portable metadata contracts and must keep this separation:

- Logical pipeline graph: portable flow from source contracts to Bronze, Silver, QA, quarantine, lineage, and approved local Gold/query outputs.
- Execution binding: Databricks/Lakeflow-specific settings, cluster/serverless/runtime options, storage paths, secrets, permissions, and schedules.
- Test binding: expectations, reconciliation checks, row-count checks, null-rate checks, lineage checks, and rollback/rerun checks.

Declarative Spark specs must be reviewable in Git, validated by local/static tests, and approval-gated before execution. They must not become hand-authored notebooks that bypass specs-as-code.

## Terraform And Multi-Cloud CI/CD Contract

Terraform is the expected IaC mechanism for governed infrastructure, but Plan 05 may only prepare or validate Terraform-ready specs unless HITL approves execution. Terraform modules must be parameterized by environment and cloud target. They must not embed provider-specific data semantics, raw paths, secrets, or production-only defaults.

CI/CD must be mapped in layers:

1. Static spec/code validation that is cloud agnostic.
2. Local runtime and model-evolution validation that runs without cloud credentials.
3. Target binding validation for Databricks and Unity Catalog.
4. Terraform plan review for infrastructure changes.
5. Approved target runtime execution.

The same pipeline shape should be portable to another cloud by replacing target bindings and Terraform variables, not by rewriting provider/model contracts.

## Python And Implementation Standards

Any Python support code must be English-only, idiomatic, and executed through `uv`. Use `uv run pytest`, `uv run ruff check`, and `uv run python -m <module>`; do not use direct `python3`. Function names must describe behavior. One-line docstrings are allowed only when useful. Common deployment spec loading, lineage checks, readiness validation, path validation, and evidence report helpers should live in shared utilities. Use handlers to separate orchestration, config validation, permission checks, lineage checks, reconciliation planning, and report generation. Use `@dataclass` only for clear domain values.

## QA Gates

Deployment planning must be protected by deployment schema tests, Databricks readiness checks, local certification reference checks, Plan 04.5 model-evolution reference checks, reconciliation planning, lineage validation planning, permissions validation, cloud-agnostic binding checks, Terraform safety checks, and regression tests over deployment specs. Tests should validate approved model references, approved local runtime evidence references, approved model-evolution evidence references, Unity Catalog catalog/schema/table targets, governed locations, no local absolute paths, no production execution without approval, coherent declarative Spark/Lakeflow/DLT/dlt-meta references when used, QA evidence destinations, target-binding separation, and explicit rollback or rerun expectations.

Expected local commands are `uv run pytest tests/specs/test_deployment_specs.py`, `uv run pytest tests/specs/test_qa_evidence_specs.py`, `uv run pytest tests/specs/test_spec_chain_system.py`, and `uv run ruff check`. Databricks runtime checks must be executed only by an approved workflow or approved operator action.

## GitHub Workflow Expectations

Development workflows should use simple self-descriptive names such as `Deployment Spec Validation`, `Cloud-Agnostic Pipeline Validation`, `Databricks Readiness`, `Terraform Plan Review`, and `QA Evidence Validation`. Workflows should validate deployment specs and readiness artifacts without running production jobs. OpenAI-powered summaries must use `OPENAI_API_KEY` from GitHub secrets only. Databricks credentials, tokens, workspace URLs, storage paths, Terraform backend settings, cloud account identifiers, and sensitive evidence must be referenced through approved secrets or configuration and must not be printed in logs.

## HITL Decisions

Human approval is required for Databricks validation execution, Unity Catalog target registration, permission changes, governed storage locations, PII/PHI handling, sample-to-larger-volume progression, quarantine policy, Terraform apply, bundle deploy, cloud resource creation, target cloud binding changes, and any destructive or production-impacting action. Approval records must include owner, decision, date, evidence path, impacted provider/entity/table, environment, target cloud, and next action.

## Definition Of Done

The plan is done when deployment specs, QA evidence expectations, Unity Catalog governance checklist, local-certification references, Plan 04.5 model-evolution references or deferrals, cloud-agnostic CI/CD mapping, Terraform readiness notes, readiness checks, and HITL approvals are prepared and reviewable. Databricks validation may proceed only through approved dev or validation workflows. Production promotion remains out of scope, and any post-Silver delivery must trace back to approved Plan 04.5 business-question SQL outputs or HITL-approved deferrals.
