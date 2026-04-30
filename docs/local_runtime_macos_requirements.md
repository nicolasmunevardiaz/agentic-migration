# Local Runtime macOS Requirements With Colima

## Purpose

This guide documents the Human in the Loop installation and verification path for optional local runtime tools used by Plan 04 local runtime certification. It is a requirements guide and evidence note. Do not install additional packages, start containers, run Databricks jobs, apply Terraform, deploy bundles, create cloud resources, use production data, or claim Databricks parity from this document alone.

Plan 04 remains portable and runtime-neutral until the dependency approvals are recorded in `reports/privacy/local_runtime_dependency_review.md` and the local runtime specs are updated.

## Current Local Observation

Observed on 2026-04-29:

- `brew`, `uv`, `docker`, and `colima` are available locally.
- `pyspark`, `delta-spark`, and `openlineage-python` are installed in `pyproject.toml` and `uv.lock` after user HITL approval for local import/spec-shape validation.
- `uv run --no-sync python -c "import pyspark; import delta; import openlineage.client; print(pyspark.__version__)"` reports PySpark `4.1.1` when using `UV_CACHE_DIR=/private/tmp/uv-cache`.
- Homebrew OpenJDK 17 exists and `/opt/homebrew/opt/openjdk@17/bin/java -version` reports OpenJDK `17.0.19`.
- The default shell `java -version` still fails until `JAVA_HOME` and `PATH` expose Homebrew OpenJDK.
- `colima status` reported `colima is not running`.
- `docker context ls` showed Colima contexts and a `DOCKER_HOST` override pointing at the Colima socket.

If this changes before installation, refresh the observation before approving runtime dependency work.

## Non-Negotiables

- Use Colima for local containers.
- Do not use Docker Desktop.
- Do not install Databricks packages for Plan 04 local certification.
- Do not run Databricks jobs.
- Do not apply Terraform.
- Do not deploy Databricks Asset Bundles.
- Do not use production data.
- Do not claim local validation is Databricks parity.

## Base Requirements

Required before optional Spark, Delta Lake OSS, OpenLineage, or Marquez validation:

- Homebrew for macOS package management.
- `uv` for Python dependency and command execution.
- Java for Spark and Delta Lake OSS local execution.
- Docker CLI configured against Colima, not Docker Desktop.
- Git configured with the user's name and email for reviewed commits.
- A local data workbench choice for Plan 04.5 drift review: PostgreSQL + DBeaver, DuckDB + dbt Core, or Snowflake after separate approval.

If `uv` is not installed, install it after HITL approval with:

```bash
brew install uv
uv --version
```

This repository already has `pyproject.toml` at the repository root. Do not run `uv init` inside this repository or from the parent `slalom/` folder. `uv init` is only for creating a new standalone Python project, not for Plan 04 dependency approval in this repo.

Before running any `uv add` or repo test command, confirm that the shell is at the repository root. Replace `/path/to/agentic-migration` with the local clone path for this repository:

```bash
cd /path/to/agentic-migration
pwd
test -f pyproject.toml
```

If `uv add` returns `No pyproject.toml found in current directory or any parent directory`, the shell is in the wrong folder. Run the `cd` command above and retry.

## Plan 04.5 Tool Selection

Plan 04 certified local Raw/Bronze to Silver contracts. Plan 04.5 must not jump to Gold star schemas. It should first create a local data workbench that lets humans inspect unresolved or weakly-normalized values, write HITL decisions, and propagate approved decisions back into specs and reports.

Recommended order:

1. Use PostgreSQL + DBeaver when humans need a familiar read/write database UI for drift review and decision entry.
2. Use DuckDB + dbt Core when the team needs fast local SQL tests, reproducible transformations, and file-backed evidence without running a database service.
3. Use Spark, Delta Lake OSS, and Spark Declarative Pipelines only after HITL approves local pipeline execution; start with dry-runs and small fixtures before any table writes.
4. Use Marquez/OpenLineage only after HITL approves Colima service start and lineage event emission.
5. Defer Snowflake until the team intentionally moves beyond local-only drift review and records cloud governance approval.

Gold design remains blocked until local drift tables and HITL decisions show which semantics are approved, rejected, or deferred.

## Git Configuration

Git is required for reviewed changes and PR traceability. These commands may run from any folder:

```bash
git config --global user.name "First Last"
git config --global user.email "name@example.com"
git config --global --get user.name
git config --global --get user.email
```

Use the approved corporate email identity. Do not commit personal secrets, local credentials, `.env` files, raw source data, or local database files.

## Colima And Docker CLI

Colima is the approved local container runtime for this repository. Docker Desktop is not approved for Plan 04 work.

Official reference: <https://colima.run/docs/getting-started/>

Expected verification flow. These commands may run from any folder:

```bash
colima start
colima status
docker context use colima
docker ps
```

If `DOCKER_HOST` is set, it may override the active Docker context. Resolve that before validating container behavior so Docker commands consistently target the Colima socket.

Optional smoke test after HITL approval:

```bash
docker run --rm hello-world
```

Colima is needed only for local container services such as PostgreSQL or Marquez. It is not required for DuckDB, dbt Core, `uv`, or metadata/spec tests.

## PostgreSQL And DBeaver For HITL Drift Review

Use PostgreSQL + DBeaver when HITL needs a persistent local database with read/write decision tables. This is the preferred interface for resolving drift because reviewers can filter source values, inspect Silver mappings, and write decisions into controlled tables such as `review.hitl_decisions`.

Use PostgreSQL for:

- Human-readable review schemas such as `review.silver_members`, `review.drift_gender_values`, `review.drift_coverage_values`, and `review.hitl_decisions`.
- Read/write edits by approved reviewers.
- SQL joins across Silver outputs, provider lineage, QA evidence, and drift candidates.
- Exporting approved decisions back to YAML and Markdown evidence.

Do not use PostgreSQL for:

- Production data.
- Databricks parity claims.
- Permanent source-of-truth model contracts.
- Secret storage.

Installation options after HITL approval:

```bash
brew install postgresql@17
brew services start postgresql@17
createdb agentic_migration_local
psql agentic_migration_local
```

If the team wants PostgreSQL to run under Colima instead of Homebrew services, record that as a Docker service approval first. Then use a repository-owned compose file and keep the data volume under an ignored local path such as `artifacts/local_db/`.

DBeaver is the approved GUI option for PostgreSQL review because it lets HITL users browse schemas, run SQL, and edit decision rows. Install after HITL approval:

```bash
brew install --cask dbeaver-community
```

Suggested local schemas:

```sql
CREATE SCHEMA IF NOT EXISTS review;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS evidence;
```

The repository owns the declarative workbench contract at:

```text
metadata/runtime_specs/local/local_postgres_workbench.yaml
```

The short deploy runbook lives at:

```text
docs/local_postgres_workbench_deploy.md
```

That YAML is the source of truth for local PostgreSQL schemas, review tables, drift tables, evidence tables, idempotency rules, and blocked operations. Do not hand-edit database objects as the durable contract; edit the YAML, review it, then rerun the deploy.

Dry-run the deploy from the repository root:

```bash
cd /path/to/agentic-migration
test -f pyproject.toml
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.local_postgres_workbench_deploy --database agentic_migration_local --dry-run
```

The dry-run writes reviewable SQL to:

```text
artifacts/local_runtime/postgres/local_workbench_schema.sql
```

Apply and verify the deploy after HITL approval:

```bash
cd /path/to/agentic-migration
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.local_postgres_workbench_deploy --database agentic_migration_local --apply --verify
```

The deploy is idempotent and uses `CREATE SCHEMA IF NOT EXISTS`, `CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ADD COLUMN IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, and guarded constraint creation. It must not emit `DROP`, `TRUNCATE`, `DELETE`, or destructive DDL.

The HITL decision table shape is:

```sql
CREATE TABLE IF NOT EXISTS review.hitl_decisions (
  decision_id text PRIMARY KEY,
  plan_id text NOT NULL,
  business_question_id text,
  drift_domain text NOT NULL,
  source_entity text,
  source_field text,
  observed_value text,
  recommended_option text,
  selected_option text,
  decision_status text NOT NULL,
  reviewer_notes text,
  evidence_path text NOT NULL,
  updated_at timestamptz DEFAULT now()
);
```

Allowed `decision_status` values should be `approved`, `rejected`, `deferred_with_human_approval`, or `needs_more_evidence`. If a decision is `needs_more_evidence`, downstream semantic modeling remains blocked for that drift domain.

## DuckDB And dbt Core For Reproducible Local Tests

Use DuckDB + dbt Core when the goal is a fast, local, file-backed SQL harness rather than a human-edited database service. DuckDB can run embedded analytical SQL locally, and the Python client can be installed as a normal Python package. dbt Core can then express reproducible SQL transformations and tests.

Use DuckDB + dbt for:

- Local drift profiling over generated CSV/Parquet/JSON evidence.
- SQL tests that can run in CI without a database service.
- Repeatable transformations from local Silver artifacts into drift-review tables.
- Comparing normalized vs source-scoped values without changing canonical specs.

Do not use DuckDB + dbt for:

- HITL row editing as the primary interface.
- Production datasets.
- Gold mart approval before drift decisions are complete.

After HITL approval, install CLI tooling:

```bash
brew install duckdb
duckdb --version
```

After HITL approval for Python/dbt dependencies, run from the repository root:

```bash
cd /path/to/agentic-migration
test -f pyproject.toml
uv add duckdb dbt-core dbt-duckdb
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync dbt --version
```

Suggested local file path:

```text
artifacts/local_workbench/agentic_migration.duckdb
```

Keep DuckDB database files under `artifacts/` so they stay out of Git.

## Java For Spark And Delta

Spark local execution requires Java. The current Spark Python installation documentation requires Java 17 or later with `JAVA_HOME` configured.

Official reference: <https://spark.apache.org/docs/latest/api/python/getting_started/install.html>

Homebrew OpenJDK 17 is installed, but the default shell must expose it before plain `java` commands work. These commands may run from any folder:

```bash
/opt/homebrew/opt/openjdk@17/bin/java -version
export JAVA_HOME=/opt/homebrew/opt/openjdk@17
export PATH="$JAVA_HOME/bin:$PATH"
java -version
```

Persist the `JAVA_HOME` and `PATH` entries in the user's shell profile only after confirming they match the local Homebrew installation. Do not commit user-specific shell configuration to this repository.

## Spark And Delta Lake OSS

Spark and Delta Lake OSS are optional local validation capabilities only. They are not required for the current Plan 04 contract tests and must not be installed until HITL approves dependency changes.

Official Delta Lake reference: <https://docs.delta.io/quick-start/>

The Plan 04 Python packages are installed in `pyproject.toml` and `uv.lock` after user HITL approval. Run verification commands from the repository root:

```bash
cd /path/to/agentic-migration
test -f pyproject.toml
```

Then run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -c "import pyspark; import delta; print('spark/delta import ok')"
```

Do not run more `uv add` commands unless a new HITL dependency approval exists. The approved packages support import/spec-shape validation only; they do not authorize Spark Declarative Pipeline execution, Delta table writes, or Databricks parity claims.

Use Spark + Delta only when:

- The team needs to validate local execution behavior that DuckDB/dbt cannot represent.
- Java is configured and plain `java -version` works in the active shell.
- HITL has approved Spark execution and Delta local writes.
- Inputs are deterministic fixtures or approved local samples.
- Outputs are written only under `artifacts/`.

Suggested local output roots:

```text
artifacts/local_runtime/spark/
artifacts/local_runtime/delta/
```

Allowed first Spark validation after HITL approval:

```bash
cd /path/to/agentic-migration
test -f pyproject.toml
export JAVA_HOME=/opt/homebrew/opt/openjdk@17
export PATH="$JAVA_HOME/bin:$PATH"
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.master('local[2]').appName('plan-04-5-smoke').getOrCreate(); print(spark.range(1).count()); spark.stop()"
```

Allowed first Delta validation after HITL approval:

```bash
cd /path/to/agentic-migration
mkdir -p artifacts/local_runtime/delta/smoke
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -c "from pyspark.sql import SparkSession; from delta import configure_spark_with_delta_pip; builder = SparkSession.builder.master('local[2]').appName('delta-smoke').config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension').config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog'); spark = configure_spark_with_delta_pip(builder).getOrCreate(); spark.range(1).write.format('delta').mode('overwrite').save('artifacts/local_runtime/delta/smoke'); print(spark.read.format('delta').load('artifacts/local_runtime/delta/smoke').count()); spark.stop()"
```

The Delta validation writes local files and therefore requires explicit HITL approval for Delta table writes before it is run.

## Spark Declarative Pipelines

Spark Declarative Pipelines are not currently enabled for execution in this repository. The approved Plan 04 package is `pyspark`, not `pyspark[pipelines]`. The Apache Spark documentation describes Spark Declarative Pipelines as a declarative framework for Spark pipelines and lists `pip install pyspark[pipelines]` as the quick install path. It also documents the `spark-pipelines` CLI with `init`, `run`, and `dry-run` commands.

Use Spark Declarative Pipelines only when:

- HITL approves adding or changing the dependency to `pyspark[pipelines]`.
- HITL approves local Spark pipeline execution.
- The pipeline uses fixtures or approved local samples only.
- `spark-pipelines dry-run` passes before any `spark-pipelines run`.
- No Databricks parity, Lakeflow parity, Unity Catalog behavior, or production readiness is claimed.

After HITL approval, run from the repository root:

```bash
cd /path/to/agentic-migration
test -f pyproject.toml
uv add "pyspark[pipelines]"
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync spark-pipelines --help
```

Allowed dry-run pattern after a repository-owned pipeline spec exists:

```bash
cd /path/to/agentic-migration
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync spark-pipelines dry-run --spec metadata/runtime_specs/local/<pipeline-spec>.yaml
```

Allowed run pattern after dry-run passes and HITL approves local writes:

```bash
cd /path/to/agentic-migration
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync spark-pipelines run --spec metadata/runtime_specs/local/<pipeline-spec>.yaml
```

Pipeline specs must reference only local paths under `artifacts/`, must not reference cloud storage, and must not use production data.

## OpenLineage

OpenLineage is an optional lineage event capability for local evidence shape validation. The Plan 04 contract may validate lineage shape without installing or emitting OpenLineage events.

Official reference: <https://openlineage.io/docs/1.44.1/client/python/>

The Plan 04 Python client package is installed in `pyproject.toml` and `uv.lock` after user HITL approval. Run verification commands from the repository root:

```bash
cd /path/to/agentic-migration
test -f pyproject.toml
```

Then run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -c "import openlineage.client; print('openlineage import ok')"
```

Do not configure remote transports, Kafka, cloud storage, or external lineage endpoints unless a separate HITL approval records the transport, destination, data exposure risk, and rollback.

## Marquez On Colima

Marquez is an optional local lineage backend and UI. If approved, run it only through containers backed by Colima. Do not use Docker Desktop.

Before any Marquez run, confirm Colima from any folder:

```bash
colima status
docker ps
```

If a repository-owned Marquez compose file is later added, run it from the repository root unless that future document says otherwise:

```bash
cd /path/to/agentic-migration
```

Any Marquez compose file or container command must keep data local, avoid production data, avoid cloud credentials, and be documented in the dependency review. Starting Marquez is a service operation and requires explicit HITL approval beyond this README.

Use Marquez only for lineage visualization after local data workbench decisions and pipeline specs are stable enough to produce useful lineage. Do not use Marquez as the source of HITL semantic decisions; it is evidence and visualization, not the decision register.

## Databricks Packages

Databricks packages, including Databricks Connect, remain outside Plan 04 local runtime certification. Databricks Connect runs code against remote Databricks compute, so it belongs to later Databricks validation planning, not the portable local certification loop.

Official reference: <https://docs.databricks.com/en/dev-tools/databricks-connect/index.html>

Do not install `databricks-connect`, Databricks CLI packages, Databricks SDK packages, or bundle tooling for Plan 04 unless a later approved plan explicitly authorizes Databricks validation work.

## Post-Approval Verification

After an approved installation, the non-repository commands may run from any folder:

```bash
java -version
colima status
docker context ls
docker ps
```

Run repository validation from the repository root:

```bash
cd /path/to/agentic-migration
test -f pyproject.toml
uv run --no-sync pytest tests/specs/test_local_runtime_specs.py
```

If package files change, also run:

```bash
uv run --no-sync pytest tests/specs tests/adapters tests/test_repository_governance.py
uv run --no-sync ruff check
```

Then update `reports/privacy/local_runtime_dependency_review.md` with approved dependencies, versions, purpose, risks, evidence, and remaining blocked actions.

## Plan 04.5 Minimum Validation Flow

Before any semantic mart or Gold design work, Plan 04.5 should prove:

1. Local database/workbench choice is approved.
2. Silver or local audit outputs are loaded into local review tables.
3. Drift tables identify unnormalized values, nullability gaps, sparse provider coverage, and conflicting source semantics.
4. HITL writes decisions to a controlled decision table or approved YAML/Markdown register.
5. Approved decisions are propagated back to specs and reports.
6. Tests prove no Gold or semantic star schema is introduced before drift decisions are complete.

Expected validation commands from the repository root:

```bash
cd /path/to/agentic-migration
test -f pyproject.toml
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/test_repository_governance.py
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync ruff check
```

Any command that starts a service, writes a local database, writes Delta files, emits lineage events, or changes dependencies requires HITL approval and an update to `reports/privacy/local_runtime_dependency_review.md`.
