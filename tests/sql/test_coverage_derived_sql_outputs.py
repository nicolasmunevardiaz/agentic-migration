from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_ROOT = REPO_ROOT / "dbt"
EVOLUTION_ROOT = REPO_ROOT / "metadata/model_specs/evolution/V0_5"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_coverage_derived_models_are_declared_in_derived_schema() -> None:
    project = load_yaml(DBT_ROOT / "dbt_project.yml")
    schema = load_yaml(DBT_ROOT / "models/derived/coverage/schema.yml")

    assert project["models"]["agentic_migration_local"]["derived"]["+schema"] == "derived"
    assert project["models"]["agentic_migration_local"]["derived"]["+materialized"] == "view"
    assert {model["name"] for model in schema["models"]} == {
        "coverage_source_normalized",
        "coverage_period_fact",
        "coverage_status_dimension",
        "coverage_member_summary",
    }


def test_coverage_derived_sql_preserves_period_grain_and_quality_flags() -> None:
    sql_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((DBT_ROOT / "models/derived/coverage").glob("*.sql"))
    )

    assert "{{ source('review', 'silver_coverage_periods') }}" in sql_text
    assert "coverage_period_id" in sql_text
    assert "patient_provider_member_id" in sql_text
    assert "has_duplicate_period_key" in sql_text
    assert "has_implausible_coverage_date" in sql_text
    assert "current_eligibility" not in sql_text.lower()
    assert "gold." not in sql_text.lower()
    assert "databricks" not in sql_text.lower()


def test_coverage_v0_5_records_coverage_evidence() -> None:
    db_state = load_yaml(EVOLUTION_ROOT / "db_state_snapshot.yaml")
    probe = load_yaml(EVOLUTION_ROOT / "normalization_probe_coverage_periods.yaml")

    assert db_state["coverage_quality_summary"]["source_relation"] == (
        "review.silver_coverage_periods"
    )
    assert db_state["derived_outputs"]["derived.coverage_period_fact"]["row_count"] == 875760
    assert (
        db_state["derived_outputs"]["derived.coverage_member_summary"]["row_count"]
        == 479813
    )
    assert db_state["derived_outputs"]["derived.coverage_status_dimension"]["row_count"] == 2
    assert len(db_state["provider_coverage_fact_summary"]) == 5
    assert probe["metrics"]["inverted_date_range_count"] == 0
    assert probe["metrics"]["implausible_coverage_date_row_count"] == 1570
    assert probe["decision"]["outcome"] == "promote_to_snapshot"
