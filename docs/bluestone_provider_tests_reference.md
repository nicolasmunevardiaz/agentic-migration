# BlueStone Provider Tests Reference

## What Is BlueStone HL7 XML?

BlueStone source files are XML documents that use HL7 v2-style message segment names. Each file has an `HL7Messages` root with repeated entity-specific message elements such as `ADT_A01` for patients and `ORU_R01` for observations.

In this project, the BlueStone parser must preserve Raw/Bronze source values from those XML messages without interpreting clinical payloads or promoting Silver semantics.

## Parser Tests

### `test_bluestone_parser_maps_hl7_xml_messages_to_headers_and_canonical_values`
Checks that every BlueStone fixture maps to both source headers and canonical names.
Key role: proves the provider parser is real, reusable, and tied to the YAML spec.

### `test_bluestone_parser_preserves_observation_cdata_without_interpreting_vitals`
Checks that `OBS_JSON` CDATA is preserved as source text.
Key role: protects provider discovery from inventing medical meaning from vitals.

### `test_bluestone_parser_rejects_wrong_message_segment`
Checks that the parser rejects a file when the XML message segment does not match the entity spec.
Key role: prevents silent ingestion of the wrong BlueStone table shape.

### `test_bluestone_parser_rejects_malformed_xml`
Checks that malformed XML fails clearly.
Key role: gives file-level quarantine a deterministic parser signal.

### `test_bluestone_parser_rejects_missing_source_row_key`
Checks that blank `LINE_ID` values fail clearly.
Key role: protects Bronze lineage and row-level reconciliation.

### `test_bluestone_parser_rejects_missing_declared_field_path`
Checks that missing XML tags declared in the spec fail clearly.
Key role: prevents hidden schema drift from becoming null-filled records.

### `test_bluestone_parser_rejects_unsupported_parser_family`
Checks that unsupported parser profiles fail clearly.
Key role: keeps parser behavior spec-driven.

## Provider Spec Tests

### `test_regression_bluestone_entity_coverage_is_stable`
Checks that BlueStone always has exactly five expected entities.
Key role: prevents accidental loss or unapproved addition of source tables.

### `test_schema_required_sections_and_bluestone_provider_metadata`
Checks that every YAML spec has required sections and correct BlueStone metadata.
Key role: keeps specs consistent and reviewable.

### `test_unit_parser_profile_declares_bluestone_hl7_xml_contract`
Checks row key, parser family, XML namespace, root tag, message segment, and row-key path.
Key role: ensures the YAML parser contract is explicit.

### `test_integration_file_patterns_resolve_local_bluestone_files`
Checks that file patterns find BlueStone XML files locally, or remain valid when data is absent in CI.
Key role: keeps local validation and GitHub CI compatible.

### `test_reconciliation_dictionary_headers_match_bluestone_yaml_mappings_and_paths`
Checks every dictionary header appears in YAML and has an XML extraction path.
Key role: prevents unmapped source fields.

### `test_privacy_sensitive_bluestone_headers_are_flagged`
Checks that identifiers, PHI, financial, and clinical fields are privacy-flagged.
Key role: keeps sensitive data visible to governance review.

### `test_bluestone_quarantine_rules_use_allowed_qa_decisions`
Checks quarantine rules use only approved decisions: stop, quarantine, or warn.
Key role: keeps data quality actions standardized.

### `test_bluestone_specs_do_not_embed_absolute_paths_or_raw_sensitive_examples`
Checks specs avoid local machine paths and raw sensitive examples.
Key role: prevents leaking private context or sensitive values into Git.

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
