# ValleyBridge Medical Privacy And Governance Review

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_4_valleybridge_medical`
status: pass_with_human_review_queue

## Sensitive Field Classes

- Direct identifiers: member names and `PATIENT_SSN`.
- Linkable identifiers: member, encounter, condition, medication, observation, and relationship reference fields.
- Demographics: gender and birth date.
- Clinical PHI: diagnosis hints, condition descriptions, medication identifiers, medication descriptions, observation payloads, and clinical dates.
- Financial signal: medication unit price.
- Coverage signal: `COVERAGE_STATUS`.

## Review Result

- Provider specs conservatively flag sensitive fields with `pii_signal: true`.
- Synthetic fixtures do not copy raw source values.
- Evidence files do not include local absolute paths or raw sensitive examples.
- No new dependencies were added.
- No Databricks, Terraform, cloud, permission, secret, or production-impacting action was performed.

## Required Human Review

- Confirm PII/PHI classifications.
- Confirm relationship hints before Silver joins.
- Confirm that `PL_DATA` remains preserved as source text until canonical modeling.
- Confirm financial handling for `MED_UNIT_PRICE` before Silver semantics.
- Confirm status normalization rules before downstream canonical contracts.
- Confirm that commented FHIR STU3 parsing is the approved source contract despite the dictionary's CSV wording.
