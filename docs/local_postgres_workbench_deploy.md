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
