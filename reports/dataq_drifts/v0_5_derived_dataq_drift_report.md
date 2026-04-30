# V0_5 Derived Data Quality Drift Report

Report id: `DATAQ_DRIFT_V0_5_2026_04_30`
Model snapshot: `metadata/model_specs/evolution/V0_5/model_snapshot.yaml`
Data scope: local `data_500k` loaded into PostgreSQL database
`agentic_migration_local`.
Generated from: PostgreSQL `derived` schema plus dbt model inventory.
Authoring rule: no remediation was applied; findings are aggregated by
provider, entity, and field/column only.
Companion matrix: `reports/dataq_drifts/v0_5_derived_dataq_drift_matrix.tsv`.
Category backlog: `reports/dataq_drifts/v0_5_dataq_category_backlog.md`.
Category matrix: `reports/dataq_drifts/v0_5_dataq_category_matrix.tsv`.

## dbt Scope

dbt inventory found 48 models, 263 data tests, 7 sources, and 469 macros.
The active `derived` selection contains 32 models across patients,
observations, coverage, encounters, conditions, medications, and cost records.

## Entity Coverage

| Provider | Patients | Coverage | Encounters | Conditions | Observations | Medications | Cost records |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| data_provider_1_aegis_care_network | 76825 | 76825 | 128019 | 192286 | 128019 | 384514 | 384514 |
| data_provider_2_bluestone_health | 102719 | 102719 | 169468 | 254161 | 169468 | 507900 | 507900 |
| data_provider_3_northcare_clinics | 51462 | 51462 | 84752 | 127181 | 84752 | 254214 | 254214 |
| data_provider_4_valleybridge_medical | 92414 | 92414 | 153087 | 229967 | 153087 | 459746 | 459746 |
| data_provider_5_pacific_shield_insurance | 552340 | 552340 | 0 | 0 | 0 | 0 | 0 |

Drift: Pacific Shield currently has patient and coverage-derived rows only.
Candidate SQL resolution: keep the provider/entity availability matrix as a
control table, then exclude missing clinical/cost entities from completeness
rules unless the provider contract declares them required.

## Data Type Findings

No provider-specific physical column type drift can exist inside one PostgreSQL
derived table because each dbt model materializes one schema-level type per
column. The observed data-type risks are therefore typed-value symptoms after
normalization:

| Entity | Field/column | Data type symptom | Providers affected |
| --- | --- | --- | --- |
| patients | birth_date | conflicting or implausible typed dates | BlueStone, NorthCare, Pacific Shield |
| coverage_periods | coverage_start_date/coverage_end_date | missing, end-date-only, or implausible typed dates | all providers |
| encounters | encounter_datetime | fully missing typed timestamp | BlueStone, ValleyBridge |
| medications | medication_datetime | fully missing typed timestamp | Aegis, NorthCare |
| cost_records | cost_date | fully missing typed date | Aegis, NorthCare |
| cost_records | cost_amount | nullable typed numeric amount | all clinical/cost providers |

No nonpositive cost amounts were observed after numeric casting.

## Drift Register

### Patients

| Drift id | Provider | Entity | Field/column | Category | Total rows | Affected rows | Severity | Candidate SQL resolution | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| DQ-PAT-001 | data_provider_1_aegis_care_network | patients | gender | standard_format | 61915 | 1097 | Medium | Create provider-scoped gender precedence and conflict rules before dimension promotion. | Open |
| DQ-PAT-002 | data_provider_2_bluestone_health | patients | gender | standard_format | 79613 | 2967 | Medium | Create provider-scoped gender precedence and conflict rules before dimension promotion. | Open |
| DQ-PAT-003 | data_provider_3_northcare_clinics | patients | gender | standard_format | 41297 | 745 | Medium | Create provider-scoped gender precedence and conflict rules before dimension promotion. | Open |
| DQ-PAT-004 | data_provider_4_valleybridge_medical | patients | gender | standard_format | 74234 | 1384 | Medium | Create provider-scoped gender precedence and conflict rules before dimension promotion. | Open |
| DQ-PAT-005 | data_provider_5_pacific_shield_insurance | patients | gender | standard_format | 222754 | 3511 | Medium | Create provider-scoped gender precedence and conflict rules before dimension promotion. | Open |
| DQ-PAT-006 | data_provider_2_bluestone_health | patients | birth_date | temporal_validity | 79613 | 4488 | High | Add source-date ranking and survivor rule for conflicting member birth dates. | Open |
| DQ-PAT-007 | data_provider_5_pacific_shield_insurance | patients | birth_date | temporal_validity | 222754 | 5469 | High | Add source-date ranking and survivor rule for conflicting member birth dates. | Open |
| DQ-PAT-008 | data_provider_3_northcare_clinics | patients | birth_date | temporal_validity | 41297 | 92 | Medium | Add birth-date bounds check and quarantine invalid dates before dimensional publish. | Open |

### Coverage

| Drift id | Provider | Entity | Field/column | Category | Total rows | Affected rows | Severity | Candidate SQL resolution | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| DQ-COV-001 | data_provider_1_aegis_care_network | coverage_periods | provider/member/plan/period key | uniqueness | 76825 | 4686 | High | Build deterministic period key with source row tiebreaker or merge exact duplicate intervals. | Open |
| DQ-COV-002 | data_provider_2_bluestone_health | coverage_periods | provider/member/plan/period key | uniqueness | 102719 | 233 | Medium | Build deterministic period key with source row tiebreaker or merge exact duplicate intervals. | Open |
| DQ-COV-003 | data_provider_3_northcare_clinics | coverage_periods | provider/member/plan/period key | uniqueness | 51462 | 2983 | High | Build deterministic period key with source row tiebreaker or merge exact duplicate intervals. | Open |
| DQ-COV-004 | data_provider_4_valleybridge_medical | coverage_periods | provider/member/plan/period key | uniqueness | 92414 | 5766 | High | Build deterministic period key with source row tiebreaker or merge exact duplicate intervals. | Open |
| DQ-COV-005 | data_provider_5_pacific_shield_insurance | coverage_periods | provider/member/plan/period key | uniqueness | 552340 | 21155 | High | Build deterministic period key with source row tiebreaker or merge exact duplicate intervals. | Open |
| DQ-COV-006 | data_provider_3_northcare_clinics | coverage_periods | coverage_start_date/coverage_end_date | temporal_validity | 51462 | 1570 | High | Apply provider-specific date parser and invalid-date quarantine before period calculations. | Open |
| DQ-COV-007 | data_provider_1_aegis_care_network | coverage_periods | coverage_start_date/coverage_end_date | nullability | 76825 | 76825 | Critical | Represent unknown coverage span explicitly; do not infer period without approved source rule. | Open |
| DQ-COV-008 | data_provider_3_northcare_clinics | coverage_periods | coverage_start_date/coverage_end_date | nullability | 51462 | 49892 | Critical | Represent unknown coverage span explicitly; do not infer period without approved source rule. | Open |
| DQ-COV-009 | data_provider_4_valleybridge_medical | coverage_periods | coverage_start_date/coverage_end_date | nullability | 92414 | 92414 | Critical | Represent unknown coverage span explicitly; do not infer period without approved source rule. | Open |
| DQ-COV-010 | data_provider_5_pacific_shield_insurance | coverage_periods | coverage_start_date | nullability | 552340 | 295062 | Critical | Separate end-date-only coverage records into a transition model until start-date semantics are approved. | Open |

### Encounters

| Drift id | Provider | Entity | Field/column | Category | Total rows | Affected rows | Severity | Candidate SQL resolution | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| DQ-ENC-001 | data_provider_2_bluestone_health | encounters | encounter_datetime | nullability | 169468 | 169468 | Critical | Use provider-specific date extraction only if approved; otherwise flag unknown encounter chronology. | Open |
| DQ-ENC-002 | data_provider_4_valleybridge_medical | encounters | encounter_datetime | nullability | 153087 | 153087 | Critical | Use provider-specific date extraction only if approved; otherwise flag unknown encounter chronology. | Open |
| DQ-ENC-003 | data_provider_1_aegis_care_network | encounters | member_reference | referential_integrity | 128019 | 80718 | Critical | Normalize member reference formats before joining to `patient_dimension`; preserve unresolved refs. | Open |
| DQ-ENC-004 | data_provider_2_bluestone_health | encounters | member_reference | referential_integrity | 169468 | 66659 | High | Normalize member reference formats before joining to `patient_dimension`; preserve unresolved refs. | Open |
| DQ-ENC-005 | data_provider_3_northcare_clinics | encounters | member_reference | referential_integrity | 84752 | 53583 | Critical | Normalize member reference formats before joining to `patient_dimension`; preserve unresolved refs. | Open |
| DQ-ENC-006 | data_provider_4_valleybridge_medical | encounters | member_reference | referential_integrity | 153087 | 96936 | Critical | Normalize member reference formats before joining to `patient_dimension`; preserve unresolved refs. | Open |

### Conditions

| Drift id | Provider | Entity | Field/column | Category | Total rows | Affected rows | Severity | Candidate SQL resolution | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| DQ-CON-001 | data_provider_1_aegis_care_network | conditions | member_reference | referential_integrity | 192286 | 113940 | Critical | Normalize member references and validate against provider-scoped patient dimension. | Open |
| DQ-CON-002 | data_provider_2_bluestone_health | conditions | member_reference | referential_integrity | 254161 | 77111 | High | Normalize member references and validate against provider-scoped patient dimension. | Open |
| DQ-CON-003 | data_provider_3_northcare_clinics | conditions | member_reference | referential_integrity | 127181 | 75404 | Critical | Normalize member references and validate against provider-scoped patient dimension. | Open |
| DQ-CON-004 | data_provider_4_valleybridge_medical | conditions | member_reference | referential_integrity | 229967 | 136521 | Critical | Normalize member references and validate against provider-scoped patient dimension. | Open |
| DQ-CON-005 | data_provider_1_aegis_care_network | conditions | encounter_reference | referential_integrity | 192286 | 77285 | Critical | Normalize encounter references and retain unresolved references in a bridge audit model. | Open |
| DQ-CON-006 | data_provider_2_bluestone_health | conditions | encounter_reference | referential_integrity | 254161 | 56747 | High | Normalize encounter references and retain unresolved references in a bridge audit model. | Open |
| DQ-CON-007 | data_provider_3_northcare_clinics | conditions | encounter_reference | referential_integrity | 127181 | 50845 | Critical | Normalize encounter references and retain unresolved references in a bridge audit model. | Open |
| DQ-CON-008 | data_provider_4_valleybridge_medical | conditions | encounter_reference | referential_integrity | 229967 | 92423 | Critical | Normalize encounter references and retain unresolved references in a bridge audit model. | Open |
| DQ-CON-009 | data_provider_2_bluestone_health | conditions | condition_source_code | standard_format | 254161 | 254161 | Critical | Build provider-specific code-system/source hint mapping before using source-code semantics. | Open |
| DQ-CON-010 | data_provider_3_northcare_clinics | conditions | condition_source_code | standard_format | 127181 | 127181 | Critical | Build provider-specific code-system/source hint mapping before using source-code semantics. | Open |
| DQ-CON-011 | data_provider_4_valleybridge_medical | conditions | condition_source_code | standard_format | 229967 | 229967 | Critical | Build provider-specific code-system/source hint mapping before using source-code semantics. | Open |

### Observations

| Drift id | Provider | Entity | Field/column | Category | Total rows | Affected rows | Severity | Candidate SQL resolution | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| DQ-OBS-001 | data_provider_1_aegis_care_network | observations | vital components | component_presence | 128019 | 34490 | High | Keep vitals wide plus component table; derive completeness flags per component and provider. | Open |
| DQ-OBS-002 | data_provider_2_bluestone_health | observations | vital components | component_presence | 169468 | 45810 | High | Keep vitals wide plus component table; derive completeness flags per component and provider. | Open |
| DQ-OBS-003 | data_provider_3_northcare_clinics | observations | vital components | component_presence | 84752 | 22863 | High | Keep vitals wide plus component table; derive completeness flags per component and provider. | Open |
| DQ-OBS-004 | data_provider_4_valleybridge_medical | observations | vital components | component_presence | 153087 | 41459 | High | Keep vitals wide plus component table; derive completeness flags per component and provider. | Open |

Observation detail: height, weight, blood pressure, pulse, and temperature are
roughly 10% sparse per provider; BMI is roughly 27% sparse per provider.
Extractor consistency for height, weight, and systolic blood pressure has zero
observed mismatches against Silver extracts.

Observation component detail:

| Provider | Total rows | Missing height | Missing weight | Missing BP pair | Missing pulse | Missing temperature | Missing BMI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| data_provider_1_aegis_care_network | 128019 | 12882 | 12640 | 12831 | 13066 | 12807 | 34490 |
| data_provider_2_bluestone_health | 169468 | 16883 | 17012 | 17079 | 16989 | 17104 | 45810 |
| data_provider_3_northcare_clinics | 84752 | 8426 | 8516 | 8550 | 8547 | 8492 | 22863 |
| data_provider_4_valleybridge_medical | 153087 | 15214 | 15300 | 15622 | 15506 | 15465 | 41459 |

### Medications

| Drift id | Provider | Entity | Field/column | Category | Total rows | Affected rows | Severity | Candidate SQL resolution | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| DQ-MED-001 | data_provider_1_aegis_care_network | medications | medication_datetime | nullability | 384514 | 384514 | Critical | Preserve null medication chronology until an approved provider date source is identified. | Open |
| DQ-MED-002 | data_provider_3_northcare_clinics | medications | medication_datetime | nullability | 254214 | 254214 | Critical | Preserve null medication chronology until an approved provider date source is identified. | Open |
| DQ-MED-003 | data_provider_1_aegis_care_network | medications | member_reference | referential_integrity | 384514 | 227703 | Critical | Normalize medication member references before dimensional joins; keep unresolved refs auditable. | Open |
| DQ-MED-004 | data_provider_2_bluestone_health | medications | member_reference | referential_integrity | 507900 | 154861 | High | Normalize medication member references before dimensional joins; keep unresolved refs auditable. | Open |
| DQ-MED-005 | data_provider_3_northcare_clinics | medications | member_reference | referential_integrity | 254214 | 150425 | Critical | Normalize medication member references before dimensional joins; keep unresolved refs auditable. | Open |
| DQ-MED-006 | data_provider_4_valleybridge_medical | medications | member_reference | referential_integrity | 459746 | 272510 | Critical | Normalize medication member references before dimensional joins; keep unresolved refs auditable. | Open |
| DQ-MED-007 | data_provider_1_aegis_care_network | medications | medication_source_code | semantic_variant | 175 | 35 | Medium | Retain variant dimension and decide canonical medication-code display after HITL review. | Open |
| DQ-MED-008 | data_provider_2_bluestone_health | medications | medication_description | semantic_variant | 175 | 35 | Medium | Retain variant dimension and decide canonical medication-description display after HITL review. | Open |
| DQ-MED-009 | data_provider_3_northcare_clinics | medications | medication_source_code | semantic_variant | 175 | 35 | Medium | Retain variant dimension and decide canonical medication-code display after HITL review. | Open |
| DQ-MED-010 | data_provider_4_valleybridge_medical | medications | medication_source_code | semantic_variant | 175 | 35 | Medium | Retain variant dimension and decide canonical medication-code display after HITL review. | Open |

Medication referential drift also affects encounter and condition references:
Aegis has 154480 orphan encounter refs and 230250 orphan condition refs;
BlueStone has 113506 and 112263; NorthCare has 101839 and 152652;
ValleyBridge has 184504 and 275727.

Medication semantic variant detail:

| Provider | Normalized code rows | Raw-code variant codes | Description variant codes | Max raw-code variants | Max description variants |
| --- | ---: | ---: | ---: | ---: | ---: |
| data_provider_1_aegis_care_network | 175 | 35 | 35 | 4 | 5 |
| data_provider_2_bluestone_health | 175 | 0 | 35 | 1 | 5 |
| data_provider_3_northcare_clinics | 175 | 35 | 35 | 4 | 5 |
| data_provider_4_valleybridge_medical | 175 | 35 | 35 | 4 | 5 |

### Cost Records

| Drift id | Provider | Entity | Field/column | Category | Total rows | Affected rows | Severity | Candidate SQL resolution | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| DQ-CST-001 | data_provider_1_aegis_care_network | cost_records | cost_amount | nullability | 384514 | 34982 | Medium | Keep amount source dimension and add provider-scoped amount completeness flag. | Open |
| DQ-CST-002 | data_provider_2_bluestone_health | cost_records | cost_amount | nullability | 507900 | 46321 | Medium | Keep amount source dimension and add provider-scoped amount completeness flag. | Open |
| DQ-CST-003 | data_provider_3_northcare_clinics | cost_records | cost_amount | nullability | 254214 | 23175 | Medium | Keep amount source dimension and add provider-scoped amount completeness flag. | Open |
| DQ-CST-004 | data_provider_4_valleybridge_medical | cost_records | cost_amount | nullability | 459746 | 41897 | Medium | Keep amount source dimension and add provider-scoped amount completeness flag. | Open |
| DQ-CST-005 | data_provider_1_aegis_care_network | cost_records | cost_date | nullability | 384514 | 384514 | Critical | Do not infer cost chronology from medication/encounter until date lineage is approved. | Open |
| DQ-CST-006 | data_provider_3_northcare_clinics | cost_records | cost_date | nullability | 254214 | 254214 | Critical | Do not infer cost chronology from medication/encounter until date lineage is approved. | Open |
| DQ-CST-007 | data_provider_1_aegis_care_network | cost_records | member_reference | referential_integrity | 384514 | 227703 | Critical | Normalize cost member references before member-level financial summaries. | Open |
| DQ-CST-008 | data_provider_2_bluestone_health | cost_records | member_reference | referential_integrity | 507900 | 154861 | High | Normalize cost member references before member-level financial summaries. | Open |
| DQ-CST-009 | data_provider_3_northcare_clinics | cost_records | member_reference | referential_integrity | 254214 | 150425 | Critical | Normalize cost member references before member-level financial summaries. | Open |
| DQ-CST-010 | data_provider_4_valleybridge_medical | cost_records | member_reference | referential_integrity | 459746 | 272510 | Critical | Normalize cost member references before member-level financial summaries. | Open |

No nonpositive cost amounts were observed in `derived.cost_record_fact`.
No orphan medication references were observed from cost records to
`derived.medication_fact`.

Cost record referential detail:

| Provider | Total rows | Orphan member refs | Orphan encounter refs | Orphan medication refs |
| --- | ---: | ---: | ---: | ---: |
| data_provider_1_aegis_care_network | 384514 | 227703 | 154480 | 0 |
| data_provider_2_bluestone_health | 507900 | 154861 | 113506 | 0 |
| data_provider_3_northcare_clinics | 254214 | 150425 | 101839 | 0 |
| data_provider_4_valleybridge_medical | 459746 | 272510 | 184504 | 0 |

## Guardrail Findings With No Current Drift

- `condition_fact` has no missing condition source code or condition
  description rows.
- `medication_fact` has no missing medication source code or medication
  description rows.
- `cost_record_fact` has no nonpositive cost amounts.
- `observation_vitals_wide` has zero height, weight, and systolic extract
  mismatches against the Silver-derived extracts.
- `coverage_period_fact` has zero inverted date rows in the current profile.

## Evidence Query Families

The report was produced from provider-grouped SQL over these dbt outputs:

- `derived.patient_dimension`: gender conflict, birth-date conflict, and
  implausible birth-date counts.
- `derived.coverage_period_fact`: duplicate period keys, implausible dates,
  inverted dates, undated rows, and end-date-only rows.
- `derived.encounter_fact`: missing encounter datetime, orphan member reference,
  and implausible datetime counts.
- `derived.condition_fact`: orphan member/encounter references, source-code hint
  mismatch, missing source code, and missing description counts.
- `derived.observation_vitals_wide`: component sparsity and Silver extract
  mismatch counts.
- `derived.medication_fact` and `derived.medication_code_dimension`: missing
  datetime, orphan references, missing code/description, and semantic variants.
- `derived.cost_record_fact`: missing amount/date, nonpositive amount, and
  orphan reference counts.

Generic query shape:

```sql
select
  provider_slug,
  count(*) as total_rows,
  count(*) filter (where <drift_predicate>) as affected_rows
from derived.<model_name>
group by provider_slug
order by provider_slug;
```

## Recommended Next SQL Work

1. Build provider/entity/field data-quality marts from this register so each
   drift has a stable SQL test predicate.
2. Add transition models for unresolved references instead of dropping rows.
3. Separate provider availability checks from defect checks so insurance-only
   providers do not fail clinical completeness rules by default.
4. Keep remediation behind a new normalization probe; this report is evidence
   only and should not change V0_5 model behavior.
