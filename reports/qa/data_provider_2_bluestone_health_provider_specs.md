# BlueStone Health Provider Specs QA Evidence

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_2_bluestone_health`
status: passed_local_validation

## Scope

- Provider specs under `metadata/provider_specs/data_provider_2_bluestone_health/`.
- Parser under `src/adapters/bluestone_health.py`.
- Synthetic fixtures under `tests/fixtures/bluestone/`.
- Parser tests under `tests/adapters/test_bluestone_health_parser.py`.
- Spec tests under `tests/specs/test_provider_specs.py`.

## Expected Local Commands

- `uv run pytest tests/specs/test_provider_specs.py`
- `uv run pytest tests/adapters`
- `uv run pytest`
- `uv run ruff check`

## Evidence Summary

| Command | Result |
| --- | --- |
| `uv run pytest tests/specs/test_provider_specs.py` | passed, 9 tests after merging `origin/develop` |
| `uv run pytest tests/adapters` | passed, 14 tests after merging `origin/develop` |
| `uv run pytest` | passed, 26 tests after merging `origin/develop` |
| `uv run ruff check` | passed |

## Notes

- The initial adapter test run failed because `pytest` on `develop` did not include the repository root on `PYTHONPATH`.
- `pyproject.toml` now declares `pythonpath = ["."]` for deterministic local and CI imports.
- No dependency install was required.
- The PR conflict in `tests/specs/test_provider_specs.py` was resolved by preserving Aegis coverage from `develop` and adding BlueStone coverage in the same test module.
