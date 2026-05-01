from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_ROOT = REPO_ROOT / "dbt"
EVOLUTION_ROOT = REPO_ROOT / "metadata/model_specs/evolution/V0_5"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_condition_derived_models_are_declared_in_derived_schema() -> None:
    project = load_yaml(DBT_ROOT / "dbt_project.yml")
    schema = load_yaml(DBT_ROOT / "models/derived/conditions/schema.yml")

    assert project["models"]["agentic_migration_local"]["derived"]["+schema"] == "derived"
    assert project["models"]["agentic_migration_local"]["derived"]["+materialized"] == "view"
    assert {model["name"] for model in schema["models"]} == {
        "condition_source_normalized",
        "condition_fact",
        "condition_code_dimension",
        "condition_record_status_dimension",
        "condition_member_summary",
    }


def test_condition_derived_sql_preserves_codes_without_clinical_interpretation() -> None:
    sql_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((DBT_ROOT / "models/derived/conditions").rglob("*.sql"))
    )

    assert "{{ source('landing', 'conditions') }}" in sql_text
    assert "condition_code_id" in sql_text
    assert "condition_source_code" in sql_text
    assert "condition_code_hint" in sql_text
    assert "has_orphan_encounter_reference" in sql_text
    assert "icd10" not in sql_text.lower()
    assert "gold." not in sql_text.lower()
    assert "databricks" not in sql_text.lower()


def test_condition_v0_5_records_condition_evidence() -> None:
    db_state = load_yaml(EVOLUTION_ROOT / "db_state_snapshot.yaml")
    probe = load_yaml(EVOLUTION_ROOT / "normalization_probe_conditions.yaml")

    assert db_state["condition_quality_summary"]["source_relation"] in {
        "review.silver_conditions",
        "landing.conditions",
    }
    assert db_state["derived_outputs"]["derived.condition_fact"]["row_count"] == 803595
    assert (
        db_state["derived_outputs"]["derived.condition_member_summary"]["row_count"]
        == 369363
    )
    assert db_state["condition_quality_summary"]["duplicate_condition_reference_count"] == 0
    assert db_state["condition_quality_summary"]["orphan_member_reference_row_count"] == 402976
    assert probe["metrics"]["condition_code_dimension_row_count"] == 320
    assert probe["decision"]["outcome"] == "promote_to_snapshot"
