# Local PostgreSQL Workbench Deploy

Use this flow to deploy the local review workbench into an existing PostgreSQL database such as `agentic_migration_local`. Run every command from the repository root:

```bash
cd /path/to/agentic-migration
test -f pyproject.toml
```

The declarative source of truth is:

```text
metadata/runtime_specs/local/local_postgres_workbench.yaml
```

Edit that YAML when schemas, tables, drift review fields, HITL decision fields, or evidence tables need to change. Do not hand-edit PostgreSQL objects as the durable contract.

## Dry Run

Render the SQL artifact without changing the database:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.local_postgres_workbench_deploy --database agentic_migration_local --dry-run
```

Review the generated SQL at:

```text
artifacts/local_runtime/postgres/local_workbench_schema.sql
```

## Apply And Verify

After HITL approval, apply the idempotent schema and verify all expected tables:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.local_postgres_workbench_deploy --database agentic_migration_local --apply --verify
```

The deploy creates `staging`, `review`, and `evidence` schemas. It uses `CREATE ... IF NOT EXISTS`, `ALTER TABLE ADD COLUMN IF NOT EXISTS`, guarded constraints, and `CREATE INDEX IF NOT EXISTS`. The deploy must not emit `DROP`, `TRUNCATE`, `DELETE`, production data access, Databricks jobs, Terraform, bundles, or Docker Desktop operations.

For manual verification:

```bash
psql -d agentic_migration_local -c "select table_schema, table_name from information_schema.tables where table_schema in ('staging','review','evidence') order by table_schema, table_name;"
```

## Plan 04.5 Model Evolution

Plan 04.5 uses the same local PostgreSQL database as the dbt Core target after the dbt layout is declared in `dbt/dbt_project.yml` and `dbt/profiles.yml`. Credentials must come from local PostgreSQL defaults, `PG*` environment variables, or `.pgpass`; do not commit secrets.

Approved local fixture load and dbt validation commands:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.local_model_evolution_workbench --database agentic_migration_local --load-fixtures --capture-state
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt parse --project-dir dbt --profiles-dir dbt
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt compile --project-dir dbt --profiles-dir dbt
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt run --project-dir dbt --profiles-dir dbt
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt test --project-dir dbt --profiles-dir dbt
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt docs generate --project-dir dbt --profiles-dir dbt
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.local_model_evolution_workbench --database agentic_migration_local --capture-dbt-artifacts --validate-sql-answers
```

These commands produce local SQL-answer evidence only. They do not create production Gold models, Databricks serving tables, Terraform resources, bundles, Docker services, or Databricks parity claims.
