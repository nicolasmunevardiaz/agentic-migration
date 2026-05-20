#!/usr/bin/env bash
set -euo pipefail

DATABASE_NAME="${DATABASE_NAME:-agentic_migration_local}"
MAINTENANCE_DATABASE="${MAINTENANCE_DATABASE:-postgres}"
export PGHOST="${PGHOST:-/tmp}"

echo "Resetting local PostgreSQL database: ${DATABASE_NAME}"
echo "Maintenance database: ${MAINTENANCE_DATABASE}"
echo "PGHOST: ${PGHOST}"

psql -v ON_ERROR_STOP=1 -d "${MAINTENANCE_DATABASE}" -c "
select pg_terminate_backend(pid)
from pg_stat_activity
where datname = '${DATABASE_NAME}'
  and pid <> pg_backend_pid();
"

dropdb --if-exists "${DATABASE_NAME}"

echo "Database dropped. ${DATABASE_NAME} no longer exists."
