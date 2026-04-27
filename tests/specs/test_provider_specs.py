import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDER = "data_provider_2_bluestone_health"
SPEC_ROOT = REPO_ROOT / "metadata" / "provider_specs" / PROVIDER
SOURCE_ROOT = REPO_ROOT / "data_500k" / PROVIDER / "year=2025"

EXPECTED_HEADERS = {
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
}

EXPECTED_SEGMENTS = {
    "patients": "ADT_A01",
    "encounters": "SIU_S12",
    "conditions": "DFT_P03",
    "medications": "RDE_O11",
    "observations": "ORU_R01",
}

SENSITIVE_HEADERS = {
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


def load_specs() -> dict[str, dict]:
    return {
        path.stem: json.loads(path.read_text())
        for path in sorted(SPEC_ROOT.glob("*.yaml"))
    }


def collect_string_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for entry in value for item in collect_string_values(entry)]
    if isinstance(value, dict):
        return [item for entry in value.values() for item in collect_string_values(entry)]
    return []


def test_regression_bluestone_entity_coverage_is_stable() -> None:
    assert set(load_specs()) == set(EXPECTED_HEADERS)


def test_schema_required_sections_and_bluestone_provider_metadata() -> None:
    for entity, spec in load_specs().items():
        assert set(spec) >= REQUIRED_TOP_LEVEL_KEYS
        assert spec["provider"]["provider_slug"] == PROVIDER
        assert spec["provider"]["provider_name"] == "BlueStone Health"
        assert spec["provider"]["provider_folder"] == PROVIDER
        assert spec["provider"]["upload_partition"] == "year=2025"
        assert spec["source"]["entity"] == entity
        assert spec["source"]["filetype"] == "hl7_xml"
        assert spec["source"]["file_extension"] == "xml"


def test_unit_parser_profile_declares_bluestone_hl7_xml_contract() -> None:
    for entity, spec in load_specs().items():
        parser_profile = spec["parser_profile"]
        parser_options = parser_profile["parser_options"]

        assert parser_profile["parser_family"] == "hl7_v2_xml_messages"
        assert parser_profile["source_row_key"] == "LINE_ID"
        assert parser_profile["canonical_row_key"] == "ROW_ID"
        assert parser_options["xml_namespace"] == "urn:hl7-org:v2xml"
        assert parser_options["root_tag"] == "HL7Messages"
        assert parser_options["message_segment"] == EXPECTED_SEGMENTS[entity]
        assert parser_options["field_paths"]["LINE_ID"] == "MSH.10"


def test_integration_file_patterns_resolve_local_bluestone_files() -> None:
    for entity, spec in load_specs().items():
        patterns = spec["source"]["expected_file_patterns"]
        assert len(patterns) == 1
        matched_files = sorted(REPO_ROOT.glob(patterns[0]))

        if SOURCE_ROOT.exists():
            assert len(matched_files) == 10
            assert all(path.parent == SOURCE_ROOT / entity for path in matched_files)
        else:
            assert patterns[0].startswith(f"data_500k/{PROVIDER}/year=2025/{entity}/")
            assert patterns[0].endswith(f"{entity}_*.xml")


def test_reconciliation_dictionary_headers_match_bluestone_yaml_mappings_and_paths() -> None:
    for entity, spec in load_specs().items():
        mapped_headers = {field["source_header"] for field in spec["mapping"]["fields"]}
        field_paths = spec["parser_profile"]["parser_options"]["field_paths"]

        assert mapped_headers == EXPECTED_HEADERS[entity]
        assert set(field_paths) == EXPECTED_HEADERS[entity]
        assert all(field_paths[header] for header in EXPECTED_HEADERS[entity])


def test_privacy_sensitive_bluestone_headers_are_flagged() -> None:
    for spec in load_specs().values():
        fields_by_header = {
            field["source_header"]: field for field in spec["mapping"]["fields"]
        }
        for header, field in fields_by_header.items():
            if header in SENSITIVE_HEADERS:
                assert field["pii_signal"] is True
                assert field["needs_human_review"] is True


def test_bluestone_quarantine_rules_use_allowed_qa_decisions() -> None:
    for spec in load_specs().values():
        rules = (
            spec["quarantine_rules"]["file_level"]
            + spec["quarantine_rules"]["row_level"]
        )
        assert rules
        for rule in rules:
            assert any(decision in rule for decision in ALLOWED_QA_DECISIONS)


def test_bluestone_specs_do_not_embed_absolute_paths_or_raw_sensitive_examples() -> None:
    forbidden_fragments = {
        "/Users/",
        "C:\\",
        "###-##-####",
    }

    for spec_path in SPEC_ROOT.glob("*.yaml"):
        values = collect_string_values(json.loads(spec_path.read_text()))
        for value in values:
            assert not any(fragment in value for fragment in forbidden_fragments)
