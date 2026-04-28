# Adapter Implementation And CI Plan

## Goal

Review adapter contracts, generate parser/adapter implementation artifacts, create fixtures, and establish CI-ready Python tests for Raw/Bronze to Silver behavior. This plan turns approved declarative contracts into runtime-neutral local implementation work that can be reviewed before local runtime certification and Databricks execution.

This plan covers adapter implementation and development CI only. It must not create production jobs, run full-volume data, create cloud resources, install local runtime dependencies, define Gold models, certify Databricks compatibility, or bypass Human in the Loop approvals.

## Required Skills

Use `adapter-contract-reviewer` to confirm readiness before generation. Use `adapter-code-generator` to generate parser/adapter code, fixtures, and local tests after approval. Use `spec-test-generator` to create spec and adapter validation tests. Use `qa-evidence-reviewer` to confirm evidence shape. Use `privacy-governance-reviewer` to review PII/PHI handling, fixtures, secrets, dependency gates, and permission-sensitive behavior.

## Definition Of Ready

Provider specs, Bronze contract, Silver entity specs, provider-to-Silver mapping matrix, modeling risk report, and required HITL approvals exist. Any unresolved mapping, parser, PII, or quarantine decision is either approved, blocked, or explicitly deferred.

## Inputs

Read provider specs, canonical model specs, mapping matrix, adapter readiness findings, spec templates, QA evidence expectations, privacy review findings, and available source fixtures. The adapter must consume specs as configuration and must not encode provider-specific assumptions directly in logic.

## Filesystem Contract

Follow `docs/agentops_filesystem_conventions.md`. Do not create private agent folders or alternative output roots. Adapter code must land under `src/adapters/`, shared functions under `src/common/`, orchestration handlers under `src/handlers/`, adapter tests under `tests/adapters/`, fixtures under `tests/fixtures/`, spec tests under `tests/specs/`, QA reports under `reports/qa/`, privacy findings under `reports/privacy/`, and temporary runtime outputs under `artifacts/`.

## Trace Logging

Append concise technical entries to `logs/adapter_implementation/<provider_slug>.md` for provider-specific adapter work. Use one provider per implementation iteration unless a human explicitly approves a shared utility change. Logs are append-only: do not purge, delete, reorder, or rewrite entries. Keep each note under one sentence and link to code, tests, reports, or fixtures.

## Expected Outputs

Create parser and adapter implementation artifacts, local fixtures, implementation tests, an adapter generation report, and a CI validation plan. Generated code must preserve source evidence in Bronze, produce Silver according to approved model specs, write quarantine outputs for invalid files or rows, and emit QA evidence hooks. The implementation must keep provider, entity, source file, checksum, source row reference, ingestion run, schema version, spec version, and adapter version traceable. Adapter code must target runtime-neutral interfaces so plan 04 can certify local runtime behavior before plan 05 prepares Databricks rollout.

## Python And Implementation Standards

Python must be English-only, idiomatic, and executed through `uv`. Use `uv run pytest`, `uv run ruff check`, and `uv run python -m <module>`; do not use direct `python3`. Function names must self-document behavior. One-line docstrings are allowed only when they clarify intent. Common logic for spec loading, parsing, normalization, casting, quarantine decisions, evidence writing, runtime interface boundaries, and error reporting must live in utilities instead of being copied across adapters. Use handlers to separate orchestration, parsing, mapping, validation, quarantine, evidence writing, and reporting. Avoid classes unless they represent clear domain values; when needed, use `@dataclass`.

## QA Gates

Adapter work must be protected by unit data tests, integration tests, schema tests, fixture regression tests, runtime-neutral interface tests, and security checks. Positive fixtures must prove accepted files parse and map correctly. Negative fixtures must prove malformed files, missing required fields, unsafe casts, schema drift, and PII exposure are stopped, warned, or quarantined according to approved decisions. Tests must be deterministic and runnable without Databricks. Databricks readiness tests belong to plan 05 and local runtime certification belongs to plan 04.

Expected local commands are `uv run pytest tests/specs`, `uv run pytest tests/adapters`, `uv run pytest tests/fixtures`, `uv run ruff check`, and `uv run python -m <approved_validation_module>` once such a module exists.

## GitHub Workflow Expectations

Development workflows should use simple self-descriptive names such as `Adapter Unit Tests`, `Spec Validation`, and `Security Checks`. Workflows should install dependencies through `uv`, run adapter fixture tests, run spec validators, run linting, and publish PR evidence. OpenAI-powered PR summaries or agent reviews must use `OPENAI_API_KEY` from GitHub secrets only. Secrets, raw PII, local paths, and generated sensitive examples must never be printed in workflow logs.

## HITL Decisions

Human review is required before adapter code is generated from any uncertain mapping, ambiguous type, PII/PHI field, quarantine rule, source coverage exception, identifier normalization, or semantic transformation. PR evidence must explain changed providers/entities, impacted specs, generated tests, risks, and expected Databricks validation.

## Definition Of Done

The plan is done when adapter contracts are reviewed, generated implementation artifacts are traceable to approved specs, local tests exist and pass, CI expectations are documented, privacy review blockers are resolved or assigned, and the PR package is ready for human review. Local runtime certification remains blocked until plan 04. Databricks execution remains blocked until plan 05 and explicit HITL approval.
