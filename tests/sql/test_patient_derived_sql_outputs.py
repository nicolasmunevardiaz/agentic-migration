from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_ROOT = REPO_ROOT / "dbt"
EVOLUTION_ROOT = REPO_ROOT / "metadata/model_specs/evolution/V0_5"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_patient_derived_models_are_declared_in_derived_schema() -> None:
    project = load_yaml(DBT_ROOT / "dbt_project.yml")
    schema = load_yaml(DBT_ROOT / "models/derived/patients/schema.yml")

    assert project["models"]["agentic_migration_local"]["derived"]["+schema"] == "derived"
    assert project["models"]["agentic_migration_local"]["derived"]["+materialized"] == "view"
    assert {model["name"] for model in schema["models"]} == {
        "patient_source_normalized",
        "patient_dimension",
        "patient_transaction_activity",
    }


def test_patient_derived_sql_preserves_provider_scoped_lineage() -> None:
    sql_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((DBT_ROOT / "models/derived/patients").rglob("*.sql"))
    )

    assert "{{ source('landing', 'members') }}" in sql_text
    assert "patient_provider_member_id" in sql_text
    assert "provider_slug" in sql_text
    assert "member_reference" in sql_text
    assert "source_lineage_ref" in sql_text
    assert "enterprise" not in sql_text.lower()
    assert "databricks" not in sql_text.lower()
    assert "gold." not in sql_text.lower()


def test_patient_derived_v0_5_records_conflict_and_activity_evidence() -> None:
    db_state = load_yaml(EVOLUTION_ROOT / "db_state_snapshot.yaml")
    probe = load_yaml(
        EVOLUTION_ROOT / "normalization_probe_patients_provider_scoped_dimension.yaml"
    )

    assert db_state["derived_outputs"]["derived.patient_dimension"]["grain"] == (
        "one provider-scoped member_reference"
    )
    assert any(
        item["provider_slug"] == "data_provider_5_pacific_shield_insurance"
        and item["patients_with_transactional_data"] == 0
        for item in db_state["provider_activity_summary"]
    )
    assert probe["target_entity_candidate"] == "derived.patient_dimension"
    assert "enterprise identity" in probe["hypothesis"]
