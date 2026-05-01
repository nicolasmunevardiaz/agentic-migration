from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_ROOT = REPO_ROOT / "dbt"
EVOLUTION_ROOT = REPO_ROOT / "metadata/model_specs/evolution/V0_5"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_encounter_derived_models_are_declared_in_derived_schema() -> None:
    project = load_yaml(DBT_ROOT / "dbt_project.yml")
    schema = load_yaml(DBT_ROOT / "models/derived/encounters/schema.yml")

    assert project["models"]["agentic_migration_local"]["derived"]["+schema"] == "derived"
    assert project["models"]["agentic_migration_local"]["derived"]["+materialized"] == "view"
    assert {model["name"] for model in schema["models"]} == {
        "encounter_source_normalized",
        "encounter_fact",
        "encounter_coverage_status_dimension",
        "encounter_record_status_dimension",
        "encounter_member_summary",
    }


def test_encounter_derived_sql_preserves_relationship_quality_flags() -> None:
    sql_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((DBT_ROOT / "models/derived/encounters").rglob("*.sql"))
    )

    assert "{{ source('review', 'silver_encounters') }}" in sql_text
    assert "encounter_provider_id" in sql_text
    assert "patient_provider_member_id" in sql_text
    assert "has_orphan_member_reference" in sql_text
    assert "has_missing_encounter_datetime" in sql_text
    assert "clinical meaning" not in sql_text.lower()
    assert "gold." not in sql_text.lower()
    assert "databricks" not in sql_text.lower()


def test_encounter_v0_5_records_encounter_evidence() -> None:
    db_state = load_yaml(EVOLUTION_ROOT / "db_state_snapshot.yaml")
    probe = load_yaml(EVOLUTION_ROOT / "normalization_probe_encounters.yaml")

    assert db_state["encounter_quality_summary"]["source_relation"] == (
        "review.silver_encounters"
    )
    assert db_state["derived_outputs"]["derived.encounter_fact"]["row_count"] == 535326
    assert (
        db_state["derived_outputs"]["derived.encounter_member_summary"]["row_count"]
        == 261959
    )
    assert db_state["encounter_quality_summary"]["duplicate_encounter_reference_count"] == 0
    assert db_state["encounter_quality_summary"]["missing_datetime_row_count"] == 322555
    assert probe["metrics"]["orphan_member_reference_row_count"] == 297896
    assert probe["decision"]["outcome"] == "promote_to_snapshot"
