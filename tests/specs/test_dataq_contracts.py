from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPO_ROOT / "metadata" / "model_specs" / "data_quality" / "contracts"

EXPECTED_CONTRACTS = {
    "accuracy_contract.yaml",
    "completeness_contract.yaml",
    "consistency_contract.yaml",
    "temporal_contract.yaml",
    "uniqueness_contract.yaml",
    "validity_contract.yaml",
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_dataq_contract_files_are_declared() -> None:
    assert {path.name for path in CONTRACT_ROOT.glob("*.yaml")} == EXPECTED_CONTRACTS


def test_dataq_contracts_have_required_governance_fields() -> None:
    for path in CONTRACT_ROOT.glob("*.yaml"):
        contract = _load_yaml(path)
        assert contract["contract_id"].startswith("DQ_CONTRACT_")
        assert contract["model_snapshot"] == "V0_5"
        assert contract["status"] in {"draft", "approved"}
        assert contract["purpose"]
        assert contract["acceptance"]["audit_grain"] == "provider_entity_field"
        assert contract["acceptance"]["remediation_requires"]


def test_accuracy_contract_blocks_unapproved_semantic_remediation() -> None:
    contract = _load_yaml(CONTRACT_ROOT / "accuracy_contract.yaml")
    approved_rules = contract["rules"]["approved_accuracy_rules"]
    clinical = contract["rules"]["clinical_semantic_review"]
    financial = contract["rules"]["financial_semantic_review"]

    assert (
        approved_rules["condition_source_code_precedence"]["rule_id"]
        == "condition_source_code_is_primary_domain_hint_is_metadata"
    )
    assert (
        approved_rules["financial_preservation"]["rule_id"]
        == "financial_amount_date_preserve_nulls_and_provider_semantics"
    )
    assert "recode_clinical_meaning" in clinical["dbt_forbidden_without_hitl"]
    assert "impute_cost_amount" in financial["dbt_forbidden_without_hitl"]
    assert (
        contract["acceptance"]["remediation_requires"]
        == "approved_contract_rule_or_HITL_approved_semantic_rule"
    )


def test_temporal_contract_requires_explicit_temporal_authority_for_utc() -> None:
    contract = _load_yaml(CONTRACT_ROOT / "temporal_contract.yaml")
    timezone_policy = contract["timezone_policy"]

    assert timezone_policy["timezone_format"] == "IANA"
    assert timezone_policy["utc_derivation_requires_explicit_temporal_authority"] is True
    assert timezone_policy["utc_derivation_precedence"] == [
        "source_row_explicit_offset",
        "approved_provider_iana_timezone",
    ]
    assert timezone_policy["source_row_explicit_offset_policy"]["status"] == "approved"
    assert timezone_policy["provider_timezone_fallback_policy"]["status"] == "approved"
    assert timezone_policy["majority_inference_policy"]["status"] == "prohibited"
    assert contract["standard_columns"]["provider_timezone"] == "provider_timezone"
