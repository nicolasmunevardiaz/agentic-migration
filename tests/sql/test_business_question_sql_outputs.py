from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_ROOT = REPO_ROOT / "dbt"
EVOLUTION_ROOT = REPO_ROOT / "metadata/model_specs/evolution/V0_2"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_dbt_project_uses_local_postgres_profile_without_committed_secret() -> None:
    project = load_yaml(DBT_ROOT / "dbt_project.yml")
    profile = (DBT_ROOT / "profiles.yml").read_text(encoding="utf-8")

    assert project["profile"] == "agentic_migration_local"
    assert "type: postgres" in profile
    assert "env_var('PGPASSWORD'" in profile
    assert "databricks" not in profile.lower()
    assert "terraform" not in profile.lower()


def test_every_business_question_has_a_versioned_dbt_sql_model() -> None:
    registry = load_yaml(EVOLUTION_ROOT / "business_question_registry.yaml")
    sql_files = {path.stem for path in (DBT_ROOT / "models/business_questions").glob("bq_*.sql")}

    assert len(registry["question_states"]) == 16
    for question in registry["question_states"]:
        model_name = question["sql_output"].split(".", 1)[1]
        assert model_name in sql_files
        sql = (DBT_ROOT / "models/business_questions" / f"{model_name}.sql").read_text(
            encoding="utf-8"
        )
        assert question["question_id"] in sql
        assert "active_batch_filter" in sql


def test_dbt_sql_outputs_stay_local_and_do_not_create_production_gold() -> None:
    sql_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((DBT_ROOT / "models/business_questions").glob("*.sql"))
    )

    forbidden = ["databricks", "unity catalog", "terraform", "production", "gold."]
    assert not any(token in sql_text.lower() for token in forbidden)
    assert "{{ source('review'" in sql_text


def test_bq_016_records_reference_alignment_probe() -> None:
    model_path = (
        DBT_ROOT / "models/business_questions/bq_016_medication_unit_prices_by_coverage.sql"
    )
    sql = model_path.read_text(encoding="utf-8")
    probe = load_yaml(EVOLUTION_ROOT / "normalization_probe_bq_016_reference_alignment.yaml")
    evidence = load_yaml(EVOLUTION_ROOT / "sql_answer_evidence.yaml")

    assert "regexp_replace(costs.encounter_reference" in sql
    assert "regexp_replace(costs.member_reference" in sql
    assert probe["decision"]["outcome"] == "promote_to_snapshot"
    assert probe["business_question_ids"] == ["BQ-016"]
    assert any(
        result["question_id"] == "BQ-016" and "semantic_review" in result
        for result in evidence["business_question_results"]
    )
