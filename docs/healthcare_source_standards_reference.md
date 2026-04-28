# Healthcare Source Standards Reference

This migration treats healthcare standards as source dialects, not as the canonical model itself. Provider specs describe how each source speaks; Bronze preserves that source truth; canonical and Silver contracts decide what the platform standardizes.

## Provider Dialects

| Provider pattern | Project provider | What it means here |
| --- | --- | --- |
| `provider_a/x12_837` | X12 claim archetype | X12 837 is the EDI transaction used to send health care claim billing information, encounter information, or both from providers to payers. In this repo, NorthCare uses an X12-like segment envelope rather than a full final X12 837 implementation. |
| `provider_b/x12_835` | X12 remittance archetype | X12 835 is the EDI transaction used for health care claim payment/advice, including payment, remittance advice, or both. It is a payer-to-provider financial response pattern and should not be modeled as clinical truth. |
| `provider_c/hl7_v2` | BlueStone Health | HL7 v2 is a message-oriented clinical/admin exchange family. BlueStone stores HL7 v2-style XML messages, so parser adapters must validate message segments and preserve source values before any semantic interpretation. |
| `provider_d/fhir` | Aegis Care Network and ValleyBridge Medical | FHIR represents health data as structured resources. Aegis uses FHIR R4-style bundles; ValleyBridge uses FHIR STU3-style bundles with source comments and encoding drift. |
| `provider_e/custom_flat_file` | Pacific Shield Insurance | Custom CSV/flat-file claims exports have no external semantic contract. The YAML provider spec therefore becomes the executable source contract, including header order, row key, drift notes, and privacy review flags. |

## Why Differences Matter

Different standards encode different business intent. X12 claim/remittance files emphasize billing and payment workflows, HL7 v2 emphasizes event messages between health systems, FHIR emphasizes resource exchange, and custom flat files reflect provider-local exports. If we flatten those too early, we risk losing lineage, mixing payer and clinical semantics, normalizing fields incorrectly, or treating provider-local identifiers as enterprise identities.

## Mitigation

We isolate each dialect behind provider-specific parser profiles and runtime-neutral adapter interfaces. Bronze keeps source payloads, headers, row keys, parser family, and drift evidence. Canonical contracts map only reviewed fields into common platform names. Silver models remain downstream and approval-gated. Local runtime certification validates parser -> Bronze -> canonical -> Silver -> quarantine -> QA -> lineage without claiming Databricks parity. Databricks rollout then certifies the governed target runtime after local evidence is ready.

## References

- X12 837 Health Care Claim transaction set.
- X12 835 Health Care Claim Payment/Advice transaction set.
- HL7 Version 2 messaging and message structure.
- HL7 FHIR overview.
