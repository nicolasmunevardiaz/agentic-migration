from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    REPO_ROOT / "metadata" / "model_specs" / "impact" / "business_question_profiles.yaml"
)
PROVIDER_SPEC_ROOT = REPO_ROOT / "metadata" / "provider_specs"

REQUIRED_TOP_LEVEL_KEYS = {
    "spec_version",
    "artifact",
    "plan_id",
    "source_business_request",
    "status",
    "scope",
    "pii_phi_policy",
    "business_question_profiles",
    "field_decisions",
}
REQUIRED_PROFILE_KEYS = {
    "question_id",
    "business_question",
    "decision_supported",
    "intended_audience",
    "business_domain_group",
    "risk_level",
    "grain",
    "required_provider_groups",
    "provider_language",
    "required_sources",
    "minimum_canonical_concepts",
    "candidate_solution_options",
    "hitl_decisions_required",
    "downstream_gold_candidate",
    "data_quality_checks",
    "required_tests",
    "allowed_next_action",
}
REQUIRED_FIELD_DECISION_KEYS = {
    "decision_id",
    "status",
    "provider",
    "source",
    "business_dependency",
    "canonical_candidate",
    "sensitivity",
    "drift_or_blocker",
    "evidence",
    "options",
    "hitl_decision_request",
    "selected_option",
    "validation",
}
ALLOWED_CONCEPTS = {
    "member_reference",
    "coverage_period",
    "encounter_event",
    "condition_record",
    "medication_record",
    "observation_record_raw",
    "cost_record",
    "source_lineage",
}
ALLOWED_RESPONSES = {
    "approve_recommended_option",
    "approve_alternative_option",
    "defer_with_human_approval",
    "reject_all_options",
    "request_more_evidence",
}
ALLOWED_ALLOWANCES = {"allowed", "allowed_bronze_only", "blocked"}
ALLOWED_DECISION_STATUSES = {
    "applied",
    "rejected",
    "deferred_with_human_approval",
    "pending_human_decision",
}


def load_profile() -> dict:
    return yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))


def all_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for entry in value for item in all_strings(entry)]
    if isinstance(value, dict):
        return [item for entry in value.values() for item in all_strings(entry)]
    return []


def expected_provider_field_count() -> int:
    count = 0
    for path in PROVIDER_SPEC_ROOT.glob("*/*.yaml"):
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        count += len(spec["mapping"]["fields"])
    return count


def assert_existing_relative_path(path_text: str) -> None:
    assert not Path(path_text).is_absolute()
    assert (REPO_ROOT / path_text).exists(), path_text


def test_business_question_profile_yaml_shape_and_scope() -> None:
    profile = load_profile()

    assert set(profile) >= REQUIRED_TOP_LEVEL_KEYS
    assert profile["artifact"] == "business_question_profiles"
    assert profile["plan_id"] == "01_2_business_question_profiling_plan"
    assert profile["source_business_request"] == "business-request.md"
    assert profile["scope"]["provider_scope"] == "all"
    assert "gold_deferred_candidate" in profile["scope"]["allowed_layers"]
    assert "enterprise_identity_resolution" in profile["scope"]["forbidden_without_hitl"]
    assert len(profile["business_question_profiles"]) == 16
    assert len(profile["field_decisions"]) == expected_provider_field_count()


def test_question_profiles_have_evidence_and_deferred_gold_candidates() -> None:
    profile = load_profile()
    question_ids = {entry["question_id"] for entry in profile["business_question_profiles"]}

    assert question_ids == {f"BQ-{number:03d}" for number in range(1, 17)}

    for entry in profile["business_question_profiles"]:
        assert set(entry) >= REQUIRED_PROFILE_KEYS
        assert entry["risk_level"] in {"low", "medium", "high", "hitl_blocked"}
        assert set(entry["minimum_canonical_concepts"]) <= ALLOWED_CONCEPTS
        assert entry["downstream_gold_candidate"]["status"] == "deferred"
        assert entry["allowed_next_action"] == "profile_only"
        assert entry["candidate_solution_options"]

        for option in entry["candidate_solution_options"]:
            assert option["risk"] in {"low", "medium", "high"}
            assert option["impact"]
            assert "required_approval" in option
            assert "recommendation" in option

        for source in entry["required_sources"]:
            assert source["provider_slug"].startswith("data_provider_")
            assert source["source_entity"] in {
                "patients",
                "encounters",
                "conditions",
                "medications",
                "observations",
            }
            assert source["source_fields"]

        for language in entry["provider_language"]:
            assert language["evidence_paths"]
            for evidence_path in language["evidence_paths"]:
                assert_existing_relative_path(evidence_path)


def test_field_decisions_have_hitl_options_and_plan_02_allowance() -> None:
    profile = load_profile()
    decision_ids = set()

    for decision in profile["field_decisions"]:
        assert set(decision) >= REQUIRED_FIELD_DECISION_KEYS
        assert decision["decision_id"] not in decision_ids
        decision_ids.add(decision["decision_id"])
        assert decision["status"] in ALLOWED_DECISION_STATUSES
        assert decision["provider"]["provider_slug"].startswith("data_provider_")
        assert decision["source"]["provider_spec_path"]
        assert_existing_relative_path(decision["source"]["provider_spec_path"])
        assert decision["business_dependency"]["question_ids"]
        assert decision["canonical_candidate"]["minimum_concept"] in ALLOWED_CONCEPTS
        assert decision["canonical_candidate"]["gold_usage"] == "deferred"
        assert decision["drift_or_blocker"]["category"]
        assert decision["selected_option"]["plan_02_allowance"] in ALLOWED_ALLOWANCES

        options = decision["options"]
        assert len(options) >= 2
        for option in options:
            assert option["risk"] in {"low", "medium", "high"}
            assert option["impact"]
            assert option["required_approval"]
            assert option["plan_02_allowance_if_selected"] in ALLOWED_ALLOWANCES
            assert "rollback_notes" in option
            assert "tests_required" in option

        hitl = decision["hitl_decision_request"]
        assert hitl["recommended_option_id"] in {option["option_id"] for option in options}
        assert set(hitl["allowed_responses"]) == ALLOWED_RESPONSES
        assert set(hitl["plan_02_consequence_by_response"]) == ALLOWED_RESPONSES
        assert hitl["minimum_evidence_reviewed"]


def test_pending_or_blocked_field_decisions_link_to_runbook() -> None:
    profile = load_profile()

    for decision in profile["field_decisions"]:
        linked_ids = decision["drift_or_blocker"]["linked_runbook_decision_ids"]
        if decision["status"] == "pending_human_decision" or decision["selected_option"][
            "plan_02_allowance"
        ] != "allowed":
            assert linked_ids, decision["decision_id"]
            assert all(linked_id.startswith("DRIFT-") for linked_id in linked_ids)
            assert decision["hitl_decision_request"]["required"] is True
        if decision["canonical_candidate"]["canonical_name_hint"] == "ROW_ID":
            assert "DRIFT-001" in linked_ids
            assert decision["selected_option"]["plan_02_allowance"] == "allowed"


def test_profile_evidence_paths_are_existing_repo_paths() -> None:
    profile = load_profile()

    for decision in profile["field_decisions"]:
        evidence = decision["evidence"]
        for paths in evidence.values():
            assert paths
            for evidence_path in paths:
                assert_existing_relative_path(evidence_path)


def test_profile_has_no_absolute_paths_or_unapproved_post_silver_outputs() -> None:
    profile = load_profile()
    strings = all_strings(profile)

    assert not any(Path(text).is_absolute() for text in strings if "/" in text)
    assert not any("data_500k/" in text for text in strings)
    assert not any("metadata/model_specs/bronze/" in text for text in strings)
    assert not any("metadata/model_specs/silver/" in text for text in strings)
    assert not any("metadata/model_specs/mappings/" in text for text in strings)
    assert not any("metadata/deployment_specs/databricks/" in text for text in strings)
    assert not any("dashboard" in text.lower() for text in strings)
    assert profile["pii_phi_policy"]["reports_logs_fixtures"] == "no_raw_sensitive_values"
