# Healthcare Source Standards Reference

This migration treats healthcare standards as source dialects, not as the canonical
model itself. A provider standard explains how a source system speaks; it does not
automatically define Silver semantics, identity, clinical meaning, financial meaning,
or Databricks table design.

## How To Read Standards In This Repo

- **Standard family**: the external or provider-local format family, such as ASC X12,
  HL7 v2, HL7 FHIR, or CSV.
- **Parser profile**: the executable contract used by this repo, such as
  `hl7_v2_xml_messages` or `fhir_r4_bundle`.
- **Source example**: a concrete source shape or field from the provider.
- **Canonical risk**: what can go wrong if the source format is treated as enterprise
  meaning too early.

## Acronyms

| Acronym | Meaning | Why it matters here |
| --- | --- | --- |
| ANSI | American National Standards Institute | ANSI accredits standards bodies; it is not itself the data format in this repo. |
| ASC X12 | Accredited Standards Committee X12 | The US EDI standards body family used for claims and payment transactions. |
| X12N | X12 Insurance subcommittee | The X12 area that owns many health care insurance transaction sets. |
| EDI | Electronic Data Interchange | Delimited business-document exchange; common for payer/provider claim workflows. |
| 837 | X12 Health Care Claim | Provider-to-payer claim or encounter billing transaction. |
| 835 | X12 Health Care Claim Payment/Advice | Payer-to-provider payment/remittance advice transaction. |
| HL7 | Health Level Seven | Clinical/admin interoperability standards family. |
| HL7 v2 | HL7 Version 2 messaging | Event/message-oriented clinical exchange using message types and segments. |
| FHIR | Fast Healthcare Interoperability Resources | Resource-oriented HL7 standard for exchanging clinical/admin health data. |
| R4 | FHIR Release 4 | FHIR version family used by Aegis source evidence. |
| STU3 | FHIR Standard for Trial Use 3 / Release 3 | FHIR version family used by ValleyBridge source evidence. |
| CSV | Comma-Separated Values | Flat-file exchange with weak semantics unless the provider dictionary defines them. |
| PHI | Protected Health Information | Health data that must remain privacy/governance reviewed. |
| PII | Personally Identifiable Information | Identifiers or demographics that can identify a person. |
| HITL | Human in the Loop | Required human decision before semantic promotion or governance changes. |

## Provider Standards

| Provider | Technical standard or source dialect | Parser profile | Concrete source example | Why this provider uses it | Key risk |
| --- | --- | --- | --- | --- | --- |
| Aegis Care Network | HL7 FHIR R4 Bundle JSON | `fhir_r4_bundle` | `Patient.id` maps to `SRC_ROW`; `Observation.valueString` is preserved as `OBS_PAYLOAD`; references look like patient/encounter links. | Aegis exports clinical entities as FHIR-style resources: Patient, Encounter, Condition, MedicationRequest, and Observation. FHIR is useful here because it carries structured clinical resource shape and references. | Do not treat FHIR references as approved joins or enterprise identity. `REC_STS` appears differently by resource, and observation payloads must not be clinically interpreted without HITL. |
| BlueStone Health | HL7 Version 2 style XML messages | `hl7_v2_xml_messages` | `ADT_A01` represents patients, `ORU_R01` represents observations, and `LINE_ID` is the source row key. | BlueStone behaves like a message feed: each XML message type represents an event-oriented clinical/admin exchange. HL7 v2 fits admission, scheduling, financial, pharmacy, and observation message patterns. | HL7 v2 messages are event payloads, not normalized tables. Segment names and CDATA payloads must be preserved until canonical semantics are approved. |
| NorthCare Clinics | ASC X12-inspired segment envelope, not a full HIPAA 837 implementation | `x12_segment_envelope` | `HDR` declares fields, `DMG` represents patients, `CLM` represents encounters, `EXPORT_ID` maps to `ROW_ID`. | NorthCare files use X12-like delimiters and segment structure because the source resembles claim/encounter exchange. It is close enough to require X12 parsing discipline, but the repo treats it as a provider-specific envelope. | Do not claim this is a complete ANSI ASC X12 837 claim. Header order, segment meaning, and clinical joins remain provider-specific evidence. |
| ValleyBridge Medical | HL7 FHIR STU3 Bundle JSON with provider comments and encoding drift | `fhir_stu3_bundle_with_comments` | Commented JSON is stripped before parsing; `MedicationOrder` is the medication resource; `DW_LOAD_SEQ` maps to `ROW_ID`. | ValleyBridge exports FHIR STU3-style clinical resources, but files include provider-local comment lines and fallback encodings. | FHIR STU3 and FHIR R4 are related but not identical. Do not merge Aegis and ValleyBridge fields just because both say FHIR. |
| Pacific Shield Insurance | Provider-local CSV claims export; conceptually related to payer/claims workflows | `csv_claims_export` | `CLM_SEQ` maps to `ROW_ID`; duplicate `DX_CD` positions map separately to `CND_ID` and `ICD_HINT`; `PAID_AMT` is financial. | Pacific Shield appears payer/claims-oriented. CSV is the actual file format, while the provider dictionary supplies field order, duplicate-header behavior, and source meaning. | CSV has no external semantic safety net. Payer-vs-clinical semantics, duplicate diagnosis fields, sparse clinical coverage, coverage status, and financial amounts require HITL. |

## Concrete Examples By Provider

### Aegis Care Network: FHIR R4 Clinical Resources

FHIR means the source is organized as resources. In Aegis, the parser reads JSON Bundles
and extracts fields from FHIR-like paths.

Example:

```text
resourceType: Patient
id: source row id -> SRC_ROW -> ROW_ID
identifier[0].value -> PT_001_ID
name[0].given[0] -> FIRST_NAME
active -> REC_STS
```

Purpose: preserve the clinical resource structure and lineage. Risk: `active`,
`status`, and `clinicalStatus` do not mean the same thing across resources without a
human-approved normalization rule.

### BlueStone Health: HL7 v2 Style XML Messages

HL7 v2 is message-oriented. BlueStone stores those message patterns as XML, with one
message segment per entity type.

Example:

```text
HL7Messages
  ADT_A01 -> patients
  SIU_S12 -> encounters
  DFT_P03 -> conditions
  RDE_O11 -> medications
  ORU_R01 -> observations
```

Purpose: represent operational events such as admission, scheduling, charge/diagnosis,
pharmacy order, and observation messages. Risk: event messages are not the same as
stable Silver tables; CDATA observation JSON must remain source text until approved.

### NorthCare Clinics: X12-Like Segment Envelope

ASC X12 is the standards family behind US EDI transactions such as 837 claims and 835
payment advice. NorthCare is **X12-like**, not a full 837 or 835 transaction in this repo.

Example:

```text
HDR*EXPORT_ID*PT_001_ID*PT_GIVEN_NAME*...
DMG*row-001*member-123*...
```

Purpose: use deterministic segment parsing for claim/encounter-shaped text files.
Risk: because this is a provider-specific envelope, the `HDR` order is authoritative
for this repo; do not infer full X12 loops, payer adjudication semantics, or 837
compliance.

### ValleyBridge Medical: FHIR STU3 With Source Comments

ValleyBridge also uses FHIR-style JSON, but it is STU3 and includes provider-local
file quirks.

Example:

```text
# provider metadata comment
{
  "resourceType": "Bundle",
  "entry": [
    {"resource": {"resourceType": "MedicationOrder", "id": "..."}}
  ]
}
```

Purpose: carry clinical resources while preserving source-specific file behavior.
Risk: STU3 `MedicationOrder` and R4 `MedicationRequest` are related concepts, but the
repo must not collapse them without an approved mapping decision.

### Pacific Shield Insurance: CSV Claims Export

Pacific Shield uses flat CSV files. The source dictionary and parser profile are the
contract because CSV alone does not explain clinical or financial semantics.

Example:

```text
CLM_SEQ,DX_LINE_ID,DX_CD,MEMBER_ID,ENCOUNTER_ID,DX_CD,DX_DESC,LINE_STS
```

Purpose: preserve claims-oriented rows and payer/coverage context. Risk: duplicate
`DX_CD` columns, `PAID_AMT`, and `COVERAGE_STATUS` can look clinical or financial
depending on context. They must not be normalized without HITL.

## Compatibility And Mixing Risk

| Combination | Compatible for lineage? | Compatible for Silver semantics? | Impact if mixed too early |
| --- | --- | --- | --- |
| Aegis FHIR R4 + ValleyBridge FHIR STU3 | Yes, if resource version and source path are preserved. | Only after version-aware mapping review. | Similar resource names can hide version differences, such as `MedicationRequest` vs `MedicationOrder`. |
| FHIR resources + HL7 v2 messages | Yes, if both preserve provider, entity, source file, row key, and parser profile. | Not automatically. | A FHIR `Encounter` resource and an HL7 scheduling message can both describe an encounter-like event but with different grain and timing. |
| X12-like NorthCare + Pacific Shield CSV claims | Yes, for claim/encounter lineage and row-level reconciliation. | Not automatically. | Claim rows, diagnosis lines, coverage status, and financial amounts can be payer workflow facts, not clinical truth. |
| Clinical providers + payer/claims exports | Yes, at Bronze and reviewed canonical lineage. | HITL required. | Combining them can create false patient identity, false condition history, or misleading financial/coverage interpretation. |
| Any provider row key -> `ROW_ID` | Yes, as source lineage only. | No. | Treating `SRC_ROW`, `LINE_ID`, `EXPORT_ID`, `DW_LOAD_SEQ`, or `CLM_SEQ` as enterprise identity breaks joins and auditability. |

## Modeling Rules

- Bronze must preserve source dialect, source row key, parser profile, provider, entity,
  source file, and checksum evidence.
- Canonical contracts may map shared source concepts, but only with source evidence and
  explicit risk notes.
- Silver must not normalize clinical status, relationship joins, observation payloads,
  payer/clinical semantics, coverage status, financial amounts, or clinical codes until
  HITL decisions are recorded in `reports/hitl/canonical_drift_decision_runbook.md`.
- X12 claim/payment standards, HL7 v2 messages, FHIR resources, and CSV claims exports
  are not interchangeable. They can be reconciled through lineage, but not merged as
  equivalent business meaning without approval.

## References

- X12 transaction sets: ASC X12 transaction IDs such as 837 Health Care Claim and 835 Health Care Claim Payment/Advice.
- HL7 Version 2: message framework with messages, trigger events, segments, fields, and delimiters.
- HL7 FHIR R4: resource-oriented standard used as Aegis source evidence.
- HL7 FHIR STU3: resource-oriented standard used as ValleyBridge source evidence.
