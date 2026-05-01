---
name: dbt-layering-orchestrator
description: "Design and evolve dbt model filesystem layers, materializations, lineage, refs, schemas, and QA gates for the local PostgreSQL model after adapters have loaded Silver tables."
user-invocable: false
---

# dbt Layering Orchestrator

Use this skill for Plan 05 dbt work when the source data is already loaded into local PostgreSQL by approved adapters and the next task is to organize, build, test, or refactor dbt models.

## Required Inputs

Read `docs/05_dbt_model_layering_and_normal_form_evolution_plan.md`, `metadata/model_specs/dbt/dbt_model_layering_contract.yaml`, `metadata/model_specs/data_quality/contracts/**`, `metadata/model_specs/silver/**`, `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`, `dbt/dbt_project.yml`, `dbt/models/sources.yml`, `dbt/models/derived/**`, `dbt/models/data_quality/**`, `dbt/macros/**`, `dbt/tests/**`, `tests/specs/**`, `tests/sql/**`, and `logs/local_runtime/local_runtime_certification.md`.

## Layering Rules

Treat dbt as the executable transformation graph and metadata contracts as the source of modeling intent. Do not create isolated SQL files that bypass `ref()`, `source()`, tests, or contracts.

Use this layer vocabulary unless the active dbt contract changes:

```text
silver/
  landing/        optional, only for dbt-visible local landing projections
  staging/        light source alignment and naming
  standardized/   deterministic format/code/temporal standardization
  normalized/     entity decomposition and stable keys
  conformed/      cross-entity and cross-provider alignment
  dq/             survivor candidates, audit helpers, quality flags

gold/
  facts/          final additive or event-grain facts
  dimensions/     final descriptive dimensions and lookup dimensions
  marts/          reusable analytical aggregates
  exchange/       external exchange-ready shapes
  exports/        controlled export shapes
```

Prefer `ephemeral` for short reusable SQL building blocks, `view` for lightweight auditable layers reused by downstream models, and `table` for expensive or final models queried repeatedly. Every materialization choice must be intentional and documented in schema YAML or the active plan when it changes runtime behavior.

## dbt Graph Rules

Use `source()` only at the edge of the graph. Use `ref()` for all dbt-to-dbt dependencies so dbt lineage, `manifest.json`, `catalog.json`, and docs remain meaningful.

Do not duplicate source logic in multiple downstream models. If multiple models need the same cleanup, create a shared upstream standardization or normalization model, or a macro when the expression is repeated across entities.

Use macros for stable, cross-entity rules such as code trimming, blank-to-null handling, provider-scoped hashes, timezone conversion, and amount parsing. Keep entity-specific business rules in the entity SQL or contract so lineage remains explainable.

## Provider And Data Quality Rules

Provider metadata belongs in a conformed/provider dimension when it becomes reusable, such as timezone, provider slug, display name, source system family, or default locale. Do not rely on majority attribution when a provider, record, or field lacks approved metadata; expose nulls and control flags instead.

Data quality models may diagnose and standardize, but production-facing derived layers must consume those standards through explicit refs or macros. A quality issue is only closed when the downstream model that users query no longer exposes the discrepancy except through approved nulls or flags.

## QA Rules

Before declaring dbt layering done, run `dbt parse`, targeted `dbt run`/`dbt test` selectors, spec tests for contracts, SQL pytest over the full local PostgreSQL data when required, and `ruff check` for Python tests. If a model path moves, update tests to discover SQL recursively and verify no stale path assumptions remain.

Trace every material layout decision in `logs/local_runtime/local_runtime_certification.md` with the plan id, affected entity, changed layer, validation command, and remaining risk.

## Stop Conditions

Stop for HITL when a dbt layer would encode business meaning, clinical interpretation, financial interpretation, provider ownership, timezone attribution, or record survivorship that is not already approved by contract. Otherwise implement the contract directly and prove it with dbt tests.
