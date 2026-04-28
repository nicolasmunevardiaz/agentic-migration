# NorthCare Clinics HITL Queue

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_3_northcare_clinics`
status: queued_for_pr_review

| Owner | Decision needed | Evidence path | Provider | Entity | Next action |
| --- | --- | --- | --- | --- | --- |
| Human reviewer | Confirm PII/PHI flags for direct identifiers, demographics, clinical fields, coverage status, medication price, and observation payload. | `reports/privacy/data_provider_3_northcare_clinics.md` | `data_provider_3_northcare_clinics` | all | Review in PR before Silver modeling. |
| Human reviewer | Confirm relationship hints before using joins in Silver contracts. | `metadata/provider_specs/data_provider_3_northcare_clinics/` | `data_provider_3_northcare_clinics` | encounters, conditions, medications, observations | Review in canonical modeling phase. |
| Human reviewer | Confirm `OBS_PAYLOAD` should remain source text in Raw/Bronze discovery. | `metadata/provider_specs/data_provider_3_northcare_clinics/observations.yaml` | `data_provider_3_northcare_clinics` | observations | Preserve payload until approved canonical model. |
| Human reviewer | Confirm the CSV wording in the dictionary is non-blocking drift because local files use X12-style envelopes. | `reports/drift/data_provider_3_northcare_clinics.md` | `data_provider_3_northcare_clinics` | all | Review parser profile in PR. |

No blocking ambiguity was encountered during local source-contract generation. The queue records required governance review before downstream semantic promotion.
