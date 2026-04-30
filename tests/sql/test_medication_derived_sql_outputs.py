from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_ROOT = REPO_ROOT / "dbt"
EVOLUTION_ROOT = REPO_ROOT / "metadata/model_specs/evolution/V0_5"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_medication_derived_models_are_declared_in_derived_schema() -> None:
    project = load_yaml(DBT_ROOT / "dbt_project.yml")
    schema = load_yaml(DBT_ROOT / "models/derived/medications/schema.yml")

    assert project["models"]["agentic_migration_local"]["derived"]["+schema"] == "derived"
    assert project["models"]["agentic_migration_local"]["derived"]["+materialized"] == "view"
    assert {model["name"] for model in schema["models"]} == {
        "medication_source_normalized",
        "medication_fact",
        "medication_code_dimension",
        "medication_code_variant_dimension",
        "medication_description_variant_dimension",
        "medication_record_status_dimension",
        "medication_member_summary",
    }


def test_medication_derived_sql_preserves_codes_without_interpretation() -> None:
    sql_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((DBT_ROOT / "models/derived/medications").glob("*.sql"))
    )

    assert "{{ source('review', 'silver_medications') }}" in sql_text
    assert "medication_code_id" in sql_text
    assert "medication_source_code" in sql_text
    assert "medication_source_code_raw" in sql_text
    assert "description_variant" in sql_text
    assert "has_orphan_condition_reference" in sql_text
    assert "has_missing_medication_datetime" in sql_text
    assert "formulary" not in sql_text.lower()
    assert "gold." not in sql_text.lower()
    assert "databricks" not in sql_text.lower()


def test_medication_v0_5_records_medication_evidence() -> None:
    db_state = load_yaml(EVOLUTION_ROOT / "db_state_snapshot.yaml")
    probe = load_yaml(EVOLUTION_ROOT / "normalization_probe_medications.yaml")

    assert db_state["medication_quality_summary"]["source_relation"] == (
        "review.silver_medications"
    )
    assert db_state["derived_outputs"]["derived.medication_fact"]["row_count"] == 1606374
    assert (
        db_state["derived_outputs"]["derived.medication_member_summary"]["row_count"]
        == 480914
    )
    assert db_state["medication_quality_summary"]["duplicate_medication_reference_count"] == 0
    assert db_state["medication_quality_summary"]["missing_datetime_row_count"] == 638728
    assert probe["metrics"]["medication_code_dimension_row_count"] == 700
    assert probe["metrics"]["medication_code_variant_dimension_row_count"] == 1015
    assert probe["metrics"]["medication_description_variant_dimension_row_count"] == 1260
    assert probe["decision"]["outcome"] == "promote_to_snapshot"
