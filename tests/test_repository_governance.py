import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def test_agentops_required_paths_exist() -> None:
    required_paths = [
        ".agent/skills",
        ".agent/spec_templates",
        "docs",
        "metadata/provider_specs",
        "metadata/model_specs/bronze",
        "metadata/model_specs/silver",
        "metadata/model_specs/mappings",
        "metadata/deployment_specs/databricks",
        "metadata/runtime_specs/local",
        "reports/qa",
        "reports/privacy",
        "reports/hitl",
        "logs",
        "logs/local_runtime",
        "src/adapters",
        "src/common",
        "src/handlers",
        "tests/specs",
        "tests/adapters",
        "tests/fixtures",
    ]

    missing = [path for path in required_paths if not (REPO_ROOT / path).exists()]

    assert missing == []


def test_large_source_data_is_not_tracked() -> None:
    assert not any(path.startswith("data_500k/") for path in tracked_files())


def test_local_and_secret_files_are_not_tracked() -> None:
    forbidden_suffixes = ("/.DS_Store",)
    forbidden_names = {".DS_Store", ".env"}
    forbidden_prefixes = (".env.",)

    violations = []
    for path in tracked_files():
        name = Path(path).name
        if (
            name in forbidden_names
            or name.startswith(forbidden_prefixes)
            or path.endswith(forbidden_suffixes)
        ):
            violations.append(path)

    assert violations == []


def test_dependabot_is_not_configured() -> None:
    assert not (REPO_ROOT / ".github" / "dependabot.yml").exists()


def test_issue_templates_exist() -> None:
    required_templates = [
        ".github/ISSUE_TEMPLATE/task.yml",
        ".github/ISSUE_TEMPLATE/hitl-decision.yml",
    ]

    missing = [path for path in required_templates if not (REPO_ROOT / path).exists()]

    assert missing == []


def test_contributing_documents_minimal_governance() -> None:
    contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "`main` is the only long-lived branch" in contributing
    assert "Conventional Commits" in contributing
    assert "chore: remove dependabot config" in contributing


def test_drift_reports_are_human_readable() -> None:
    drift_reports = [
        REPO_ROOT / "reports" / "drift" / "data_provider_1_aegis_care_network.md",
        REPO_ROOT / "reports" / "drift" / "data_provider_2_bluestone_health.md",
    ]

    for report in drift_reports:
        content = report.read_text(encoding="utf-8")
        assert "## How To Read This" in content
        assert "## Reader Glossary" in content
        assert "HITL" in content


def test_fixture_directory_is_documented() -> None:
    readme = REPO_ROOT / "tests" / "fixtures" / "README.md"
    content = readme.read_text(encoding="utf-8")

    assert "synthetic source files" in content
    assert "Aegis" in content
    assert "BlueStone" in content
    assert "Do not copy real records" in content


def test_canonical_plan_requires_drift_decision_runbook() -> None:
    plan = (REPO_ROOT / "docs" / "02_canonical_model_and_contracts_plan.md").read_text(
        encoding="utf-8"
    )
    skill = REPO_ROOT / ".agent" / "skills" / "drift-decision-resolver" / "SKILL.md"
    runbook = REPO_ROOT / "reports" / "hitl" / "canonical_drift_decision_runbook.md"

    assert skill.exists()
    assert runbook.exists()
    assert "drift-decision-resolver" in plan
    assert "canonical_drift_decision_runbook.md" in plan
    assert "must not treat them as resolved" in plan


def test_drift_decision_resolver_is_registered() -> None:
    skill = (
        REPO_ROOT / ".agent" / "skills" / "drift-decision-resolver" / "SKILL.md"
    ).read_text(encoding="utf-8")
    strategy = (REPO_ROOT / "docs" / "agentops_skill_strategy.md").read_text(
        encoding="utf-8"
    )
    technical_prd = (
        REPO_ROOT / "docs" / "technical_prd_agentops_operating_spec.md"
    ).read_text(encoding="utf-8")

    assert "canonical_drift_decision_runbook.md" in skill
    assert "pending_human_decision" in skill
    assert "deferred_with_human_approval" in skill
    assert "drift-decision-resolver" in strategy
    assert "drift-decision-resolver" in technical_prd


def test_canonical_drift_decision_runbook_has_required_gate_fields() -> None:
    runbook = (
        REPO_ROOT / "reports" / "hitl" / "canonical_drift_decision_runbook.md"
    ).read_text(encoding="utf-8")

    assert "Plan 02 may start only after" in runbook
    assert "Decision ID" in runbook
    assert "Blocks Plan 02" in runbook
    assert "Final Decision" in runbook
    assert "Files Updated" in runbook
    assert "Validation Evidence" in runbook


def test_agentic_rollout_invokes_drift_decision_gate() -> None:
    rollout = (REPO_ROOT / "docs" / "agentic_rollout.md").read_text(encoding="utf-8")

    assert "drift-decision-resolver" in rollout
    assert "canonical_drift_decision_runbook.md" in rollout
    assert "Do not generate Bronze/Silver model specs" in rollout


def test_business_question_profile_contract_is_registered() -> None:
    plan = (REPO_ROOT / "docs" / "01_2_business_question_profiling_plan.md").read_text(
        encoding="utf-8"
    )
    template = (
        REPO_ROOT / ".agent" / "spec_templates" / "business_question_profile.template.yaml"
    ).read_text(encoding="utf-8")
    skill = (
        REPO_ROOT / ".agent" / "skills" / "business-question-profiler" / "SKILL.md"
    ).read_text(encoding="utf-8")
    canonical_plan = (
        REPO_ROOT / "docs" / "02_canonical_model_and_contracts_plan.md"
    ).read_text(encoding="utf-8")

    assert "business_question_profiles" in template
    assert "field_decisions" in template
    assert "hitl_decision_request" in template
    assert "plan_02_allowance" in template
    assert "field-level decision" in plan
    assert "field decision" in skill
    assert "Plan 02 allowance" in canonical_plan


def test_local_runtime_stage_is_registered() -> None:
    rollout = (REPO_ROOT / "docs" / "agentic_rollout.md").read_text(encoding="utf-8")
    strategy = (REPO_ROOT / "docs" / "agentops_skill_strategy.md").read_text(
        encoding="utf-8"
    )
    prd = (
        REPO_ROOT / "docs" / "technical_prd_agentops_operating_spec.md"
    ).read_text(encoding="utf-8")

    assert (REPO_ROOT / "docs" / "04_local_runtime_and_contract_certification_plan.md").exists()
    assert (REPO_ROOT / "docs" / "05_databricks_validation_and_rollout_plan.md").exists()
    assert (
        REPO_ROOT / ".agent" / "skills" / "local-runtime-harness-planner" / "SKILL.md"
    ).exists()
    assert "local-runtime-harness-planner" in rollout
    assert "local-runtime-harness-planner" in strategy
    assert "Local Runtime Certification Plane" in prd
