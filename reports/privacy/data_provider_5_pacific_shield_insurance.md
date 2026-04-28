# Pacific Shield Insurance Privacy And Governance Review

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_5_pacific_shield_insurance`
status: `allowed_with_review_record`

## Review Summary

The generated provider specs flag direct identifiers, dates, clinical codes, coverage status, medication information, financial amounts, and observation payloads as PII/PHI or sensitive healthcare signals. Fixtures are synthetic and do not copy raw source values.

## Sensitive Fields

- Direct identifiers: `MEMBER_ID`, `MBR_FIRST_NAME`, `MBR_LAST_NAME`, `MBR_SSN`.
- Demographics and dates: `MBR_SEX`, `MBR_DOB`, `ELIG_START_DT`, `ELIG_END_DT`, `SVC_DT`, `FILL_DT`.
- Clinical and relationship fields: `ENCOUNTER_ID`, `DX_LINE_ID`, `DX_CD`, `DX_DESC`, `DRUG_CD`, `DRUG_NM`, `OBS_CLM_ID`, `VITALS_JSON`.
- Coverage and financial fields: `COVERAGE_STATUS`, `PAID_AMT`.

## Dependency Risk

No new dependencies are introduced. Existing `pyyaml`, `pytest`, and `ruff` are sufficient for the generated specs, parser, and validation tests.

## Evidence Issues

- Source-type classification is intentionally neutral as `claims_export` and needs later human review before canonical modeling.
- Sparse local clinical source coverage is documented in drift and HITL evidence.
- Duplicate `DX_CD` mapping is preserved by source position and needs downstream semantic review.

## Required Approvals

- Human review of PII/PHI classification before Silver modeling.
- Human review of duplicate-header modeling impact.
- Human review of relationship confidence and coverage status semantics.
- Human approval before any Databricks execution.

## Recommended Next Action

Proceed with local PR review after tests pass and repo governance allows PR creation. Do not promote the source-type label or PHI decisions into canonical semantics without HITL approval.
