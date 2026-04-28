# ValleyBridge Medical HITL Queue

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_4_valleybridge_medical`
status: queued_for_pr_review

| Owner | Decision needed | Evidence path | Provider | Entity | Next action |
| --- | --- | --- | --- | --- | --- |
| Human reviewer | Confirm PII/PHI flags for direct identifiers, demographics, clinical fields, coverage status, medication price, and observation payload. | `reports/privacy/data_provider_4_valleybridge_medical.md` | `data_provider_4_valleybridge_medical` | all | Review in PR before Silver modeling. |
| Human reviewer | Confirm relationship hints before using joins in Silver contracts. | `metadata/provider_specs/data_provider_4_valleybridge_medical/` | `data_provider_4_valleybridge_medical` | encounters, conditions, medications, observations | Review in canonical modeling phase. |
| Human reviewer | Confirm `PL_DATA` should remain source text in Raw/Bronze discovery. | `metadata/provider_specs/data_provider_4_valleybridge_medical/observations.yaml` | `data_provider_4_valleybridge_medical` | observations | Preserve payload until approved canonical model. |
| Human reviewer | Confirm the CSV wording in the dictionary is non-blocking drift because local files use commented FHIR STU3 Bundle JSON. | `reports/drift/data_provider_4_valleybridge_medical.md` | `data_provider_4_valleybridge_medical` | all | Review parser profile in PR. |
| Human reviewer | Confirm status fields remain source text until canonical status normalization is approved. | `metadata/provider_specs/data_provider_4_valleybridge_medical/` | `data_provider_4_valleybridge_medical` | all | Defer normalization to canonical modeling. |

No blocking ambiguity was encountered during local source-contract generation. The queue records required governance review before downstream semantic promotion.
