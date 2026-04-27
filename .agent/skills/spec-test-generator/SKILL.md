---
name: spec-test-generator
description: "Generate Python validators and tests for declarative provider, model, mapping, adapter, QA evidence, deployment, lineage, reconciliation, and scope-control specs."
user-invocable: false
---

# Spec Test Generator

Use this skill when declarative YAML or JSON specs and provider parsers need executable Python validation. This is a generator skill: it turns the PRD's test strategy into local tests that can run in GitHub CI before any Databricks execution.

Respect the active plan focus. During provider discovery and profiling, generate or update tests for the active provider/spec responsibility only unless a shared utility change is explicitly required. During canonical review, generate cross-provider tests for model contracts and mapping matrices.

Read the Technical PRD, `docs/agentops_skill_strategy.md`, `.agent/spec_templates/`, provider specs, provider parser code, parser fixtures, model specs, deployment specs, and existing test conventions. Generate or update validators under `tests/specs/`, parser tests under `tests/adapters/`, and reusable helpers only when they reduce duplication.

The minimum test suite should cover provider source specs, provider parser behavior, canonical model specs, provider-to-Silver mapping matrices, adapter specs, QA evidence specs, Databricks deployment specs, full spec-chain resolution, and business-rule scope guards. Tests should be deterministic, fixture-based, and runnable without Databricks.

Prefer descriptive test names. Validate YAML parseability, required keys, allowed values, provider/entity coverage, row-key presence, parser family, source header references, PII flags, canonical type consistency, required lineage fields, quarantine decisions, absolute-path rejection, no unapproved post-Silver targets, and cross-layer referential integrity. For provider parsers, validate positive parsing for each entity fixture, source-header to canonical mapping, row-key extraction, wrong entity/resource rejection, malformed file rejection, missing row-key behavior, no raw PII fixtures, and CI compatibility when local ignored source data is absent.

Do not write tests that depend on production data, cloud credentials, Databricks runtime, or model-graded review. Do not make tests pass by weakening the spec or parser contract. If a spec or parser contract is ambiguous, produce a clear failing test and a Human in the Loop question. Do not purge, delete, reorder, or rewrite trace logs.

Return a concise report with generated test files, parser fixture paths, validators created, parser behavior covered, coverage by declarative layer, known gaps, failing assumptions, and recommended next action.
