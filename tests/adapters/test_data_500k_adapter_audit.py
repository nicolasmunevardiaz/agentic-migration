import json
from pathlib import Path

from src.common.adapter_runtime import AdapterRunResult
from src.handlers.data_500k_adapter_audit import (
    ProviderAuditTarget,
    build_audit_record,
    build_provider_targets,
    write_jsonl,
    write_summary,
)


def noop_runner(**_: object) -> AdapterRunResult:
    return AdapterRunResult()


def test_data_500k_audit_defaults_to_registered_adapter_targets() -> None:
    targets = build_provider_targets(Path.cwd())

    assert set(targets) == {
        "data_provider_1_aegis_care_network",
        "data_provider_2_bluestone_health",
        "data_provider_3_northcare_clinics",
        "data_provider_4_valleybridge_medical",
        "data_provider_5_pacific_shield_insurance",
    }


def test_data_500k_audit_jsonl_preserves_plan_and_file_level_fields(
    tmp_path: Path,
) -> None:
    target = ProviderAuditTarget(
        provider_slug="data_provider_test",
        runner=noop_runner,
        provider_spec_root=Path("metadata/provider_specs/data_provider_test"),
        data_root=Path("data_500k/data_provider_test/year=2025"),
        evidence_path="reports/qa/data_provider_test.md",
    )
    record = build_audit_record(
        timestamp="2026-04-29T10:00:00-05:00",
        target=target,
        entity="patients",
        source_file=Path("data_500k/data_provider_test/year=2025/patients/patients_001.json"),
        status="failed",
        decision="fail",
        plan_id="04_local_runtime_and_contract_certification_plan",
        checksum="abc123",
        error_type="ValueError",
        message="synthetic parser failure",
    )
    jsonl_path = tmp_path / "audit.jsonl"

    write_jsonl(jsonl_path, [record])

    loaded = json.loads(jsonl_path.read_text(encoding="utf-8"))
    assert loaded["plan_id"] == "04_local_runtime_and_contract_certification_plan"
    assert loaded["provider"] == "data_provider_test"
    assert loaded["entity"] == "patients"
    assert loaded["source_checksum"] == "abc123"
    assert loaded["status"] == "failed"
    assert loaded["decision"] == "fail"
    assert loaded["error_type"] == "ValueError"


def test_data_500k_audit_summary_documents_complete_evidence_rules(
    tmp_path: Path,
) -> None:
    target = ProviderAuditTarget(
        provider_slug="data_provider_test",
        runner=noop_runner,
        provider_spec_root=Path("metadata/provider_specs/data_provider_test"),
        data_root=Path("data_500k/data_provider_test/year=2025"),
        evidence_path="reports/qa/data_provider_test.md",
    )
    record = build_audit_record(
        timestamp="2026-04-29T10:00:00-05:00",
        target=target,
        entity="patients",
        source_file=Path("data_500k/data_provider_test/year=2025/patients/patients_001.json"),
        status="passed",
        decision="accepted",
        plan_id="03_adapter_implementation_and_ci_plan",
    )
    summary_path = tmp_path / "summary.md"

    write_summary(summary_path, [record], Path("artifacts/qa/data_500k_adapter_load_audit.jsonl"))

    summary = summary_path.read_text(encoding="utf-8")
    assert "Default command audits every registered provider target" in summary
    assert "complete integration evidence should run without provider filtering" in summary
    assert "`skipped` is allowed only when the entire local provider dataset is absent" in summary
