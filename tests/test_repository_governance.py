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
        "reports/qa",
        "reports/privacy",
        "reports/hitl",
        "logs",
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
