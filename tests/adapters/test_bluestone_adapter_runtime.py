import json
from hashlib import sha256
from pathlib import Path

import pytest

from src.common.adapter_runtime import evidence_contains_sensitive_raw_value
from src.handlers.bluestone_adapter import run_bluestone_adapter_for_file

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = REPO_ROOT / "metadata/provider_specs/data_provider_2_bluestone_health"
MODEL_ROOT = REPO_ROOT / "metadata/model_specs"
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/bluestone"
DATA_ROOT = REPO_ROOT / "data_500k/data_provider_2_bluestone_health/year=2025"

EXPECTED_SILVER_ENTITIES = {
    "patients": {"members", "coverage_periods"},
    "encounters": {"encounters"},
    "conditions": {"conditions"},
    "medications": {"medications", "cost_records"},
    "observations": {"observations"},
}


@pytest.mark.parametrize("entity", sorted(EXPECTED_SILVER_ENTITIES))
def test_bluestone_adapter_emits_bronze_and_canonical_silver_rows(entity: str) -> None:
    result = run_bluestone_adapter_for_file(
        entity=entity,
        source_file=FIXTURE_ROOT / f"{entity}_message.xml",
        ingestion_run_id="test-run-001",
        provider_spec_root=SPEC_ROOT,
        model_root=MODEL_ROOT,
    )

    assert len(result.bronze_records) == 1
    bronze = result.bronze_records[0]
    assert bronze.provider_slug == "data_provider_2_bluestone_health"
    assert bronze.source_entity == entity
    assert bronze.source_checksum
    assert bronze.source_lineage_ref
    assert bronze.adapter_version == "0.1.0"
    assert bronze.ingestion_run_id == "test-run-001"
    assert bronze.quarantine_status == "accepted"

    assert set(result.silver_rows) == EXPECTED_SILVER_ENTITIES[entity]
    assert result.quarantine_records == []


def test_bluestone_adapter_uses_model_specs_for_silver_column_names() -> None:
    result = run_bluestone_adapter_for_file(
        entity="conditions",
        source_file=FIXTURE_ROOT / "conditions_message.xml",
        ingestion_run_id="test-run-001",
        provider_spec_root=SPEC_ROOT,
        model_root=MODEL_ROOT,
    )
    condition_row = result.silver_rows["conditions"][0]

    assert condition_row["condition_reference"] == "condition-occurrence-alpha"
    assert condition_row["member_reference"] == "member-alpha"
    assert "COND_REF" not in condition_row
    assert "CUST_REF" not in condition_row


def test_bluestone_adapter_derives_observation_values_from_approved_payload_contract() -> None:
    result = run_bluestone_adapter_for_file(
        entity="observations",
        source_file=FIXTURE_ROOT / "observations_message.xml",
        ingestion_run_id="test-run-001",
        provider_spec_root=SPEC_ROOT,
        model_root=MODEL_ROOT,
    )
    observation_row = result.silver_rows["observations"][0]
    payload = json.loads(observation_row["observation_payload_raw"])

    assert payload["type"] == "vitals"
    assert observation_row["height_cm"] == "170"
    assert observation_row["weight_kg"] is None
    assert observation_row["systolic_bp"] == "120"


def test_bluestone_adapter_warns_on_invalid_ingestion_decimal(tmp_path: Path) -> None:
    invalid_medication = tmp_path / "medications_message.xml"
    xml_text = (FIXTURE_ROOT / "medications_message.xml").read_text(encoding="utf-8")
    invalid_medication.write_text(
        xml_text.replace("<RXE.22>12.34</RXE.22>", "<RXE.22>not-decimal</RXE.22>"),
        encoding="utf-8",
    )

    result = run_bluestone_adapter_for_file(
        entity="medications",
        source_file=invalid_medication,
        ingestion_run_id="test-run-001",
        provider_spec_root=SPEC_ROOT,
        model_root=MODEL_ROOT,
    )

    assert "medications" in result.silver_rows
    assert result.silver_rows["cost_records"][0]["cost_amount"] is None
    assert result.quarantine_records == []
    assert {item.decision for item in result.qa_evidence} == {"warn"}


def test_bluestone_adapter_warns_on_malformed_optional_observation_payload(
    tmp_path: Path,
) -> None:
    invalid_observation = tmp_path / "observations_message.xml"
    xml_text = (FIXTURE_ROOT / "observations_message.xml").read_text(encoding="utf-8")
    invalid_observation.write_text(
        xml_text.replace(
            '{"type":"vitals","height":{"value":170,"u":"cm"},'
            '"blood_pressure":{"systolic":120,"diastolic":80,"u":"mmHg"}}',
            "{not-json",
        ),
        encoding="utf-8",
    )

    result = run_bluestone_adapter_for_file(
        entity="observations",
        source_file=invalid_observation,
        ingestion_run_id="test-run-001",
        provider_spec_root=SPEC_ROOT,
        model_root=MODEL_ROOT,
    )

    assert result.quarantine_records == []
    assert result.silver_rows["observations"][0]["observation_payload_raw"] is None
    assert {item.decision for item in result.qa_evidence} == {"warn"}


def test_bluestone_adapter_evidence_does_not_include_raw_sensitive_values() -> None:
    result = run_bluestone_adapter_for_file(
        entity="patients",
        source_file=FIXTURE_ROOT / "patients_message.xml",
        ingestion_run_id="test-run-001",
        provider_spec_root=SPEC_ROOT,
        model_root=MODEL_ROOT,
    )

    assert not evidence_contains_sensitive_raw_value(result.qa_evidence)
    evidence_text = " ".join(str(item.to_dict()) for item in result.qa_evidence)
    assert "tax-synthetic" not in evidence_text
    assert "synthetic-given" not in evidence_text


@pytest.mark.parametrize("entity", sorted(EXPECTED_SILVER_ENTITIES))
def test_bluestone_adapter_runs_against_local_data_500k_files(entity: str) -> None:
    sample_files = sorted((DATA_ROOT / entity).glob(f"{entity}_*.xml"))
    if not sample_files:
        pytest.skip("data_500k local BlueStone dataset is not present in this environment")

    assert len(sample_files) == 10
    failures = []
    for sample_file in sample_files:
        try:
            result = run_bluestone_adapter_for_file(
                entity=entity,
                source_file=sample_file,
                ingestion_run_id="local-data-500k-sample",
                provider_spec_root=SPEC_ROOT,
                model_root=MODEL_ROOT,
            )

            assert result.bronze_records, sample_file
            assert set(result.silver_rows) == EXPECTED_SILVER_ENTITIES[entity], sample_file
            assert result.quarantine_records == [], sample_file
            assert all(record.source_checksum for record in result.bronze_records)
            assert all(record.source_lineage_ref for record in result.bronze_records)
            assert not evidence_contains_sensitive_raw_value(result.qa_evidence)
        except Exception as error:  # noqa: BLE001
            checksum = sha256(sample_file.read_bytes()).hexdigest()
            failures.append(
                "provider=data_provider_2_bluestone_health "
                f"entity={entity} source_file={sample_file} checksum={checksum} "
                f"error_type={type(error).__name__} decision=fail message={error}"
            )

    assert failures == []
