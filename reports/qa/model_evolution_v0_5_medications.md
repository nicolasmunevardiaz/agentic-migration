# Model Evolution V0_5 Medications QA

V0_5 normalizes `review.silver_medications` into local dbt derived views under the
`derived` schema. The source data scope remains solely `data_500k`.

Derived outputs:

- `derived.medication_source_normalized`: 1,606,374 rows.
- `derived.medication_fact`: 1,606,374 rows.
- `derived.medication_code_dimension`: 700 rows.
- `derived.medication_code_variant_dimension`: 1,015 rows.
- `derived.medication_description_variant_dimension`: 1,260 rows.
- `derived.medication_record_status_dimension`: 3 rows.
- `derived.medication_member_summary`: 480,914 rows.

Key QA findings:

- No duplicate provider-scoped medication references were found.
- No missing medication source code or description rows were found.
- 105 provider-scoped normalized codes have raw source-code variants.
- 140 provider-scoped normalized codes have description variants.
- Maximum raw code variants per normalized code: 4.
- Maximum description variants per normalized code: 5.
- 638,728 rows have missing medication datetime.
- 805,499 medication rows have member references that do not match `derived.patient_dimension`.
- 554,329 medication rows have encounter references that do not match `derived.encounter_fact`.
- 770,892 medication rows have condition references that do not match `derived.condition_fact`.

QA status:

- dbt run for seven medication derived views: pass.
- dbt test for medication derived models and custom medication tests: pass, 57/57.

No drug taxonomy, medication class, formulary, financial interpretation, Gold model, or
Databricks parity claim is introduced in this entity addition.
