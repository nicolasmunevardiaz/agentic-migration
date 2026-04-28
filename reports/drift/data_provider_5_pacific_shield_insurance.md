# Pacific Shield Insurance Drift Summary

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_5_pacific_shield_insurance`
status: generated

## How To Read This

This report explains differences between the Pacific Shield source dictionary, local CSV files, and the executable parser contract. Drift does not automatically mean a blocker; it means the provider-specific source behavior is documented for review.

Local validation passing means the YAML specs, parser, fixtures, and tests are internally consistent. It does not approve final Silver semantics, PII/PHI decisions, relationship confidence, or Databricks execution.

## Reader Glossary

- CSV claims export: the executable parser profile for Pacific Shield comma-delimited source files.
- Data-first chunk: a CSV file that starts directly with data rows and relies on dictionary column order.
- Duplicate header preservation: the parser keeps repeated source header positions, such as `DX_CD`, instead of collapsing them.
- HITL: Human in the Loop. A human must confirm the decision before it becomes an approved semantic decision.
- Parser contract: the source shape the parser is expected to support.
- Row key: the source field used to identify each source row.

## Findings

- Row-key drift: Pacific Shield uses `CLM_SEQ` as the source row key while other providers use different row-key headers.
- File-shape drift: local CSV chunks may include comment metadata, an Excel-style `sep=,` preamble, a header row, or data rows that depend on dictionary order.
- Header drift: `conditions` repeats `DX_CD`; the parser preserves both positions for `CND_ID` and `ICD_HINT`.
- Source-type drift: provider discovery uses neutral `claims_export` and defers payer-vs-clinical semantics to later HITL/canonical review.
- Source coverage drift: local clinical entity chunks are structurally present but may contain no data rows in sampled files; coverage review remains visible in HITL evidence.

## Entity Resources

| Entity | File extension | Source row key | Parser profile |
| --- | --- | --- | --- |
| patients | `csv` | `CLM_SEQ` | `csv_claims_export` |
| encounters | `csv` | `CLM_SEQ` | `csv_claims_export` |
| conditions | `csv` | `CLM_SEQ` | `csv_claims_export` |
| medications | `csv` | `CLM_SEQ` | `csv_claims_export` |
| observations | `csv` | `CLM_SEQ` | `csv_claims_export` |

## Decision

Use `csv_claims_export` as the executable provider parser profile. In plain language, this means Pacific Shield CSV files are parsed using the dictionary column order, while allowing comment metadata, optional `sep=,` preambles, optional header rows, and duplicate-header position preservation.

## What Passed And What Still Needs Review

- Passed locally: the Pacific Shield parser and specs agree on the `csv_claims_export` profile, fixtures exist for each entity, and parser/spec tests validate the contract.
- Still needs human review before broader adapter readiness: final source-type semantics, PII/PHI handling, duplicate `DX_CD` downstream modeling impact, relationship hints, coverage status handling, medication financial amount handling, sparse clinical source coverage, and Databricks execution approval.
