---
name: local-runtime-harness-planner
description: "Define and validate the cloud-agnostic local runtime harness, runtime profiles, adapter interfaces, local lineage evidence, dependency approval gates, and local certification evidence before Databricks rollout."
user-invocable: false
---

# Local Runtime Harness Planner

Use this skill after adapter implementation artifacts exist and before Databricks rollout planning. This is a planner skill: it defines the local runtime certification contract that proves adapters and model contracts can run through portable interfaces without cloud credentials.

Read provider specs, canonical model specs, provider-to-Silver mapping matrix, adapter code, adapter tests, fixtures, QA reports, privacy reports, HITL records, and `docs/04_local_runtime_and_contract_certification_plan.md`. Confirm that contracts and canonical models remain runtime-neutral and that Databricks is treated as a target certification runtime, not the modeling authority.

Produce local runtime specs under `metadata/runtime_specs/local/`, a QA certification report under `reports/qa/`, a dependency review under `reports/privacy/`, runtime validation tests under `tests/specs/`, and trace entries under `logs/local_runtime/local_runtime_certification.md`.

## Interface Contract

The local runtime contract must define the provider parser interface, Bronze writer interface, canonical mapper interface, Silver writer interface, quarantine writer interface, QA evidence writer interface, lineage emitter interface, and runtime adapter interface. The contract must show how the flow moves through `provider parser -> Bronze -> canonical mapping -> Silver -> quarantine -> QA evidence -> lineage evidence`.

## Runtime Profiles

Define `local_dev`, `databricks_dev`, and `databricks_prod` as separate profiles. The `local_dev` profile must not contain Databricks tokens, workspace paths, Unity Catalog targets, production data paths, Terraform settings, or bundle deployment commands. Local output paths must be constrained to `artifacts/`.

## Dependency Gates

Spark Declarative Pipelines, Delta Lake OSS, OpenLineage, Marquez, Docker services, Databricks packages, and dependency scanner changes are candidates only until HITL approval exists. Do not install, pin, or approve these dependencies from this skill. Record each candidate dependency with purpose, risk, owner, approval status, and blocked action.

## Checks

Validate that local certification says `local_validated`, not `databricks_certified`. Validate that local lineage evidence is a shape contract or approved local output, not Unity Catalog lineage. Validate that adapters consume specs through runtime-neutral interfaces. Validate that local runtime evidence does not weaken parser, model, privacy, or quarantine decisions.

## Non-Negotiables

Do not run Databricks jobs, deploy bundles, apply Terraform, create cloud resources, start Docker services, install dependencies, use production data, or claim parity with Databricks Runtime, Lakeflow managed orchestration, Auto CDC, Unity Catalog permissions, serverless behavior, cloud IAM, performance, or exact Databricks event logs.

## Output Format

Return a concise report with status, runtime specs created, interface coverage, dependency approval gaps, local QA evidence, lineage evidence, blocked items, HITL decisions required, and recommended next action.
