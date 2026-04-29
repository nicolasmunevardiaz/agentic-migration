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
