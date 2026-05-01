#!/usr/bin/env bash
set -euo pipefail

DATABASE_NAME="${DATABASE_NAME:-agentic_migration_local}"
MAINTENANCE_DATABASE="${MAINTENANCE_DATABASE:-postgres}"
UV_CACHE_DIR="${UV_CACHE_DIR:-/private/tmp/uv-cache}"
export DATABASE_NAME
export PGHOST="${PGHOST:-/tmp}"
export PGDATABASE="${PGDATABASE:-${DATABASE_NAME}}"
export UV_CACHE_DIR

if [[ ! -f pyproject.toml ]]; then
  echo "Run this script from the repository root." >&2
  exit 1
fi

echo "Provisioning local PostgreSQL database: ${DATABASE_NAME}"
echo "Maintenance database: ${MAINTENANCE_DATABASE}"
echo "PGHOST: ${PGHOST}"
echo "UV_CACHE_DIR: ${UV_CACHE_DIR}"

if psql -v ON_ERROR_STOP=1 -d "${MAINTENANCE_DATABASE}" -At -c \
  "select 1 from pg_database where datname = '${DATABASE_NAME}'" | grep -q 1; then
  echo "Database already exists: ${DATABASE_NAME}" >&2
  echo "Run scripts/local_reset_postgres.sh first for a clean provision." >&2
  exit 1
fi

createdb "${DATABASE_NAME}"

uv run --no-sync python -m src.handlers.local_postgres_workbench_deploy \
  --database "${DATABASE_NAME}" \
  --apply \
  --verify

uv run --no-sync python -m src.handlers.local_model_evolution_workbench \
  --database "${DATABASE_NAME}" \
  --load-data-500k \
  --capture-state

echo "Provision complete. Landing tables are loaded in ${DATABASE_NAME}."
echo "Next step: run dbt with dbt run --project-dir dbt --profiles-dir dbt"
