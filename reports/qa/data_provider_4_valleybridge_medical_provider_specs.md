# ValleyBridge Medical Provider Specs QA Evidence

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_4_valleybridge_medical`
status: passed_local_validation

## Scope

- Provider specs under `metadata/provider_specs/data_provider_4_valleybridge_medical/`.
- Parser under `src/adapters/valleybridge_medical.py`.
- Synthetic fixtures under `tests/fixtures/valleybridge/`.
- Parser tests under `tests/adapters/test_valleybridge_medical_parser.py`.
- Spec tests under `tests/specs/test_provider_specs.py`.

## Expected Local Commands

- `uv run pytest tests/specs/test_provider_specs.py`
- `uv run pytest tests/adapters/test_valleybridge_medical_parser.py`
- `uv run pytest tests/adapters`
- `uv run pytest`
- `uv run ruff check`

## Evidence Summary

| Command | Result |
| --- | --- |
| `uv run pytest tests/specs/test_provider_specs.py` | passed, 9 tests |
| `uv run pytest tests/adapters/test_valleybridge_medical_parser.py` | passed, 15 tests |
| `uv run pytest tests/adapters` | passed, 43 tests |
| `uv run pytest` | passed, 64 tests |
| `uv run ruff check` | passed |

## Notes

- No dependency install was required.
- Parser tests cover comment-line stripping, encoding fallback, row-key extraction, wrong resource type rejection, malformed JSON rejection, missing field-path rejection, and unsupported parser profile rejection.
- FHIR STU3 parser behavior is fixture-based and runnable without Databricks.
