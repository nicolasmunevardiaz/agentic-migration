# Business Question Profiling And Reverse Engineering Plan

## Goal

Reverse-engineer the minimum canonical model from business need after provider
discovery and before canonical Bronze/Silver modeling. This is Plan `01.2`: it consumes
the source contracts from `docs/01_provider_discovery_and_specs_plan.md` and produces
business profiling metadata that `docs/02_canonical_model_and_contracts_plan.md` must
read before modeling.

This plan prevents the team from over-modeling source exports, promoting provider-local
table names into enterprise concepts, or jumping from drift reports directly into a
canonical Silver design without understanding what the acquired provider/payer network
needs to answer.

## Inputs

Read `business-request.md`, `.agent/spec_templates/business_question_profile.template.yaml`,
all `metadata/provider_specs/**`, all `reports/drift/**`, all `reports/privacy/**`,
all `reports/hitl/**`, all `reports/qa/**`, and
`reports/hitl/canonical_drift_decision_runbook.md`.

The active business request asks for VBC-oriented analytics around member overlap,
provider/payer attribution, enrollment gaps, gender and age distribution, TCOC, condition
and medication catalogs, treatment pattern alignment, vitals, coverage status, and
unit-price benchmarking. Treat those questions as business intent and reverse-engineering
input, not as permission to generate Gold tables or approve clinical/financial semantics.

## Operating Focus

Work as a cross-provider business reverse-engineering reviewer. Read each provider in
its own language first:

- Aegis Care Network: FHIR R4 clinical resources.
- BlueStone Health: HL7 v2-style XML messages.
- NorthCare Clinics: X12-like segment envelopes.
- ValleyBridge Medical: FHIR STU3 resources with provider file quirks.
- Pacific Shield Insurance: CSV claims export with payer/claims semantics.

Then map the business request to provider evidence, minimum canonical concepts, risk,
HITL decisions, and future Gold candidates.

## Decision Mapping

Business decisions must be mapped in three places:

- `reports/hitl/canonical_drift_decision_runbook.md`: blocking semantic, privacy,
  identity, relationship, clinical, financial, and payload decisions.
- `metadata/model_specs/impact/business_question_profiles.yaml`: structured profiles
  for each business question, including grain, source dependencies, required fields,
  risks, candidate solution options, HITL status, test needs, and downstream Gold
  candidate.
- Field-level decision records inside `business_question_profiles.yaml`: provider,
  entity, source field, source meaning, candidate canonical concept, business question
  dependency, candidate options, selected or pending HITL decision, risk/impact, and
  Plan 02 allowance.
- `metadata/model_specs/impact/modeling_risk_report.md`: canonical modeling risks once
  Bronze/Silver specs are generated.

Do not hide decisions in prose-only reports, adapter code, notebooks, dashboards, or
unstructured PR comments.

## Required Skills

Use `business-question-profiler` as the primary skill. Use
`privacy-governance-reviewer` for PII/PHI and access decisions. Use
`hitl-escalation-controller` when a question requires identity resolution, clinical
interpretation, financial interpretation, payer/provider attribution, or unresolved
relationship confidence.

## Expected Outputs

Create `metadata/model_specs/impact/business_question_profiles.yaml` using
`.agent/spec_templates/business_question_profile.template.yaml` as the contract. The
artifact must have two required levels:

- `business_question_profiles`: question-level business intent, grain, evidence,
  risk, minimum canonical concepts, and deferred Gold candidates.
- `field_decisions`: provider/entity/field-level decision records that explain how
  each source field needed by the business request may enter Bronze, Silver, deferred
  Gold, or stay blocked.

Each question-level profile must include:

- business question id and text from `business-request.md`
- decision supported and intended audience
- business domain group
- risk level: `low`, `medium`, `high`, or `hitl_blocked`
- provider language and evidence paths
- grain and required provider/payer sources
- required source entities and fields
- minimum canonical concepts
- candidate solution options with risk, impact, and recommendation
- HITL decisions required
- downstream Gold candidate, explicitly deferred
- data quality checks and tests required
- allowed next action

Each field-level decision must include:

- stable decision id
- provider slug and provider display name
- provider source standard or dialect
- source entity and source field/header/path
- provider-language meaning and evidence paths
- business questions and minimum canonical concepts that depend on the field
- candidate Bronze handling and candidate Silver handling
- candidate Gold usage, explicitly deferred
- sensitivity classification, including `pii_signal` and PHI notes
- drift or blocker category
- option set with risk, impact, required approval, tests required, and recommendation
- HITL request when a decision is not safely auto-applied
- selected option or `pending_human_decision`
- Plan 02 allowance: `allowed`, `allowed_bronze_only`, or `blocked`

Append concise trace entries to `logs/canonical_model/canonical_review.md` using
`plan=01_2_business_question_profiling_plan` and `provider=all`.

## Field-Level Decision Contract

Business profiling does not approve a canonical model by itself. It creates context
engineering for Plan 02 by reducing each modeling ambiguity to a repeatable
provider/entity/field decision.

Each business-critical source field must be evaluated in this order:

1. Provider source language: what the field means inside that provider's own dialect,
   such as FHIR R4, HL7 v2-style XML, X12-like segments, FHIR STU3, or payer CSV claims.
2. Evidence: provider spec path, drift report, privacy report, parser test, QA report,
   and any HITL note that supports or challenges the meaning.
3. Business dependency: which question from `business-request.md` needs the field and
   whether the field is required, optional, or only useful for reconciliation.
4. Minimum canonical concept: the smallest Bronze/Silver concept that can preserve the
   field without over-promoting business meaning.
5. Decision options: at least two options for medium, high, or HITL-blocked fields,
   each with risk, impact, tests, and rollback notes.
6. HITL request: the precise decision a human must make, using the standardized
   `hitl_decision_request` shape in the template.
7. Plan 02 allowance: whether canonical modeling may use the field, may preserve it
   only as source lineage/source fact, or must stop until approval exists.

This matrix is intentionally more granular than the canonical drift runbook. The
runbook records cross-provider blocking decisions. The field decision matrix records
the exact provider/entity/field choices that make the runbook decision implementable.

## HITL Input Contract

HITL decisions must be presented as closed, risk-ranked options, not open-ended prose.
The reviewer should receive:

- decision id
- provider/entity/source field
- business question dependency
- source evidence and drift evidence
- recommended option
- alternatives with risk, impact, and rollback notes
- exact approval requested
- Plan 02 consequence for each option

The allowed HITL response should be one of:

- `approve_recommended_option`
- `approve_alternative_option`
- `defer_with_human_approval`
- `reject_all_options`
- `request_more_evidence`

If the response is `approve_alternative_option`, the human must name the approved
option id. If the response is `defer_with_human_approval`, the decision must specify
whether Plan 02 may proceed with Bronze-only source preservation or must remain
blocked. If the response is `request_more_evidence`, Plan 02 is blocked for that field.

## Workflow

1. Inventory questions in `business-request.md` and group them by decision purpose:
   attribution, enrollment, demographics, cost, conditions, medications, treatment
   patterns, observations, price benchmarking, and reconciliation.
2. For each question, map the provider-specific source language and evidence:
   FHIR fields, HL7 message fields, X12-like segments, CSV claims headers, drift reports,
   privacy reports, and parser QA evidence.
3. Derive minimum canonical concepts, not final analytics tables:
   `member_reference`, `coverage_period`, `encounter_event`, `condition_record`,
   `medication_record`, `observation_record_raw`, `cost_record`, and `source_lineage`.
4. Build field-level decision records for every source field required or materially
   useful for the business request. Every record must connect provider/entity/field to
   business question, canonical concept, option set, HITL status, and Plan 02 allowance.
5. Propose candidate solution options for each profile and field decision, such as:
   source-preserved only, normalized with explicit HITL approval, defer to Gold, or
   require additional source evidence.
6. Score each option with risk and impact so HITL can choose among concrete alternatives
   instead of deciding from an open-ended question.
7. Record future Gold candidates only as candidates:
   `member_overlap`, `attribution_summary`, `tcoc_by_member`, `condition_catalog`,
   `medication_catalog`, `treatment_patterns`, `vitals_summary`, and
   `unit_price_benchmark`.
8. Map every high-risk profile or field decision to the canonical drift decision
   runbook before Plan 02.
9. Generate or update tests only after the profile schema and canonical contract are
   approved.

## PII/PHI Development Policy

All provider fields with `pii_signal: true` are sensitive across providers. Development
must not perform irreversible masking or destructive redaction of source-preserved
Bronze evidence. Instead:

- Preserve raw values only in controlled source/Bronze paths.
- Avoid raw values in reports, logs, docs, and committed fixtures.
- Use synthetic fixtures for parser and spec tests.
- Mark sensitive fields in provider, business profile, and model contracts.
- Require role-based access, masking, tokenization, or policy views in serving/query
  layers before end-user exposure.
- Keep downstream exposure blocked until privacy/governance decisions are recorded.

## Minimum Canonical Concepts

| Concept | Purpose | Not allowed without HITL |
| --- | --- | --- |
| `member_reference` | Preserve source member/patient references and source-system identity context. | Enterprise identity resolution or payer attribution. |
| `coverage_period` | Represent payer/provider coverage or eligibility periods and gaps. | Benefits interpretation or continuous enrollment classification. |
| `encounter_event` | Preserve encounter, visit, appointment, service, or claim-event context. | Treating all encounter-like rows as clinically equivalent. |
| `condition_record` | Preserve diagnosis/condition source facts and code text. | Code crosswalk or confirmed diagnosis semantics. |
| `medication_record` | Preserve medication order, fill, product, or claim source facts. | Product-code unification or therapeutic equivalence. |
| `observation_record_raw` | Preserve observation/vitals payload lineage. | Parsing vitals into clinical measures. |
| `cost_record` | Preserve paid amount, billed amount, unit price, and financial context. | TCOC, benchmark, contract, or shared-savings interpretation. |
| `source_lineage` | Preserve provider, entity, file, checksum, row key, parser profile, and run metadata. | Using source row keys as business identity. |

## Test Strategy

Business profiling is protected by schema and governance tests before analytics tests.
Once the profile artifact exists, add tests for:

- schema validity for business question profiles
- schema validity for field-level decisions and HITL decision requests
- mapping completeness from question -> concept -> provider evidence
- mapping completeness from question -> provider -> entity -> field -> candidate
  canonical concept
- option risk/impact presence for HITL decisions
- selected option consistency with Plan 02 allowance
- invalid or missing dates
- duplicate or conflicting identities
- coverage gaps and multiple periods
- unmatched provider/payer members
- unmapped diagnosis and medication codes
- reconciliation counts by provider/entity
- PII/PHI flags and no raw sensitive examples in reports/logs/fixtures

## PR Evidence Expectations

Any PR for this plan must include:

- source business request path
- provider specs and reports reviewed
- profiles created or updated
- candidate solution options and risk/impact summary
- HITL decisions reduced, clarified, or newly required
- downstream Plan 02 impact
- tests run
- explicit statement that no Gold tables, metrics, dashboards, identity resolution,
  clinical interpretation, financial interpretation, or Databricks execution were
  generated.

## Out Of Scope

This plan does not generate Gold tables, dashboards, VBC metrics, identity resolution,
clinical interpretation, therapeutic adherence logic, formulary compliance, TCOC
analytics, or unit-price benchmarking. Those are downstream outputs after HITL approval,
canonical model validation, and governed serving controls.

## Definition Of Done

The plan is done when every business question has a structured profile, each profile
maps to minimum canonical concepts and provider evidence, every business-critical
source field has a provider/entity/field decision record, HITL-blocked decisions are
visible in the runbook, PII/PHI handling is explicit, candidate solution options are
ranked by risk/impact, and Plan 02 can proceed without guessing business intent or
silently promoting provider-local semantics.
