# Pacific Shield Insurance HITL Queue

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_5_pacific_shield_insurance`
status: `review_required_non_blocking_for_provider_discovery`

| Owner | Decision | Date | Evidence path | Provider | Entity | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| Data governance reviewer | Confirm `claims_export` source type or replace it during canonical modeling. | 2026-04-28 | `reports/drift/data_provider_5_pacific_shield_insurance.md` | `data_provider_5_pacific_shield_insurance` | all | Keep neutral source type in provider specs until reviewed. |
| Privacy reviewer | Confirm PII/PHI field flags and redaction expectations. | 2026-04-28 | `reports/privacy/data_provider_5_pacific_shield_insurance.md` | `data_provider_5_pacific_shield_insurance` | all | Do not downgrade sensitive fields without approval. |
| Data model reviewer | Decide how duplicate `DX_CD` should feed canonical condition modeling. | 2026-04-28 | `metadata/provider_specs/data_provider_5_pacific_shield_insurance/conditions.yaml` | `data_provider_5_pacific_shield_insurance` | conditions | Preserve both positions in Raw/Bronze until canonical decision. |
| Data quality reviewer | Review sparse local clinical source coverage and decide whether additional source evidence is needed. | 2026-04-28 | `reports/drift/data_provider_5_pacific_shield_insurance.md` | `data_provider_5_pacific_shield_insurance` | encounters, conditions, medications, observations | Treat as non-blocking for provider specs; block Databricks validation until reviewed. |
| Data model reviewer | Confirm relationship confidence for member, encounter, condition, medication, and observation references. | 2026-04-28 | `metadata/provider_specs/data_provider_5_pacific_shield_insurance/` | `data_provider_5_pacific_shield_insurance` | all | Keep relationship hints as source evidence only. |

## Blocked Next Actions

- Do not approve Databricks execution from this provider discovery output.
- Do not finalize payer-vs-clinical semantics in Silver models.
- Do not collapse duplicate `DX_CD` fields into one canonical meaning without review.
