# BlueStone Health HITL Queue

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_2_bluestone_health`
status: queued_for_pr_review

| Owner | Decision needed | Evidence path | Provider | Entity | Next action |
| --- | --- | --- | --- | --- | --- |
| Human reviewer | Confirm PII/PHI flags for direct identifiers, clinical payloads, coverage status, and medication price. | `reports/privacy/data_provider_2_bluestone_health.md` | `data_provider_2_bluestone_health` | all | Review in PR before Silver modeling. |
| Human reviewer | Confirm relationship hints before using joins in Silver contracts. | `metadata/provider_specs/data_provider_2_bluestone_health/` | `data_provider_2_bluestone_health` | encounters, conditions, medications, observations | Review in canonical modeling phase. |
| Human reviewer | Confirm `OBS_JSON` should remain source text in Raw/Bronze discovery. | `metadata/provider_specs/data_provider_2_bluestone_health/observations.yaml` | `data_provider_2_bluestone_health` | observations | Preserve payload until approved canonical model. |

No blocking ambiguity was encountered during local source-contract generation. The queue records required governance review before downstream semantic promotion.
