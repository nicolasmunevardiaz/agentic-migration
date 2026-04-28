# Databricks Validation And Rollout Plan

## Goal

Prepare approved Databricks and Unity Catalog validation for Raw/Bronze to Silver migration outputs after local runtime certification is complete. This plan defines how reviewed specs, adapter artifacts, local certification evidence, QA evidence, and governance controls become a Databricks-ready validation package.

This plan covers Databricks validation and rollout planning only. It must not discover provider behavior, design the canonical model, build the local runtime harness, apply Terraform, deploy bundles, create cloud resources, run production jobs, promote beyond Silver, or execute full-volume data without explicit Human in the Loop approval.

## Required Skills

Use `databricks-rollout-planner` as the primary rollout planning skill. Use `qa-evidence-reviewer` to validate evidence contracts, QA decisions, rerun behavior, and failure handling. Use `privacy-governance-reviewer` to review PII/PHI, permissions, Unity Catalog targets, secrets, and approval requirements.

## Definition Of Ready

Provider specs, canonical model specs, adapter readiness report, generated adapter artifacts, local runtime specs, local runtime certification report, spec tests, adapter tests, QA evidence contract, and privacy review findings are available. GitHub CI has passed local/static validation. Human approval exists for Databricks validation execution.

## Inputs

Read model specs, local runtime specs, deployment templates, adapter readiness output, QA evidence expectations, local certification evidence, privacy review output, Unity Catalog target assumptions, Databricks environment constraints, and the Technical PRD. Use Databricks as the runtime for representative data validation only after local certification, GitHub CI, and human approval.

## Filesystem Contract

Follow `docs/agentops_filesystem_conventions.md`. Do not create private agent folders or alternative output roots. Databricks deployment specs must land under `metadata/deployment_specs/databricks/`, QA evidence plans under `reports/qa/`, privacy and governance findings under `reports/privacy/`, HITL approval records under `reports/hitl/`, deployment validation tests under `tests/specs/`, and local runtime outputs under `artifacts/`.

## Trace Logging

Append concise technical entries to `logs/databricks_rollout/rollout_readiness.md`. Use `provider=all` for platform-level rollout readiness and use a provider slug only when the event concerns provider-specific validation. Logs are append-only: do not purge, delete, reorder, or rewrite entries. Keep each note under one sentence and link to deployment specs, QA evidence, or HITL approvals.

## Expected Outputs

Create Databricks deployment specs under `metadata/deployment_specs/databricks/*.yaml`, a Databricks validation plan, a QA evidence contract, a Unity Catalog governance checklist, and a HITL approval record. Deployment specs may reference Databricks Asset Bundles, Lakeflow/DLT, dlt-meta, workflows, jobs, governed storage locations, quarantine outputs, manifests, and QA evidence tables, but execution remains approval-gated. Deployment specs must consume the runtime-neutral contracts certified by plan 04 instead of redefining provider, canonical, or Silver semantics.

## Python And Implementation Standards

Any Python support code must be English-only, idiomatic, and executed through `uv`. Use `uv run pytest`, `uv run ruff check`, and `uv run python -m <module>`; do not use direct `python3`. Function names must describe behavior. One-line docstrings are allowed only when useful. Common deployment spec loading, lineage checks, readiness validation, path validation, and evidence report helpers should live in shared utilities. Use handlers to separate orchestration, config validation, permission checks, lineage checks, reconciliation planning, and report generation. Use `@dataclass` only for clear domain values.

## QA Gates

Deployment planning must be protected by deployment schema tests, Databricks readiness checks, local certification reference checks, reconciliation planning, lineage validation planning, permissions validation, and regression tests over deployment specs. Tests should validate approved model references, approved local runtime evidence references, Unity Catalog catalog/schema/table targets, governed locations, no local absolute paths, no production execution without approval, coherent Lakeflow/DLT or dlt-meta references when used, QA evidence destinations, and explicit rollback or rerun expectations.

Expected local commands are `uv run pytest tests/specs/test_deployment_specs.py`, `uv run pytest tests/specs/test_qa_evidence_specs.py`, `uv run pytest tests/specs/test_spec_chain_system.py`, and `uv run ruff check`. Databricks runtime checks must be executed only by an approved workflow or approved operator action.

## GitHub Workflow Expectations

Development workflows should use simple self-descriptive names such as `Databricks Readiness`, `Deployment Spec Validation`, and `QA Evidence Validation`. Workflows should validate deployment specs and readiness artifacts without running production jobs. OpenAI-powered summaries must use `OPENAI_API_KEY` from GitHub secrets only. Databricks credentials, tokens, workspace URLs, storage paths, and sensitive evidence must be referenced through approved secrets or configuration and must not be printed in logs.

## HITL Decisions

Human approval is required for Databricks validation execution, Unity Catalog target registration, permission changes, governed storage locations, PII/PHI handling, sample-to-larger-volume progression, quarantine policy, and any destructive or production-impacting action. Approval records must include owner, decision, date, evidence path, impacted provider/entity/table, environment, and next action.

## Definition Of Done

The plan is done when deployment specs, QA evidence expectations, Unity Catalog governance checklist, local-certification references, readiness checks, and HITL approvals are prepared and reviewable. Databricks validation may proceed only through approved dev or validation workflows. Production promotion and post-Silver delivery remain out of scope.
