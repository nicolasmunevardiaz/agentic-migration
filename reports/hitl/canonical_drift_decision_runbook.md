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
| DRIFT-001 | Status normalization across Aegis and BlueStone | pending_human_decision | yes | TBD | TBD | Aegis all entities; BlueStone all entities | `reports/drift/data_provider_1_aegis_care_network.md`; `reports/drift/data_provider_2_bluestone_health.md`; `reports/hitl/data_provider_1_aegis_care_network.md` | TBD | Decide whether canonical status is deferred, source-preserved only, or normalized in Silver. | TBD | TBD |
| DRIFT-002 | PII/PHI handling for identifiers, names, birth dates, clinical payloads, coverage, and financial fields | pending_human_decision | yes | TBD | TBD | Aegis patients/medications/observations; BlueStone all entities | `reports/privacy/data_provider_1_aegis_care_network.md`; `reports/privacy/data_provider_2_bluestone_health.md`; `reports/hitl/data_provider_1_aegis_care_network.md`; `reports/hitl/data_provider_2_bluestone_health.md` | TBD | Confirm field classifications and any masking/redaction expectations before canonical contracts. | TBD | TBD |
| DRIFT-003 | Relationship confidence for patient, encounter, condition, medication, and observation links | pending_human_decision | yes | TBD | TBD | Aegis clinical references; BlueStone relationship hints | `reports/drift/data_provider_1_aegis_care_network.md`; `reports/hitl/data_provider_2_bluestone_health.md`; `metadata/provider_specs/data_provider_1_aegis_care_network/`; `metadata/provider_specs/data_provider_2_bluestone_health/` | TBD | Decide which relationships can be used for Silver joins and which remain source lineage only. | TBD | TBD |
| DRIFT-004 | Observation payload preservation versus interpretation | pending_human_decision | yes | TBD | TBD | Aegis observations; BlueStone observations | `reports/drift/data_provider_1_aegis_care_network.md`; `reports/drift/data_provider_2_bluestone_health.md`; `metadata/provider_specs/data_provider_1_aegis_care_network/observations.yaml`; `metadata/provider_specs/data_provider_2_bluestone_health/observations.yaml` | TBD | Decide whether observation payloads remain opaque source text through Silver or receive approved structured fields. | TBD | TBD |
| DRIFT-005 | Parser-contract drift for BlueStone XML despite CSV wording | pending_human_decision | yes | TBD | TBD | BlueStone all entities | `reports/drift/data_provider_2_bluestone_health.md`; `metadata/provider_specs/data_provider_2_bluestone_health/`; `src/adapters/bluestone_health.py`; `tests/adapters/test_bluestone_health_parser.py` | TBD | Confirm `hl7_v2_xml_messages` is the approved source parser contract for canonical planning. | TBD | TBD |

## How To Close A Decision

1. Human reviewer sets `Owner`, `Date`, and `Final Decision`.
2. Agent applies the decision to affected specs, reports, tests, and logs.
3. Agent records changed files and validation evidence.
4. Status becomes `applied` only after validation passes.
