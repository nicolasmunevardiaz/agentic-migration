# Provider Discovery And Specs Plan

## Goal

Generate reliable provider/entity YAML specs from the current provider exports and their `column_dictionary.md` files. This plan turns source evidence into versioned source contracts that downstream canonical modeling, adapter generation, QA, and Databricks rollout can consume.

This plan covers Raw/Bronze source understanding only. It must not create Silver semantics, Gold models, dashboards, KPIs, production jobs, or cloud resources.

## Operating Focus

Run this plan as a provider specialist. The agent must work on exactly one provider at a time and must not switch providers within the same iteration. Finish or explicitly block the current provider before starting another provider. Do not perform canonical cross-provider review in this plan beyond recording drift evidence that will be reviewed later.

## Required Skills

Use `provider-spec-generator` as the primary generation skill. Use `privacy-governance-reviewer` to classify PII/PHI and review evidence redaction. Use `spec-test-generator` to define the Python tests that protect generated provider specs.

## Definition Of Ready

The Technical PRD and AgentOps skill strategy are available. Provider folders exist under `data_500k/`. Each provider has a readable `column_dictionary.md` or a documented blocker. The expected spec shape is available in `.agent/spec_templates/provider_entity_profile.template.yaml`.

## Inputs

Read `data_500k/**/column_dictionary.md`, raw file paths, provider folder names, the Technical PRD, the skill strategy, and the provider entity profile template. Treat dictionaries and file structure as evidence, not final model design.

## Filesystem Contract

Follow `docs/agentops_filesystem_conventions.md`. Do not create private agent folders or alternative output roots. Provider specs must land under `metadata/provider_specs/`, drift evidence under `reports/drift/`, HITL decisions under `reports/hitl/`, privacy findings under `reports/privacy/`, spec tests under `tests/specs/`, and reusable Python helpers under `src/common/` or `src/handlers/`.

## Trace Logging

Append concise technical entries to `logs/provider_discovery/<provider_slug>.md` for the provider being profiled. Each entry must include timestamp, plan id, provider slug, skill name, event, artifact path, and a short note. Logs are append-only: do not purge, delete, reorder, or rewrite entries. Keep each note under one sentence and link to artifacts instead of copying findings into the log.

## Expected Outputs

Create one provider/entity spec per discovered entity under `metadata/provider_specs/<provider_slug>/<entity>.yaml`. Create a provider drift summary, a Human in the Loop queue, and a provider-spec validation test plan. Each spec must include provider identity, source type, upload partition, filetype, extension, entity, expected file patterns, parser profile, source row key, canonical row key hint, field mappings, relationship hints, PII signals, known drift, quarantine expectations, QA expectations, and review reasons.

## Python And Implementation Standards

Any generated Python must be English-only, idiomatic, and executed through `uv`. Use `uv run pytest`, `uv run ruff check`, and `uv run python -m <module>`; do not use direct `python3`. Function names must describe behavior clearly. Use one-line docstrings only when they add useful intent. Keep shared parsing, YAML loading, path handling, and report writing in common utilities. Use handlers to separate orchestration from parsing, validation, file IO, and report generation. Avoid classes unless they clarify the domain; when classes are needed, use `@dataclass`.

## QA Gates

Provider specs must be protected by schema tests, unit data tests, regression tests, and data quality tests. Tests should validate YAML parseability, required keys, provider/entity coverage, row-key presence, allowed parser families, file extensions, source header coverage, PII flags, no raw PII examples, no local absolute paths, and stable generated shape. Tests must be deterministic, fixture-based, and runnable without Databricks.

Expected local commands are `uv run pytest tests/specs/test_provider_specs.py`, `uv run pytest tests/specs/test_provider_spec_snapshots.py`, and `uv run ruff check`.

## GitHub Workflow Expectations

The development workflow should use a simple self-descriptive name such as `Spec Validation`. It should install dependencies through `uv`, run provider spec tests, run formatting and lint checks, and publish a PR-ready validation summary. If OpenAI-powered steps are used later, the workflow must reference `OPENAI_API_KEY` from repository or environment secrets and must never print or persist the secret.

## HITL Decisions

Human review is required for source coverage gaps, ambiguous source headers, uncertain parser profiles, PII/PHI classification, identifiers with leading zeros, relationship hints, and fields that appear to carry clinical or financial meaning. The HITL record must include owner, decision, date, evidence path, provider, entity, and next action.

## Definition Of Done

The plan is done for a provider when that provider's discovered entities have YAML specs or documented blockers, generated specs are covered by Python validation, drift and privacy findings are visible, unresolved decisions are routed to Human in the Loop, and the provider trace log has a completed or blocked entry. No Databricks execution is authorized by this plan.
