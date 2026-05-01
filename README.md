# Agentic Migration Local Workbench

This repository supports a local PostgreSQL + dbt workflow for loading `data_500k` through approved adapters, writing canonical landing tables, and building layered dbt models on top of those tables.

The clean local state is an absent project database. The reset script drops the whole local project database; the provision script creates it again, deploys only the `landing` schema, and loads all adapter output into `landing.*`. dbt is run after provision.

## Prerequisites

Run commands from the repository root:

```bash
test -f pyproject.toml
```

PostgreSQL must be reachable locally. The default connection uses:

```bash
PGHOST=/tmp
DATABASE_NAME=agentic_migration_local
```

You can override either variable when needed:

```bash
PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_provision_postgres.sh
```

## Reset / Rollback

Use reset when you want to discard all local project database state. This intentionally drops the entire `agentic_migration_local` database so the next deploy starts from nothing.

```bash
PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_reset_postgres.sh
```

Verify the database no longer exists:

```bash
PGHOST=/tmp psql -d postgres -At -c "select 1 from pg_database where datname = 'agentic_migration_local';"
```

The command should return no rows.

## Provision Before dbt

Provision creates the database, creates only the `landing` schema, creates all landing tables, then loads all local `data_500k` files through the approved adapter handlers.

```bash
PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_provision_postgres.sh
```

The provision script runs:

```text
createdb agentic_migration_local
uv run --no-sync python -m src.handlers.local_postgres_workbench_deploy --apply --verify
uv run --no-sync python -m src.handlers.local_model_evolution_workbench --load-data-500k --capture-state
```

After provision, PostgreSQL contains loaded landing tables such as:

```text
landing.members
landing.encounters
landing.conditions
landing.medications
landing.observations
landing.coverage_periods
landing.cost_records
```

After provision, the only project schema in PostgreSQL should be `landing`. `data_quality`, `review`, `scratch`, `ops`, and `evidence` are not created by the default local provision path.

Optional inspection queries:

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local psql -c "
select table_schema, table_name
from information_schema.tables
where table_schema = 'landing'
order by table_schema, table_name;
"
```

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local psql -c "
select 'landing.members' as table_name, count(*) from landing.members
union all
select 'landing.encounters', count(*) from landing.encounters
union all
select 'landing.conditions', count(*) from landing.conditions
union all
select 'landing.medications', count(*) from landing.medications
union all
select 'landing.observations', count(*) from landing.observations
union all
select 'landing.coverage_periods', count(*) from landing.coverage_periods
union all
select 'landing.cost_records', count(*) from landing.cost_records;
"
```

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local psql -c "
select provider_slug, count(*) as member_rows
from landing.members
group by provider_slug
order by provider_slug;
"
```

## Build dbt Models

Build the derived dbt model layer after provision:

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt run --project-dir dbt --profiles-dir dbt --select path:models/derived
```

The `dbt/models/data_quality/` folder remains in the repository for contract-driven audits, but it is not part of the default local provision/build path and should not be materialized into PostgreSQL unless a data quality audit run is explicitly requested.

To parse the full dbt project without creating database objects:

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt parse --project-dir dbt --profiles-dir dbt
```

dbt reads `landing.*` through `source()` and creates configured relations in `derived`.

## Validate

Run dbt tests for the derived layer:

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt test --project-dir dbt --profiles-dir dbt --select path:models/derived
```

Run Python/spec validation:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs tests/sql
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync ruff check tests/specs tests/sql
```

## Fast Operator Sequence

For a full clean rebuild:

```bash
PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_reset_postgres.sh

PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_provision_postgres.sh

PGHOST=/tmp PGDATABASE=agentic_migration_local \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt run --project-dir dbt --profiles-dir dbt --select path:models/derived

PGHOST=/tmp PGDATABASE=agentic_migration_local \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync dbt test --project-dir dbt --profiles-dir dbt --select path:models/derived
```

Use reset as the rollback path whenever local state needs to be discarded and rebuilt from contracts, adapters, and dbt models.
