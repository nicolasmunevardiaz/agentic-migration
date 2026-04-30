from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_ROOT = REPO_ROOT / "dbt"
EVOLUTION_ROOT = REPO_ROOT / "metadata/model_specs/evolution/V0_5"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_cost_record_derived_models_are_declared_in_derived_schema() -> None:
    project = load_yaml(DBT_ROOT / "dbt_project.yml")
    schema = load_yaml(DBT_ROOT / "models/derived/cost_records/schema.yml")

    assert project["models"]["agentic_migration_local"]["derived"]["+schema"] == "derived"
    assert project["models"]["agentic_migration_local"]["derived"]["+materialized"] == "view"
    assert {model["name"] for model in schema["models"]} == {
        "cost_record_source_normalized",
        "cost_record_fact",
        "cost_amount_source_dimension",
        "cost_record_status_dimension",
        "cost_record_member_summary",
    }


def test_cost_record_derived_sql_preserves_source_amounts_without_interpretation() -> None:
    sql_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((DBT_ROOT / "models/derived/cost_records").glob("*.sql"))
    )

    assert "{{ source('review', 'silver_cost_records') }}" in sql_text
    assert "source_cost_amount" in sql_text
    assert "source_cost_amount_field_name" in sql_text
    assert "has_missing_cost_amount" in sql_text
    assert "has_orphan_medication_reference" in sql_text
    assert "benchmark" not in sql_text.lower()
    assert "payment_conclusion" not in sql_text.lower()
    assert "gold." not in sql_text.lower()
    assert "databricks" not in sql_text.lower()


def test_cost_record_v0_5_records_cost_evidence() -> None:
    db_state = load_yaml(EVOLUTION_ROOT / "db_state_snapshot.yaml")
    probe = load_yaml(EVOLUTION_ROOT / "normalization_probe_cost_records.yaml")

    assert db_state["cost_record_quality_summary"]["source_relation"] == (
        "review.silver_cost_records"
    )
    assert db_state["derived_outputs"]["derived.cost_record_fact"]["row_count"] == 1606374
    assert (
        db_state["derived_outputs"]["derived.cost_record_member_summary"]["row_count"]
        == 480914
    )
    assert db_state["cost_record_quality_summary"]["missing_amount_row_count"] == 146375
    assert db_state["cost_record_quality_summary"]["orphan_medication_reference_row_count"] == 0
    assert probe["metrics"]["cost_amount_source_dimension_row_count"] == 4
    assert probe["decision"]["outcome"] == "promote_to_snapshot"
