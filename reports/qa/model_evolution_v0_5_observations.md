# Model Evolution V0_5 Observations Nested QA

V0_5 decomposes `review.silver_observations.observation_payload_raw` into local dbt
derived views under the `derived` schema. The source data scope remains solely
`data_500k`.

Derived outputs:

- `derived.observation_payload_source_normalized`: 535,326 rows.
- `derived.observation_vitals_wide`: 535,326 rows.
- `derived.observation_vital_components`: 3,279,647 rows.

Nested components promoted:

- `height_cm` in `cm`: 481,921 rows.
- `weight_kg` in `kg`: 481,858 rows.
- `systolic_bp` in `mmHg`: 481,244 rows.
- `diastolic_bp` in `mmHg`: 481,244 rows.
- `pulse_lpm` in `lpm`: 481,218 rows.
- `temperature_c` in `C`: 481,458 rows.
- `bmi` in `kg/m2`: 390,704 rows.

QA status:

- dbt compile for observation derived models: pass.
- dbt run for three observation derived views: pass.
- dbt test for observation derived models and custom nested tests: pass, 27/27.
- Silver extract consistency for height, weight, and systolic blood pressure: 0 mismatches.

No raw payload values, PII, PHI examples, clinical interpretation, Gold model, or
Databricks parity claim are introduced in this iteration.
