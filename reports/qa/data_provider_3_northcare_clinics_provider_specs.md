# NorthCare Clinics Provider Specs QA Evidence

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_3_northcare_clinics`
status: passed_local_validation

## Scope

- Provider specs under `metadata/provider_specs/data_provider_3_northcare_clinics/`.
- Parser under `src/adapters/northcare_clinics.py`.
- Synthetic fixtures under `tests/fixtures/northcare/`.
- Parser tests under `tests/adapters/test_northcare_clinics_parser.py`.
- Spec tests under `tests/specs/test_provider_specs.py`.

## Expected Local Commands

- `uv run pytest tests/specs/test_provider_specs.py`
- `uv run pytest tests/adapters/test_northcare_clinics_parser.py`
- `uv run pytest tests/adapters`
- `uv run pytest`
- `uv run ruff check`

## Evidence Summary

| Command | Result |
| --- | --- |
| `uv run pytest tests/specs/test_provider_specs.py` | passed, 9 tests |
| `uv run pytest tests/adapters/test_northcare_clinics_parser.py` | passed, 14 tests |
| `uv run pytest tests/adapters` | passed, 28 tests |
| `uv run pytest` | passed, 49 tests |
| `uv run ruff check` | passed |

## Notes

- No dependency install was required.
- Initial NorthCare parser negative test was tightened to isolate wrong entity segment rejection from HDR mapping rejection.
- X12-style parser behavior is fixture-based and runnable without Databricks.
