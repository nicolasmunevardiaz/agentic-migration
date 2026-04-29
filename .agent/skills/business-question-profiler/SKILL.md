---
name: business-question-profiler
description: "Profile healthcare migration business questions after provider discovery and before canonical modeling by reading business-request.md plus provider specs/reports, mapping each question to provider-specific source language, grain, evidence, minimum canonical concepts, candidate solution options, risk/impact, HITL decisions, Gold candidates, and required validation tests."
user-invocable: false
---

# Business Question Profiler

## Purpose

Use this skill after provider discovery and before canonical modeling when business
questions, analytics goals, VBC questions, payer/provider attribution, cost,
demographics, condition/medication catalogs, treatment patterns, observations, or
benchmarking needs are being used to shape canonical Bronze/Silver contracts or future
Gold outputs.

This skill prevents over-modeling and reduces HITL ambiguity. It derives minimum
canonical concepts from business need, proposes concrete solution options with
risk/impact, and avoids generating Gold analytics or silently approving identity,
clinical, financial, or privacy semantics.

## Required Inputs

Read `business-request.md`, `docs/01_2_business_question_profiling_plan.md`,
`.agent/spec_templates/business_question_profile.template.yaml`, provider specs, drift
reports, privacy reports, HITL runbooks, QA evidence, and any active PR context.
Provider specs are source evidence. Business questions are decision intent, not
implementation permission.

Read each provider in its source language before abstracting:

- Aegis Care Network: FHIR R4 clinical resources.
- BlueStone Health: HL7 v2-style XML messages.
- NorthCare Clinics: X12-like segment envelopes.
- ValleyBridge Medical: FHIR STU3 resources with provider file quirks.
- Pacific Shield Insurance: CSV claims export with payer/claims semantics.

## Required Outputs

Produce or update:

- `metadata/model_specs/impact/business_question_profiles.yaml`
- HITL updates in `reports/hitl/canonical_drift_decision_runbook.md` when a question
  requires semantic, identity, privacy, clinical, or financial approval
- concise trace entries in `logs/canonical_model/canonical_review.md` during canonical
  review

## Profile Shape

The output YAML must contain both `business_question_profiles` and `field_decisions`.
Question-level profiles explain why the business needs a concept. Field-level decisions
explain how a specific provider/entity/field may safely enter Bronze, Silver, deferred
Gold, or remain blocked.

Each business question profile must include:

- question id
- business question
- decision supported
- intended audience
- risk level: `low`, `medium`, `high`, or `hitl_blocked`
- grain
- required provider groups: provider, payer, or both
- provider-specific language and evidence summary
- required source entities and fields
- minimum canonical concepts
- candidate solution options with `option`, `risk`, `impact`, `required_approval`, and
  `recommendation`
- downstream Gold candidate, if any
- PII/PHI fields and access expectations
- semantic risks
- HITL decisions required
- data quality checks
- required tests
- evidence paths
- allowed next action

Each field decision must include:

- stable decision id
- provider slug and provider display name
- provider source standard or dialect
- source entity and source field/header/path
- provider-language meaning
- evidence paths
- business question dependencies
- required or optional usage
- minimum canonical concept
- candidate Bronze handling
- candidate Silver handling
- candidate Gold usage, explicitly deferred
- `pii_signal`, PHI notes, and access expectation
- drift or blocker category
- option set with `option_id`, `description`, `risk`, `impact`, `required_approval`,
  `tests_required`, `rollback_notes`, and `recommendation`
- HITL decision request with closed response choices
- selected option or `pending_human_decision`
- Plan 02 allowance: `allowed`, `allowed_bronze_only`, or `blocked`

## HITL Decision Request Shape

For any medium, high, or HITL-blocked field decision, provide a standardized HITL input:

- `decision_id`
- `question_for_human`
- `recommended_option_id`
- `allowed_responses`: `approve_recommended_option`, `approve_alternative_option`,
  `defer_with_human_approval`, `reject_all_options`, `request_more_evidence`
- `plan_02_consequence_by_response`
- `minimum_evidence_reviewed`
- `human_response`, initialized as `pending_human_decision` unless approval already
  exists in the runbook

Never ask HITL to answer an open-ended semantic question without concrete options,
risk, impact, and Plan 02 consequences.

## Minimum Canonical Concepts

Use these concepts before proposing tables:

- `member_reference`
- `coverage_period`
- `encounter_event`
- `condition_record`
- `medication_record`
- `observation_record_raw`
- `cost_record`
- `source_lineage`

Do not create final Gold tables from this skill. Gold candidates may be named only as
future outputs. Prefer minimum concepts over final table names.

## PII/PHI Rule

Treat `pii_signal: true` as sensitive across all providers. In development, do not
perform irreversible masking or destructive redaction of source-preserved Bronze
evidence. Instead, require controlled access, synthetic fixtures, no raw values in
reports/logs, sensitive field flags in contracts, and role-based masking/tokenization or
policy views before end-user exposure.

## Checks

Confirm the question maps to real provider evidence. Confirm the grain is explicit.
Separate source row keys from business identity. Separate provider clinical facts from
payer claims facts. Identify any need for identity resolution, code crosswalks, coverage
gap logic, cost interpretation, observation parsing, or treatment association rules.
For each business-critical source field, create a provider/entity/field decision record
that maps source meaning to business dependency, minimum canonical concept, option set,
HITL state, and Plan 02 allowance. For each medium, high, or HITL-blocked question or
field, propose at least two concrete options, such as source-preserved only, normalized
with explicit HITL approval, defer to Gold, or require additional evidence. Mark
unresolved semantic options as HITL-blocked unless approval already exists.

## Non-Negotiables

Do not infer enterprise identity, clinical truth, payer attribution, TCOC, therapeutic
association, diagnosis/medication catalog equivalence, or financial benchmark semantics
without HITL approval. Do not expose raw PII/PHI in reports, logs, fixtures, or PR
evidence. Do not denormalize source exports into Gold outputs during Bronze/Silver
planning. Do not allow a field into Silver as a normalized semantic column unless its
field-level decision is approved or explicitly deferred with human approval and Plan 02
allowance.

## QA Expectations

Profiles should later be protected by schema tests, field-decision schema tests, HITL
decision request schema tests, mapping completeness tests from question to provider to
entity to field to candidate canonical concept, provider/entity reconciliation tests,
option risk/impact checks, selected-option consistency checks, invalid date checks,
duplicate identity checks, coverage gap checks, unmatched provider/payer member checks,
unmapped code checks, and PII/PHI redaction checks.

## Output Format

Return a concise report with business questions profiled, provider language reviewed,
risk classification summary, field decisions created, canonical concepts derived,
candidate options and recommendations, Gold candidates deferred, HITL blockers, evidence
paths, test requirements, and recommended next action.
