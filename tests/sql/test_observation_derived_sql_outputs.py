from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_ROOT = REPO_ROOT / "dbt"
EVOLUTION_ROOT = REPO_ROOT / "metadata/model_specs/evolution/V0_5"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_observation_derived_models_are_declared_in_derived_schema() -> None:
    project = load_yaml(DBT_ROOT / "dbt_project.yml")
    schema = load_yaml(DBT_ROOT / "models/derived/observations/schema.yml")

    assert project["models"]["agentic_migration_local"]["derived"]["+schema"] == "derived"
    assert project["models"]["agentic_migration_local"]["derived"]["+materialized"] == "view"
    assert {model["name"] for model in schema["models"]} == {
        "observation_payload_source_normalized",
        "observation_vital_components",
        "observation_vitals_wide",
    }


def test_observation_derived_sql_extracts_nested_payload_without_raw_examples() -> None:
    sql_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((DBT_ROOT / "models/derived/observations").glob("*.sql"))
    )

    assert "{{ source('review', 'silver_observations') }}" in sql_text
    assert "observation_payload_raw #>> '{height,value}'" in sql_text
    assert "observation_payload_raw #>> '{blood_pressure,systolic}'" in sql_text
    assert "payload_value_path" in sql_text
    assert "patient_provider_member_id" in sql_text
    assert "source_lineage_ref" in sql_text
    assert "diagnosis" not in sql_text.lower()
    assert "gold." not in sql_text.lower()
    assert "databricks" not in sql_text.lower()


def test_observation_v0_5_records_nested_payload_evidence() -> None:
    db_state = load_yaml(EVOLUTION_ROOT / "db_state_snapshot.yaml")
    probe = load_yaml(EVOLUTION_ROOT / "normalization_probe_observations_nested_payload.yaml")

    assert db_state["observation_nested_summary"]["nested_column"] == (
        "observation_payload_raw"
    )
    assert (
        db_state["derived_outputs"]["derived.observation_payload_source_normalized"][
            "row_count"
        ]
        == 535326
    )
    assert (
        db_state["derived_outputs"]["derived.observation_vital_components"]["row_count"]
        == 3279647
    )
    assert db_state["observation_nested_summary"]["silver_extract_mismatch_rows"] == 0
    assert len(db_state["provider_payload_summary"]) == 4
    assert probe["decision"]["outcome"] == "promote_to_snapshot"
    assert probe["business_question_ids"] == []
    assert probe["metrics"]["component_counts"]["bmi"] == 390704
