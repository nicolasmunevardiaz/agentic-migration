import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

PROVIDER_CONFIGS = {
    "data_provider_1_aegis_care_network": {
        "provider_name": "Aegis Care Network",
        "filetype": "fhir_r4",
        "file_extension": "json",
        "parser_family": "fhir_r4_bundle",
        "row_key": "SRC_ROW",
        "expected_resource_types": {
            "patients": "Patient",
            "encounters": "Encounter",
            "conditions": "Condition",
            "medications": "MedicationRequest",
            "observations": "Observation",
        },
        "expected_headers": {
            "patients": {
                "SRC_ROW",
                "PT_001_ID",
                "FIRST_NAME",
                "LAST_NAME",
                "SSN",
                "GDR_CD",
                "BDT_VAL",
                "INIT_DT_RAW",
                "END_DT_RAW",
                "REC_STS",
            },
            "encounters": {
                "SRC_ROW",
                "APPT_KEY",
                "PT_001_ID",
                "APPT_DT_RAW",
                "COVERAGE_STATUS",
                "REC_STS",
            },
            "conditions": {
                "SRC_ROW",
                "CND_KEY",
                "CND_SRC_ID",
                "PT_001_ID",
                "APPT_REF",
                "ICD_HINT",
                "DX_DESCR",
                "REC_STS",
            },
            "medications": {
                "SRC_ROW",
                "RX_OCC_KEY",
                "MED_KEY",
                "PT_001_ID",
                "APPT_REF",
                "LINK_CND",
                "MED_NM_TXT",
                "UNIT_COST",
                "ORD_DT_RAW",
                "REC_STS",
            },
            "observations": {
                "SRC_ROW",
                "OBS_KEY",
                "PT_001_ID",
                "APPT_REF",
                "OBS_DT_RAW",
                "OBS_PAYLOAD",
                "REC_STS",
            },
        },
        "sensitive_headers": {
            "PT_001_ID",
            "FIRST_NAME",
            "LAST_NAME",
            "SSN",
            "GDR_CD",
            "BDT_VAL",
            "APPT_KEY",
            "APPT_DT_RAW",
            "COVERAGE_STATUS",
            "CND_KEY",
            "CND_SRC_ID",
            "APPT_REF",
            "ICD_HINT",
            "DX_DESCR",
            "RX_OCC_KEY",
            "MED_KEY",
            "LINK_CND",
            "MED_NM_TXT",
            "UNIT_COST",
            "ORD_DT_RAW",
            "OBS_KEY",
            "OBS_DT_RAW",
            "OBS_PAYLOAD",
        },
    },
    "data_provider_2_bluestone_health": {
        "provider_name": "BlueStone Health",
        "filetype": "hl7_xml",
        "file_extension": "xml",
        "parser_family": "hl7_v2_xml_messages",
        "row_key": "LINE_ID",
        "expected_segments": {
            "patients": "ADT_A01",
            "encounters": "SIU_S12",
            "conditions": "DFT_P03",
            "medications": "RDE_O11",
            "observations": "ORU_R01",
        },
        "expected_headers": {
            "patients": {
                "LINE_ID",
                "CUST_ID",
                "MBR_FIRST_NM",
                "MBR_LAST_NM",
                "TAX_ID",
                "SEX_CD",
                "DOB_TXT",
                "ENROLL_DT",
                "TERM_DT",
                "STS_CD",
            },
            "encounters": {
                "LINE_ID",
                "VISIT_ID",
                "PT_LINK",
                "VISIT_DT",
                "COVERAGE_STATUS",
                "ACT_FLAG",
            },
            "conditions": {
                "LINE_ID",
                "COND_REF",
                "COND_SKU",
                "CUST_REF",
                "VISIT_REF",
                "DX_CODE",
                "COND_NARR",
                "ROW_STS",
            },
            "medications": {
                "LINE_ID",
                "RX_OCC_ID",
                "RX_PROD_CD",
                "PID_REF",
                "E_REF",
                "RX_DX_REF",
                "DRUG_DESC",
                "RX_UNIT_AMT",
                "ORDER_TS",
                "REC_FLAG",
            },
            "observations": {
                "LINE_ID",
                "MEAS_ID",
                "PARENT_PT",
                "EN_REF",
                "MEAS_DT",
                "OBS_JSON",
                "ACT_FLAG",
            },
        },
        "sensitive_headers": {
            "CUST_ID",
            "MBR_FIRST_NM",
            "MBR_LAST_NM",
            "TAX_ID",
            "SEX_CD",
            "DOB_TXT",
            "ENROLL_DT",
            "TERM_DT",
            "VISIT_ID",
            "PT_LINK",
            "VISIT_DT",
            "COVERAGE_STATUS",
            "COND_REF",
            "COND_SKU",
            "CUST_REF",
            "VISIT_REF",
            "DX_CODE",
            "COND_NARR",
            "RX_OCC_ID",
            "RX_PROD_CD",
            "PID_REF",
            "E_REF",
            "RX_DX_REF",
            "DRUG_DESC",
            "RX_UNIT_AMT",
            "ORDER_TS",
            "MEAS_ID",
            "PARENT_PT",
            "EN_REF",
            "MEAS_DT",
            "OBS_JSON",
        },
    },
    "data_provider_3_northcare_clinics": {
        "provider_name": "NorthCare Clinics",
        "filetype": "x12",
        "file_extension": "txt",
        "parser_family": "x12_segment_envelope",
        "row_key": "EXPORT_ID",
        "expected_segments": {
            "patients": "DMG",
            "encounters": "CLM",
            "conditions": "HI",
            "medications": "SV1",
            "observations": "REF",
        },
        "expected_headers": {
            "patients": {
                "EXPORT_ID",
                "PT_001_ID",
                "PT_GIVEN_NAME",
                "PT_FAMILY_NAME",
                "SSN_NUM",
                "GDR_CD",
                "BDT_VAL",
                "REG_START_RAW",
                "REG_END_RAW",
                "REC_STS",
            },
            "encounters": {
                "EXPORT_ID",
                "APPT_KEY",
                "PT_REF",
                "APPT_DT_RAW",
                "COVERAGE_STATUS",
                "REC_STS",
            },
            "conditions": {
                "EXPORT_ID",
                "CND_KEY",
                "CND_TYPE_ID",
                "PT_REF",
                "APPT_REF",
                "ICD_HINT",
                "CND_LONG_TXT",
                "REC_STS",
            },
            "medications": {
                "EXPORT_ID",
                "RX_ROW_KEY",
                "MED_KEY",
                "PT_REF",
                "APPT_REF",
                "PARENT_CND",
                "MED_PRODUCT_NM",
                "MED_PRICE",
                "ORD_DT_RAW",
                "REC_STS",
            },
            "observations": {
                "EXPORT_ID",
                "OBS_KEY",
                "PT_REF",
                "APPT_REF",
                "OBS_DT_RAW",
                "OBS_PAYLOAD",
                "REC_STS",
            },
        },
        "sensitive_headers": {
            "PT_001_ID",
            "PT_GIVEN_NAME",
            "PT_FAMILY_NAME",
            "SSN_NUM",
            "GDR_CD",
            "BDT_VAL",
            "REG_START_RAW",
            "REG_END_RAW",
            "APPT_KEY",
            "PT_REF",
            "APPT_DT_RAW",
            "COVERAGE_STATUS",
            "CND_KEY",
            "CND_TYPE_ID",
            "APPT_REF",
            "ICD_HINT",
            "CND_LONG_TXT",
            "RX_ROW_KEY",
            "MED_KEY",
            "PARENT_CND",
            "MED_PRODUCT_NM",
            "MED_PRICE",
            "ORD_DT_RAW",
            "OBS_KEY",
            "OBS_DT_RAW",
            "OBS_PAYLOAD",
        },
    },
    "data_provider_4_valleybridge_medical": {
        "provider_name": "ValleyBridge Medical",
        "filetype": "fhir_stu3",
        "file_extension": "json",
        "parser_family": "fhir_stu3_bundle_with_comments",
        "row_key": "DW_LOAD_SEQ",
        "expected_resource_types": {
            "patients": "Patient",
            "encounters": "Encounter",
            "conditions": "Condition",
            "medications": "MedicationOrder",
            "observations": "Observation",
        },
        "expected_headers": {
            "patients": {
                "DW_LOAD_SEQ",
                "PTKEY",
                "NAME_FIRST",
                "NAME_LAST",
                "PATIENT_SSN",
                "SX_FLAG",
                "DT_BORN",
                "COV_START",
                "COV_END",
                "REC_FLAG",
            },
            "encounters": {
                "DW_LOAD_SEQ",
                "CNTCT_ID",
                "CLI_ID",
                "EVT_DTTM",
                "COVERAGE_STATUS",
                "ROW_STS",
            },
            "conditions": {
                "DW_LOAD_SEQ",
                "CREF_ID",
                "DX_CAT_CD",
                "PID_REF",
                "E_REF",
                "DX_HINT",
                "DX_STORY",
                "STS_CD",
            },
            "medications": {
                "DW_LOAD_SEQ",
                "M_OCC_SEQ",
                "M_KEY",
                "PARENT_PT",
                "EN_REF",
                "DX_LINK_ID",
                "MED_LBL",
                "LINE_PRICE",
                "MED_DT",
                "ACT_FLAG",
            },
            "observations": {
                "DW_LOAD_SEQ",
                "OBV_ID",
                "PT_LINK",
                "VISIT_REF",
                "TS_OBS",
                "PL_DATA",
                "REC_FLAG",
            },
        },
        "sensitive_headers": {
            "PTKEY",
            "NAME_FIRST",
            "NAME_LAST",
            "PATIENT_SSN",
            "SX_FLAG",
            "DT_BORN",
            "COV_START",
            "COV_END",
            "CNTCT_ID",
            "CLI_ID",
            "EVT_DTTM",
            "COVERAGE_STATUS",
            "CREF_ID",
            "DX_CAT_CD",
            "PID_REF",
            "E_REF",
            "DX_HINT",
            "DX_STORY",
            "M_OCC_SEQ",
            "M_KEY",
            "PARENT_PT",
            "EN_REF",
            "DX_LINK_ID",
            "MED_LBL",
            "LINE_PRICE",
            "MED_DT",
            "OBV_ID",
            "PT_LINK",
            "VISIT_REF",
            "TS_OBS",
            "PL_DATA",
        },
    },
    "data_provider_5_pacific_shield_insurance": {
        "provider_name": "Pacific Shield Insurance",
        "filetype": "csv",
        "file_extension": "csv",
        "parser_family": "csv_claims_export",
        "row_key": "CLM_SEQ",
        "expected_headers": {
            "patients": {
                "CLM_SEQ",
                "MEMBER_ID",
                "MBR_FIRST_NAME",
                "MBR_LAST_NAME",
                "MBR_SSN",
                "MBR_SEX",
                "MBR_DOB",
                "ELIG_START_DT",
                "ELIG_END_DT",
                "MBR_STS",
            },
            "encounters": {
                "CLM_SEQ",
                "ENCOUNTER_ID",
                "MEMBER_ID",
                "SVC_DT",
                "COVERAGE_STATUS",
                "CLM_STS",
            },
            "conditions": {
                "CLM_SEQ",
                "DX_LINE_ID",
                "DX_CD",
                "MEMBER_ID",
                "ENCOUNTER_ID",
                "DX_DESC",
                "LINE_STS",
            },
            "medications": {
                "CLM_SEQ",
                "RX_CLM_ID",
                "DRUG_CD",
                "MEMBER_ID",
                "ENCOUNTER_ID",
                "DX_LINE_REF",
                "DRUG_NM",
                "PAID_AMT",
                "FILL_DT",
                "CLM_STS",
            },
            "observations": {
                "CLM_SEQ",
                "OBS_CLM_ID",
                "MEMBER_ID",
                "ENCOUNTER_ID",
                "SVC_DT",
                "VITALS_JSON",
                "CLM_STS",
            },
        },
        "expected_header_sequences": {
            "patients": [
                "CLM_SEQ",
                "MEMBER_ID",
                "MBR_FIRST_NAME",
                "MBR_LAST_NAME",
                "MBR_SSN",
                "MBR_SEX",
                "MBR_DOB",
                "ELIG_START_DT",
                "ELIG_END_DT",
                "MBR_STS",
            ],
            "encounters": [
                "CLM_SEQ",
                "ENCOUNTER_ID",
                "MEMBER_ID",
                "SVC_DT",
                "COVERAGE_STATUS",
                "CLM_STS",
            ],
            "conditions": [
                "CLM_SEQ",
                "DX_LINE_ID",
                "DX_CD",
                "MEMBER_ID",
                "ENCOUNTER_ID",
                "DX_CD",
                "DX_DESC",
                "LINE_STS",
            ],
            "medications": [
                "CLM_SEQ",
                "RX_CLM_ID",
                "DRUG_CD",
                "MEMBER_ID",
                "ENCOUNTER_ID",
                "DX_LINE_REF",
                "DRUG_NM",
                "PAID_AMT",
                "FILL_DT",
                "CLM_STS",
            ],
            "observations": [
                "CLM_SEQ",
                "OBS_CLM_ID",
                "MEMBER_ID",
                "ENCOUNTER_ID",
                "SVC_DT",
                "VITALS_JSON",
                "CLM_STS",
            ],
        },
        "sensitive_headers": {
            "MEMBER_ID",
            "MBR_FIRST_NAME",
            "MBR_LAST_NAME",
            "MBR_SSN",
            "MBR_SEX",
            "MBR_DOB",
            "ELIG_START_DT",
            "ELIG_END_DT",
            "ENCOUNTER_ID",
            "SVC_DT",
            "COVERAGE_STATUS",
            "DX_LINE_ID",
            "DX_CD",
            "DX_DESC",
            "RX_CLM_ID",
            "DRUG_CD",
            "DX_LINE_REF",
            "DRUG_NM",
            "PAID_AMT",
            "FILL_DT",
            "OBS_CLM_ID",
            "VITALS_JSON",
        },
    },
}

ALLOWED_QA_DECISIONS = {"stop_pipeline", "quarantine_data", "warn"}
REQUIRED_TOP_LEVEL_KEYS = {
    "spec_version",
    "provider",
    "source",
    "parser_profile",
    "mapping",
    "relationships",
    "drift",
    "quarantine_rules",
    "qa_expectations",
    "human_review",
    "readiness",
}


def load_specs(provider: str) -> dict[str, dict]:
    spec_root = REPO_ROOT / "metadata" / "provider_specs" / provider
    return {
        path.stem: yaml.safe_load(path.read_text())
        for path in sorted(spec_root.glob("*.yaml"))
    }


def collect_string_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for entry in value for item in collect_string_values(entry)]
    if isinstance(value, dict):
        return [item for entry in value.values() for item in collect_string_values(entry)]
    return []


def resolve_resource_path(resource: dict, path: str) -> object:
    if path in resource:
        return resource[path]

    current: object = resource
    for part in path.split("."):
        if "[" in part:
            name, index_text = part.split("[", 1)
            index = int(index_text.rstrip("]"))
            current = current[name][index]  # type: ignore[index]
        else:
            current = current[part]  # type: ignore[index]
    return current


def test_regression_provider_entity_coverage_is_stable() -> None:
    for provider, config in PROVIDER_CONFIGS.items():
        assert set(load_specs(provider)) == set(config["expected_headers"])


def test_schema_required_sections_and_provider_metadata() -> None:
    for provider, config in PROVIDER_CONFIGS.items():
        for entity, spec in load_specs(provider).items():
            assert set(spec) >= REQUIRED_TOP_LEVEL_KEYS
            assert spec["provider"]["provider_slug"] == provider
            assert spec["provider"]["provider_name"] == config["provider_name"]
            assert spec["provider"]["upload_partition"] == "year=2025"
            assert spec["source"]["entity"] == entity
            assert spec["source"]["filetype"] == config["filetype"]
            assert spec["source"]["file_extension"] == config["file_extension"]


def test_unit_parser_profiles_declare_provider_contracts() -> None:
    for provider, config in PROVIDER_CONFIGS.items():
        for entity, spec in load_specs(provider).items():
            parser_profile = spec["parser_profile"]
            parser_options = parser_profile["parser_options"]
            row_key = config["row_key"]

            assert parser_profile["parser_family"] == config["parser_family"]
            assert parser_profile["source_row_key"] == row_key
            assert parser_profile["canonical_row_key"] == "ROW_ID"
            if config["parser_family"] != "csv_claims_export":
                assert parser_options["field_paths"][row_key]

            if config["parser_family"] == "fhir_r4_bundle":
                assert parser_options["bundle_entry_path"] == "entry[].resource"
                assert parser_options["resource_type"] == config["expected_resource_types"][entity]
                assert parser_options["field_paths"][row_key] == "id"
            if config["parser_family"] == "hl7_v2_xml_messages":
                assert parser_options["xml_namespace"] == "urn:hl7-org:v2xml"
                assert parser_options["root_tag"] == "HL7Messages"
                assert parser_options["message_segment"] == config["expected_segments"][entity]
                assert parser_options["field_paths"][row_key] == "MSH.10"
            if config["parser_family"] == "x12_segment_envelope":
                assert parser_options["segment_terminator"] == "~"
                assert parser_options["element_separator"] == "*"
                assert parser_options["header_segment"] == "HDR"
                assert parser_options["entity_segment"] == config["expected_segments"][entity]
                assert parser_options["field_paths"][row_key] == "segment[1]"
            if config["parser_family"] == "fhir_stu3_bundle_with_comments":
                assert parser_options["comment_prefix"] == "#"
                assert parser_options["bundle_entry_path"] == "entry[].resource"
                assert "cp1252" in parser_options["encoding_candidates"]
                assert parser_options["resource_type"] == config["expected_resource_types"][entity]
                assert parser_options["field_paths"][row_key] == "id"
            if config["parser_family"] == "csv_claims_export":
                assert parser_options["delimiter"] == ","
                assert parser_options["optional_preamble"] == "sep=,"
                assert parser_options["header_mode"] == "optional_header_or_dictionary_order"
                assert parser_options["duplicate_header_policy"] == "preserve_positions"
                assert parser_options["expected_headers"] == config[
                    "expected_header_sequences"
                ][entity]
                assert parser_options["expected_headers"][0] == row_key


def test_integration_file_patterns_resolve_local_provider_files() -> None:
    for provider, config in PROVIDER_CONFIGS.items():
        source_root = REPO_ROOT / "data_500k" / provider / "year=2025"
        for entity, spec in load_specs(provider).items():
            patterns = spec["source"]["expected_file_patterns"]
            assert len(patterns) == 1
            matched_files = sorted(REPO_ROOT.glob(patterns[0]))

            if source_root.exists():
                assert len(matched_files) == 10
                assert all(path.parent == source_root / entity for path in matched_files)
            else:
                assert patterns[0].startswith(f"data_500k/{provider}/year=2025/{entity}/")
                assert patterns[0].endswith(
                    f"{entity}_*.{config['file_extension']}"
                )


def test_integration_local_fhir_bundles_match_declared_paths_when_available() -> None:
    provider = "data_provider_1_aegis_care_network"
    source_root = REPO_ROOT / "data_500k" / provider / "year=2025"
    if not source_root.exists():
        return

    for spec in load_specs(provider).values():
        pattern = spec["source"]["expected_file_patterns"][0]
        sample_file = sorted(REPO_ROOT.glob(pattern))[0]
        bundle = json.loads(sample_file.read_text())
        resource = bundle["entry"][0]["resource"]

        assert bundle["resourceType"] == "Bundle"
        assert resource["resourceType"] == spec["parser_profile"]["parser_options"]["resource_type"]

        for field_path in spec["parser_profile"]["parser_options"]["field_paths"].values():
            assert resolve_resource_path(resource, field_path) is not None


def test_reconciliation_dictionary_headers_match_yaml_mappings_and_paths() -> None:
    for provider, config in PROVIDER_CONFIGS.items():
        for entity, spec in load_specs(provider).items():
            expected_headers = config["expected_headers"][entity]
            mapped_headers = {field["source_header"] for field in spec["mapping"]["fields"]}

            assert mapped_headers == expected_headers
            parser_options = spec["parser_profile"]["parser_options"]
            if config["parser_family"] == "csv_claims_export":
                expected_header_sequence = config["expected_header_sequences"][entity]
                assert parser_options["expected_headers"] == expected_header_sequence
                assert all(
                    field["source_index"] < len(expected_header_sequence)
                    for field in spec["mapping"]["fields"]
                )
                assert [
                    expected_header_sequence[field["source_index"]]
                    for field in spec["mapping"]["fields"]
                ] == [
                    field["source_header"] for field in spec["mapping"]["fields"]
                ]
            else:
                field_paths = parser_options["field_paths"]
                assert set(field_paths) == expected_headers
                assert all(field_paths[header] for header in expected_headers)


def test_privacy_sensitive_headers_are_flagged() -> None:
    for provider, config in PROVIDER_CONFIGS.items():
        for spec in load_specs(provider).values():
            fields_by_header = {
                field["source_header"]: field for field in spec["mapping"]["fields"]
            }
            for header, field in fields_by_header.items():
                if header in config["sensitive_headers"]:
                    assert field["pii_signal"] is True
                if field["pii_signal"] is True:
                    assert field["needs_human_review"] is True or header.endswith("_DT_RAW")


def test_quarantine_rules_use_allowed_qa_decisions() -> None:
    for provider in PROVIDER_CONFIGS:
        for spec in load_specs(provider).values():
            rules = (
                spec["quarantine_rules"]["file_level"]
                + spec["quarantine_rules"]["row_level"]
            )
            assert rules
            for rule in rules:
                assert any(decision in rule for decision in ALLOWED_QA_DECISIONS)


def test_specs_do_not_embed_absolute_paths_or_raw_sensitive_examples() -> None:
    forbidden_fragments = {
        "/Users/",
        "C:\\",
        "###-##-####",
    }

    for provider in PROVIDER_CONFIGS:
        spec_root = REPO_ROOT / "metadata" / "provider_specs" / provider
        for spec_path in spec_root.glob("*.yaml"):
            values = collect_string_values(yaml.safe_load(spec_path.read_text()))
            for value in values:
                assert not any(fragment in value for fragment in forbidden_fragments)
