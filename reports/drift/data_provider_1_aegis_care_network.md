# Aegis Care Network Drift Summary

Provider: `data_provider_1_aegis_care_network`
Plan: `01_provider_discovery_and_specs_plan`

## Source Evidence

- Provider dictionary declares `filetype: fhir_r4`, `file_extension: json`, and stable row key `SRC_ROW`.
- Local source layout contains five clinical entities: `patients`, `encounters`, `conditions`, `medications`, and `observations`.
- Each entity has ten `*.json` files under `data_500k/data_provider_1_aegis_care_network/year=2025/<entity>/`.
- Sampled files are FHIR-style JSON bundles with `entry[].resource`.
- Sampled resources use flattened FHIR path-like keys such as `identifier[0].value`; the specialized parser supports flat keys and nested fallback traversal.

## Drift Findings

- The dictionary describes logical export headers, while files expose nested FHIR resource paths.
- `SRC_ROW` is represented in specs as the logical row key and extracted from FHIR `id`.
- `REC_STS` is entity-specific in the bundle: `active`, `status`, or `clinicalStatus.coding[0].code`.
- Clinical relationship fields are represented by FHIR references and require reconciliation before adapter readiness.
- `OBS_PAYLOAD` is a vitals JSON string in `valueString`; parser tests preserve it as source text without interpreting vitals.

## Impact

- Specs are not adapter-ready until HITL confirms status normalization, PII handling, and relationship confidence.
- A specialized parser now exists for Aegis provider discovery validation.
- No canonical Silver semantics were inferred in this provider discovery pass.
