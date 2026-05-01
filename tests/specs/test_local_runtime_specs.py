from pathlib import Path

import yaml

from src.handlers.local_postgres_workbench_deploy import render_deploy_sql

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = REPO_ROOT / "metadata" / "runtime_specs" / "local"


def load_runtime_yaml(name: str) -> dict:
    return yaml.safe_load((RUNTIME_ROOT / name).read_text(encoding="utf-8"))


def collect_string_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for entry in value for item in collect_string_values(entry)]
    if isinstance(value, dict):
        return [item for entry in value.values() for item in collect_string_values(entry)]
    return []


def test_local_runtime_profile_declares_scope_and_dependency_gates() -> None:
    profile = load_runtime_yaml("local_runtime_profile.yaml")

    assert profile["profile_name"] == "local_dev"
    assert profile["status"] == "local_runtime_contract_validated"
    assert set(profile["profiles"]) == {"local_dev", "databricks_dev", "databricks_prod"}
    assert profile["allowed_paths"]["runtime_outputs"].startswith("artifacts/")
    assert profile["evidence_status"]["local_validation_state"] == "local_validated"
    assert profile["evidence_status"]["databricks_validation_state"] == (
        "not_databricks_certified"
    )
    dependencies = {
        dependency["name"]: dependency
        for dependency in profile["candidate_dependencies"]
    }
    assert dependencies["pyspark"]["approval_status"] == "approved_for_local_import_only"
    assert dependencies["delta-spark"]["approval_status"] == "approved_for_local_import_only"
    assert (
        dependencies["openlineage-python"]["approval_status"]
        == "approved_for_local_import_only"
    )
    assert dependencies["marquez"]["approval_status"] == "pending_human_approval"
    assert profile["evidence_status"]["dependency_installation_state"] == (
        "python_packages_installed_import_only"
    )
    assert profile["evidence_status"]["databricks_validation_state"] == (
        "not_databricks_certified"
    )


def test_runtime_interface_contract_covers_required_interfaces() -> None:
    contract = load_runtime_yaml("runtime_interface_contract.yaml")
    expected_interfaces = {
        "provider_parser",
        "bronze_writer",
        "canonical_mapper",
        "silver_writer",
        "quarantine_writer",
        "qa_evidence_writer",
        "lineage_emitter",
        "runtime_adapter",
    }

    assert set(contract["interfaces"]) == expected_interfaces
    assert contract["runtime_profile"] == "local_dev"
    assert contract["certification_state"]["local_validation_state"] == "local_validated"
    assert contract["certification_state"]["databricks_validation_state"] == (
        "not_databricks_certified"
    )
    assert contract["flow"] == [
        "provider_parser",
        "bronze_writer",
        "canonical_mapper",
        "silver_writer",
        "quarantine_writer",
        "qa_evidence_writer",
        "lineage_emitter",
        "runtime_adapter",
    ]


def test_local_runtime_specs_do_not_embed_databricks_or_production_execution() -> None:
    forbidden_fragments = {
        "DATABRICKS" + "_TOKEN",
        "databricks://",
        "/Workspace/",
        "terraform apply",
        "bundle deploy",
        "production_data_path",
    }

    for spec_path in RUNTIME_ROOT.glob("*.yaml"):
        values = collect_string_values(yaml.safe_load(spec_path.read_text()))
        assert not any(
            fragment in value
            for value in values
            for fragment in forbidden_fragments
        )


def test_dependency_review_records_approved_import_only_packages() -> None:
    privacy_report = (
        REPO_ROOT / "reports" / "privacy" / "local_runtime_dependency_review.md"
    ).read_text(encoding="utf-8")
    qa_report = (REPO_ROOT / "reports" / "qa" / "local_runtime_certification.md").read_text(
        encoding="utf-8"
    )

    assert "python_dependencies_approved_for_local_import_only" in privacy_report
    assert "`pyspark` | `4.1.1`" in privacy_report
    assert "`delta-spark` | `4.2.0`" in privacy_report
    assert "`openlineage-python` | `1.46.0`" in privacy_report
    assert "Do not start Docker services" in privacy_report
    assert "Do not write Delta tables" in privacy_report
    assert "pyspark>=4.1.1" in qa_report
    assert "not_databricks_certified" in qa_report


def test_macos_requirements_use_portable_paths_and_colima_only() -> None:
    requirements = (
        REPO_ROOT / "docs" / "local_runtime_macos_requirements.md"
    ).read_text(encoding="utf-8")

    assert "Docker Desktop is not approved" in requirements
    assert "cd /path/to/agentic-migration" in requirements
    assert "/Users/" not in requirements
    assert "OneDrive" not in requirements


def test_local_runtime_reports_separate_local_and_databricks_certification() -> None:
    qa_report = (REPO_ROOT / "reports" / "qa" / "local_runtime_certification.md").read_text(
        encoding="utf-8"
    )
    privacy_report = (
        REPO_ROOT / "reports" / "privacy" / "local_runtime_dependency_review.md"
    ).read_text(encoding="utf-8")

    assert "validation_state: `local_validated`" in qa_report
    assert "databricks_state: `not_databricks_certified`" in qa_report
    assert "python_dependencies_approved_for_local_import_only" in privacy_report


def test_local_postgres_workbench_spec_declares_expected_schemas_and_tables() -> None:
    spec = load_runtime_yaml("local_postgres_workbench.yaml")

    assert spec["artifact"] == "local_postgres_workbench"
    assert spec["database"]["engine"] == "postgresql"
    assert spec["database"]["default_database"] == "agentic_migration_local"
    assert {schema["name"] for schema in spec["schemas"]} == {"landing"}
    assert spec["landing_tables"]["enabled"] is True
    assert set(spec["landing_tables"]["generated_table_names"]) == {
        "landing.conditions",
        "landing.cost_records",
        "landing.coverage_periods",
        "landing.encounters",
        "landing.medications",
        "landing.members",
        "landing.observations",
    }
    assert spec["manual_tables"] == []


def test_local_postgres_workbench_rendered_sql_is_idempotent_and_safe() -> None:
    sql = render_deploy_sql(
        RUNTIME_ROOT / "local_postgres_workbench.yaml",
        REPO_ROOT,
    )
    upper_sql = sql.upper()

    assert "CREATE SCHEMA IF NOT EXISTS" in sql
    assert "CREATE TABLE IF NOT EXISTS" in sql
    assert "ADD COLUMN IF NOT EXISTS" in sql
    assert "CREATE INDEX IF NOT EXISTS" in sql
    assert '"landing"."members"' in sql
    assert '"review"' not in sql
    assert '"scratch"' not in sql
    assert '"evidence"' not in sql
    assert '"ops"' not in sql
    assert '"data_quality"' not in sql
    assert "DROP " not in upper_sql
    assert "TRUNCATE " not in upper_sql
    assert "DELETE " not in upper_sql
