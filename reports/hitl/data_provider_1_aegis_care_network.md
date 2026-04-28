# Aegis Care Network HITL Queue

Provider: `data_provider_1_aegis_care_network`
Plan: `01_provider_discovery_and_specs_plan`

| Decision | Provider | Entity | Evidence | Recommended Option | Status |
| --- | --- | --- | --- | --- | --- |
| Confirm direct PII handling for member identifiers, names, SSN, and birth date. | data_provider_1_aegis_care_network | patients | `metadata/provider_specs/data_provider_1_aegis_care_network/patients.yaml` | Keep PII flagged and block downstream exposure until masking policy exists. | pending |
| Confirm member id uniqueness assumptions. | data_provider_1_aegis_care_network | all | `reports/drift/data_provider_1_aegis_care_network.md` | Treat `PT_001_ID` as source member reference only, not enterprise identity. | pending |
| Confirm `REC_STS` normalization per FHIR resource type. | data_provider_1_aegis_care_network | all | `metadata/provider_specs/data_provider_1_aegis_care_network/` | Preserve source status in Bronze and defer canonical status until modeling. | pending |
| Confirm clinical code semantics. | data_provider_1_aegis_care_network | conditions, medications | `metadata/provider_specs/data_provider_1_aegis_care_network/conditions.yaml`, `metadata/provider_specs/data_provider_1_aegis_care_network/medications.yaml` | Treat codes as source facts; do not infer crosswalks in provider discovery. | pending |
| Confirm financial value governance. | data_provider_1_aegis_care_network | medications | `metadata/provider_specs/data_provider_1_aegis_care_network/medications.yaml` | Keep `UNIT_COST` PHI/financial flagged and require approval before analytics use. | pending |
| Confirm vitals payload handling. | data_provider_1_aegis_care_network | observations | `metadata/provider_specs/data_provider_1_aegis_care_network/observations.yaml` | Preserve `OBS_PAYLOAD` as source JSON string until adapter validation. | pending |
