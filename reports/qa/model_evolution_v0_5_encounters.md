# Model Evolution V0_5 Encounters QA

V0_5 normalizes `review.silver_encounters` into local dbt derived views under
the `derived` schema. The source data scope remains solely `data_500k`.

Derived outputs:

- `derived.encounter_source_normalized`: 535,326 rows.
- `derived.encounter_fact`: 535,326 rows.
- `derived.encounter_coverage_status_dimension`: 3 rows.
- `derived.encounter_record_status_dimension`: 3 rows.
- `derived.encounter_member_summary`: 261,959 rows.

Key QA findings:

- No duplicate provider-scoped encounter references were found.
- BlueStone and ValleyBridge have missing encounter datetimes on every encounter row.
- 297,896 encounter rows have member references that do not match `derived.patient_dimension`
  and are preserved as relationship QA flags.
- No implausible encounter datetimes were found.

QA status:

- dbt run for five encounter derived views: pass.
- dbt test for encounter derived models and custom encounter tests: pass, 34/34.

No clinical interpretation, forced member join, Gold model, or Databricks parity claim is
introduced in this entity addition.
