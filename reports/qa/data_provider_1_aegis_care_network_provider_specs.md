# Aegis Care Network Provider Spec QA Summary

Provider: `data_provider_1_aegis_care_network`
Plan: `01_provider_discovery_and_specs_plan`

## Test Families

- Unit tests validate parser family, source row key, required keys, allowed QA decisions, PII flags, and FHIR path declarations.
- Integration tests validate expected file patterns resolve Aegis local source files.
- Local data integration tests parse sampled FHIR bundles when `data_500k/` is present, while CI can still validate the spec contract without the ignored local dataset.
- Reconciliation tests validate every dictionary header is represented in each YAML mapping and has a FHIR path.
- Regression tests validate stable entity coverage and resource type expectations.
- Schema tests validate YAML parseability, top-level sections, relative paths, and provider metadata.
- Privacy tests validate sensitive fields are flagged and evidence avoids raw sensitive source values.
- Adapter parser tests validate the specialized Aegis parser maps provider specs to parsed records and rejects wrong resource types.

## Evidence Paths

- Specs: `metadata/provider_specs/data_provider_1_aegis_care_network/`
- Tests: `tests/specs/test_provider_specs.py`
- Parser: `src/adapters/aegis_care_network.py`
- Parser tests: `tests/adapters/test_aegis_care_network_parser.py`
- Drift: `reports/drift/data_provider_1_aegis_care_network.md`
- Privacy: `reports/privacy/data_provider_1_aegis_care_network.md`
- HITL: `reports/hitl/data_provider_1_aegis_care_network.md`

## Expected Commands

- `uv run pytest tests/specs/test_provider_specs.py`
- `uv run pytest tests/adapters/test_aegis_care_network_parser.py`
- `uv run pytest`
- `uv run ruff check`

## Local Results

- `uv run pytest tests/specs/test_provider_specs.py`: 9 passed.
- `uv run pytest tests/adapters/test_aegis_care_network_parser.py`: 3 passed.
- `uv run pytest`: 15 passed.
- `uv run ruff check`: passed.
