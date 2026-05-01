# dbt Rollout Prompts

## Purpose

This document contains plug-and-play prompts for Plan 05 dbt model layering and normal-form evolution. The workflow is entity-specific and intentionally hybrid: Codex performs deterministic SQL/dbt work, PostgreSQL probes, contract review, and QA; HITL reviews ambiguous evidence directly in PostgreSQL and makes fast modeling decisions when contracts do not already resolve the issue.

Use this rollout after approved adapters have loaded `data_500k` into PostgreSQL `landing.*`. The default dbt target is the PostgreSQL `staging` schema for models under `dbt/models/derived/**`.

## Required Context

Every prompt must use `docs/05_dbt_model_layering_and_normal_form_evolution_plan.md` as the active plan and must read these agreements/contracts before changing models:

```text
metadata/provider_specs/**
metadata/model_specs/bronze/bronze_contract.yaml
metadata/model_specs/silver/**
metadata/model_specs/mappings/provider_to_silver_matrix.yaml
metadata/model_specs/data_quality/contracts/**
metadata/model_specs/dbt/dbt_model_layering_contract.yaml
metadata/model_specs/evolution/V0_5/**
dbt/dbt_project.yml
dbt/profiles.yml
dbt/models/sources.yml
dbt/models/derived/**
dbt/macros/**
dbt/tests/**
tests/specs/**
tests/sql/**
reports/dataq_drifts/**
reports/hitl/**
reports/privacy/**
reports/qa/**
logs/local_runtime/**
```

Use these skills: `dbt-layering-orchestrator`, `relational-normal-form-reviewer`, `local-postgres-dbt-modeling-orchestrator`, `spec-test-generator`, `qa-evidence-reviewer`, `privacy-governance-reviewer`, and `hitl-escalation-controller`.

## Operating Rules

Start every entity with a status quo audit. Reuse existing dbt models, schema YAML, tests, probes, reports, and trace logs when valid. Do not reload source files, rewrite adapters, hand-patch PostgreSQL as durable model history, or bypass dbt lineage.

For every entity, work from PostgreSQL evidence outward:

```text
landing.<entity> -> dbt source() -> staging dbt models -> entity silver layers -> entity gold candidates
```

Before changing SQL, inspect every column for provider scope, null semantics, nested structures, duplicate keys, mixed grain, orphan references, unsafe casts, temporal ambiguity, unit/code ambiguity, sparse unmapped fields, and PII/PHI exposure. Use small SQL probes first, then promote only contract-backed changes.

Escalate to HITL when an issue is not easy to resolve from contracts and SQL evidence. HITL is required for ownership, business meaning, clinical meaning, financial meaning, privacy exposure, provider timezone defaults, cross-provider identity, survivorship preference, semantic mapping, or field deprecation. Do not ask HITL for deterministic cleanup already covered by contract: blank-to-null, trim/lower/upper normalization, provider-scoped hashes, approved timezone conversion, approved decimal normalization, and explicit unresolved flags.

Every HITL request must include:

```text
entity
provider scope
field/column
observed examples
counts and impact
contract references reviewed
candidate options
recommended default
affected dbt models/tests
rollback target
```

## Validation Lanes

Use `DBT_THREADS=10` by default on the local Mac M4/48 GB RAM environment.

```bash
# Parse only, no database objects.
PGHOST=/tmp PGDATABASE=agentic_migration_local DBT_THREADS=10 \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt parse --project-dir dbt --profiles-dir dbt

# Rebuild the staging layer from landing.
PGHOST=/tmp PGDATABASE=agentic_migration_local DBT_THREADS=10 \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt run --project-dir dbt --profiles-dir dbt --select path:models/derived

# Fast smoke, currently 58 tests.
PGHOST=/tmp PGDATABASE=agentic_migration_local DBT_THREADS=10 \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt test --project-dir dbt --profiles-dir dbt --selector staging_smoke

# Critical regression, currently 110 tests.
PGHOST=/tmp PGDATABASE=agentic_migration_local DBT_THREADS=10 \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt test --project-dir dbt --profiles-dir dbt --selector staging_critical

# Full certification, currently 267 tests.
PGHOST=/tmp PGDATABASE=agentic_migration_local DBT_THREADS=10 \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt test --project-dir dbt --profiles-dir dbt --selector staging_full
```

Smoke is for quick confidence. Critical is for model-risk regression. Full certification is required before PR, merge, approval, or any material key/grain/survivorship/contract change.

## Entity Rollout Order

Run one entity at a time unless two entities have disjoint write scopes and no unresolved shared contract.

```text
1. providers/domains
2. patients
3. coverage
4. encounters
5. conditions
6. medications
7. observations
8. cost_records
```

The provider/domain step should create or refine reusable conformed dimensions only when the contracts support them. Patients must remain provider-scoped unless a cross-provider identity contract is approved.

## Ready-To-Use Entity Prompts

Each prompt is ready to copy into Codex. Do not collapse these prompts into one generic instruction: each entity has different normalization risk, HITL boundaries, and QA needs.

### Prompt 05A: Providers And Domains

```text
You are Codex executing Plan 05 dbt model layering and normal-form evolution for providers/domains.

Use docs/05_dbt_model_layering_and_normal_form_evolution_plan.md and docs/dbt_rollout.md as the active plan and rollout. Read all required contracts and agreements listed in docs/dbt_rollout.md before making changes.

Use these skills: dbt-layering-orchestrator, relational-normal-form-reviewer, local-postgres-dbt-modeling-orchestrator, spec-test-generator, qa-evidence-reviewer, privacy-governance-reviewer, and hitl-escalation-controller.

Work as a dbt model architect and relational normal-form reviewer. Start from PostgreSQL landing data and existing dbt staging outputs. Focus on provider slug, display name, source system family, timezone policy, code-system/domain mappings, provider-scoped keys, and reusable conformed dimensions.

This is a hybrid HITL workflow. Codex owns deterministic SQL probes, dbt edits, tests, lineage, and evidence. HITL owns provider meaning, provider default policy, timezone attribution, and any decision not already governed by contract. Escalate to HITL when a provider/domain issue is not easy to resolve from contracts and SQL evidence.

Produce or update only the needed dbt files, schema YAML, dbt tests, SQL pytest coverage, normalization probes under metadata/model_specs/evolution/V0_5/ when needed, and trace entries under logs/local_runtime/local_runtime_certification.md. Do not create a cross-provider patient identity or provider default without HITL approval.

Run validation with uv and parallel dbt execution using DBT_THREADS=10. Minimum gates are dbt parse, dbt run for changed selectors, staging_smoke, targeted provider/domain tests, relevant pytest tests, and ruff for touched tests. Run staging_full before PR/merge or after material key/grain/survivorship changes.

Do not reload adapters, rewrite source files, create Databricks artifacts, infer hidden business/clinical/financial meaning, silently drop rows, or weaken tests to pass.
```

### Prompt 05B: Patients

```text
You are Codex executing Plan 05 dbt model layering and normal-form evolution for patients.

Use docs/05_dbt_model_layering_and_normal_form_evolution_plan.md and docs/dbt_rollout.md as the active plan and rollout. Read all required contracts and agreements listed in docs/dbt_rollout.md before making changes.

Use these skills: dbt-layering-orchestrator, relational-normal-form-reviewer, local-postgres-dbt-modeling-orchestrator, spec-test-generator, qa-evidence-reviewer, privacy-governance-reviewer, and hitl-escalation-controller.

Work as a dbt model architect and relational normal-form reviewer. Start from landing.members and existing staging patient models. Inspect every patient column for provider scope, member identity, demographic null semantics, gender/date validity, duplicate keys, conflicting source rows, sparse unmapped fields, and PII/PHI exposure. Patients may belong to one or more providers; do not collapse provider-scoped identity into a global identity unless a cross-provider identity contract is approved.

This is a hybrid HITL workflow. Codex owns deterministic SQL probes, dbt edits, tests, lineage, and evidence. HITL owns cross-provider identity decisions, demographic survivorship preferences that affect interpretation, and privacy-sensitive handling not already governed by contract.

Produce or update only dbt files under dbt/models/derived/patients/, schema YAML, patient dbt tests, patient SQL pytest coverage, normalization probes under metadata/model_specs/evolution/V0_5/ when needed, and trace entries under logs/local_runtime/local_runtime_certification.md.

Run validation with uv and parallel dbt execution using DBT_THREADS=10. Minimum gates are dbt parse, dbt run for changed selectors, staging_smoke, targeted patient dbt tests, relevant pytest tests, and ruff for touched tests. Run staging_full before PR/merge or after material key/grain/survivorship changes.

Do not reload adapters, rewrite source files, create Databricks artifacts, infer hidden business/clinical/financial meaning, silently drop rows, or weaken tests to pass.
```

### Prompt 05C: Coverage

```text
You are Codex executing Plan 05 dbt model layering and normal-form evolution for coverage.

Use docs/05_dbt_model_layering_and_normal_form_evolution_plan.md and docs/dbt_rollout.md as the active plan and rollout. Read all required contracts and agreements listed in docs/dbt_rollout.md before making changes.

Use these skills: dbt-layering-orchestrator, relational-normal-form-reviewer, local-postgres-dbt-modeling-orchestrator, spec-test-generator, qa-evidence-reviewer, privacy-governance-reviewer, and hitl-escalation-controller.

Work as a dbt model architect and relational normal-form reviewer. Start from landing.coverage_periods and existing staging coverage models. Inspect every coverage column for provider scope, member reference, period grain, status domains, duplicate period keys, survivor candidates, open-ended boundaries, inverted dates, payer/provider semantics, and temporal ambiguity.

This is a hybrid HITL workflow. Codex owns deterministic SQL probes, dbt edits, tests, lineage, and evidence. HITL owns survivorship preferences that change business interpretation, payer/provider semantic decisions, and any coverage status meaning not already governed by contract.

Produce or update only dbt files under dbt/models/derived/coverage/, schema YAML, coverage dbt tests, coverage SQL pytest coverage, normalization probes under metadata/model_specs/evolution/V0_5/ when needed, and trace entries under logs/local_runtime/local_runtime_certification.md.

Run validation with uv and parallel dbt execution using DBT_THREADS=10. Minimum gates are dbt parse, dbt run for changed selectors, staging_smoke, targeted coverage dbt tests, relevant pytest tests, and ruff for touched tests. Run staging_full before PR/merge or after material key/grain/survivorship changes.

Do not reload adapters, rewrite source files, create Databricks artifacts, infer hidden business/clinical/financial meaning, silently drop rows, or weaken tests to pass.
```

### Prompt 05D: Encounters

```text
You are Codex executing Plan 05 dbt model layering and normal-form evolution for encounters.

Use docs/05_dbt_model_layering_and_normal_form_evolution_plan.md and docs/dbt_rollout.md as the active plan and rollout. Read all required contracts and agreements listed in docs/dbt_rollout.md before making changes.

Use these skills: dbt-layering-orchestrator, relational-normal-form-reviewer, local-postgres-dbt-modeling-orchestrator, spec-test-generator, qa-evidence-reviewer, privacy-governance-reviewer, and hitl-escalation-controller.

Work as a dbt model architect and relational normal-form reviewer. Start from landing.encounters and existing staging encounter models. Inspect every encounter column for event grain, provider/member references, encounter reference uniqueness, datetime standardization, coverage status, record status dimensions, orphan relationships, temporal ambiguity, and PII/PHI exposure.

This is a hybrid HITL workflow. Codex owns deterministic SQL probes, dbt edits, tests, lineage, and evidence. HITL owns ambiguous encounter type, clinical interpretation, unresolved timezone policy, and business-impact decisions not already governed by contract.

Produce or update only dbt files under dbt/models/derived/encounters/, schema YAML, encounter dbt tests, encounter SQL pytest coverage, normalization probes under metadata/model_specs/evolution/V0_5/ when needed, and trace entries under logs/local_runtime/local_runtime_certification.md.

Run validation with uv and parallel dbt execution using DBT_THREADS=10. Minimum gates are dbt parse, dbt run for changed selectors, staging_smoke, targeted encounter dbt tests, relevant pytest tests, and ruff for touched tests. Run staging_full before PR/merge or after material key/grain/survivorship changes.

Do not reload adapters, rewrite source files, create Databricks artifacts, infer hidden business/clinical/financial meaning, silently drop rows, or weaken tests to pass.
```

### Prompt 05E: Conditions

```text
You are Codex executing Plan 05 dbt model layering and normal-form evolution for conditions.

Use docs/05_dbt_model_layering_and_normal_form_evolution_plan.md and docs/dbt_rollout.md as the active plan and rollout. Read all required contracts and agreements listed in docs/dbt_rollout.md before making changes.

Use these skills: dbt-layering-orchestrator, relational-normal-form-reviewer, local-postgres-dbt-modeling-orchestrator, spec-test-generator, qa-evidence-reviewer, privacy-governance-reviewer, and hitl-escalation-controller.

Work as a dbt model architect and relational normal-form reviewer. Start from landing.conditions and existing staging condition models. Inspect every condition column for condition code/domain normalization, provider/member/encounter references, condition reference uniqueness, code hint conflicts, missing or mixed clinical code systems, orphan relationships, and clinical-code ambiguity.

This is a hybrid HITL workflow. Codex owns deterministic SQL probes, dbt edits, tests, lineage, and evidence. HITL owns clinical semantic mappings, code-domain interpretation, and any condition meaning not already governed by contract.

Produce or update only dbt files under dbt/models/derived/conditions/, schema YAML, condition dbt tests, condition SQL pytest coverage, normalization probes under metadata/model_specs/evolution/V0_5/ when needed, and trace entries under logs/local_runtime/local_runtime_certification.md.

Run validation with uv and parallel dbt execution using DBT_THREADS=10. Minimum gates are dbt parse, dbt run for changed selectors, staging_smoke, targeted condition dbt tests, relevant pytest tests, and ruff for touched tests. Run staging_full before PR/merge or after material key/grain/survivorship changes.

Do not reload adapters, rewrite source files, create Databricks artifacts, infer hidden business/clinical/financial meaning, silently drop rows, or weaken tests to pass.
```

### Prompt 05F: Medications

```text
You are Codex executing Plan 05 dbt model layering and normal-form evolution for medications.

Use docs/05_dbt_model_layering_and_normal_form_evolution_plan.md and docs/dbt_rollout.md as the active plan and rollout. Read all required contracts and agreements listed in docs/dbt_rollout.md before making changes.

Use these skills: dbt-layering-orchestrator, relational-normal-form-reviewer, local-postgres-dbt-modeling-orchestrator, spec-test-generator, qa-evidence-reviewer, privacy-governance-reviewer, and hitl-escalation-controller.

Work as a dbt model architect and relational normal-form reviewer. Start from landing.medications and existing staging medication models. Inspect every medication column for medication code variants, descriptions, provider/member/encounter/condition references, medication reference uniqueness, medication event datetime, code-system ambiguity, description-code conflicts, nested or mixed-grain fields, and clinical semantics.

This is a hybrid HITL workflow. Codex owns deterministic SQL probes, dbt edits, tests, lineage, and evidence. HITL owns clinical medication semantics, canonical medication grouping beyond contract, and any description/code interpretation not already governed by contract.

Produce or update only dbt files under dbt/models/derived/medications/, schema YAML, medication dbt tests, medication SQL pytest coverage, normalization probes under metadata/model_specs/evolution/V0_5/ when needed, and trace entries under logs/local_runtime/local_runtime_certification.md.

Run validation with uv and parallel dbt execution using DBT_THREADS=10. Minimum gates are dbt parse, dbt run for changed selectors, staging_smoke, targeted medication dbt tests, relevant pytest tests, and ruff for touched tests. Run staging_full before PR/merge or after material key/grain/survivorship changes.

Do not reload adapters, rewrite source files, create Databricks artifacts, infer hidden business/clinical/financial meaning, silently drop rows, or weaken tests to pass.
```

### Prompt 05G: Observations

```text
You are Codex executing Plan 05 dbt model layering and normal-form evolution for observations.

Use docs/05_dbt_model_layering_and_normal_form_evolution_plan.md and docs/dbt_rollout.md as the active plan and rollout. Read all required contracts and agreements listed in docs/dbt_rollout.md before making changes.

Use these skills: dbt-layering-orchestrator, relational-normal-form-reviewer, local-postgres-dbt-modeling-orchestrator, spec-test-generator, qa-evidence-reviewer, privacy-governance-reviewer, and hitl-escalation-controller.

Work as a dbt model architect and relational normal-form reviewer. Start from landing.observations and existing staging observation models. Inspect every observation column for nested payload decomposition, vital components, units, values, provider/member references, observation reference uniqueness, observation datetime, wide/component reconciliation, unit/code ambiguity, and clinical interpretation risk.

This is a hybrid HITL workflow. Codex owns deterministic SQL probes, dbt edits, tests, lineage, and evidence. HITL owns clinical interpretation, unit conversions not contract-backed, ambiguous nested payload semantics, and any observation meaning not already governed by contract.

Produce or update only dbt files under dbt/models/derived/observations/, schema YAML, observation dbt tests, observation SQL pytest coverage, normalization probes under metadata/model_specs/evolution/V0_5/ when needed, and trace entries under logs/local_runtime/local_runtime_certification.md.

Run validation with uv and parallel dbt execution using DBT_THREADS=10. Minimum gates are dbt parse, dbt run for changed selectors, staging_smoke, targeted observation dbt tests, relevant pytest tests, and ruff for touched tests. Run staging_full before PR/merge or after material key/grain/survivorship changes.

Do not reload adapters, rewrite source files, create Databricks artifacts, infer hidden business/clinical/financial meaning, silently drop rows, or weaken tests to pass.
```

### Prompt 05H: Cost Records

```text
You are Codex executing Plan 05 dbt model layering and normal-form evolution for cost_records.

Use docs/05_dbt_model_layering_and_normal_form_evolution_plan.md and docs/dbt_rollout.md as the active plan and rollout. Read all required contracts and agreements listed in docs/dbt_rollout.md before making changes.

Use these skills: dbt-layering-orchestrator, relational-normal-form-reviewer, local-postgres-dbt-modeling-orchestrator, spec-test-generator, qa-evidence-reviewer, privacy-governance-reviewer, and hitl-escalation-controller.

Work as a dbt model architect and relational normal-form reviewer. Start from landing.cost_records and existing staging cost-record models. Inspect every cost column for amount source fields, decimal validity, financial event dates, provider/member/encounter/medication references, cost record reference uniqueness, status dimensions, member/fact reconciliation, mixed financial grain, and financial meaning risk.

This is a hybrid HITL workflow. Codex owns deterministic SQL probes, dbt edits, tests, lineage, and evidence. HITL owns financial interpretation, amount semantics, survivorship that changes financial meaning, and any cost mapping not already governed by contract.

Produce or update only dbt files under dbt/models/derived/cost_records/, schema YAML, cost-record dbt tests, cost-record SQL pytest coverage, normalization probes under metadata/model_specs/evolution/V0_5/ when needed, and trace entries under logs/local_runtime/local_runtime_certification.md.

Run validation with uv and parallel dbt execution using DBT_THREADS=10. Minimum gates are dbt parse, dbt run for changed selectors, staging_smoke, targeted cost-record dbt tests, relevant pytest tests, and ruff for touched tests. Run staging_full before PR/merge or after material key/grain/survivorship changes.

Do not reload adapters, rewrite source files, create Databricks artifacts, infer hidden business/clinical/financial meaning, silently drop rows, or weaken tests to pass.
```

## HITL Working Loop

When HITL is needed, pause implementation and provide a compact decision packet. The human reviews SQL examples directly in PostgreSQL, chooses or revises the recommended option, and the agent records the decision in the appropriate report/contract/probe before implementation continues.

Preferred HITL cadence:

```text
probe -> summarize options -> HITL decision -> contract/probe update -> dbt change -> targeted QA -> smoke -> trace
```

This keeps decisions fluid while preserving durable model history.
