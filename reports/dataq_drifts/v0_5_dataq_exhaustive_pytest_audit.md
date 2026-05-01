# V0_5 Exhaustive Data Quality Pytest Audit

Report id: `DATAQ_EXHAUSTIVE_PYTEST_AUDIT_V0_5_2026_04_30`
Scope: PostgreSQL/dbt-derived data quality audit over local `data_500k`.
Database: `agentic_migration_local`
Schema: `derived`
Authoring rule: this audit intentionally fails while open drifts exist.

## Why This Exists

The earlier report-contract test validates that the drift documentation is
well-formed. That is useful, but it does not re-scan the 1.6M+ derived records.
This audit is the stronger layer: pytest connects to PostgreSQL, executes
category-specific aggregate SQL against the dbt-derived views, writes JSONL logs
by category, and fails if any provider/entity/field check has affected rows.

## Test Artifact

Unit/integration test:

```text
tests/sql/test_dataq_category_audit.py
```

The test uses:

- `pytest` for one failing test per canonical data-quality category;
- `pydantic` to validate every emitted audit finding;
- `psycopg2` to query local PostgreSQL;
- JSONL logs under `artifacts/qa/`.

## Command

```bash
PGHOST=/tmp PGDATABASE=agentic_migration_local \
UV_CACHE_DIR=/private/tmp/uv-cache \
uv run --no-sync pytest tests/sql/test_dataq_category_audit.py
```

## Current Result

The audit failed as expected because open drifts exist:

```text
6 failed in 636.28s (0:10:36)
```

Failure count by category:

| Category | Audit rows | Failing checks | Sum affected rows |
| --- | ---: | ---: | ---: |
| Accuracy | 12 | 11 | 1338395 |
| Completeness | 37 | 31 | 2595648 |
| Consistency | 50 | 46 | 4488626 |
| Timeliness | 16 | 10 | 1600015 |
| Uniqueness | 5 | 5 | 34823 |
| Validity | 18 | 5 | 612971 |

The affected-row sums are not deduplicated across categories. A single record
can fail multiple quality dimensions, which is expected for this audit.

## Generated Category Logs

| Category | JSONL log |
| --- | --- |
| Accuracy | `artifacts/qa/dataq_accuracy_audit.jsonl` |
| Completeness | `artifacts/qa/dataq_completeness_audit.jsonl` |
| Consistency | `artifacts/qa/dataq_consistency_audit.jsonl` |
| Timeliness | `artifacts/qa/dataq_timeliness_audit.jsonl` |
| Uniqueness | `artifacts/qa/dataq_uniqueness_audit.jsonl` |
| Validity | `artifacts/qa/dataq_validity_audit.jsonl` |

Each JSONL record uses provider/entity/field grain and includes:

- `timestamp`
- `plan_id`
- `model_snapshot`
- `category`
- `check_id`
- `provider`
- `entity`
- `field_column`
- `total_rows`
- `affected_rows`
- `severity`
- `status`
- `evidence_grain`
- `resolution_hint`

No row-level values, PHI/PII samples, or raw payload excerpts are emitted.

## Category Coverage

### Completeness

Scans missing required or expected fields across encounters, medications, cost
records, coverage periods, and observation components.

Examples:

- missing `encounter_datetime`
- missing `medication_datetime`
- missing `cost_date`
- missing `cost_amount`
- unknown or partial coverage period dates
- sparse observation components such as height, weight, BP, and BMI

### Uniqueness

Scans duplicate provider/member/period keys in `coverage_period_fact`.

### Validity

Scans typed/date/domain validity:

- implausible birth dates;
- implausible or inverted coverage dates;
- condition source-code hint mismatches;
- nonpositive cost amount guardrail.

### Consistency

Scans contradictions and cross-entity mismatches:

- demographic conflicts;
- orphan member references;
- orphan encounter references;
- orphan condition references;
- medication code/description variants.

### Timeliness

Scans chronology and time-zone readiness:

- missing business timestamps/dates;
- missing `provider_timezone` contract columns for temporal fact outputs.

### Accuracy

Scans issues that SQL can detect but cannot safely correct without HITL:

- clinical semantic review needed for medication/condition code behavior;
- financial semantic review needed for incomplete cost amount/date behavior.

## Runtime Finding

Because V0_5 derived outputs are PostgreSQL views, the exhaustive audit is
computationally expensive. The 6-category pytest run took 10 minutes and 36
seconds locally. The next scalable step should be materialized dbt audit models
or incremental category metric tables so CI can evaluate data quality without
recomputing every derived view repeatedly.

## Expected Use

This test should fail until the category backlog is remediated or explicit
approved deferrals are encoded. Passing this test too early would be suspicious:
the current purpose is to expose drift, not hide it.
