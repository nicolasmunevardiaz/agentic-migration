from pathlib import Path

import pytest

from src.adapters.aegis_care_network import (
    AegisParseError,
    parse_aegis_bundle_with_spec,
    parse_aegis_entity_file,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = REPO_ROOT / "metadata/provider_specs/data_provider_1_aegis_care_network"
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/aegis"

EXPECTED_FIXTURE_VALUES = {
    "patients": ("PT_001_ID", "member-1"),
    "encounters": ("APPT_KEY", "encounter-1"),
    "conditions": ("CND_KEY", "condition-1"),
    "medications": ("MED_OCC_KEY", "medication-order-1"),
    "observations": ("OBS_KEY", "observation-1"),
}


@pytest.mark.parametrize("entity", sorted(EXPECTED_FIXTURE_VALUES))
def test_aegis_parser_maps_entity_bundle_to_headers_and_canonical_values(entity: str) -> None:
    records = parse_aegis_entity_file(
        entity,
        FIXTURE_ROOT / f"{entity}_bundle.json",
        SPEC_ROOT,
    )
    canonical_name, expected_value = EXPECTED_FIXTURE_VALUES[entity]

    assert len(records) == 1
    assert records[0].values_by_canonical[canonical_name] == expected_value


def test_aegis_parser_maps_flat_fhir_patient_bundle_to_headers_and_canonical_values() -> None:
    records = parse_aegis_entity_file(
        "patients",
        FIXTURE_ROOT / "patients_bundle.json",
        SPEC_ROOT,
    )

    assert len(records) == 1
    record = records[0]
    assert record.provider_slug == "data_provider_1_aegis_care_network"
    assert record.entity == "patients"
    assert record.source_row_key == "SRC_ROW"
    assert set(record.values_by_header) == {
        field["source_header"]
        for field in record_spec("patients")["mapping"]["fields"]
    }
    assert record.values_by_header["SRC_ROW"] == record.values_by_canonical["ROW_ID"]
    assert record.values_by_header["PT_001_ID"] == record.values_by_canonical["PT_001_ID"]


def test_aegis_parser_maps_observation_payload_without_interpreting_vitals() -> None:
    records = parse_aegis_entity_file(
        "observations",
        FIXTURE_ROOT / "observations_bundle.json",
        SPEC_ROOT,
    )

    assert len(records) == 1
    record = records[0]
    assert record.values_by_header["OBS_PAYLOAD"] == record.values_by_canonical["OBS_PAYLOAD"]
    assert isinstance(record.values_by_header["OBS_PAYLOAD"], str)


def test_aegis_parser_rejects_wrong_resource_type() -> None:
    spec = record_spec("patients")
    source_file = FIXTURE_ROOT / "observations_bundle.json"

    with pytest.raises(AegisParseError, match="Expected Patient resource"):
        parse_aegis_bundle_with_spec(source_file, spec)


def test_aegis_parser_rejects_malformed_bundle(tmp_path: Path) -> None:
    malformed = tmp_path / "patients_bundle.json"
    malformed.write_text('{"resourceType": "Bundle",', encoding="utf-8")

    with pytest.raises(AegisParseError, match="Malformed Aegis FHIR bundle JSON"):
        parse_aegis_entity_file("patients", malformed, SPEC_ROOT)


def test_aegis_parser_rejects_missing_source_row_key(tmp_path: Path) -> None:
    missing_row_key = tmp_path / "patients_bundle.json"
    missing_row_key.write_text(
        """
        {
          "resourceType": "Bundle",
          "entry": [
            {
              "resource": {
                "resourceType": "Patient",
                "id": "",
                "identifier[0].value": "member-1",
                "identifier[1].value": "synthetic-ssn",
                "name[0].given[0]": "Synthetic",
                "name[0].family": "Patient",
                "gender": "unknown",
                "birthDate": "1970-01-01",
                "period.start": "2025-01-01",
                "period.end": "",
                "active": true
              }
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    with pytest.raises(AegisParseError, match="Missing source row key SRC_ROW"):
        parse_aegis_entity_file("patients", missing_row_key, SPEC_ROOT)


def record_spec(entity: str) -> dict:
    import yaml

    return yaml.safe_load((SPEC_ROOT / f"{entity}.yaml").read_text())
