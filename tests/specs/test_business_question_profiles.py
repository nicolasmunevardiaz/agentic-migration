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
    "approved_resolution",
    "hitl_decisions_required",
    "hitl_decisions_applied",
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
    "resolved_decision",
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
ALLOWED_DECISION_STATUSES = {"applied"}


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
    assert "gold_candidate_input" in profile["scope"]["allowed_layers"]
    assert profile["scope"]["forbidden_without_hitl"] == []
    assert len(profile["business_question_profiles"]) == 16
    assert len(profile["field_decisions"]) == expected_provider_field_count()


def test_question_profiles_have_evidence_and_applied_normalization() -> None:
    profile = load_profile()
    question_ids = {entry["question_id"] for entry in profile["business_question_profiles"]}

    assert question_ids == {f"BQ-{number:03d}" for number in range(1, 17)}

    for entry in profile["business_question_profiles"]:
        assert set(entry) >= REQUIRED_PROFILE_KEYS
        assert entry["risk_level"] in {"low", "medium", "high"}
        assert set(entry["minimum_canonical_concepts"]) <= ALLOWED_CONCEPTS
        assert entry["downstream_gold_candidate"]["status"] == "approved_for_downstream_design"
        assert entry["allowed_next_action"] == "plan_02_allowed"
        assert entry["candidate_solution_options"] == []
        assert entry["hitl_decisions_required"] == []
        assert entry["approved_resolution"]["status"] == "applied"
        assert entry["approved_resolution"]["approved_by"]
        assert entry["approved_resolution"]["approval_date"]
        assert entry["approved_resolution"]["decision"]

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


def test_field_decisions_are_applied_and_allow_plan_02() -> None:
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
        assert decision["canonical_candidate"]["gold_usage"] == "approved_business_input"
        assert (
            decision["canonical_candidate"]["silver_handling"]
            == "normalize_to_canonical_concept"
        )
        assert decision["canonical_candidate"]["normalization_contract"]
        assert decision["drift_or_blocker"]["category"]
        assert decision["drift_or_blocker"]["blocks_plan_02"] is False
        assert decision["selected_option"]["plan_02_allowance"] == "allowed"
        assert "options" not in decision
        assert decision["resolved_decision"]["status"] == "applied"
        assert decision["resolved_decision"]["decision"]
        assert decision["resolved_decision"]["plan_02_allowance"] == "allowed"

        hitl = decision["hitl_decision_request"]
        assert hitl["required"] is False
        assert hitl["status"] == "approved"
        assert hitl["approved_by"]
        assert hitl["approved_decision"]
        assert hitl["human_response"]["response"] == "approved_normalization"
        assert hitl["minimum_evidence_reviewed"]


def test_applied_field_decisions_link_to_runbook() -> None:
    profile = load_profile()

    for decision in profile["field_decisions"]:
        linked_ids = decision["drift_or_blocker"]["linked_runbook_decision_ids"]
        assert linked_ids, decision["decision_id"]
        assert all(linked_id.startswith("DRIFT-") for linked_id in linked_ids)
        assert decision["status"] == "applied"
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


def test_profile_contains_no_pending_options_or_deferrals() -> None:
    profile_text = PROFILE_PATH.read_text(encoding="utf-8")

    forbidden_fragments = [
        "pending_human_decision",
        "deferred",
        "defer",
        "option_id: A",
        "option_id: B",
        "option_id: C",
        "approve_recommended_option",
        "approve_alternative_option",
        "request_more_evidence",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in profile_text
