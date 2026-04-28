# Aegis Care Network Drift Summary

Provider: `data_provider_1_aegis_care_network`
Plan: `01_provider_discovery_and_specs_plan`

## How To Read This

This report explains differences between the Aegis source files and the standard provider spec contract. "Drift" does not automatically mean a failure. It means the provider has a format, naming pattern, or data behavior that the migration must handle explicitly.

Local validation passing means the YAML specs, parser, fixtures, and tests are internally consistent. It does not mean every clinical or governance decision is approved for adapter implementation or Databricks execution.

## Reader Glossary

- Adapter-ready: safe to use as input for adapter implementation without unresolved human decisions.
- HITL: Human in the Loop. A human must confirm the decision before the agent treats it as approved.
- Parser profile: the named parsing strategy the code uses for this provider's files.
- PII/PHI handling: classification and protection of personal or protected health information.
- Relationship confidence: how sure we are that references between entities, such as patient-to-encounter, are correct.
- Row key: the source field used to identify a row or source record.
- Status normalization: deciding how provider-specific status fields map into a consistent status meaning.

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

- Specs passed local provider-discovery validation, but they are not adapter-ready until HITL confirms status normalization, PII/PHI handling, and relationship confidence.
- A specialized parser now exists for Aegis provider discovery validation.
- No canonical Silver semantics were inferred in this provider discovery pass.

## Plain-Language Decisions

- `REC_STS` appears in different places depending on the entity. A human must confirm how these statuses should be normalized before adapter work treats them as one consistent field.
- Relationship fields use FHIR references. A human must confirm that those references are reliable enough for downstream joins or lineage.
- `OBS_PAYLOAD` is preserved as source text. The parser intentionally does not interpret the vitals JSON because that would create clinical meaning outside this discovery scope.
