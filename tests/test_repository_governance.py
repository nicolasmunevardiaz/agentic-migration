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
