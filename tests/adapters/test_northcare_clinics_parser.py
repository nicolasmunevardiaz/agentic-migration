import json
from pathlib import Path

import pytest

from src.adapters.northcare_clinics import (
    NorthCareParseError,
    load_spec,
    parse_northcare_file,
    parse_northcare_text,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = REPO_ROOT / "metadata" / "provider_specs" / "data_provider_3_northcare_clinics"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "northcare"

EXPECTED_CANONICAL_VALUES = {
    "patients": ("ROW_ID", "export-patient-001"),
    "encounters": ("APPT_KEY", "appt-alpha"),
    "conditions": ("CND_KEY", "condition-occurrence-alpha"),
    "medications": ("MED_OCC_KEY", "medication-occurrence-alpha"),
    "observations": ("OBS_KEY", "observation-alpha"),
}


@pytest.mark.parametrize("entity", sorted(EXPECTED_CANONICAL_VALUES))
def test_northcare_parser_maps_x12_segments_to_headers_and_canonical_values(
    entity: str,
) -> None:
    records = parse_northcare_file(
        FIXTURE_ROOT / f"{entity}_message.txt",
        SPEC_ROOT / f"{entity}.yaml",
    )
    canonical_name, expected_value = EXPECTED_CANONICAL_VALUES[entity]

    assert len(records) == 1
    assert records[0]["values_by_header"]["EXPORT_ID"].startswith("export-")
    assert records[0]["values_by_canonical"][canonical_name] == expected_value


def test_northcare_parser_uses_hdr_order_for_unprefixed_coverage_status() -> None:
    records = parse_northcare_file(
        FIXTURE_ROOT / "encounters_message.txt",
        SPEC_ROOT / "encounters.yaml",
    )

    assert records[0]["values_by_header"]["COVERAGE_STATUS"] == "COVERED"
    assert records[0]["values_by_canonical"]["COVERAGE_STATUS"] == "COVERED"


def test_northcare_parser_preserves_observation_payload_without_interpreting_vitals() -> None:
    records = parse_northcare_file(
        FIXTURE_ROOT / "observations_message.txt",
        SPEC_ROOT / "observations.yaml",
    )
    payload = records[0]["values_by_canonical"]["OBS_PAYLOAD"]

    assert json.loads(payload)["type"] == "vitals"
    assert records[0]["values_by_header"]["OBS_PAYLOAD"] == payload


def test_northcare_parser_rejects_wrong_entity_segment() -> None:
    spec = load_spec(SPEC_ROOT / "encounters.yaml")
    text = """
    ISA*synthetic~
    GS*synthetic~
    ST*837*0001~
    HDR*CLM01:EXPORT_ID*CLM02:APPT_KEY*CLM03:PT_REF*CLM04:APPT_DT_RAW*COVERAGE_STATUS*CLM05:REC_STS~
    DMG*export-encounter-001*appt-alpha*member-alpha*2025-02-01*COVERED*1~
    SE*5*0001~
    GE*1*1~
    IEA*1*000000001~
    """

    with pytest.raises(NorthCareParseError, match="Expected entity segment CLM"):
        parse_northcare_text(text, spec)


def test_northcare_parser_rejects_malformed_envelope() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")

    with pytest.raises(NorthCareParseError, match="missing segment terminator"):
        parse_northcare_text("ISA*missing-terminator", spec)


def test_northcare_parser_rejects_missing_header_segment() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    text = """
    ISA*synthetic~
    GS*synthetic~
    ST*837*0001~
    DMG*export-patient-001*member-alpha*synthetic-given*synthetic-family*synthetic-tax-id*U*1980-01-01*2025-01-01**1~
    SE*4*0001~
    GE*1*1~
    IEA*1*000000001~
    """

    with pytest.raises(NorthCareParseError, match="missing HDR"):
        parse_northcare_text(text, spec)


def test_northcare_parser_rejects_missing_source_row_key() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    text = """
    ISA*synthetic~
    GS*synthetic~
    ST*837*0001~
    HDR*DMG01:EXPORT_ID*DMG02:PT_001_ID*DMG03:PT_GIVEN_NAME*DMG04:PT_FAMILY_NAME*DMG05:SSN_NUM*DMG06:GDR_CD*DMG07:BDT_VAL*DMG08:REG_START_RAW*DMG09:REG_END_RAW*DMG10:REC_STS~
    DMG**member-alpha*synthetic-given*synthetic-family*synthetic-tax-id*U*1980-01-01*2025-01-01**1~
    SE*5*0001~
    GE*1*1~
    IEA*1*000000001~
    """

    with pytest.raises(NorthCareParseError, match="Missing source row key EXPORT_ID"):
        parse_northcare_text(text, spec)


def test_northcare_parser_rejects_element_count_mismatch() -> None:
    spec = load_spec(SPEC_ROOT / "encounters.yaml")
    text = """
    ISA*synthetic~
    GS*synthetic~
    ST*837*0001~
    HDR*CLM01:EXPORT_ID*CLM02:APPT_KEY*CLM03:PT_REF*CLM04:APPT_DT_RAW*COVERAGE_STATUS*CLM05:REC_STS~
    CLM*export-encounter-001*appt-alpha*member-alpha*2025-02-01*COVERED~
    SE*5*0001~
    GE*1*1~
    IEA*1*000000001~
    """

    with pytest.raises(NorthCareParseError, match="Element count mismatch"):
        parse_northcare_text(text, spec)


def test_northcare_parser_rejects_unsupported_parser_family() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    spec["parser_profile"]["parser_family"] = "unsupported_family"

    with pytest.raises(NorthCareParseError, match="Unsupported parser family"):
        parse_northcare_text((FIXTURE_ROOT / "patients_message.txt").read_text(), spec)


def test_northcare_fixtures_do_not_copy_sensitive_source_examples() -> None:
    forbidden_fragments = {
        "###-##-####",
        "NORTHCARECLINIC",
    }

    for fixture_path in FIXTURE_ROOT.glob("*.txt"):
        fixture_text = fixture_path.read_text()
        assert not any(fragment in fixture_text for fragment in forbidden_fragments)
