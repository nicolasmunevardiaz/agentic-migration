# V0_5 Cost Records Derived QA

## Scope

- Active model snapshot: `metadata/model_specs/evolution/V0_5/`
- Source relation: `review.silver_cost_records`
- Source data scope: `data_500k` batch `plan-04-5-v0-3-data-500k`
- dbt derived models: `dbt/models/derived/cost_records/`
- dbt tests: `dbt/tests/derived/cost_records/`

## Derived Outputs

| Relation | Row count | Grain |
| --- | ---: | --- |
| `derived.cost_record_source_normalized` | 1,606,374 | one provider-scoped medication financial source row |
| `derived.cost_record_fact` | 1,606,374 | one provider-scoped medication financial source fact |
| `derived.cost_amount_source_dimension` | 4 | one provider-scoped source financial amount field |
| `derived.cost_record_status_dimension` | 3 | one status observed in active batch |
| `derived.cost_record_member_summary` | 480,914 | one provider-scoped member reference |

## Provider Summary

| Provider | Fact rows | Missing amount | Missing date | Orphan member ref | Orphan encounter ref | Orphan medication ref |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `data_provider_1_aegis_care_network` | 384,514 | 34,982 | 384,514 | 227,703 | 154,480 | 0 |
| `data_provider_2_bluestone_health` | 507,900 | 46,321 | 0 | 154,861 | 113,506 | 0 |
| `data_provider_3_northcare_clinics` | 254,214 | 23,175 | 254,214 | 150,425 | 101,839 | 0 |
| `data_provider_4_valleybridge_medical` | 459,746 | 41,897 | 0 | 272,510 | 184,504 | 0 |

## Source Amount Fields

| Provider | Source field | Rows | Populated amount | Missing amount |
| --- | --- | ---: | ---: | ---: |
| `data_provider_1_aegis_care_network` | `UNIT_COST` | 384,514 | 349,532 | 34,982 |
| `data_provider_2_bluestone_health` | `RX_UNIT_AMT` | 507,900 | 461,579 | 46,321 |
| `data_provider_3_northcare_clinics` | `MED_PRICE` | 254,214 | 231,039 | 23,175 |
| `data_provider_4_valleybridge_medical` | `LINE_PRICE` | 459,746 | 417,849 | 41,897 |

## Quality Status Counts

| Status | Rows |
| --- | ---: |
| `review_missing_date` | 580,571 |
| `review_orphan_member_reference` | 392,697 |
| `complete` | 338,750 |
| `review_orphan_encounter_reference` | 147,981 |
| `review_missing_amount` | 146,375 |

## Validation

- `dbt run --select path:models/derived/cost_records`: pass, 5 views.
- `dbt test --select path:models/derived/cost_records path:tests/derived/cost_records`: pass, 42 tests.

## Governance Notes

- No financial interpretation, benchmark, payment conclusion, or Gold output was introduced.
- `source_cost_amount` remains a provider-scoped PHI financial source fact with source-field lineage.
- All relationship gaps remain explicit QA flags rather than inferred fixes.
