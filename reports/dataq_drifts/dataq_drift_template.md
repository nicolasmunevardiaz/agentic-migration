# Data Quality Drift Report Template

Report scope: local PostgreSQL/dbt derived models only. Reports must stay
aggregated by provider, entity, and field/column. Do not include row-level
values, raw payload excerpts, PHI/PII samples, or attempted fixes.

## Header

- Report id:
- Model snapshot:
- Data scope:
- Generated from:
- dbt inventory:
- Authoring rule:

## Drift Severity

- Critical: whole-entity coverage gap, 100% missing required field, or drift
  that blocks stable downstream joins.
- High: referential integrity failure, temporal impossibility, duplicate key
  behavior, or field drift affecting more than 10% of an entity/provider slice.
- Medium: field conflicts, sparse-but-expected optional values, or standard
  format drift that can be resolved with provider-specific SQL rules.
- Low: observed variation with no current correctness impact, but worth
  preserving in lineage or metadata.

## Drift Register

Each drift row should follow this grain:

| Drift id | Provider | Entity | Field/column | Category | Total rows | Affected rows | Severity | Evidence source | Candidate SQL resolution | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |

Allowed categories:

- entity_coverage
- nullability
- uniqueness
- referential_integrity
- data_type
- standard_format
- temporal_validity
- semantic_variant
- component_presence

Candidate SQL resolution should be a strategy only. It should not imply that a
fix was applied.

## Evidence Queries

Include the query family or dbt model used for each finding. Prefer aggregated
SQL such as:

```sql
select
  provider_slug,
  count(*) as total_rows,
  count(*) filter (where <drift_predicate>) as affected_rows
from derived.<model>
group by provider_slug
order by provider_slug;
```

## Review Notes

- HITL required:
- Dependencies before remediation:
- Recommended next action:
