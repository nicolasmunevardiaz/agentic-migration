from pathlib import Path

import yaml

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
    assert profile["status"] == "contract_defined_not_executed"
    assert profile["allowed_paths"]["runtime_outputs"].startswith("artifacts/")
    assert profile["evidence_status"]["local_validation_state"] == "local_validated"
    assert profile["evidence_status"]["databricks_validation_state"] == (
        "not_databricks_certified"
    )
    assert all(
        dependency["approval_status"] == "pending_human_approval"
        for dependency in profile["candidate_dependencies"]
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


def test_local_runtime_reports_separate_local_and_databricks_certification() -> None:
    qa_report = (REPO_ROOT / "reports" / "qa" / "local_runtime_certification.md").read_text(
        encoding="utf-8"
    )
    privacy_report = (
        REPO_ROOT / "reports" / "privacy" / "local_runtime_dependency_review.md"
    ).read_text(encoding="utf-8")

    assert "validation_state: `local_validated`" in qa_report
    assert "databricks_state: `not_databricks_certified`" in qa_report
    assert "dependencies_blocked_pending_hitl" in privacy_report
