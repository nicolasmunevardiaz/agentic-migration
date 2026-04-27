# Aegis Care Network Privacy And Dependency Review

Provider: `data_provider_1_aegis_care_network`
Plan: `01_provider_discovery_and_specs_plan`

## Privacy Status

Status: `human_review_required`

- Direct PII fields are flagged in specs: member id, first name, last name, SSN, birth date, and patient references.
- PHI-bearing clinical fields are flagged in specs: encounters, conditions, medications, observations, clinical dates, medication details, vitals payload, and coverage status.
- Reports and specs intentionally avoid copying raw source values.
- Parser fixtures use synthetic placeholder values only and do not copy raw source rows.
- Evidence uses relative paths only.

## Dependency Review

Status: `allowed_with_review_record`

- Added package: `PyYAML`
- Purpose: parse and validate declarative YAML specs in local tests and GitHub CI.
- Source: standard Python package resolved by `uv`.
- Lockfile: `uv.lock` updated.
- Risk notes: no runtime healthcare data processing is introduced by this dependency; it is used for local spec validation.

## Parser Review

- Specialized parser: `src/adapters/aegis_care_network.py`
- The parser consumes Aegis provider specs and FHIR bundle JSON inputs.
- The parser preserves source values in memory for adapter tests but does not log, print, or commit raw source data.
- Parser tests use synthetic fixtures under `tests/fixtures/aegis/`.

## Required Human Approvals

- Confirm masking/redaction policy for direct identifiers before downstream exposure.
- Confirm PHI classification for clinical fields and coverage status.
- Confirm `REC_STS` normalization rules per entity before adapter implementation.
- Confirm relationship confidence for patient, encounter, condition, medication, and observation references.

## Blockers

- No blocker for provider spec PR creation.
- Adapter readiness remains blocked pending HITL decisions above.
