import json
from pathlib import Path

import pytest

from src.adapters.valleybridge_medical import (
    ValleyBridgeParseError,
    load_spec,
    parse_valleybridge_file,
    parse_valleybridge_text,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = REPO_ROOT / "metadata" / "provider_specs" / "data_provider_4_valleybridge_medical"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "valleybridge"

EXPECTED_CANONICAL_VALUES = {
    "patients": ("ROW_ID", "dw-patient-001"),
    "encounters": ("APPT_KEY", "contact-alpha"),
    "conditions": ("CND_KEY", "condition-occurrence-alpha"),
    "medications": ("MED_OCC_KEY", "medication-occurrence-alpha"),
    "observations": ("OBS_KEY", "observation-alpha"),
}


@pytest.mark.parametrize("entity", sorted(EXPECTED_CANONICAL_VALUES))
def test_valleybridge_parser_maps_fhir_resources_to_headers_and_canonical_values(
    entity: str,
) -> None:
    records = parse_valleybridge_file(
        FIXTURE_ROOT / f"{entity}_bundle.json",
        SPEC_ROOT / f"{entity}.yaml",
    )
    canonical_name, expected_value = EXPECTED_CANONICAL_VALUES[entity]

    assert len(records) == 1
    assert records[0]["values_by_header"]["DW_LOAD_SEQ"].startswith("dw-")
    assert records[0]["values_by_canonical"][canonical_name] == expected_value


def test_valleybridge_parser_strips_comment_metadata_lines() -> None:
    spec = load_spec(SPEC_ROOT / "encounters.yaml")
    fixture_text = (FIXTURE_ROOT / "encounters_bundle.json").read_text()

    records = parse_valleybridge_text(fixture_text, spec)

    assert records[0]["values_by_canonical"]["COVERAGE_STATUS"] == "COVERED"


def test_valleybridge_parser_uses_declared_encoding_fallback(tmp_path: Path) -> None:
    cp1252_fixture = tmp_path / "patients_cp1252.json"
    fixture_bytes = (
        b"# format=fhir+json\n"
        b'{"resourceType":"Bundle","type":"searchset","entry":[{"resource":{'
        b'"resourceType":"Patient","id":"dw-patient-cp1252",'
        b'"identifier[0].value":"member-alpha",'
        b'"identifier[1].value":"synthetic-tax-id",'
        b'"name[0].given[0]":"synthetic-given",'
        b'"name[0].family":"synthetic-familia-\xf1",'
        b'"gender":"U","birthDate":"1980-01-01",'
        b'"period.start":"2025-01-01","period.end":"","active":"1"'
        b"}}]}"
    )
    cp1252_fixture.write_bytes(fixture_bytes)

    records = parse_valleybridge_file(cp1252_fixture, SPEC_ROOT / "patients.yaml")
    expected_suffix = bytes([0xF1]).decode("cp1252")

    assert records[0]["values_by_header"]["DW_LOAD_SEQ"] == "dw-patient-cp1252"
    assert records[0]["values_by_canonical"]["PT_LAST_NM"].endswith(expected_suffix)


def test_valleybridge_parser_preserves_observation_payload_without_interpreting_vitals() -> None:
    records = parse_valleybridge_file(
        FIXTURE_ROOT / "observations_bundle.json",
        SPEC_ROOT / "observations.yaml",
    )
    payload = records[0]["values_by_canonical"]["OBS_PAYLOAD"]

    assert json.loads(payload)["type"] == "vitals"
    assert records[0]["values_by_header"]["PL_DATA"] == payload


def test_valleybridge_parser_rejects_wrong_resource_type() -> None:
    spec = load_spec(SPEC_ROOT / "encounters.yaml")

    with pytest.raises(ValleyBridgeParseError, match="Expected resourceType Encounter"):
        parse_valleybridge_text((FIXTURE_ROOT / "patients_bundle.json").read_text(), spec)


def test_valleybridge_parser_rejects_malformed_json() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")

    with pytest.raises(ValleyBridgeParseError, match="Malformed ValleyBridge FHIR JSON"):
        parse_valleybridge_text("# format=fhir+json\n{\"resourceType\":\"Bundle\"", spec)


def test_valleybridge_parser_rejects_missing_bundle_entries() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    json_text = '{"resourceType":"Bundle","type":"searchset","entry":[]}'

    with pytest.raises(ValleyBridgeParseError, match="Expected Bundle entries"):
        parse_valleybridge_text(json_text, spec)


def test_valleybridge_parser_rejects_missing_source_row_key() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    json_text = """
    {
      "resourceType": "Bundle",
      "entry": [
        {
          "resource": {
            "resourceType": "Patient",
            "id": "",
            "identifier[0].value": "member-alpha",
            "identifier[1].value": "synthetic-tax-id",
            "name[0].given[0]": "synthetic-given",
            "name[0].family": "synthetic-family",
            "gender": "U",
            "birthDate": "1980-01-01",
            "period.start": "2025-01-01",
            "period.end": "",
            "active": "1"
          }
        }
      ]
    }
    """

    with pytest.raises(ValleyBridgeParseError, match="Missing source row key DW_LOAD_SEQ"):
        parse_valleybridge_text(json_text, spec)


def test_valleybridge_parser_rejects_missing_declared_field_path() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    json_text = """
    {
      "resourceType": "Bundle",
      "entry": [
        {
          "resource": {
            "resourceType": "Patient",
            "id": "dw-patient-001",
            "identifier[0].value": "member-alpha"
          }
        }
      ]
    }
    """

    with pytest.raises(ValleyBridgeParseError, match="Missing declared field path"):
        parse_valleybridge_text(json_text, spec)


def test_valleybridge_parser_rejects_unsupported_parser_family() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    spec["parser_profile"]["parser_family"] = "unsupported_family"

    with pytest.raises(ValleyBridgeParseError, match="Unsupported parser family"):
        parse_valleybridge_text((FIXTURE_ROOT / "patients_bundle.json").read_text(), spec)


def test_valleybridge_fixtures_do_not_copy_sensitive_source_examples() -> None:
    forbidden_fragments = {
        "###-##-####",
        "VALLEYBRIDGE",
    }

    for fixture_path in FIXTURE_ROOT.glob("*.json"):
        fixture_text = fixture_path.read_text()
        assert not any(fragment in fixture_text for fragment in forbidden_fragments)
