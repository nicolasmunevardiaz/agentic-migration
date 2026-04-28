# ValleyBridge Medical Drift Summary

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_4_valleybridge_medical`
status: generated

## How To Read This

This report explains differences between the ValleyBridge source dictionary and the files the parser must actually read. "Drift" does not automatically mean a failure. It means the provider's real source shape differs from a generic expectation and must be documented.

Local validation passing means the YAML specs, parser, fixtures, and tests are internally consistent. It does not mean every mapping, PII/PHI decision, or downstream adapter decision is approved.

## Reader Glossary

- Commented FHIR JSON: JSON source files that begin with a metadata comment line before the FHIR Bundle.
- Encoding fallback: deterministic decoding through declared encodings when UTF-8 cannot decode a source file.
- Executable parser profile: the named parser mode that is implemented in code and referenced by the YAML specs.
- FHIR STU3: the FHIR version family declared by ValleyBridge source metadata.
- HITL: Human in the Loop. A human must confirm the decision before the agent treats it as approved.
- Parser contract: the source shape the parser is expected to support.
- Row key: the source field used to identify a row or source record.

## Findings

- Row-key drift: ValleyBridge uses `DW_LOAD_SEQ` as the source row key while other providers use different headers.
- Filetype drift: the dictionary describes CSV row grain, but raw files use commented FHIR STU3 Bundle JSON.
- Parser profile: ValleyBridge requires comment-stripping FHIR Bundle parsing with one repeated resource type per entity.
- Encoding drift: at least patient source files require a deterministic non-UTF-8 fallback such as `cp1252`.
- Observation drift: `PL_DATA` is preserved as source text and must not be semantically interpreted during provider discovery.

## Entity Resources

| Entity | Resource type | Source row key |
| --- | --- | --- |
| patients | `Patient` | `DW_LOAD_SEQ` |
| encounters | `Encounter` | `DW_LOAD_SEQ` |
| conditions | `Condition` | `DW_LOAD_SEQ` |
| medications | `MedicationOrder` | `DW_LOAD_SEQ` |
| observations | `Observation` | `DW_LOAD_SEQ` |

## Decision

Use `fhir_stu3_bundle_with_comments` as the executable provider parser profile. In plain language, this means ValleyBridge `.json` files should be parsed as FHIR STU3 Bundle JSON after removing metadata comment lines and decoding with declared fallback encodings. Treat the CSV wording as documented non-blocking drift because `filetype: fhir_stu3` and local raw files agree on the executable parser profile.

## What Passed And What Still Needs Review

- Passed locally: the ValleyBridge parser and specs agree on the `fhir_stu3_bundle_with_comments` profile, fixtures exist for each entity, and parser/spec tests validate the contract.
- Still needs human review before broader adapter readiness: final mapping confidence, PII/PHI handling, status normalization, relationship hints, medication price handling, and any downstream interpretation of `PL_DATA`.
