---
name: qa-evidence-reviewer
description: "Review QA evidence, test families, decisions, rerun behavior, and feedback-loop completeness for Raw/Bronze to Silver migration."
user-invocable: false
---

# QA Evidence Reviewer

Use this skill when reviewing QA strategy, test plans, validation evidence, or adapter feedback loops for Raw/Bronze -> Silver. This is a reviewer skill: it checks whether test evidence is complete, deterministic, traceable, and strong enough to drive safe iteration.

Validate that QA is organized by test families: unit tests de datos, integration tests, end-to-end/system tests, data quality tests, schema tests, regression tests, and reconciliation tests. Confirm that each check emits evidence with test name, family, stage, provider, entity, source file, checksum, YAML spec path, expected value, observed value, failure count, decision, and evidence path.

For adapter implementation evidence, confirm whether local `data_500k` source data was present. If present, QA must state the number of files exercised per provider/entity and must not claim local source validation from a single handpicked sample. Failed loads must remain visible with provider, entity, exact file path, checksum when available, error type, decision, message, and evidence path. Do not allow per-file skips to hide corrupt data; only an absent local dataset may be skipped for CI portability.

Require the generated `artifacts/qa/data_500k_adapter_load_audit.jsonl` and `artifacts/qa/data_500k_adapter_load_audit.md` whenever local data exists. The audit must be produced by `uv run --no-sync python -m src.handlers.data_500k_adapter_audit` without provider filters for complete evidence. Review provider-filtered audit output only as troubleshooting evidence, not as a substitute for the all-target run.

When QA evidence says validation passed, verify that the report clearly states what passed and what did not. Passing parser/spec tests means the repository artifact is internally consistent and PR-ready; it does not mean mappings, PII/PHI handling, status normalization, relationship confidence, Databricks execution, or adapter readiness have been approved by a human. Local runtime certification means `local_validated`; it does not mean `databricks_certified`. Require reports to keep those meanings separate.

Do not replace descriptive test names with opaque rule IDs. Do not allow failed checks to disappear into logs. Do not let model-graded review replace deterministic parser, adapter, schema, data quality, runtime, lineage-shape, or reconciliation checks. Do not allow local QA reports to claim Unity Catalog permissions, Lakeflow managed orchestration, Auto CDC, production performance, or Databricks event-log validation.

Return a concise report with missing test families, evidence gaps, incorrect decisions, rerun requirements, and recommended adapter corrections.
