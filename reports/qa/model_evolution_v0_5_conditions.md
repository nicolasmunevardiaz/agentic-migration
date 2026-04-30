# Model Evolution V0_5 Conditions QA

V0_5 normalizes `review.silver_conditions` into local dbt derived views under the
`derived` schema. The source data scope remains solely `data_500k`.

Derived outputs:

- `derived.condition_source_normalized`: 803,595 rows.
- `derived.condition_fact`: 803,595 rows.
- `derived.condition_code_dimension`: 320 rows.
- `derived.condition_record_status_dimension`: 3 rows.
- `derived.condition_member_summary`: 369,363 rows.

Key QA findings:

- No duplicate provider-scoped condition references were found.
- No missing source code, code hint, or description rows were found.
- 402,976 condition rows have member references that do not match `derived.patient_dimension`.
- 277,300 condition rows have encounter references that do not match `derived.encounter_fact`.
- Aegis source code equals code hint for 192,286 rows; the duplicate-code semantics remain
  source facts and are not clinically interpreted.

QA status:

- dbt run for five condition derived views: pass.
- dbt test for condition derived models and custom condition tests: pass, 36/36.

No diagnosis hierarchy, code crosswalk, clinical interpretation, Gold model, or Databricks
parity claim is introduced in this entity addition.
