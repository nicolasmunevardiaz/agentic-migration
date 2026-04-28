# Local Runtime And Contract Certification Plan

## Goal

Certify that approved provider adapters, Bronze/Silver contracts, QA evidence, and lineage expectations can run through a portable local validation loop before Databricks rollout planning begins.

This plan creates the cloud-agnostic runtime interface and local certification evidence for Raw/Bronze -> Silver behavior. It must not install runtime dependencies, run Databricks, deploy bundles, create cloud resources, apply Terraform, use production data, or claim parity with Databricks Runtime, Lakeflow, or Unity Catalog.

## Operating Focus

Run this plan as a local runtime architect. The agent may review all approved provider adapters and model specs together because the goal is shared runtime certification, not provider discovery or canonical modeling. The agent must keep the canonical model and contracts runtime-neutral. Databricks is a target certification runtime, not the source of modeling truth.

## Required Skills

Use `local-runtime-harness-planner` as the primary planning skill. Use `adapter-contract-reviewer` to confirm that adapters consume contracts through runtime-neutral interfaces. Use `qa-evidence-reviewer` to validate local certification evidence and keep it separate from Databricks certification. Use `privacy-governance-reviewer` to review dependency, fixture, lineage, and local artifact risks. Use `spec-test-generator` to define validation for runtime specs and interface contracts. Use `hitl-escalation-controller` if dependency approval, local runtime tooling, semantic mapping, or evidence is missing.

## Definition Of Ready

Provider specs, canonical model specs, provider-to-Silver mapping matrix, adapter implementation artifacts, adapter tests, QA evidence, and required HITL approvals exist or are explicitly blocked. Plan 03 adapter PRs are approved or merged. No unresolved mapping, PII, quarantine, source coverage, or relationship decision is required for local certification unless it is explicitly deferred with human approval.

## Inputs

Read provider specs, model specs, mapping matrix, adapter code, adapter tests, fixtures, QA evidence, privacy reports, HITL records, and the Technical PRD. Treat Spark Declarative Pipelines, Delta Lake OSS, OpenLineage, and Marquez as candidate local validation capabilities behind HITL-gated dependencies, not as installed requirements in this plan update.

## Filesystem Contract

Follow `docs/agentops_filesystem_conventions.md`. Do not create private agent folders or alternative output roots. Local runtime specs must land under `metadata/runtime_specs/local/`, QA evidence under `reports/qa/`, privacy/dependency findings under `reports/privacy/`, HITL records under `reports/hitl/`, runtime validation tests under `tests/specs/`, local certification trace logs under `logs/local_runtime/`, and temporary runtime outputs under `artifacts/`.

## Trace Logging

Append concise technical entries to `logs/local_runtime/local_runtime_certification.md`. Use `provider=all` for shared runtime events and a provider slug only when a finding concerns one provider adapter. Logs are append-only: do not purge, delete, reorder, or rewrite entries. Keep each note under one sentence and link to specs, reports, tests, or fixtures.

## Expected Outputs

Create `metadata/runtime_specs/local/local_runtime_profile.yaml`, `metadata/runtime_specs/local/runtime_interface_contract.yaml`, `reports/qa/local_runtime_certification.md`, `reports/privacy/local_runtime_dependency_review.md`, and runtime spec tests. The local runtime contract must define the provider parser interface, Bronze writer interface, canonical mapper interface, Silver writer interface, quarantine writer interface, QA evidence writer interface, lineage emitter interface, and runtime adapter interface.

Local certification must validate the intended flow:

```text
provider parser -> Bronze -> canonical mapping -> Silver -> quarantine -> QA evidence -> lineage evidence
```

The local runtime profile must define `local_dev` separately from `databricks_dev` and `databricks_prod`, reject Databricks-only secrets or workspace paths in local execution, and document candidate dependencies that require HITL approval before installation.

## Runtime Strategy

The local validation loop may use Spark Declarative Pipelines, Delta Lake OSS, contracts-as-code, OpenLineage, Marquez, and deterministic fixtures after dependency approval. Local validation should prove functional correctness, contract compatibility, deterministic quarantine behavior, traceability, and lineage evidence shape. It must not claim to validate Unity Catalog permissions, Databricks Runtime optimizations, serverless behavior, managed Lakeflow orchestration, Lakeflow Auto CDC, production performance, cloud IAM, or exact Databricks event logs.

Databricks rollout planning begins only after local certification evidence exists. Plan 05 validates runtime compatibility with Lakeflow, Unity Catalog, governed storage, permissions, and approved representative data execution.

## Python And Implementation Standards

Any generated Python must be English-only, idiomatic, and executed through `uv`. Use `uv run pytest`, `uv run ruff check`, and `uv run python -m <module>`; do not use direct `python3`. Common runtime spec loading, interface validation, QA evidence validation, path validation, and dependency review helpers should live under `src/common/` or `src/handlers/`. Do not install Spark, Delta, OpenLineage, Marquez, Docker tooling, or Databricks packages without HITL approval and privacy-governance review.

## QA Gates

Local runtime certification must be protected by runtime spec schema tests, adapter contract tests, integration tests over fixtures, lineage evidence shape tests, QA evidence tests, and scope guard tests. Tests should validate that runtime contracts reference approved provider/model/adapter specs, local profile paths stay under `artifacts/`, Databricks secrets are absent from local specs, runtime evidence uses `local_validated` instead of `databricks_certified`, and plan 04 does not authorize Unity Catalog registration, Databricks execution, Terraform, bundle deployment, or production data.

Expected local commands are `uv run pytest tests/specs`, `uv run pytest tests/adapters`, `uv run pytest tests/test_repository_governance.py`, and `uv run ruff check`.

## GitHub Workflow Expectations

Development workflows should use simple self-descriptive names such as `Local Runtime Certification`, `Runtime Spec Validation`, and `Adapter Integration Tests`. Workflows should validate specs, interfaces, fixtures, QA evidence, and local runtime scope without cloud credentials. Any Databricks, cloud, Docker, Spark, Delta, OpenLineage, or Marquez dependency must be reviewed and approved before installation.

## HITL Decisions

Human approval is required before adding or installing Spark, Delta, OpenLineage, Marquez, Docker services, Databricks packages, cloud credentials, or dependency scanner exceptions. Human review is also required when local certification depends on semantic assumptions, unresolved provider mappings, lineage interpretation, or quarantine behavior not approved in previous plans.

## Definition Of Done

The plan is done when local runtime specs, interface contracts, QA evidence, dependency review, runtime validation tests, and trace logs are reviewable and local QA passes. Databricks validation remains blocked until plan 05 and explicit HITL approval.
