from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = (
    REPO_ROOT / "metadata" / "model_specs" / "mappings" / "provider_to_silver_matrix.yaml"
)
PROFILE_PATH = (
    REPO_ROOT / "metadata" / "model_specs" / "impact" / "business_question_profiles.yaml"
)
SILVER_ROOT = REPO_ROOT / "metadata" / "model_specs" / "silver"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def source_key(field: dict) -> tuple[str, int | None]:
    return field["source_header"], field.get("source_index")


def provider_field_keys(path_text: str) -> set[tuple[str, int | None]]:
    spec = load_yaml(REPO_ROOT / path_text)
    return {source_key(field) for field in spec["mapping"]["fields"]}


def field_decisions_by_id() -> dict[str, dict]:
    profile = load_yaml(PROFILE_PATH)
    return {
        decision["decision_id"]: decision
        for decision in profile["field_decisions"]
    }


def matrix() -> dict:
    return load_yaml(MATRIX_PATH)


def runbook_text() -> str:
    return (
        REPO_ROOT / "reports" / "hitl" / "canonical_drift_decision_runbook.md"
    ).read_text(encoding="utf-8")


def test_provider_to_silver_matrix_shape_and_coverage() -> None:
    spec = matrix()

    assert spec["artifact"] == "provider_to_silver_matrix"
    assert spec["plan_id"] == "02_canonical_model_and_contracts_plan"
    assert spec["status"] == "approved"
    assert spec["mapping_policy"]["provider_specs_are_source_contracts"] is True
    assert spec["mapping_policy"]["source_scoped_references_only"] is True
    assert spec["mapping_policy"]["no_enterprise_identity_resolution"] is True
    assert spec["coverage_summary"]["provider_count"] == 5
    assert spec["coverage_summary"]["provider_spec_count"] == 25
    assert spec["coverage_summary"]["silver_entity_count"] == 7
    assert len(spec["mappings"]) == spec["coverage_summary"]["mapping_count"]
    assert len(spec["mappings"]) >= 300

    entities = {row["silver_entity"] for row in spec["mappings"]}
    assert entities == set(spec["silver_entities"])


def test_matrix_rows_reference_applied_field_decisions_and_runbook() -> None:
    decisions = field_decisions_by_id()
    runbook = runbook_text()

    for row in matrix()["mappings"]:
        assert row["provider_slug"].startswith("data_provider_")
        assert row["source_entity"]
        assert row["provider_spec_path"]
        assert row["silver_entity"]
        assert row["silver_column"]
        assert row["target_type"]
        assert row["mapping_confidence"] == "approved"
        assert row["plan_02_allowance"] == "allowed"
        assert row["approval_status"] == "applied"
        assert row["linked_runbook_decision_ids"]

        for decision_id in row["linked_runbook_decision_ids"]:
            assert f"| {decision_id} |" in runbook
            decision_line = next(
                line for line in runbook.splitlines() if line.startswith(f"| {decision_id} |")
            )
            assert "| applied | no |" in decision_line

        if row["source_header"] == "__metadata__":
            assert row["field_decision_id"] == "DRIFT-001-lineage-metadata"
            assert row["linked_runbook_decision_ids"] == ["DRIFT-001"]
            continue

        assert row["field_decision_id"] in decisions
        decision = decisions[row["field_decision_id"]]
        assert decision["status"] == "applied"
        assert decision["selected_option"]["plan_02_allowance"] == "allowed"
        assert decision["selected_option"]["selected_decision"] == "normalize_to_canonical_concept"
        assert (
            row["source_header"],
            row.get("source_index"),
        ) in provider_field_keys(row["provider_spec_path"])


def test_matrix_has_no_duplicate_conflicting_source_targets() -> None:
    seen = set()

    for row in matrix()["mappings"]:
        key = (
            row["provider_slug"],
            row["source_entity"],
            row["source_field_key"],
            row["silver_entity"],
            row["silver_column"],
        )
        assert key not in seen, key
        seen.add(key)


def test_every_silver_column_mapping_is_present_in_matrix() -> None:
    matrix_keys = {
        (
            row["provider_slug"],
            row["source_entity"],
            row["source_header"],
            row.get("source_index"),
            row["silver_entity"],
            row["silver_column"],
        )
        for row in matrix()["mappings"]
    }

    for path in SILVER_ROOT.glob("*.yaml"):
        silver = load_yaml(path)
        for column in silver["columns"]:
            for mapping in column["source_mappings"]:
                key = (
                    mapping["provider_slug"],
                    mapping["source_entity"],
                    mapping["source_header"],
                    mapping.get("source_index"),
                    silver["entity"],
                    column["name"],
                )
                assert key in matrix_keys, key
