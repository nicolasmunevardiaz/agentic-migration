# V0_5 Data Quality Programmatic Validation

Report id: `DATAQ_PROGRAMMATIC_VALIDATION_V0_5_2026_04_30`
Scope: report-contract validation only. This validation does not resolve data
quality drifts, mutate dbt models, or write to PostgreSQL.

## Validation Objective

The drift reports now have two layers:

- Granular evidence: `v0_5_derived_dataq_drift_matrix.tsv`
- Category backlog: `v0_5_dataq_category_matrix.tsv` and
  `v0_5_dataq_category_backlog.md`

The new unit test validates that those files behave like governed contracts
instead of free-form documentation.

## Test Artifact

Unit test: `tests/specs/test_dataq_drift_reports.py`

The test uses Pydantic models to validate:

- exact TSV headers;
- drift id prefixes by entity family;
- allowed granular categories;
- allowed canonical data-quality categories;
- severity and status domains;
- non-negative counts;
- `affected_rows <= total_rows`;
- expected granular drift count by category;
- uniqueness of drift ids and category drift ids;
- coverage from every granular `resolution_hint` into a category backlog item;
- backlinks from the primary report into the category artifacts;
- presence of every category id in the category backlog narrative.

## Current Expected Contract

Granular drift matrix:

| Granular category | Expected rows |
| --- | ---: |
| component_presence | 24 |
| nullability | 18 |
| referential_integrity | 32 |
| semantic_variant | 7 |
| standard_format | 8 |
| temporal_validity | 4 |
| uniqueness | 5 |

Category matrix:

| Canonical category | Required |
| --- | --- |
| Accuracy | yes |
| Completeness | yes |
| Consistency | yes |
| Timeliness | yes |
| Uniqueness | yes |
| Validity | yes |

## Command

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync pytest tests/specs/test_dataq_drift_reports.py
```

Current result:

```text
tests/specs/test_dataq_drift_reports.py ...... [100%]
6 passed
```

Lint command:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-sync ruff check tests/specs/test_dataq_drift_reports.py
```

Current result:

```text
All checks passed!
```

## Intended Failure Modes

The test should fail if:

- a report row is edited manually and breaks TSV shape;
- a new drift category appears without being added to the contract;
- a new resolution strategy is introduced without a category backlog mapping;
- counts are negative or affected counts exceed totals;
- category docs drift away from the machine-readable matrix;
- the primary report stops linking to the category backlog.

## Limitation

This is a report-contract unit test. It confirms that mapped findings are
complete and governed, but it does not re-profile PostgreSQL. The next stronger
layer should be dbt audit models that materialize category metrics directly
from the `derived` schema.

## Stronger PostgreSQL Audit

The stronger PostgreSQL-backed audit is documented separately:

```text
reports/dataq_drifts/v0_5_dataq_exhaustive_pytest_audit.md
```

It runs `tests/sql/test_dataq_category_audit.py`, emits one JSONL log per
category under `artifacts/qa/`, and is expected to fail while open drifts remain.
