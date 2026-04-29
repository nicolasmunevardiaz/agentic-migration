from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = REPO_ROOT / "metadata" / "model_specs"
PROFILE_PATH = MODEL_ROOT / "impact" / "business_question_profiles.yaml"
RUNBOOK_PATH = REPO_ROOT / "reports" / "hitl" / "canonical_drift_decision_runbook.md"
BRONZE_PATH = MODEL_ROOT / "bronze" / "bronze_contract.yaml"
MATRIX_PATH = MODEL_ROOT / "mappings" / "provider_to_silver_matrix.yaml"
RISK_PATH = MODEL_ROOT / "impact" / "modeling_risk_report.md"
PROVIDER_ROOT = REPO_ROOT / "metadata" / "provider_specs"
SILVER_ROOT = MODEL_ROOT / "silver"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def all_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for entry in value for item in all_strings(entry)]
    if isinstance(value, dict):
        return [item for entry in value.values() for item in all_strings(entry)]
    return []


def test_plan_02_readiness_gate_is_clear() -> None:
    profile = load_yaml(PROFILE_PATH)
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")

    assert profile["status"] == "approved"
    assert profile["scope"]["hitl_approval"]["status"] == "approved"
    assert len(profile["business_question_profiles"]) == 16
    assert all(
        entry["allowed_next_action"] == "plan_02_allowed"
        for entry in profile["business_question_profiles"]
    )
    assert all(decision["status"] == "applied" for decision in profile["field_decisions"])
    assert all(
        decision["selected_option"]["plan_02_allowance"] == "allowed"
        for decision in profile["field_decisions"]
    )

    assert "Status: `ready_for_plan_02`" in runbook
    for number in range(1, 15):
        decision_id = f"DRIFT-{number:03d}"
        line = next(line for line in runbook.splitlines() if line.startswith(f"| {decision_id} |"))
        assert "| applied | no |" in line


def test_bronze_silver_and_matrix_chain_reconciles_provider_specs() -> None:
    bronze = load_yaml(BRONZE_PATH)
    matrix = load_yaml(MATRIX_PATH)
    provider_specs = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in PROVIDER_ROOT.glob("*/*.yaml")
    }

    bronze_paths = {contract["provider_spec_path"] for contract in bronze["source_contracts"]}
    matrix_paths = {
        row["provider_spec_path"]
        for row in matrix["mappings"]
        if row["source_header"] != "__metadata__"
    }

    assert bronze_paths == provider_specs
    assert matrix_paths <= provider_specs
    assert bronze["readiness"]["model_ready"] is True
    assert matrix["coverage_summary"]["field_decision_count"] == 205

    for path in SILVER_ROOT.glob("*.yaml"):
        silver = load_yaml(path)
        assert silver["entity"] in matrix["silver_entities"]
        assert silver["readiness"]["model_ready"] is True
        assert set(silver["provider_coverage"]["providers"]) <= {
            "data_provider_1_aegis_care_network",
            "data_provider_2_bluestone_health",
            "data_provider_3_northcare_clinics",
            "data_provider_4_valleybridge_medical",
            "data_provider_5_pacific_shield_insurance",
        }


def test_generated_modeling_risk_report_documents_boundaries() -> None:
    report = RISK_PATH.read_text(encoding="utf-8")

    assert "Plan 02 readiness is clear" in report
    assert "enterprise identity resolution is not performed" in report
    assert "diagnostic truth" in report
    assert "benchmark conclusions" in report
    assert "Pacific Shield duplicate `DX_CD`" in report
    assert "Databricks rollout" in report


def test_generated_specs_do_not_create_out_of_scope_artifacts() -> None:
    generated_paths = [
        BRONZE_PATH,
        MATRIX_PATH,
        RISK_PATH,
        *sorted(SILVER_ROOT.glob("*.yaml")),
    ]
    strings = []
    for path in generated_paths:
        if path.suffix == ".yaml":
            strings.extend(all_strings(load_yaml(path)))
        else:
            strings.append(path.read_text(encoding="utf-8"))

    databricks_specs = REPO_ROOT / "metadata" / "deployment_specs" / "databricks"
    assert not list(databricks_specs.glob("*.yaml"))
    assert not any(Path(text).is_absolute() for text in strings if "/" in text)
    assert not any("dashboard" in text.lower() for text in strings)
    assert not any("kpi" in text.lower() for text in strings)
    assert not any("raw sensitive value example" in text.lower() for text in strings)
