# Test Fixtures

This directory contains synthetic source files used by parser and provider-spec tests. Fixtures are small, fake examples that mirror the source shape of each provider without copying real provider data or sensitive values.

Fixtures are not migration outputs and are not canonical model examples. They exist to prove that provider parsers can read the file formats declared in `metadata/provider_specs/`.

## How To Read This Directory

| Path | Provider | Format | Used by |
| --- | --- | --- | --- |
| `aegis/*.json` | Aegis Care Network | FHIR-style JSON bundles | `tests/adapters/test_aegis_care_network_parser.py` |
| `bluestone/*.xml` | BlueStone Health | HL7-style XML messages | `tests/adapters/test_bluestone_health_parser.py` |
| `northcare/*.txt` | NorthCare Clinics | X12-style segment envelopes | `tests/adapters/test_northcare_clinics_parser.py` |
| `valleybridge/*.json` | ValleyBridge Medical | Commented FHIR STU3 JSON bundles | `tests/adapters/test_valleybridge_medical_parser.py` |

## Glossary

- Fixture: a small synthetic file used by tests to exercise parser behavior.
- Synthetic value: fake data such as `member-alpha`, `line-patient-001`, or `synthetic-given`.
- Provider parser: code under `src/adapters/` that reads one provider's source shape.
- Provider spec: YAML under `metadata/provider_specs/` that declares expected files, parser profile, row key, and mappings.
- Parser profile: the named parsing strategy the spec expects the parser to support.
- Row key: the source field used to identify one source record.
- PII/PHI: personal or protected health information. Fixtures must not contain real PII/PHI.

## Provider Notes

### Aegis

Aegis fixtures are FHIR-style JSON bundles. They use flattened FHIR path-like keys such as `identifier[0].value` because the provider discovery evidence shows source fields in that shape.

Current files:

- `aegis/patients_bundle.json`
- `aegis/observations_bundle.json`

These fixtures validate that the Aegis parser can map JSON bundle resources into `values_by_header` and `values_by_canonical`, and that observation payloads are preserved as source text instead of being clinically interpreted.

### BlueStone

BlueStone fixtures are HL7-style XML message files. Each file contains a single repeated message segment for one entity, such as `ADT_A01` for patients or `ORU_R01` for observations.

Current files:

- `bluestone/patients_message.xml`
- `bluestone/encounters_message.xml`
- `bluestone/conditions_message.xml`
- `bluestone/medications_message.xml`
- `bluestone/observations_message.xml`

These fixtures validate that the BlueStone parser supports the `hl7_v2_xml_messages` parser profile, reads entity-specific message segments, rejects malformed or mismatched XML, and preserves embedded observation JSON without interpreting it.

### NorthCare

NorthCare fixtures are X12-style text envelopes with `~` segment terminators, `*` element separators, an `HDR` segment that declares source headers by position, and one entity segment per fixture.

Current files:

- `northcare/patients_message.txt`
- `northcare/encounters_message.txt`
- `northcare/conditions_message.txt`
- `northcare/medications_message.txt`
- `northcare/observations_message.txt`

These fixtures validate that the NorthCare parser supports the `x12_segment_envelope` parser profile, reads the `HDR` segment as the authoritative field order, rejects malformed or mismatched envelopes, and preserves observation payload text without interpreting it.

### ValleyBridge

ValleyBridge fixtures are FHIR STU3-style JSON bundles with a leading metadata comment line. They use flattened FHIR path-like keys because the provider source exposes resource fields in that shape.

Current files:

- `valleybridge/patients_bundle.json`
- `valleybridge/encounters_bundle.json`
- `valleybridge/conditions_bundle.json`
- `valleybridge/medications_bundle.json`
- `valleybridge/observations_bundle.json`

These fixtures validate that the ValleyBridge parser supports the `fhir_stu3_bundle_with_comments` parser profile, strips metadata comments, handles declared encoding fallbacks, rejects malformed or mismatched resources, and preserves observation payload text without interpreting it.

## Rules For Adding Fixtures

- Use fake values only. Do not copy real records, names, identifiers, addresses, tokens, or clinical notes.
- Keep fixtures small: one or two records are usually enough.
- Match the provider's actual source shape, including nesting, message segments, field names, row keys, and weird-but-important drift.
- Add or update parser tests under `tests/adapters/` when adding a fixture.
- Add or update provider specs under `metadata/provider_specs/` when a fixture represents a new parser contract.
- If a fixture demonstrates an unresolved decision, document that decision in `reports/drift/` or `reports/hitl/`.

## Expected Validation

Run:

```text
uv run pytest tests/adapters
uv run pytest tests/specs/test_provider_specs.py
uv run pytest
```
