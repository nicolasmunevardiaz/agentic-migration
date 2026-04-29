# Canonical Drift Decision Runbook

Plan: `02_canonical_model_and_contracts_plan`
Owner: Human reviewer
Status: `not_ready_for_plan_02`

## Purpose

This runbook is the cross-provider decision register that must be reviewed before canonical Bronze/Silver modeling starts. It links drift, privacy, QA, HITL, provider specs, and final implementation changes so decisions do not remain buried in separate reports.

Plan 02 may start only after every item with `blocks_plan_02: yes` is marked `applied`, `rejected`, or `deferred_with_human_approval`.

## Status Values

- `pending_human_decision`: a human decision is still required.
- `approved`: a human has approved the decision, but implementation updates are not complete.
- `applied`: approved decision has been reflected in specs/reports/tests/logs and validated.
- `rejected`: reviewed and explicitly rejected.
- `deferred_with_human_approval`: explicitly deferred by a human and no longer blocks plan 02.

## Decision Register

| Decision ID | Topic | Status | Blocks Plan 02 | Owner | Date | Providers / Entities | Evidence | Final Decision | Implementation Notes | Files Updated | Validation Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DRIFT-001 | Source row-key lineage maps provider row keys to `ROW_ID` only | applied | no | Codex | 2026-04-28 | All providers / all entities | `metadata/provider_specs/data_provider_1_aegis_care_network/`; `metadata/provider_specs/data_provider_2_bluestone_health/`; `metadata/provider_specs/data_provider_3_northcare_clinics/`; `metadata/provider_specs/data_provider_4_valleybridge_medical/`; `metadata/provider_specs/data_provider_5_pacific_shield_insurance/`; `reports/qa/*_provider_specs.md` | `SRC_ROW`, `LINE_ID`, `EXPORT_ID`, `DW_LOAD_SEQ`, and `CLM_SEQ` may map to canonical `ROW_ID` as source lineage identifiers only; they are not enterprise identity, patient identity, or Silver relationship keys. | Existing provider specs already declare `canonical_row_key: ROW_ID` and source row-key mappings; canonical modeling may use `ROW_ID` for lineage/reconciliation only. | `reports/hitl/canonical_drift_decision_runbook.md`; `logs/canonical_model/canonical_review.md` | `uv run pytest tests/test_repository_governance.py` passed; `uv run pytest tests/specs/test_provider_specs.py` passed; `uv run ruff check` passed. |
| DRIFT-002 | Status normalization across all provider/entity status fields | pending_human_decision | yes | TBD | TBD | All providers / all entities | `reports/drift/data_provider_1_aegis_care_network.md`; `reports/drift/data_provider_2_bluestone_health.md`; `reports/drift/data_provider_3_northcare_clinics.md`; `reports/drift/data_provider_4_valleybridge_medical.md`; `reports/drift/data_provider_5_pacific_shield_insurance.md`; `reports/hitl/data_provider_1_aegis_care_network.md`; `reports/hitl/data_provider_4_valleybridge_medical.md` | TBD | Decide whether Silver preserves raw status only, defers status semantics, or defines an approved normalized status field across provider-specific `REC_STS`, `STS_CD`, `ACT_FLAG`, `ROW_STS`, `REC_FLAG`, `MBR_STS`, `CLM_STS`, and `LINE_STS` variants. | TBD | TBD |
| DRIFT-003 | PII/PHI handling, masking/redaction expectations, and sensitive Silver exposure | approved | yes | Human reviewer | 2026-04-28 | All providers / all entities | `reports/privacy/data_provider_1_aegis_care_network.md`; `reports/privacy/data_provider_2_bluestone_health.md`; `reports/privacy/data_provider_3_northcare_clinics.md`; `reports/privacy/data_provider_4_valleybridge_medical.md`; `reports/privacy/data_provider_5_pacific_shield_insurance.md`; `reports/hitl/data_provider_1_aegis_care_network.md`; `reports/hitl/data_provider_2_bluestone_health.md`; `reports/hitl/data_provider_3_northcare_clinics.md`; `reports/hitl/data_provider_4_valleybridge_medical.md`; `reports/hitl/data_provider_5_pacific_shield_insurance.md`; `docs/01_2_business_question_profiling_plan.md` | Treat every `pii_signal: true` field as sensitive across providers; do not perform irreversible masking in development; restrict access and avoid raw values in reports/logs/fixtures; require role-based masking, tokenization, or policy views before end-user exposure. | Apply this policy to model specs, business question profiles, serving/query controls, and tests before marking applied; this approval does not authorize downstream exposure or semantic promotion. | `reports/hitl/canonical_drift_decision_runbook.md`; `docs/01_2_business_question_profiling_plan.md`; `.agent/skills/business-question-profiler/SKILL.md`; `docs/agentops_skill_strategy.md` | Pending tests for business question profiles and model specs; current provider privacy reports remain evidence. |
| DRIFT-004 | Relationship confidence for patient, encounter, condition, medication, and observation references | pending_human_decision | yes | TBD | TBD | All providers / encounters, conditions, medications, observations, patients | `metadata/provider_specs/data_provider_1_aegis_care_network/`; `metadata/provider_specs/data_provider_2_bluestone_health/`; `metadata/provider_specs/data_provider_3_northcare_clinics/`; `metadata/provider_specs/data_provider_4_valleybridge_medical/`; `metadata/provider_specs/data_provider_5_pacific_shield_insurance/`; `reports/hitl/data_provider_1_aegis_care_network.md`; `reports/hitl/data_provider_2_bluestone_health.md`; `reports/hitl/data_provider_3_northcare_clinics.md`; `reports/hitl/data_provider_4_valleybridge_medical.md`; `reports/hitl/data_provider_5_pacific_shield_insurance.md` | TBD | Decide which relationship hints can be modeled as Silver foreign-key candidates and which must remain source lineage only; do not infer enterprise identity resolution. | TBD | TBD |
| DRIFT-005 | Observation payload preservation versus clinical interpretation | pending_human_decision | yes | TBD | TBD | All providers / observations | `metadata/provider_specs/data_provider_1_aegis_care_network/observations.yaml`; `metadata/provider_specs/data_provider_2_bluestone_health/observations.yaml`; `metadata/provider_specs/data_provider_3_northcare_clinics/observations.yaml`; `metadata/provider_specs/data_provider_4_valleybridge_medical/observations.yaml`; `metadata/provider_specs/data_provider_5_pacific_shield_insurance/observations.yaml`; `reports/drift/data_provider_1_aegis_care_network.md`; `reports/drift/data_provider_2_bluestone_health.md`; `reports/drift/data_provider_3_northcare_clinics.md`; `reports/drift/data_provider_4_valleybridge_medical.md`; `reports/drift/data_provider_5_pacific_shield_insurance.md` | TBD | Decide whether `OBS_PAYLOAD`, `OBS_JSON`, `PL_DATA`, and `VITALS_JSON` remain opaque source text through Silver or receive approved structured clinical fields. | TBD | TBD |
| DRIFT-006 | BlueStone parser-contract drift for HL7 XML despite CSV wording | pending_human_decision | yes | TBD | TBD | BlueStone / all entities | `reports/drift/data_provider_2_bluestone_health.md`; `reports/hitl/data_provider_2_bluestone_health.md`; `metadata/provider_specs/data_provider_2_bluestone_health/`; `src/adapters/bluestone_health.py`; `tests/adapters/test_bluestone_health_parser.py` | TBD | Confirm `hl7_v2_xml_messages` is the approved source parser contract for canonical planning. | TBD | TBD |
| DRIFT-007 | NorthCare parser-contract drift for X12-style envelopes despite CSV wording | pending_human_decision | yes | TBD | TBD | NorthCare / all entities | `reports/drift/data_provider_3_northcare_clinics.md`; `reports/hitl/data_provider_3_northcare_clinics.md`; `metadata/provider_specs/data_provider_3_northcare_clinics/`; `src/adapters/northcare_clinics.py`; `tests/adapters/test_northcare_clinics_parser.py` | TBD | Confirm `x12_segment_envelope` is the approved source parser contract for canonical planning. | TBD | TBD |
| DRIFT-008 | ValleyBridge parser-contract drift for commented FHIR STU3 JSON despite CSV wording | pending_human_decision | yes | TBD | TBD | ValleyBridge / all entities | `reports/drift/data_provider_4_valleybridge_medical.md`; `reports/hitl/data_provider_4_valleybridge_medical.md`; `metadata/provider_specs/data_provider_4_valleybridge_medical/`; `src/adapters/valleybridge_medical.py`; `tests/adapters/test_valleybridge_medical_parser.py` | TBD | Confirm `fhir_stu3_bundle_with_comments` is the approved source parser contract, including comment stripping and deterministic encoding fallback. | TBD | TBD |
| DRIFT-009 | Pacific Shield CSV claims export parser behavior and source-type semantics | pending_human_decision | yes | TBD | TBD | Pacific Shield / all entities | `reports/drift/data_provider_5_pacific_shield_insurance.md`; `reports/hitl/data_provider_5_pacific_shield_insurance.md`; `reports/privacy/data_provider_5_pacific_shield_insurance.md`; `metadata/provider_specs/data_provider_5_pacific_shield_insurance/`; `src/adapters/pacific_shield_insurance.py`; `tests/adapters/test_pacific_shield_insurance_parser.py` | TBD | Confirm `csv_claims_export` parser behavior and decide whether neutral `claims_export` source type remains acceptable for canonical modeling or needs replacement before Silver contracts. | TBD | TBD |
| DRIFT-010 | Pacific Shield duplicate `DX_CD` modeling impact | pending_human_decision | yes | TBD | TBD | Pacific Shield / conditions | `metadata/provider_specs/data_provider_5_pacific_shield_insurance/conditions.yaml`; `reports/drift/data_provider_5_pacific_shield_insurance.md`; `reports/hitl/data_provider_5_pacific_shield_insurance.md` | TBD | Decide whether duplicate `DX_CD` positions continue as separate source mappings for `CND_ID` and `ICD_HINT`, are collapsed, or require another approved canonical shape. | TBD | TBD |
| DRIFT-011 | Pacific Shield sparse clinical source coverage | pending_human_decision | yes | TBD | TBD | Pacific Shield / encounters, conditions, medications, observations | `reports/drift/data_provider_5_pacific_shield_insurance.md`; `reports/hitl/data_provider_5_pacific_shield_insurance.md`; `reports/qa/data_provider_5_pacific_shield_insurance_provider_specs.md` | TBD | Decide whether current sparse local clinical coverage is sufficient for Plan 02 source evidence or additional provider evidence is required before canonical contracts. | TBD | TBD |
| DRIFT-012 | Coverage status semantics | pending_human_decision | yes | TBD | TBD | All providers / encounters and patients where present | `reports/privacy/data_provider_1_aegis_care_network.md`; `reports/privacy/data_provider_2_bluestone_health.md`; `reports/privacy/data_provider_3_northcare_clinics.md`; `reports/privacy/data_provider_4_valleybridge_medical.md`; `reports/privacy/data_provider_5_pacific_shield_insurance.md`; `metadata/provider_specs/**/encounters.yaml`; `metadata/provider_specs/**/patients.yaml` | TBD | Decide whether `COVERAGE_STATUS` and coverage date fields remain source-preserved PHI/financial signals or receive approved Silver semantics. | TBD | TBD |
| DRIFT-013 | Medication financial amount handling | pending_human_decision | yes | TBD | TBD | All providers / medications | `reports/privacy/data_provider_1_aegis_care_network.md`; `reports/privacy/data_provider_2_bluestone_health.md`; `reports/privacy/data_provider_3_northcare_clinics.md`; `reports/privacy/data_provider_4_valleybridge_medical.md`; `reports/privacy/data_provider_5_pacific_shield_insurance.md`; `metadata/provider_specs/**/medications.yaml` | TBD | Decide whether medication price/paid amount fields remain source-preserved sensitive financial values or receive approved Silver type, nullability, and exposure rules. | TBD | TBD |
| DRIFT-014 | Clinical code and description semantics for conditions and medications | pending_human_decision | yes | TBD | TBD | All providers / conditions and medications | `metadata/provider_specs/**/conditions.yaml`; `metadata/provider_specs/**/medications.yaml`; `reports/hitl/data_provider_1_aegis_care_network.md`; `reports/hitl/data_provider_5_pacific_shield_insurance.md`; `reports/privacy/data_provider_2_bluestone_health.md`; `reports/privacy/data_provider_3_northcare_clinics.md`; `reports/privacy/data_provider_4_valleybridge_medical.md` | TBD | Decide whether condition/medication codes and descriptions are modeled as raw source facts only or receive approved clinical canonical semantics. | TBD | TBD |

## Current HITL Escalation Packet

```yaml
status: blocked
reason: missing_human_decision
active_plan: "02_canonical_model_and_contracts_plan"
provider: "all"
artifact: "reports/hitl/canonical_drift_decision_runbook.md"
failed_attempts: 0
last_error: "Blocking runbook decisions remain pending_human_decision."
question_for_human: "Should Plan 02 defer all semantic promotions and allow only source-preserved lineage modeling, or should specific normalization/relationship/PII/clinical/financial decisions be approved now per runbook ID?"
recommended_option: "Approve deferral of semantic promotion for Plan 02 and permit only source-preserved, lineage-first Bronze/Silver contracts after the runbook is updated."
options:
  - "Approve deferral of semantic promotion for all blocking decisions and permit source-preserved lineage-first modeling."
  - "Approve specific normalization, relationship, PII/PHI, clinical, and financial decisions by runbook ID."
  - "Require additional provider evidence before Plan 02 canonical modeling continues."
evidence:
  - "reports/hitl/canonical_drift_decision_runbook.md"
  - "reports/drift/"
  - "reports/privacy/"
  - "reports/hitl/"
  - "metadata/provider_specs/"
blocked_next_action: "Do not generate Bronze/Silver model specs, mapping matrices, model tests, Databricks rollout artifacts, adapter changes, or PRs."
```

## How To Close A Decision

1. Human reviewer sets `Owner`, `Date`, and `Final Decision`.
2. Agent applies the decision to affected specs, reports, tests, and logs.
3. Agent records changed files and validation evidence.
4. Status becomes `applied` only after validation passes.
