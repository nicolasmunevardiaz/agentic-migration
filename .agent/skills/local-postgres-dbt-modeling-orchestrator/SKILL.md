---
name: local-postgres-dbt-modeling-orchestrator
description: "Operate Plan 04.5 local PostgreSQL and dbt Core model iterations as idempotent CI/CD-style deployments with snapshot rollback, HITL drift decisions, and robust local tests."
user-invocable: false
---

# Local PostgreSQL dbt Modeling Orchestrator

Use this skill for Plan 04.5 work after local runtime certification and before Databricks rollout. This skill owns local PostgreSQL deploys, dbt Core readiness, model evolution snapshots, iteration packets, business-question registry versions, data loading into Bronze/Silver review tables, drift normalization, HITL decision write-back, tested SQL outputs, and terminal-driven QA.

## Required Inputs

Read `docs/04_5_local_data_workbench_and_model_evolution_plan.md`, `docs/local_postgres_workbench_deploy.md`, `.agent/spec_templates/model_iteration_packet.template.yaml`, `.agent/spec_templates/normalization_probe.template.yaml`, `.agent/spec_templates/semantic_discovery_issue.template.yaml`, `metadata/provider_specs/**`, `metadata/model_specs/bronze/bronze_contract.yaml`, `metadata/model_specs/silver/**`, `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`, `metadata/model_specs/impact/business_question_profiles.yaml`, `metadata/runtime_specs/local/**`, `src/**`, and `tests/**`.

## Required Outputs

Create or update a complete model snapshot under `metadata/model_specs/evolution/V0_N/`. Each snapshot must include `model_snapshot.yaml`, a complete PostgreSQL DDL image, a `business_question_registry` entry for the exact `business_question_profiles.yaml` version being implemented, and an `iteration_packet.yaml` with links to database, dbt, lineage, QA, HITL, and rollback evidence. Add or update terminal-run tests under `tests/` and implementation code under `src/` only after the declarative metadata exists. Append concise trace entries to `logs/local_runtime/local_runtime_certification.md`.

## Operating Rules

Treat PostgreSQL deploys as local CI/CD pipelines: dry-run, apply, verify, test, then record evidence. Do not patch tables manually. Do not preserve backward compatibility during Plan 04.5; instead, make each material model iteration a clean full snapshot with an explicit rollback target.

dbt Core is the preferred local orchestration and testing tool for material normalization iterations after its project layout and profile are declared in metadata or docs. dbt must not become an alternate source of truth; metadata contracts remain primary.

Every resolved business question must eventually have versioned SQL that answers it against PostgreSQL or a HITL-approved deferral. If normalization changes business meaning, update `business_question_profiles.yaml`, assign a new business-question registry version in the active snapshot, and add/adjust tests.

Before advancing to the next model iteration, validate the iteration packet. It must say which business question improved, which model changed, which SQL proves it, what broke, what data evidence supports the decision, what tests passed, what HITL decision is still needed, and how to restore the last stable snapshot.

If the database reveals nested payloads, wrong-entity fields, mixed grain, unsafe casts, duplicate keys, orphan relationships, unit/code ambiguity, temporal ambiguity, PII/PHI exposure, or sparse unmapped fields, first create a normalization probe when it is safe to do so. Decompose the problem, create a temp or scratch transition table, test a candidate normalization, and measure before/after quality. Create a semantic discovery issue only when ownership, meaning, privacy, clinical interpretation, financial interpretation, or business impact remains ambiguous after the probe or cannot be safely probed. Do not flatten, move, drop, or coerce the data silently.

## Checks

Validate that the active snapshot references Bronze, Silver, provider-to-Silver matrix, business-question profiles, runtime specs, deploy handler, deploy runbook, quality gates, rollback, the business-question registry version, and the iteration packet. Validate that PostgreSQL feedback, dbt artifact feedback, lineage feedback when approved, QA feedback, HITL feedback, business-question progress, normalization probes, semantic discovery issues when needed, and quality metrics are present before advancement. Validate that no snapshot contains production paths, Databricks execution, Terraform, bundle deploy, Docker Desktop, or unapproved serving model claims. Validate that `business_question_profiles.yaml` is treated as a living contract whenever normalization changes business meaning.

## Non-Negotiables

All execution is local. No production data, Databricks jobs, Terraform, bundle deploys, cloud resources, Docker Desktop, or production Gold marts. HITL decisions must be written through review tables or versioned evidence, not private notes. Every major normalization change requires a new `V0_N` snapshot, business-question registry versioning when applicable, an iteration packet, and tests.

## DoD

The active snapshot deploys idempotently to local PostgreSQL, rollback is fully defined, the iteration packet is complete, tests cover unit/integration/regression/e2e behavior, drift/HITL tables are ready for review, every business question has tested local SQL output or HITL-approved deferral, and the PR evidence identifies changed contracts, commands run, risks, rollback, and blocked downstream work.
