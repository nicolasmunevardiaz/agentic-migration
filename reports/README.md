# Reports Guide

`reports/` contains human-readable evidence for decisions, QA, privacy, drift, and governance. These files explain why generated specs and code are safe enough to review; they are not runtime inputs.

## What Is Here

- `drift/`: source and provider drift summaries discovered during profiling.
- `hitl/`: Human in the Loop queues and decision registers. `canonical_drift_decision_runbook.md` records cross-provider decisions such as parser approval, PII handling, and ingestion nullability.
- `privacy/`: PII/PHI, dependency, secret, permission, and governance reviews.
- `qa/`: validation evidence, command results, repo governance reports, and adapter QA summaries.

## Inputs And Outputs

Inputs are specs, tests, logs, and human decisions. Outputs are review packets that support PRs and future rollout gates.

Mini example:

```text
reports/hitl/canonical_drift_decision_runbook.md
  records DRIFT-015: ingestion fields are nullable

metadata/model_specs/**/*.yaml
  applies that decision

reports/qa/canonical_nullability_reconciliation.md
  records the tests that prove the change is consistent
```

## How To Use It

Read `reports/hitl/` to understand approved or pending decisions. Read `reports/privacy/` before changing sensitive fields, fixtures, dependencies, or cloud behavior. Read `reports/qa/` to confirm which local checks passed and what evidence supports a PR.

## Validate This Layer

Use `uv`; do not call `python` or `pytest` directly.

```bash
uv run --no-sync pytest tests/test_repository_governance.py
uv run --no-sync pytest tests/specs tests/adapters
uv run --no-sync pytest
uv run --no-sync ruff check
```

Main test categories connected to reports are governance checks, QA evidence regression checks, privacy/source-data safety checks, integration tests that prove evidence paths are coherent, and full-suite regression before PR creation.
