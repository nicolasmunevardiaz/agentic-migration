# NorthCare Clinics Drift Summary

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_3_northcare_clinics`
status: generated

## How To Read This

This report explains differences between the NorthCare source dictionary and the files the parser must actually read. "Drift" does not automatically mean a failure. It means the provider's real source shape differs from a generic expectation and must be documented.

Local validation passing means the YAML specs, parser, fixtures, and tests are internally consistent. It does not mean every mapping, PII/PHI decision, or downstream adapter decision is approved.

## Reader Glossary

- Executable parser profile: the named parser mode that is implemented in code and referenced by the YAML specs.
- HDR segment: the NorthCare segment that declares source headers in positional order.
- HITL: Human in the Loop. A human must confirm the decision before the agent treats it as approved.
- Parser contract: the source shape the parser is expected to support.
- Row key: the source field used to identify a row or source record.
- X12-style envelope: text files with segment terminators and element separators, similar to X12 control files.

## Findings

- Row-key drift: NorthCare uses `EXPORT_ID` as the source row key while other providers use different headers.
- Filetype drift: the dictionary describes CSV row grain, but raw files use X12-style segment envelopes with `HDR` field mapping.
- Parser profile: NorthCare requires segment parsing with `~` terminators, `*` separators, and one repeated entity segment per file.
- Header drift: `encounters` includes unprefixed `COVERAGE_STATUS`, so the parser must trust `HDR` order instead of segment labels only.
- Observation drift: `OBS_PAYLOAD` is preserved as source text and must not be semantically interpreted during provider discovery.

## Entity Segments

| Entity | Segment | Source row key |
| --- | --- | --- |
| patients | `DMG` | `EXPORT_ID` |
| encounters | `CLM` | `EXPORT_ID` |
| conditions | `HI` | `EXPORT_ID` |
| medications | `SV1` | `EXPORT_ID` |
| observations | `REF` | `EXPORT_ID` |

## Decision

Use `x12_segment_envelope` as the executable provider parser profile. In plain language, this means NorthCare `.txt` files should be parsed as X12-style segment envelopes, not as plain CSV files. Treat the CSV wording as documented non-blocking drift because `filetype: x12` and local raw files agree on the executable parser profile.

## What Passed And What Still Needs Review

- Passed locally: the NorthCare parser and specs agree on the `x12_segment_envelope` profile, fixtures exist for each entity, and parser/spec tests validate the contract.
- Still needs human review before broader adapter readiness: final mapping confidence, PII/PHI handling, relationship hints, medication price handling, and any downstream interpretation of `OBS_PAYLOAD`.
