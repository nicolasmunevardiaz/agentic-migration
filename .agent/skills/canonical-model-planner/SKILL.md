---
name: canonical-model-planner
description: "Create canonical Bronze/Silver model specs from provider/entity YAML specs, including provider-to-Silver mappings, impact analysis, and human-review decisions."
user-invocable: false
---

# Canonical Model Planner

## Purpose

Use this skill after `provider-spec-generator` has produced provider/entity YAML specs. This is a planner skill: it designs the canonical Bronze/Silver model from source evidence and records modeling risks before any adapter code or deployment job is generated.

## Operating Focus

Work as a generalist canonical reviewer. Read all approved provider specs together to identify shared canonical concepts, coverage gaps, drift, type conflicts, and modeling risks. Do not perform provider discovery or adapter implementation inside this skill.

## Required Inputs

Read `metadata/provider_specs/<provider_slug>/<entity>.yaml`, the topology PRD, governance requirements, and existing model templates. Provider specs are source contracts. Treat them as evidence, not as the final model.

## Required Outputs

Produce `metadata/model_specs/bronze/bronze_contract.yaml`, one `metadata/model_specs/silver/<entity>.yaml` per approved Silver entity, `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`, `metadata/model_specs/impact/modeling_risk_report.md`, and append trace entries to `logs/canonical_model/canonical_review.md`.

## Checks

Group source fields by canonical concept. Validate provider coverage for each Silver entity. Identify safe types, unsafe casts, required fields, optional fields, lineage columns, PII handling, key candidates, relationship confidence, quarantine criteria, and QA expectations. Detect drift, missing providers, duplicate mappings, conflicting types, payer-only limitations, and fields that require Human in the Loop.

## Non-Negotiables

Do not let one provider's source dialect define the canonical model by accident. Do not generate Databricks rollout specs. Do not resolve identity across providers automatically. Do not approve clinical or financial semantics without human review. Do not purge, delete, reorder, or rewrite trace logs.

## Trace Logging

Append short entries to `logs/canonical_model/canonical_review.md` using the shared format from `docs/agentops_filesystem_conventions.md`. Use `provider=all` for cross-provider modeling events and a specific provider slug only for provider-specific drift or blockers. If a log entry is wrong, append a correction entry.

## DoD

The skill is done when every approved Silver entity has a declarative model spec, every model column traces back to provider spec fields or approved lineage metadata, every required field has a quarantine behavior, every risky decision has a human-review reason, the provider-to-Silver matrix explains coverage and gaps, and the canonical trace log has a completed or blocked entry.

## Output Format

Return a concise report with generated model spec paths, trace log path, entity readiness, provider coverage, modeling risks, blocked fields/entities, human decisions required, and recommended next action.
