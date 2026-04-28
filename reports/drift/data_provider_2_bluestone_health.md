# BlueStone Health Drift Summary

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_2_bluestone_health`
status: generated

## How To Read This

This report explains differences between the BlueStone source dictionary and the files the parser must actually read. "Drift" does not automatically mean a failure. It means the provider's real source shape differs from the generic expectation and must be documented.

Local validation passing means the YAML specs, parser, fixtures, and tests are internally consistent. It does not mean every mapping, PII/PHI decision, or downstream adapter decision is approved.

## Reader Glossary

- CDATA: XML text wrapper that lets the file store text such as JSON without treating it as XML tags.
- Executable parser profile: the named parser mode that is implemented in code and referenced by the YAML specs.
- HITL: Human in the Loop. A human must confirm the decision before the agent treats it as approved.
- HL7 XML: healthcare message data represented as XML.
- Message segment: the repeated XML message type that corresponds to one entity, such as patients or encounters.
- Parser contract: the source shape the parser is expected to support.
- Row key: the source field used to identify a row or source record.

## Findings

- Row-key drift: BlueStone uses `LINE_ID` as the source row key while other providers may use different row-key headers.
- Filetype drift: the dictionary says CSV with `.xml`, but provider metadata and local source files indicate HL7 XML.
- Parser profile: BlueStone requires namespace-aware HL7 XML message parsing with one repeated message segment per entity.
- Observation drift: `OBS_JSON` is embedded as XML text/CDATA and must be preserved as source text.

## Entity Segments

| Entity | Message segment | Source row key |
| --- | --- | --- |
| patients | `ADT_A01` | `LINE_ID` |
| encounters | `SIU_S12` | `LINE_ID` |
| conditions | `DFT_P03` | `LINE_ID` |
| medications | `RDE_O11` | `LINE_ID` |
| observations | `ORU_R01` | `LINE_ID` |

## Decision

Use `hl7_v2_xml_messages` as the executable provider parser profile. In plain language, this means BlueStone files should be parsed as HL7-style XML messages, not as CSV files. Treat the CSV wording as documented drift, not as the parser contract.

## What Passed And What Still Needs Review

- Passed locally: the BlueStone parser and specs agree on the `hl7_v2_xml_messages` profile, fixtures exist for each entity, and parser/spec tests validate the contract.
- Still needs human review before broader adapter readiness: final mapping confidence, PII/PHI handling, and any downstream interpretation of embedded observation JSON.
