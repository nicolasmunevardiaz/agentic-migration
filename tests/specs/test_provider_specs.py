import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDER = "data_provider_1_aegis_care_network"
SPEC_ROOT = REPO_ROOT / "metadata" / "provider_specs" / PROVIDER
SOURCE_ROOT = REPO_ROOT / "data_500k" / PROVIDER / "year=2025"

EXPECTED_HEADERS = {
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
}

EXPECTED_RESOURCE_TYPES = {
    "patients": "Patient",
    "encounters": "Encounter",
    "conditions": "Condition",
    "medications": "MedicationRequest",
    "observations": "Observation",
}

SENSITIVE_HEADERS = {
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
        path.stem: yaml.safe_load(path.read_text())
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


def test_regression_entity_coverage_is_stable() -> None:
    assert set(load_specs()) == set(EXPECTED_HEADERS)


def test_schema_required_sections_and_provider_metadata() -> None:
    for entity, spec in load_specs().items():
        assert set(spec) >= REQUIRED_TOP_LEVEL_KEYS
        assert spec["provider"]["provider_slug"] == PROVIDER
        assert spec["provider"]["provider_name"] == "Aegis Care Network"
        assert spec["provider"]["upload_partition"] == "year=2025"
        assert spec["source"]["entity"] == entity
        assert spec["source"]["filetype"] == "fhir_r4"
        assert spec["source"]["file_extension"] == "json"


def test_unit_parser_profile_declares_standard_aegis_contract() -> None:
    for entity, spec in load_specs().items():
        parser_profile = spec["parser_profile"]
        parser_options = parser_profile["parser_options"]

        assert parser_profile["parser_family"] == "fhir_r4_bundle"
        assert parser_profile["source_row_key"] == "SRC_ROW"
        assert parser_profile["canonical_row_key"] == "ROW_ID"
        assert parser_options["bundle_entry_path"] == "entry[].resource"
        assert parser_options["resource_type"] == EXPECTED_RESOURCE_TYPES[entity]
        assert parser_options["field_paths"]["SRC_ROW"] == "id"


def test_integration_file_patterns_resolve_local_aegis_files() -> None:
    for entity, spec in load_specs().items():
        patterns = spec["source"]["expected_file_patterns"]
        assert len(patterns) == 1
        matched_files = sorted(REPO_ROOT.glob(patterns[0]))

        if SOURCE_ROOT.exists():
            assert len(matched_files) == 10
            assert all(path.parent == SOURCE_ROOT / entity for path in matched_files)
        else:
            assert patterns[0].startswith(f"data_500k/{PROVIDER}/year=2025/{entity}/")
            assert patterns[0].endswith(f"{entity}_*.json")


def test_integration_local_fhir_bundles_match_declared_paths_when_available() -> None:
    if not SOURCE_ROOT.exists():
        return

    for spec in load_specs().values():
        pattern = spec["source"]["expected_file_patterns"][0]
        sample_file = sorted(REPO_ROOT.glob(pattern))[0]
        bundle = json.loads(sample_file.read_text())
        resource = bundle["entry"][0]["resource"]

        assert bundle["resourceType"] == "Bundle"
        assert resource["resourceType"] == spec["parser_profile"]["parser_options"]["resource_type"]

        for field_path in spec["parser_profile"]["parser_options"]["field_paths"].values():
            assert resolve_resource_path(resource, field_path) is not None


def test_reconciliation_dictionary_headers_match_yaml_mappings_and_paths() -> None:
    for entity, spec in load_specs().items():
        mapped_headers = {field["source_header"] for field in spec["mapping"]["fields"]}
        field_paths = spec["parser_profile"]["parser_options"]["field_paths"]

        assert mapped_headers == EXPECTED_HEADERS[entity]
        assert set(field_paths) == EXPECTED_HEADERS[entity]
        assert all(field_paths[header] for header in EXPECTED_HEADERS[entity])


def test_privacy_sensitive_headers_are_flagged() -> None:
    for spec in load_specs().values():
        fields_by_header = {
            field["source_header"]: field for field in spec["mapping"]["fields"]
        }
        for header, field in fields_by_header.items():
            if header in SENSITIVE_HEADERS:
                assert field["pii_signal"] is True
            if field["pii_signal"] is True:
                assert field["needs_human_review"] is True or header.endswith("_DT_RAW")


def test_quarantine_rules_use_allowed_qa_decisions() -> None:
    for spec in load_specs().values():
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

    for spec_path in SPEC_ROOT.glob("*.yaml"):
        values = collect_string_values(yaml.safe_load(spec_path.read_text()))
        for value in values:
            assert not any(fragment in value for fragment in forbidden_fragments)
