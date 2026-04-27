# Aegis Provider Tests Reference

## What Is FHIR?

FHIR means Fast Healthcare Interoperability Resources. It is an HL7 standard for representing and exchanging healthcare data in a structured, reusable way.

In this project, Aegis files look like FHIR-style JSON bundles, so the parser must understand that shape before the data can safely move toward Bronze/Silver.

## Parser Tests

### `test_aegis_parser_maps_flat_fhir_patient_bundle_to_headers_and_canonical_values`
Checks that the Aegis parser turns a patient fixture into both source headers and canonical names.  
Key role: proves the provider parser is real, reusable, and tied to the YAML spec.

### `test_aegis_parser_maps_observation_payload_without_interpreting_vitals`
Checks that observation payloads are preserved as source text, not clinically interpreted.  
Key role: protects provider discovery from inventing medical meaning.

### `test_aegis_parser_rejects_wrong_resource_type`
Checks that the parser rejects a file when the entity type does not match the spec.  
Key role: prevents silent ingestion of the wrong clinical resource.

## Provider Spec Tests

### `test_regression_entity_coverage_is_stable`
Checks that Aegis always has exactly five expected entities.  
Key role: prevents accidental loss or unapproved addition of source tables.

### `test_schema_required_sections_and_provider_metadata`
Checks that every YAML spec has required sections and correct provider metadata.  
Key role: keeps specs consistent and reviewable.

### `test_unit_parser_profile_declares_standard_aegis_contract`
Checks row key, parser family, bundle path, and expected resource type.  
Key role: ensures the YAML parser contract is explicit.

### `test_integration_file_patterns_resolve_local_aegis_files`
Checks that file patterns find Aegis files locally, or remain valid when data is absent in CI.  
Key role: keeps local validation and GitHub CI compatible.

### `test_integration_local_fhir_bundles_match_declared_paths_when_available`
Checks that declared paths exist in sampled local FHIR-style bundles.  
Key role: confirms specs match the real provider file shape.

### `test_reconciliation_dictionary_headers_match_yaml_mappings_and_paths`
Checks every dictionary header appears in YAML and has an extraction path.  
Key role: prevents unmapped source fields.

### `test_privacy_sensitive_headers_are_flagged`
Checks that identifiers, PHI, financial, and clinical fields are privacy-flagged.  
Key role: keeps sensitive data visible to governance review.

### `test_quarantine_rules_use_allowed_qa_decisions`
Checks quarantine rules use only approved decisions: stop, quarantine, or warn.  
Key role: keeps data quality actions standardized.

### `test_specs_do_not_embed_absolute_paths_or_raw_sensitive_examples`
Checks specs avoid local machine paths and raw sensitive examples.  
Key role: prevents leaking private context or sensitive data into Git.

## Repository Governance Tests

### `test_agentops_required_paths_exist`
Checks that the expected AgentOps folder structure exists.  
Key role: keeps agents writing artifacts into standard locations.

### `test_large_source_data_is_not_tracked`
Checks that `data_500k/` is not committed to Git.  
Key role: prevents large or sensitive source data from entering the repo.

### `test_local_and_secret_files_are_not_tracked`
Checks that files like `.env` and `.DS_Store` are not committed.  
Key role: protects secrets and keeps the repository clean.
