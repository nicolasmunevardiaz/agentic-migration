from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "metadata/model_specs/dbt/dbt_model_layering_contract.yaml"
DERIVED_ROOT = REPO_ROOT / "dbt/models/derived"

EXPECTED_MODEL_LOCATIONS = {
    "silver/normalized": {
        "patient_source_normalized.sql",
        "observation_payload_source_normalized.sql",
        "encounter_source_normalized.sql",
        "condition_source_normalized.sql",
        "medication_source_normalized.sql",
        "cost_record_source_normalized.sql",
        "coverage_source_normalized.sql",
    },
    "silver/dq": {
        "patient_transaction_activity.sql",
        "coverage_period_survivor_candidate.sql",
    },
    "gold/facts": {
        "observation_vital_components.sql",
        "encounter_fact.sql",
        "condition_fact.sql",
        "medication_fact.sql",
        "cost_record_fact.sql",
        "coverage_period_fact.sql",
        "coverage_period_survivor_fact.sql",
    },
    "gold/dimensions": {
        "encounter_coverage_status_dimension.sql",
        "encounter_record_status_dimension.sql",
        "condition_code_dimension.sql",
        "condition_record_status_dimension.sql",
        "medication_code_dimension.sql",
        "medication_code_variant_dimension.sql",
        "medication_description_variant_dimension.sql",
        "medication_record_status_dimension.sql",
        "cost_amount_source_dimension.sql",
        "cost_record_status_dimension.sql",
        "coverage_status_dimension.sql",
        "patient_dimension.sql",
    },
    "gold/marts": {
        "observation_vitals_wide.sql",
        "encounter_member_summary.sql",
        "condition_member_summary.sql",
        "medication_member_summary.sql",
        "cost_record_member_summary.sql",
        "coverage_member_summary.sql",
    },
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_dbt_model_layering_contract_is_declared() -> None:
    contract = _load_yaml(CONTRACT_PATH)

    assert contract["contract_id"] == "DBT_MODEL_LAYERING_CONTRACT_V0_5"
    assert contract["model_snapshot"] == "V0_5"
    assert contract["status"] == "approved"
    assert contract["layer_contract"]["silver"]["production_consumption"] is False
    assert contract["layer_contract"]["gold"]["production_consumption"] is True
    assert contract["provider_dimension_rule"]["required_future_model"] == "dim_provider"


def test_derived_sql_models_live_under_approved_layer_paths() -> None:
    sql_paths = sorted(DERIVED_ROOT.rglob("*.sql"))
    assert len(sql_paths) == 34

    for path in sql_paths:
        relative = path.relative_to(DERIVED_ROOT)
        relative_parts = relative.parts
        assert len(relative_parts) >= 4
        layer_key = "/".join(relative_parts[1:3])
        assert layer_key in EXPECTED_MODEL_LOCATIONS
        assert path.name in EXPECTED_MODEL_LOCATIONS[layer_key]


def test_source_normalized_models_are_not_gold_models() -> None:
    for path in DERIVED_ROOT.rglob("*source_normalized.sql"):
        assert "/silver/normalized/" in path.as_posix()
        assert "/gold/" not in path.as_posix()
