---
name: drift-decision-resolver
description: "Resolve provider drift before canonical modeling by reading all reports globally, preparing HITL-ready business/governance decisions, recording final decisions in the canonical drift decision runbook, and verifying that approved decisions are applied to specs, reports, tests, and logs before plan 02 continues."
user-invocable: false
---

# Drift Decision Resolver

## Purpose

Use this skill at the start of canonical modeling and whenever provider drift, privacy findings, QA evidence, or HITL queues must be resolved across providers before Bronze/Silver contracts are created. This is a global decision-resolution skill: it turns scattered drift findings into an auditable decision runbook and verifies that approved decisions have been applied.

This skill may recommend decisions and prepare implementation edits, but it must not silently approve business meaning, PII/PHI classification, relationship confidence, identity assumptions, quarantine behavior, or clinical/financial semantics. Decisions that change meaning or governance posture require Human in the Loop.

## Required Inputs

Read all available provider evidence together:

- `reports/drift/*.md`
- `reports/privacy/*.md`
- `reports/hitl/*.md`
- `reports/qa/*.md`
- `metadata/provider_specs/**`
- `docs/technical_prd_agentops_operating_spec.md`
- `docs/02_canonical_model_and_contracts_plan.md`
- `logs/provider_discovery/*.md`

Treat provider specs as source contracts and reports as evidence. Do not let one provider's dialect become the canonical rule unless the runbook records that decision with owner, date, evidence, and rationale.

## Required Output

Maintain `reports/hitl/canonical_drift_decision_runbook.md` as the cross-provider decision register for plan 02 readiness. Each decision must include:

- decision id
- status: `pending_human_decision`, `approved`, `rejected`, `deferred_with_human_approval`, or `applied`
- decision owner
- decision date
- providers/entities impacted
- source evidence paths
- final decision
- implementation notes
- files updated
- validation evidence
- whether the item blocks canonical modeling

## Workflow

1. Inventory all drift, privacy, QA, and HITL findings across providers.
2. Group related findings into global decision topics such as row keys, status normalization, relationship confidence, PII/PHI handling, payload preservation, code semantics, financial fields, and parser-contract drift.
3. For each topic, write or update a runbook entry with evidence paths and a recommended option.
4. If the decision changes semantics, PII/PHI handling, relationship confidence, quarantine behavior, or adapter/model readiness, mark it `pending_human_decision` until a human explicitly decides.
5. After a human decision exists, apply the decision to the required artifacts: provider specs, drift reports, privacy reports, HITL records, model-readiness notes, tests, and trace logs.
6. Validate with `uv run pytest` and `uv run ruff check` or narrower commands when the change is scoped.
7. Mark the entry `applied` only when the runbook cites updated files and validation evidence.

## Canonical Readiness Gate

Plan 02 must not start canonical Bronze/Silver modeling while any runbook entry has `blocks_plan_02: yes` and status other than `applied`, `rejected`, or `deferred_with_human_approval`.

If unresolved drift remains, return `status: blocked` and use `hitl-escalation-controller` with a specific human question. Do not proceed by guessing.

## Non-Negotiables

Do not approve clinical meaning, financial meaning, identity resolution, PII/PHI downgrades, masking policy, relationship joins, Silver required fields, unsafe casts, or Databricks execution without explicit HITL approval.

Do not hide decisions in prose-only drift reports. Final decisions must be visible in the runbook and reflected in the artifacts they affect.

Do not start or modify canonical model specs until blocking drift decisions are resolved or explicitly deferred by a human.

## Trace Logging

Append concise entries to `logs/canonical_model/canonical_review.md` using `provider=all` for global decisions and a provider slug only for provider-specific application work. Logs are append-only.

## Output Format

Return a concise report with:

- governance status
- runbook path
- decisions added or updated
- blocking decisions
- approved decisions applied
- files changed
- validation commands and results
- allowed next action
