# Model Evolution V0_5 Coverage QA

V0_5 normalizes `review.silver_coverage_periods` into local dbt derived views under
the `derived` schema. The source data scope remains solely `data_500k`.

Derived outputs:

- `derived.coverage_source_normalized`: 875,760 rows.
- `derived.coverage_period_fact`: 875,760 rows.
- `derived.coverage_status_dimension`: 2 rows.
- `derived.coverage_member_summary`: 479,813 rows.

Key QA findings:

- No inverted coverage date ranges were found.
- 1,570 NorthCare rows have implausible historical dates and are flagged, not corrected.
- 34,823 rows participate in duplicate provider/member/status/date period keys.
- Pacific Shield has coverage rows for every provider-scoped member and every member has
  multiple coverage statuses in the active local batch.

QA status:

- dbt compile for coverage derived models: pass.
- dbt run for four coverage derived views: pass.
- dbt test for coverage derived models and custom coverage tests: pass, 30/30.

No current eligibility inference, financial interpretation, Gold model, or Databricks
parity claim is introduced in this iteration.
