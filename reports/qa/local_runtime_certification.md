# Local Runtime Certification

plan_id: `04_local_runtime_and_contract_certification_plan`
provider: `all`
status: `local_runtime_contract_validated`
validation_state: `local_validated`
databricks_state: `not_databricks_certified`

## Summary

This report certifies the Plan 04 local runtime contract and adapter evidence without claiming Databricks compatibility. Local Python packages for Spark, Delta Lake OSS, and OpenLineage are installed and import-verified for local import/spec-shape validation only. This report does not certify Spark Declarative Pipeline execution, Delta table writes, OpenLineage transport emission, Marquez, Docker services, Databricks packages, Databricks Runtime, Unity Catalog, Terraform, bundles, cloud services, or production data.

## Interface Coverage

- Provider parser interface: defined in `metadata/runtime_specs/local/runtime_interface_contract.yaml`.
- Bronze writer interface: defined.
- Canonical mapper interface: defined.
- Silver writer interface: defined.
- Quarantine writer interface: defined.
- QA evidence writer interface: defined.
- Lineage emitter interface: defined.
- Runtime adapter interface: defined.

## Dependency Evidence

- `pyproject.toml` includes `pyspark>=4.1.1`, `delta-spark>=4.2.0`, and `openlineage-python>=1.46.0`.
- `uv.lock` resolves `pyspark` `4.1.1`, `delta-spark` `4.2.0`, and `openlineage-python` `1.46.0`.
- Import check: `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -c "import pyspark; import delta; import openlineage.client; print(pyspark.__version__)"` returned `4.1.1`.
- Java direct check: `/opt/homebrew/opt/openjdk@17/bin/java -version` returned OpenJDK `17.0.19`.
- Default shell Java state: `java -version` still needs `JAVA_HOME` and `PATH` configuration before plain `java` resolves.
- Colima state: installed but not running; Marquez and container-backed lineage evidence remain blocked pending explicit service-start approval.

## Adapter Audit Evidence

Plan 04 refreshed `data_500k` audit evidence because local source data exists.

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -m src.handlers.data_500k_adapter_audit --plan-id 04_local_runtime_and_contract_certification_plan
```

Result: passed.

- JSONL evidence: `artifacts/qa/data_500k_adapter_load_audit.jsonl`
- Markdown summary: `artifacts/qa/data_500k_adapter_load_audit.md`
- Total records: `250`
- Status counts: `{'passed': 250}`
- Providers: all five approved providers, 50 records each.
- Failures: none.
- Skips: none.

## Validation Commands

| Command | Result |
| --- | --- |
| `git diff --check` | passed |
| `/opt/homebrew/opt/openjdk@17/bin/java -version` | passed, OpenJDK `17.0.19` |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync python -c "import pyspark; import delta; import openlineage.client; print(pyspark.__version__)"` | passed, PySpark `4.1.1` |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs` | passed, 46 tests |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/adapters` | passed, 143 tests |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/test_repository_governance.py` | passed, 14 tests |
| `UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync ruff check` | passed |

## Local Certification Boundary

Local certification may validate provider parser output, Bronze/Silver contract shape, canonical mapping, quarantine behavior, QA evidence shape, and lineage evidence shape. It must not claim Unity Catalog permissions, Databricks Runtime behavior, Lakeflow orchestration, Auto CDC, serverless behavior, cloud IAM, production performance, or exact Databricks event logs.

## Next Action

Run `repo-governance-auditor` and create the PR only if it returns `allowed_next_action: create_pr`.
