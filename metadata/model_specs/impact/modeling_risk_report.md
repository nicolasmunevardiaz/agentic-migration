# Canonical Modeling Risk Report

Plan: `02_canonical_model_and_contracts_plan`
Provider: `all`
Status: `approved`
Approval date: `2026-04-29`

## Readiness

Plan 02 readiness is clear. The business question profile is approved, all 205 field decisions are applied, and DRIFT-001 through DRIFT-014 are applied with `Blocks Plan 02 = no`.

## Coverage

- `members`: 5 providers mapped (data_provider_1_aegis_care_network, data_provider_2_bluestone_health, data_provider_3_northcare_clinics, data_provider_4_valleybridge_medical, data_provider_5_pacific_shield_insurance).
- `coverage_periods`: 5 providers mapped (data_provider_1_aegis_care_network, data_provider_2_bluestone_health, data_provider_3_northcare_clinics, data_provider_4_valleybridge_medical, data_provider_5_pacific_shield_insurance).
- `encounters`: 5 providers mapped (data_provider_1_aegis_care_network, data_provider_2_bluestone_health, data_provider_3_northcare_clinics, data_provider_4_valleybridge_medical, data_provider_5_pacific_shield_insurance).
- `conditions`: 5 providers mapped (data_provider_1_aegis_care_network, data_provider_2_bluestone_health, data_provider_3_northcare_clinics, data_provider_4_valleybridge_medical, data_provider_5_pacific_shield_insurance).
- `medications`: 5 providers mapped (data_provider_1_aegis_care_network, data_provider_2_bluestone_health, data_provider_3_northcare_clinics, data_provider_4_valleybridge_medical, data_provider_5_pacific_shield_insurance).
- `observations`: 5 providers mapped (data_provider_1_aegis_care_network, data_provider_2_bluestone_health, data_provider_3_northcare_clinics, data_provider_4_valleybridge_medical, data_provider_5_pacific_shield_insurance).
- `cost_records`: 5 providers mapped (data_provider_1_aegis_care_network, data_provider_2_bluestone_health, data_provider_3_northcare_clinics, data_provider_4_valleybridge_medical, data_provider_5_pacific_shield_insurance).

## Key Risks And Controls

- Source-scoped identity: member, encounter, condition, medication, and observation references remain provider-scoped; enterprise identity resolution is not performed.
- PII/PHI posture: sensitive source values are flagged in contracts and must not be emitted in reports, logs, fixtures, or PR evidence.
- Clinical semantics: condition, medication, and observation fields are modeled as source facts; diagnostic truth, therapeutic equivalence, and treatment recommendations are not inferred.
- Financial semantics: medication financial amounts are modeled as source cost facts; benchmark conclusions, contract interpretation, and TCOC calculations are not produced by these contracts.
- Pacific Shield duplicate `DX_CD`: duplicate positions are preserved with position-aware lineage and separate mappings.
- Sparse source coverage: Pacific Shield claims-backed clinical coverage is accepted with provider coverage visible in the matrix.
- Parser drift: BlueStone XML, NorthCare segment envelopes, ValleyBridge STU3 quirks, and Pacific Shield CSV claims behavior are approved by runbook decisions.

## Generated Artifacts

- `metadata/model_specs/bronze/bronze_contract.yaml`
- `metadata/model_specs/silver/members.yaml`
- `metadata/model_specs/silver/coverage_periods.yaml`
- `metadata/model_specs/silver/encounters.yaml`
- `metadata/model_specs/silver/conditions.yaml`
- `metadata/model_specs/silver/medications.yaml`
- `metadata/model_specs/silver/observations.yaml`
- `metadata/model_specs/silver/cost_records.yaml`
- `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`
- `metadata/model_specs/impact/modeling_risk_report.md`

## Validation Evidence

- Passed: `uv run pytest tests/specs/test_model_specs.py tests/specs/test_provider_to_silver_matrix.py tests/specs/test_spec_chain_system.py`
- Passed: `uv run pytest`
- Passed: `uv run ruff check`

## Out Of Scope

No adapter implementation, Databricks rollout, post-Silver analytics outputs, metric definitions, enterprise identity resolution, clinical interpretation, or financial benchmark conclusions are introduced by this plan.
