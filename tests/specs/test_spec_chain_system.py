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
PLAN_04_5_PATH = REPO_ROOT / "docs" / "04_5_local_data_workbench_and_model_evolution_plan.md"
PLAN_05_PATH = REPO_ROOT / "docs" / "05_databricks_validation_and_rollout_plan.md"
ROLLOUT_PATH = REPO_ROOT / "docs" / "agentic_rollout.md"
PRD_PATH = REPO_ROOT / "docs" / "technical_prd_agentops_operating_spec.md"
SKILL_STRATEGY_PATH = REPO_ROOT / "docs" / "agentops_skill_strategy.md"
FILESYSTEM_CONVENTIONS_PATH = REPO_ROOT / "docs" / "agentops_filesystem_conventions.md"
ORCHESTRATOR_SKILL_PATH = (
    REPO_ROOT
    / ".agent"
    / "skills"
    / "local-postgres-dbt-modeling-orchestrator"
    / "SKILL.md"
)
ITERATION_PACKET_TEMPLATE_PATH = (
    REPO_ROOT / ".agent" / "spec_templates" / "model_iteration_packet.template.yaml"
)
SEMANTIC_ISSUE_TEMPLATE_PATH = (
    REPO_ROOT / ".agent" / "spec_templates" / "semantic_discovery_issue.template.yaml"
)
NORMALIZATION_PROBE_TEMPLATE_PATH = (
    REPO_ROOT / ".agent" / "spec_templates" / "normalization_probe.template.yaml"
)


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


def test_plan_04_5_is_propagated_as_operating_plan() -> None:
    plan = PLAN_04_5_PATH.read_text(encoding="utf-8")
    rollout = ROLLOUT_PATH.read_text(encoding="utf-8")
    prd = PRD_PATH.read_text(encoding="utf-8")
    skill_strategy = SKILL_STRATEGY_PATH.read_text(encoding="utf-8")
    filesystem = FILESYSTEM_CONVENTIONS_PATH.read_text(encoding="utf-8")
    skill = ORCHESTRATOR_SKILL_PATH.read_text(encoding="utf-8")

    required_plan_sections = [
        "## Purpose",
        "## Scope",
        "## Authority And Source Of Truth",
        "## Central Model Registry",
        "## Iteration Packet Contract",
        "## Real-Time Feedback Loop",
        "## Required Templates",
        "## DoR",
        "## Execution Model",
        "## Normalization Depth",
        "## Chaotic Discovery Guardrails",
        "## Quality Metrics",
        "## dbt And PostgreSQL Requirements",
        "## Advancement Gate",
        "## DoD",
    ]
    for section in required_plan_sections:
        assert section in plan

    assert "tested local SQL output" in plan
    assert "business_question_registry" in plan
    assert "iteration_packet.yaml" in plan
    assert "db_state_snapshot.yaml" in plan
    assert "dbt_artifacts_manifest.yaml" in plan
    assert "lineage_summary.yaml" in plan
    assert "qa_gate_summary.yaml" in plan
    assert "rollback_plan.yaml" in plan
    assert ".agent/spec_templates/model_iteration_packet.template.yaml" in plan
    assert ".agent/spec_templates/normalization_probe.template.yaml" in plan
    assert ".agent/spec_templates/semantic_discovery_issue.template.yaml" in plan
    assert "first decompose the problem into a normalization probe" in plan
    assert "scratch transition table" in plan
    assert "Create a semantic discovery issue only when" in plan
    assert "entity mismatch counts" in plan
    assert "PostgreSQL feedback after every deploy" in plan
    assert "OpenLineage/Marquez feedback" in plan
    assert "metadata/model_specs/evolution/V0_N/" in plan
    assert "## Prompt 4.5: Local Data Workbench And Model Evolution" in rollout
    assert "| Local data workbench and model evolution |" in rollout
    assert "business-question registry version BQ_V0_N" in rollout
    assert "normalization_probe.template.yaml" in rollout
    assert "semantic_discovery_issue.template.yaml" in rollout
    assert "first decompose the problem into a small normalization probe" in rollout
    assert "Prompt 4.5" in rollout
    assert "local-postgres-dbt-modeling-orchestrator" in prd
    assert "Local Model Evolution Plane" in prd
    assert "Plan 04.5 acceptance is stricter" in prd
    assert "local-postgres-dbt-modeling-orchestrator" in skill_strategy
    assert "business-question registry version" in filesystem
    assert "iteration packet" in skill
    assert "normalization probe" in skill
    assert "semantic discovery issue" in skill
    assert "Every resolved business question" in skill

    packet_template = load_yaml(ITERATION_PACKET_TEMPLATE_PATH)
    probe_template = load_yaml(NORMALIZATION_PROBE_TEMPLATE_PATH)
    issue_template = load_yaml(SEMANTIC_ISSUE_TEMPLATE_PATH)
    assert packet_template["artifact"] == "model_iteration_packet"
    assert "entity_mismatch_checks" in packet_template["database_feedback"]
    assert "nested_payload_checks" in packet_template["database_feedback"]
    assert probe_template["artifact"] == "normalization_probe"
    assert probe_template["scratch"]["schema"] == "scratch"
    assert "promote_to_snapshot" in probe_template["decision"]["allowed_outcomes"]
    assert "revise_probe" in probe_template["decision"]["allowed_outcomes"]
    assert issue_template["artifact"] == "semantic_discovery_issue"
    assert "nested_payload" in issue_template["allowed_issue_types"]
    assert "entity_mismatch" in issue_template["allowed_issue_types"]
    assert "request_hitl" in issue_template["required_action"]["allowed_actions"]


def test_plan_05_keeps_databricks_rollout_cloud_agnostic() -> None:
    plan = PLAN_05_PATH.read_text(encoding="utf-8")

    required_sections = [
        "## Cloud-Agnostic Architecture Requirement",
        "## Declarative Spark And Pipeline Contract",
        "## Terraform And Multi-Cloud CI/CD Contract",
    ]
    for section in required_sections:
        assert section in plan

    assert "Databricks-oriented but the project architecture remains cloud agnostic" in plan
    assert "Databricks, Unity Catalog, Lakeflow, and Databricks Asset Bundles" in plan
    assert "Spark Declarative Pipelines" in plan
    assert "Terraform modules must be parameterized" in plan
    assert "The same pipeline shape should be portable to another cloud" in plan
    assert "target-binding separation" in plan
    assert "Plan 04.5 model-evolution evidence" in plan
    assert "`terraform apply` remains blocked until explicit HITL approval" in plan
