# BlueStone Health Drift Summary

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_2_bluestone_health`
status: generated

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

Use `hl7_v2_xml_messages` as the executable provider parser profile. Treat the CSV wording as documented drift, not as the parser contract.
