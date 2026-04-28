from pathlib import Path

import pytest

from src.adapters.pacific_shield_insurance import (
    PacificShieldParseError,
    load_spec,
    parse_pacific_shield_file,
    parse_pacific_shield_text,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = (
    REPO_ROOT
    / "metadata"
    / "provider_specs"
    / "data_provider_5_pacific_shield_insurance"
)
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "pacific_shield"

FIXTURES_BY_ENTITY = {
    "patients": "patients_preamble.csv",
    "encounters": "encounters_header.csv",
    "conditions": "conditions_duplicate_header.csv",
    "medications": "medications_data_first.csv",
    "observations": "observations_data_first.csv",
}

EXPECTED_CANONICAL_VALUES = {
    "patients": ("PT_001_ID", "MEMBER-SYN-001"),
    "encounters": ("APPT_KEY", "ENCOUNTER-SYN-001"),
    "conditions": ("CND_KEY", "COND-SYN-001"),
    "medications": ("MED_OCC_KEY", "MED-OCC-SYN-001"),
    "observations": ("OBS_KEY", "OBS-SYN-001"),
}


@pytest.mark.parametrize("entity", sorted(FIXTURES_BY_ENTITY))
def test_pacific_shield_parser_maps_csv_rows_to_headers_and_canonical_values(
    entity: str,
) -> None:
    records = parse_pacific_shield_file(
        FIXTURE_ROOT / FIXTURES_BY_ENTITY[entity],
        SPEC_ROOT / f"{entity}.yaml",
    )
    canonical_name, expected_value = EXPECTED_CANONICAL_VALUES[entity]

    assert len(records) == 1
    assert records[0]["values_by_header"]["CLM_SEQ"].startswith("R_P05_SYN_")
    assert records[0]["values_by_canonical"][canonical_name] == expected_value


def test_pacific_shield_parser_preserves_duplicate_condition_header_positions() -> None:
    records = parse_pacific_shield_file(
        FIXTURE_ROOT / "conditions_duplicate_header.csv",
        SPEC_ROOT / "conditions.yaml",
    )
    record = records[0]

    assert record["values_by_header"]["DX_CD"] == [
        "COND-CATALOG-001",
        "ICD-SYN-001",
    ]
    assert record["values_by_canonical"]["CND_ID"] == "COND-CATALOG-001"
    assert record["values_by_canonical"]["ICD_HINT"] == "ICD-SYN-001"


def test_pacific_shield_parser_accepts_comment_preamble_and_header_rows() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")

    records = parse_pacific_shield_text(
        (FIXTURE_ROOT / "patients_preamble.csv").read_text(),
        spec,
    )

    assert records[0]["values_by_canonical"]["ROW_ID"] == "R_P05_SYN_0001"


def test_pacific_shield_parser_accepts_dictionary_order_data_first_rows() -> None:
    spec = load_spec(SPEC_ROOT / "medications.yaml")

    records = parse_pacific_shield_text(
        (FIXTURE_ROOT / "medications_data_first.csv").read_text(),
        spec,
    )

    assert records[0]["values_by_canonical"]["MED_ID"] == "MED-SYN-001"


def test_pacific_shield_parser_rejects_missing_source_row_key() -> None:
    spec = load_spec(SPEC_ROOT / "encounters.yaml")
    csv_text = (
        '"CLM_SEQ","ENCOUNTER_ID","MEMBER_ID","SVC_DT","COVERAGE_STATUS","CLM_STS"\n'
        '"","ENCOUNTER-SYN-001","MEMBER-SYN-001","2025-02-01","COVERED","1"\n'
    )

    with pytest.raises(PacificShieldParseError, match="Missing source row key CLM_SEQ"):
        parse_pacific_shield_text(csv_text, spec)


def test_pacific_shield_parser_rejects_malformed_row_width() -> None:
    spec = load_spec(SPEC_ROOT / "observations.yaml")
    csv_text = '"R_P05_SYN_0005","OBS-SYN-001"\n'

    with pytest.raises(PacificShieldParseError, match="Malformed CSV row"):
        parse_pacific_shield_text(csv_text, spec)


def test_pacific_shield_parser_rejects_wrong_entity_header_shape() -> None:
    spec = load_spec(SPEC_ROOT / "encounters.yaml")
    wrong_header_text = (FIXTURE_ROOT / "patients_preamble.csv").read_text()

    with pytest.raises(PacificShieldParseError, match="Unexpected header shape"):
        parse_pacific_shield_text(wrong_header_text, spec)


def test_pacific_shield_parser_rejects_unsupported_parser_family() -> None:
    spec = load_spec(SPEC_ROOT / "patients.yaml")
    spec["parser_profile"]["parser_family"] = "unsupported_family"

    with pytest.raises(PacificShieldParseError, match="Unsupported parser family"):
        parse_pacific_shield_text((FIXTURE_ROOT / "patients_preamble.csv").read_text(), spec)


def test_pacific_shield_fixtures_do_not_copy_sensitive_source_examples() -> None:
    forbidden_fragments = {
        "***-**-",
        "Thiago",
        "Gomez",
        "P05_PT",
    }

    for fixture_path in FIXTURE_ROOT.glob("*.csv"):
        fixture_text = fixture_path.read_text()
        assert not any(fragment in fixture_text for fragment in forbidden_fragments)
