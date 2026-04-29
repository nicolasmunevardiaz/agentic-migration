# Canonical Model And Contracts Plan

## Goal

Convert approved provider/entity specs into canonical Bronze and Silver model contracts. This plan creates the intermediate modeling layer that prevents any single provider dialect from accidentally becoming the enterprise model.

This plan covers Bronze/Silver contracts only. It must not define Gold models, KPIs, dashboards, production promotion, identity resolution across providers, or clinical interpretation without human approval.

## Operating Focus

Run this plan as a generalist canonical review. Unlike provider discovery, this plan must read all approved provider specs together to identify shared entities, source drift, coverage gaps, type conflicts, and canonical modeling risks. The agent should not jump into adapter implementation or provider-specific cleanup while reviewing the canonical model.

## Required Skills

Use `business-question-profiler` inputs from Plan `01.2` to understand business intent, provider language, minimum canonical concepts, field-level decision records, HITL requests, and candidate solution options before canonical modeling starts. Use `drift-decision-resolver` to resolve or explicitly defer blocking provider drift decisions across all reports before canonical modeling starts. Use `canonical-model-planner` as the primary modeling skill only after the business question profiles and drift decision runbook are ready. Use `privacy-governance-reviewer` to validate PII/PHI treatment and governance posture. Use `spec-test-generator` to define and generate Python validation for model specs and mapping matrices. Use `hitl-escalation-controller` if any blocking decision lacks a human owner, final decision, or approved deferral.

## Definition Of Ready

Provider specs exist under `metadata/provider_specs/<provider_slug>/<entity>.yaml` or have documented blockers. Provider drift findings and HITL decisions from discovery are available. Business question profiles exist at `metadata/model_specs/impact/business_question_profiles.yaml` or have a documented blocker from Plan `01.2`. The profile artifact must follow `.agent/spec_templates/business_question_profile.template.yaml` and include both `business_question_profiles` and `field_decisions`. Every required business-critical field must have a selected option or an approved deferral, and its Plan 02 allowance must be `allowed` or `allowed_bronze_only`; unresolved `blocked` field decisions stop this plan. The cross-provider decision runbook exists at `reports/hitl/canonical_drift_decision_runbook.md`. Every runbook item with `blocks_plan_02: yes` or `Blocks Plan 02` set to `yes` is marked `applied`, `rejected`, or `deferred_with_human_approval`, with owner, date, evidence paths, files updated, and validation evidence. The expected model template is available in `.agent/spec_templates/silver_entity_model.template.yaml`.

## Inputs

Read `business-request.md`, `metadata/model_specs/impact/business_question_profiles.yaml`, `.agent/spec_templates/business_question_profile.template.yaml`, provider specs, provider drift summaries, privacy reports, QA reports, HITL queues, the canonical drift decision runbook, the Technical PRD, the skill strategy, and model templates. Provider specs are source contracts. Business question profiles are modeling intent and risk evidence, not permission to generate Gold analytics. Field decisions are provider/entity/field-level constraints for Bronze/Silver modeling; they do not authorize identity resolution, clinical interpretation, financial interpretation, or Gold analytics unless the linked HITL decision explicitly does so. Treat all of these as evidence for canonical modeling, not as the target model.

## Filesystem Contract

Follow `docs/agentops_filesystem_conventions.md`. Do not create private agent folders or alternative output roots. The canonical drift decision runbook must live at `reports/hitl/canonical_drift_decision_runbook.md`. Bronze contracts must land under `metadata/model_specs/bronze/`, Silver contracts under `metadata/model_specs/silver/`, mapping matrices under `metadata/model_specs/mappings/`, modeling risk reports under `metadata/model_specs/impact/`, HITL decisions under `reports/hitl/`, privacy findings under `reports/privacy/`, and model validation tests under `tests/specs/`.

## Trace Logging

Append concise technical entries to `logs/canonical_model/canonical_review.md`. Use `provider=all` for cross-provider modeling events and use a specific provider slug only when the note concerns one provider's drift or blocker. Logs are append-only: do not purge, delete, reorder, or rewrite entries. Keep each note under one sentence and link to artifacts instead of copying report content into the log.

## Expected Outputs

Create `metadata/model_specs/bronze/bronze_contract.yaml`, one `metadata/model_specs/silver/<entity>.yaml` per approved Silver entity, `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`, and `metadata/model_specs/impact/modeling_risk_report.md`. The contracts must define grain, approved columns, types, nullability, lineage fields, required fields, candidate keys, provider coverage, source mappings, quarantine behavior, PII classification, modeling risks, and HITL decisions.

Before those model artifacts are created, read Plan `01.2` business question profiles and field decisions, then update `reports/hitl/canonical_drift_decision_runbook.md` with every drift decision that blocks or informs canonical modeling. If any blocking runbook decision remains unresolved, or if any required field decision is still `pending_human_decision` with Plan 02 allowance `blocked`, stop with a HITL escalation packet instead of generating canonical model specs.

## Python And Implementation Standards

Any generated Python must be English-only, idiomatic, and executed through `uv`. Use `uv run pytest`, `uv run ruff check`, and `uv run python -m <module>`; do not use direct `python3`. Function names must be self-documenting. Use one-line docstrings only for non-obvious intent. Put shared YAML loading, spec graph traversal, canonical field comparison, and validation helpers in common utilities. Use handlers to separate orchestration from validation, reconciliation, and report generation. Prefer functions and `@dataclass` value objects over stateful classes.

## QA Gates

Canonical model specs must be protected by schema tests, integration tests, data quality tests, reconciliation tests, and regression tests. Tests should validate model YAML shape, required lineage columns, provider coverage, column types, nullability, source references, safe casts, duplicate canonical mappings, missing provider support, PII flags, and explicit HITL markers for unsafe decisions. The provider-to-Silver matrix must reconcile every approved model column to approved provider evidence or approved lineage metadata.

Expected local commands are `uv run pytest tests/specs/test_model_specs.py`, `uv run pytest tests/specs/test_provider_to_silver_matrix.py`, `uv run pytest tests/specs/test_spec_chain_system.py`, and `uv run ruff check`.

## GitHub Workflow Expectations

The development workflow should use a simple self-descriptive name such as `Model Contract Validation`. It should run model spec validation, mapping matrix checks, snapshot tests for generated contracts, and scope guards that prevent unapproved post-Silver logic. If OpenAI-powered review is used later, it must read `OPENAI_API_KEY` only from GitHub secrets and must not expose prompts containing sensitive source values.

## HITL Decisions

Human review is required for Silver required fields, ambiguous types, unsafe casts, candidate keys, relationship confidence, PII/PHI classification, quarantine behavior, provider coverage gaps, and any field whose meaning is clinical or financial. Approval records must link to provider specs, business question field decisions, and modeling evidence.

The canonical drift decision runbook is the source of truth for final drift decisions entering this plan. Discovery-phase HITL queues may identify pending questions, but plan 02 must not treat them as resolved until the runbook records a final decision and implementation status.

## Definition Of Done

The plan is done when Bronze and Silver model contracts exist, each approved Silver column traces to provider evidence or approved lineage metadata, model tests pass, modeling risks are documented, unresolved semantic or governance decisions are assigned to Human in the Loop, and the canonical trace log has a completed or blocked entry. No adapter code or Databricks execution is authorized by this plan.
