import json
from pathlib import Path

import pytest

from src.adapters.bluestone_health import BlueStoneParseError, load_spec, parse_file, parse_xml_text

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = REPO_ROOT / "metadata" / "provider_specs" / "data_provider_2_bluestone_health"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "bluestone"

EXPECTED_CANONICAL_VALUES = {
    "patients": ("ROW_ID", "line-patient-001"),
    "encounters": ("APPT_KEY", "visit-alpha"),
    "conditions": ("CND_KEY", "condition-occurrence-alpha"),
    "medications": ("MED_OCC_KEY", "medication-occurrence-alpha"),
    "observations": ("OBS_KEY", "observation-alpha"),
}


@pytest.mark.parametrize("entity", sorted(EXPECTED_CANONICAL_VALUES))
def test_bluestone_parser_maps_hl7_xml_messages_to_headers_and_canonical_values(
    entity: str,
) -> None:
    records = parse_file(FIXTURE_ROOT / f"{entity}_message.xml", SPEC_ROOT / f"{entity}.yaml")
    canonical_name, expected_value = EXPECTED_CANONICAL_VALUES[entity]

    assert len(records) == 1
    assert records[0]["values_by_header"]["LINE_ID"].startswith("line-")
    assert records[0]["values_by_canonical"][canonical_name] == expected_value


def test_bluestone_parser_preserves_observation_cdata_without_interpreting_vitals() -> None:
    records = parse_file(
        FIXTURE_ROOT / "observations_message.xml",
        SPEC_ROOT / "observations.yaml",
    )
    payload = records[0]["values_by_canonical"]["OBS_PAYLOAD"]

    assert json.loads(payload)["type"] == "vitals"
    assert records[0]["values_by_header"]["OBS_JSON"] == payload


def test_bluestone_parser_rejects_wrong_message_segment() -> None:
    with pytest.raises(BlueStoneParseError, match="Expected message segment SIU_S12"):
        parse_file(FIXTURE_ROOT / "patients_message.xml", SPEC_ROOT / "encounters.yaml")


def test_bluestone_parser_rejects_malformed_xml() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")

    with pytest.raises(BlueStoneParseError, match="Malformed BlueStone HL7 XML"):
        parse_xml_text("<HL7Messages><ADT_A01>", spec)


def test_bluestone_parser_rejects_missing_source_row_key() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    xml_text = """
    <HL7Messages xmlns="urn:hl7-org:v2xml">
      <ADT_A01>
        <MSH.10></MSH.10>
        <PID.3>member-alpha</PID.3>
        <PID.5.2>synthetic-given</PID.5.2>
        <PID.5.1>synthetic-family</PID.5.1>
        <PID.19>tax-synthetic-001</PID.19>
        <PID.8>U</PID.8>
        <PID.7>1980-01-01</PID.7>
        <PV1.44>2025-01-01</PV1.44>
        <PV1.45></PV1.45>
        <PID.32>1</PID.32>
      </ADT_A01>
    </HL7Messages>
    """

    with pytest.raises(BlueStoneParseError, match="Missing source row key LINE_ID"):
        parse_xml_text(xml_text, spec)


def test_bluestone_parser_rejects_missing_declared_field_path() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    xml_text = """
    <HL7Messages xmlns="urn:hl7-org:v2xml">
      <ADT_A01>
        <MSH.10>line-patient-001</MSH.10>
        <PID.3>member-alpha</PID.3>
      </ADT_A01>
    </HL7Messages>
    """

    with pytest.raises(BlueStoneParseError, match="Missing declared field path"):
        parse_xml_text(xml_text, spec)


def test_bluestone_parser_rejects_unsupported_parser_family() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    spec["parser_profile"]["parser_family"] = "unsupported_family"

    with pytest.raises(BlueStoneParseError, match="Unsupported parser family"):
        parse_xml_text((FIXTURE_ROOT / "patients_message.xml").read_text(), spec)
