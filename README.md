# Agentic Migration

This repo owns the local flow that moves raw `data_500k` files into PostgreSQL through provider contracts, canonical modeling metadata, and provider adapters. Its responsibility ends at the `landing` layer: it provisions the local database, creates landing tables, interprets each provider file, and loads normalized rows according to metadata. Analytical modeling/dbt lives in the separate `../slalom` repo.

## Repo Logic

- `metadata/`: domain contracts and canonical model specs. It defines which columns exist, their canonical/silver names, and how each provider maps into them. Example: `FIRST_NAME`, `MBR_FIRST_NM`, `PT_GIVEN_NAME`, `NAME_FIRST`, and `MBR_FIRST_NAME` land as `pt_first_nm`.
- `src/adapters/`: provider adapters. Each adapter knows its source headers, file shapes, and conversion rules, but should not invent data or drop contracted fields.
- `src/common/adapter_runtime.py`: shared adapter runtime for parsing and conversion. Cross-provider rules live here, including ISO dates, `DD/MM/YYYY`, `YYYYMMDD`, and epoch seconds.
- `src/handlers/`: orchestration for deploy, reset, incremental `data_500k` loading, and state snapshots.
- `tests/`: coverage for contracts, mappings, adapters, and local runtime behavior.

## Minimum Runtime

Install only the packages needed for this local loader:

```bash
brew install uv postgresql@17
brew services start postgresql@17
uv --version
psql --version
```

Run commands from the repo root and do not run `uv init` here; this repo already owns `pyproject.toml`.

## Local Load

Local PostgreSQL usually uses:

```bash
PGHOST=/tmp
DATABASE_NAME=agentic_migration_local
```

Full reset:

```bash
PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_reset_postgres.sh
```

Provision and load from `data_500k`:

```bash
PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_provision_postgres.sh
```

The flow creates `landing.members`, `landing.encounters`, `landing.conditions`, `landing.medications`, `landing.observations`, `landing.coverage_periods`, and `landing.cost_records`.

## Quick Validation

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local psql -c "
select provider_slug, count(*) from landing.members group by provider_slug order by 1;"

UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs tests/adapters
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync ruff check src tests
```

## Troubleshooting

- If PostgreSQL is missing columns, check `metadata/model_specs/silver/*.yaml` and `metadata/model_specs/mappings/provider_to_silver_matrix.yaml` first; then redeploy with `local_postgres_workbench_deploy --apply --verify`.
- If a CSV loads zero rows, confirm the matching adapter in `src/adapters/` recognizes the file entity and real headers.
- If a date lands empty, inspect the source format and extend `parse_date` in `src/common/adapter_runtime.py`. NorthCare DOB arrives as epoch seconds and is already supported.
- If loading looks stuck, watch for `loaded_file=...` output; the loader commits incrementally per file to avoid holding all of `data_500k` in memory.
- If you need a clean local database, run reset + provision; avoid mixing old rows with newer contracts.
