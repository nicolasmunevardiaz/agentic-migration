# Agentic Migration Local Loader

This repository owns local data profiling, provider adapters, and PostgreSQL landing-load
operations for `data_500k`.

The dbt project has moved to:

```text
/Users/nicolas.munevardiaz/Library/CloudStorage/OneDrive-Slalom/slalom/slalom
```

Use this repository when you need to reset PostgreSQL, provision the local database, or reload
provider data into the landing schema. Use the dbt repository when you need model layering,
normalization, tests, docs, or dbt artifacts.

## Prerequisites

Run commands from this repository root:

```bash
test -f pyproject.toml
```

PostgreSQL must be reachable locally. The default local connection is:

```bash
PGHOST=/tmp
DATABASE_NAME=agentic_migration_local
```

## Reset / Rollback

Reset intentionally drops the whole local project database. This is the clean rollback path before
re-provisioning from source files and adapter contracts.

```bash
PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_reset_postgres.sh
```

Verify the database no longer exists:

```bash
PGHOST=/tmp psql -d postgres -At -c "select 1 from pg_database where datname = 'agentic_migration_local';"
```

The command should return no rows.

## Provision

Provision creates the database, deploys only the `landing` schema, creates landing tables, and
loads all local `data_500k` files through approved adapter handlers.

```bash
PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_provision_postgres.sh
```

The provision script runs:

```text
createdb agentic_migration_local
uv run --no-sync python -m src.handlers.local_postgres_workbench_deploy --apply --verify
uv run --no-sync python -m src.handlers.local_model_evolution_workbench --load-data-500k --capture-state
```

After provision, the only project schema created by this repository should be:

```text
landing
```

The loaded landing tables are:

```text
landing.members
landing.encounters
landing.conditions
landing.medications
landing.observations
landing.coverage_periods
landing.cost_records
```

## Inspect

List landing tables:

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local psql -c "
select table_schema, table_name
from information_schema.tables
where table_schema = 'landing'
order by table_schema, table_name;
"
```

Check row counts:

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

Check provider coverage:

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local psql -c "
select provider_slug, count(*) as member_rows
from landing.members
group by provider_slug
order by provider_slug;
"
```

## Validate

Run loader/spec validation:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync ruff check src tests
```

## Fast Operator Sequence

For a full clean reload:

```bash
PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_reset_postgres.sh

PGHOST=/tmp DATABASE_NAME=agentic_migration_local ./scripts/local_provision_postgres.sh
```

Then switch to the dbt repository for model work:

```bash
cd /Users/nicolas.munevardiaz/Library/CloudStorage/OneDrive-Slalom/slalom/slalom
```
