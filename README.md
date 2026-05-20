# Agentic Migration

This repo owns the local flow that moves raw `data_500k` files into PostgreSQL through provider contracts, canonical modeling metadata, and provider adapters. Its responsibility ends at the `landing` layer: it provisions the local database, creates landing tables, interprets each provider file, and loads normalized rows according to metadata. Analytical modeling and dbt work live in the separate `../slalom` repo.

## System Boundary

This repository must stop at PostgreSQL `landing.*`.

```text
CURRENT / APPROVED FLOW

raw local source files
data_500k/data_provider_*/year=2025/*
    |
    v
provider source contracts
metadata/provider_specs/<provider>/<entity>.yaml
    |
    v
canonical model contracts
metadata/model_specs/silver/*.yaml
    |
    |  canonical meaning, column set, source mappings,
    |  lineage fields, nullable/required behavior
    v
adapter execution layer
src/adapters/*
src/common/adapter_runtime.py
src/handlers/*
    |
    |  adapters identify each provider file shape
    |  adapters parse raw rows / bundles / messages
    |  adapters normalize source headers and source values
    |  adapters preserve provider lineage and source references
    |  runtime maps parsed provider fields into canonical columns
    |  handlers emit canonical rows for each landing entity
    v
PostgreSQL deploy + load
src.handlers.local_postgres_workbench_deploy
src.handlers.local_model_evolution_workbench
    |
    v
schema: landing
    |
    |  materialized as PostgreSQL TABLES
    |  not review tables
    |  not dbt views
    v
landing.members
landing.encounters
landing.conditions
landing.medications
landing.observations
landing.coverage_periods
landing.cost_records
    |
    v
STOP in this repository
    |
    v
../slalom/dbt
source('landing', ...)
    |
    v
standardized -> derived -> dwh
```

```text
OLD / DO NOT USE AS THE SOURCE-OF-TRUTH FOR DBT

data_500k
    ->
review.silver_*

That historical review-layer pattern is not the active contract for this repo.
The active contract is landing.* and dbt consumes landing.* directly.
```

If you see `staging`, `standardized`, `derived`, or `dwh` objects in the same PostgreSQL database, those come from the dbt repository after `landing`, not from this repository's provision/load path.

The canonical model in this repository is the contract under `metadata/model_specs/silver/*.yaml`. `landing.*` is the PostgreSQL table materialization of that canonical contract for local loading and dbt consumption.

## What This Repo Owns

- `metadata/`: provider contracts, runtime specs, and canonical model specs.
- `src/adapters/`: provider-specific parsers for the raw file formats.
- `src/common/adapter_runtime.py`: shared casting, mapping, and normalization logic.
- `src/handlers/`: local deploy and `data_500k` load entrypoints.
- `tests/`: contract, mapping, adapter, and local runtime coverage.

```text
repo root
├── README.md
├── docs/
├── metadata/
│   ├── model_specs/
│   ├── provider_specs/
│   └── runtime_specs/
├── scripts/
├── src/
│   ├── adapters/
│   ├── common/
│   └── handlers/
└── tests/
    ├── adapters/
    ├── fixtures/
    └── specs/
```

Root-level navigation should start here in `README.md`. This is the primary overview for repository structure, runtime boundary, and the `landing.*` flow.

Helpful follow-up docs:

- [docs/local_postgres_workbench_deploy.md](docs/local_postgres_workbench_deploy.md)
- [src/README.md](src/README.md)
- [docs/local_runtime_macos_requirements.md](docs/local_runtime_macos_requirements.md)

## Prerequisites

Run everything from the repository root.

### 1. Install local tools

```bash
brew install uv postgresql@17
uv --version
psql --version
```

### 2. Start PostgreSQL

```bash
brew services start postgresql@17
PGHOST=/tmp psql -d postgres -At -c "select version();"
```

If the `psql` check fails with a socket error, PostgreSQL is not ready yet or is listening somewhere other than `/tmp`.

### 3. Sync the project environment

This repo already owns `pyproject.toml` and `uv.lock`, so do not run `uv init`.

```bash
uv sync --dev
```

After that, the repo-standard commands use `uv run --no-sync`.

### 4. Confirm local source data exists

The load flow expects a local `data_500k/` directory in the repo root. That dataset is intentionally not tracked by git.

```bash
test -d data_500k && echo "data_500k present" || echo "data_500k missing"
```

The provider specs look for paths like:

```text
data_500k/data_provider_<n>_<provider_slug>/year=2025/<entity>/*
```

## Quick Start

Use these defaults unless you intentionally need another local database:

```bash
export PGHOST=/tmp
export DATABASE_NAME=agentic_migration_local
export PGDATABASE=agentic_migration_local
export UV_CACHE_DIR=/private/tmp/uv-cache
```

Reset the local database:

```bash
./scripts/local_reset_postgres.sh
```

Provision the schema and load all registered `data_500k` provider files:

```bash
./scripts/local_provision_postgres.sh
```

What that script does:

1. Creates `agentic_migration_local`.
2. Applies the local PostgreSQL landing schema.
3. Loads adapter output into `landing.members`, `landing.encounters`, `landing.conditions`, `landing.medications`, `landing.observations`, `landing.coverage_periods`, and `landing.cost_records`.
4. Captures a local state snapshot under `artifacts/`.

`landing` is materialized to PostgreSQL tables. The runtime spec declares `landing_tables`, and the local runtime tests verify the generated SQL uses `CREATE TABLE IF NOT EXISTS` for `landing.*`.

## Manual Flow

If you want to inspect each step instead of using the wrapper script:

Dry-run the generated schema SQL:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.local_postgres_workbench_deploy \
  --database agentic_migration_local \
  --dry-run
```

Apply and verify the landing schema:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.local_postgres_workbench_deploy \
  --database agentic_migration_local \
  --apply \
  --verify
```

Load all `data_500k` files and capture state:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.local_model_evolution_workbench \
  --database agentic_migration_local \
  --load-data-500k \
  --capture-state
```

## Validation

Smoke-test the runtime contract:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs/test_local_runtime_specs.py -q
```

Run the main local validation suite:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs tests/adapters tests/test_repository_governance.py
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync ruff check src tests
```

Check loaded row counts in PostgreSQL:

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local psql -c "
select 'members' as entity, count(*) from landing.members
union all
select 'encounters', count(*) from landing.encounters
union all
select 'conditions', count(*) from landing.conditions
union all
select 'medications', count(*) from landing.medications
union all
select 'observations', count(*) from landing.observations
union all
select 'coverage_periods', count(*) from landing.coverage_periods
union all
select 'cost_records', count(*) from landing.cost_records
order by 1;"
```

Check provider distribution:

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local psql -c "
select provider_slug, count(*)
from landing.members
group by provider_slug
order by provider_slug;"
```

## Troubleshooting

- `uv run --no-sync ...` fails because dependencies are missing:
  run `uv sync --dev` first.
- `psql: connection to server on socket \"/tmp/.s.PGSQL.5432\" failed`:
  start PostgreSQL with `brew services start postgresql@17` and retry the `psql` health check.
- `Database already exists` during provision:
  run `./scripts/local_reset_postgres.sh` before `./scripts/local_provision_postgres.sh`.
- A provider/entity loads zero rows:
  inspect the matching `metadata/provider_specs/<provider>/<entity>.yaml` file and confirm the expected file patterns match the real files in `data_500k/`.
- A date field lands empty:
  inspect the source format and extend `parse_date` in `src/common/adapter_runtime.py`.
- Loading appears slow:
  watch for `loaded_file=...` log lines; the loader commits file by file instead of keeping the entire dataset in memory.

## Boundary

This repository stops at the PostgreSQL `landing` load. It should not create durable post-landing modeling layers such as `standardized`, `derived`, or `dwh`. Once the local load is complete, move to the separate dbt repository for modeled transformations and downstream analytics.
