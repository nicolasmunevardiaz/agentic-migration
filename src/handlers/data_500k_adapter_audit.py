from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import Any

from src.common.adapter_runtime import AdapterRunResult, compute_file_checksum, load_yaml
from src.handlers.aegis_adapter import run_aegis_adapter_for_file
from src.handlers.bluestone_adapter import run_bluestone_adapter_for_file
from src.handlers.northcare_adapter import run_northcare_adapter_for_file

DEFAULT_PLAN_ID = "03_adapter_implementation_and_ci_plan"
DEFAULT_ENTITIES = ("conditions", "encounters", "medications", "observations", "patients")


AdapterRunner = Callable[..., AdapterRunResult]


@dataclass(frozen=True)
class ProviderAuditTarget:
    provider_slug: str
    runner: AdapterRunner
    provider_spec_root: Path
    data_root: Path
    evidence_path: str


def build_provider_targets(repo_root: Path) -> dict[str, ProviderAuditTarget]:
    provider_spec_root = repo_root / "metadata/provider_specs"
    return {
        "data_provider_1_aegis_care_network": ProviderAuditTarget(
            provider_slug="data_provider_1_aegis_care_network",
            runner=run_aegis_adapter_for_file,
            provider_spec_root=provider_spec_root / "data_provider_1_aegis_care_network",
            data_root=repo_root / "data_500k/data_provider_1_aegis_care_network/year=2025",
            evidence_path="reports/qa/data_provider_1_aegis_care_network_adapter_implementation.md",
        ),
        "data_provider_2_bluestone_health": ProviderAuditTarget(
            provider_slug="data_provider_2_bluestone_health",
            runner=run_bluestone_adapter_for_file,
            provider_spec_root=provider_spec_root / "data_provider_2_bluestone_health",
            data_root=repo_root / "data_500k/data_provider_2_bluestone_health/year=2025",
            evidence_path="reports/qa/data_provider_2_bluestone_health_adapter_implementation.md",
        ),
        "data_provider_3_northcare_clinics": ProviderAuditTarget(
            provider_slug="data_provider_3_northcare_clinics",
            runner=run_northcare_adapter_for_file,
            provider_spec_root=provider_spec_root / "data_provider_3_northcare_clinics",
            data_root=repo_root / "data_500k/data_provider_3_northcare_clinics/year=2025",
            evidence_path="reports/qa/data_provider_3_northcare_clinics_adapter_implementation.md",
        ),
    }


def audit_data_500k(
    repo_root: Path,
    provider_slugs: list[str],
    output_dir: Path,
    plan_id: str = DEFAULT_PLAN_ID,
    entities: tuple[str, ...] = DEFAULT_ENTITIES,
) -> int:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "data_500k_adapter_load_audit.jsonl"
    summary_path = output_dir / "data_500k_adapter_load_audit.md"
    targets = build_provider_targets(repo_root)
    records: list[dict[str, Any]] = []

    for provider_slug in provider_slugs:
        target = targets[provider_slug]
        if not target.data_root.exists():
            records.append(
                build_audit_record(
                    timestamp=timestamp,
                    target=target,
                    entity="*",
                    source_file=None,
                    status="skipped",
                    decision="skip_dataset_absent",
                    plan_id=plan_id,
                    message=f"Dataset root is absent: {relative_path(target.data_root, repo_root)}",
                )
            )
            continue

        for entity in entities:
            source_files = source_files_for_entity(repo_root, target, entity)
            if not source_files:
                records.append(
                    build_audit_record(
                        timestamp=timestamp,
                        target=target,
                        entity=entity,
                        source_file=None,
                        status="failed",
                        decision="fail",
                        plan_id=plan_id,
                        error_type="MissingSourceFiles",
                        message="Dataset root exists but no files matched provider spec pattern.",
                    )
                )
                continue

            for source_file in source_files:
                records.append(
                    audit_source_file(
                        timestamp=timestamp,
                        repo_root=repo_root,
                        target=target,
                        entity=entity,
                        source_file=source_file,
                        plan_id=plan_id,
                    )
                )

    write_jsonl(jsonl_path, records)
    write_summary(summary_path, records, relative_path(jsonl_path, repo_root))
    return 1 if any(record["status"] == "failed" for record in records) else 0


def source_files_for_entity(
    repo_root: Path,
    target: ProviderAuditTarget,
    entity: str,
) -> list[Path]:
    provider_spec = load_yaml(target.provider_spec_root / f"{entity}.yaml")
    files: list[Path] = []
    for pattern in provider_spec["source"]["expected_file_patterns"]:
        files.extend(Path(path) for path in glob((repo_root / pattern).as_posix()))
    return sorted(set(files))


def audit_source_file(
    timestamp: str,
    repo_root: Path,
    target: ProviderAuditTarget,
    entity: str,
    source_file: Path,
    plan_id: str,
) -> dict[str, Any]:
    checksum = compute_file_checksum(source_file)
    try:
        result = target.runner(
            entity=entity,
            source_file=source_file,
            ingestion_run_id="data-500k-adapter-audit",
            provider_spec_root=target.provider_spec_root,
            model_root=repo_root / "metadata/model_specs",
            evidence_path=target.evidence_path,
        )
    except Exception as error:  # noqa: BLE001
        return build_audit_record(
            timestamp=timestamp,
            target=target,
            entity=entity,
            source_file=relative_path(source_file, repo_root),
            checksum=checksum,
            status="failed",
            decision="fail",
            plan_id=plan_id,
            error_type=type(error).__name__,
            message=str(error),
        )

    qa_decisions = sorted({item.decision for item in result.qa_evidence})
    return build_audit_record(
        timestamp=timestamp,
        target=target,
        entity=entity,
        source_file=relative_path(source_file, repo_root),
        checksum=checksum,
        status="passed",
        decision="accepted",
        plan_id=plan_id,
        bronze_record_count=len(result.bronze_records),
        silver_entities=sorted(result.silver_rows),
        silver_row_count=sum(len(rows) for rows in result.silver_rows.values()),
        quarantine_record_count=len(result.quarantine_records),
        qa_evidence_count=len(result.qa_evidence),
        qa_decisions=qa_decisions,
    )


def build_audit_record(
    timestamp: str,
    target: ProviderAuditTarget,
    entity: str,
    source_file: Path | None,
    status: str,
    decision: str,
    plan_id: str,
    checksum: str | None = None,
    error_type: str | None = None,
    message: str = "",
    bronze_record_count: int = 0,
    silver_entities: list[str] | None = None,
    silver_row_count: int = 0,
    quarantine_record_count: int = 0,
    qa_evidence_count: int = 0,
    qa_decisions: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "timestamp": timestamp,
        "plan_id": plan_id,
        "provider": target.provider_slug,
        "entity": entity,
        "source_file": source_file.as_posix() if source_file else "",
        "source_checksum": checksum or "",
        "status": status,
        "decision": decision,
        "error_type": error_type or "",
        "message": message,
        "bronze_record_count": bronze_record_count,
        "silver_entities": silver_entities or [],
        "silver_row_count": silver_row_count,
        "quarantine_record_count": quarantine_record_count,
        "qa_evidence_count": qa_evidence_count,
        "qa_decisions": qa_decisions or [],
        "evidence_path": target.evidence_path,
    }


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    content = "\n".join(json.dumps(record, sort_keys=True) for record in records)
    path.write_text(f"{content}\n", encoding="utf-8")


def relative_path(path: Path, repo_root: Path) -> Path:
    try:
        return path.relative_to(repo_root)
    except ValueError:
        return path


def write_summary(
    summary_path: Path,
    records: list[dict[str, Any]],
    jsonl_path: Path,
) -> None:
    plan_ids = sorted({record["plan_id"] for record in records})
    providers = sorted({record["provider"] for record in records})
    provider_counts = {
        provider: sum(1 for record in records if record["provider"] == provider)
        for provider in providers
    }
    entity_counts = {
        f"{record['provider']}::{record['entity']}": sum(
            1
            for item in records
            if item["provider"] == record["provider"] and item["entity"] == record["entity"]
        )
        for record in records
        if record["entity"] != "*"
    }
    statuses = {
        status: sum(1 for record in records if record["status"] == status)
        for status in sorted({record["status"] for record in records})
    }
    failures = [record for record in records if record["status"] == "failed"]
    skips = [record for record in records if record["status"] == "skipped"]

    lines = [
        "# data_500k Adapter Load Audit",
        "",
        "## Scope",
        "",
        f"- Plan ids: `{', '.join(plan_ids)}`",
        f"- Registered providers audited: `{', '.join(providers)}`",
        f"- JSONL detail: `{jsonl_path.as_posix()}`",
        f"- Total records: `{len(records)}`",
        f"- Status counts: `{statuses}`",
        f"- Records by provider: `{provider_counts}`",
        f"- Records by provider/entity: `{entity_counts}`",
        "",
        "## Rules",
        "",
        "- Default command audits every registered provider target, every default entity, "
        "and every "
        "source file matching the provider spec patterns.",
        "- `--provider` is for focused diagnosis only; complete integration evidence should run "
        "without provider filtering.",
        "- `skipped` is allowed only when the entire local provider dataset is absent.",
        "- If a provider dataset exists, missing files, parser failures, and load failures are "
        "`failed` records with file-level evidence.",
        "",
        "## Failures",
        "",
    ]
    if failures:
        for failure in failures:
            lines.append(
                "- "
                f"provider={failure['provider']} entity={failure['entity']} "
                f"source_file={failure['source_file']} checksum={failure['source_checksum']} "
                f"error_type={failure['error_type']} decision={failure['decision']} "
                f"message={failure['message']}"
            )
    else:
        lines.append("- None.")

    lines.extend(["", "## Skips", ""])
    if skips:
        for skip in skips:
            lines.append(
                "- "
                f"provider={skip['provider']} entity={skip['entity']} "
                f"decision={skip['decision']} message={skip['message']}"
            )
    else:
        lines.append("- None.")

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Plan 03 adapters against ignored local data_500k source files."
    )
    parser.add_argument(
        "--provider",
        action="append",
        choices=sorted(build_provider_targets(Path.cwd())),
        help=(
            "Provider slug to audit for focused diagnosis. Repeat for multiple providers. "
            "Omit this option for complete evidence over all registered providers."
        ),
    )
    parser.add_argument(
        "--plan-id",
        default=DEFAULT_PLAN_ID,
        help="Plan id written into each audit record.",
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts/qa",
        help="Directory for generated audit JSONL and Markdown summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    provider_slugs = args.provider or sorted(build_provider_targets(repo_root))
    return audit_data_500k(
        repo_root=repo_root,
        provider_slugs=provider_slugs,
        output_dir=repo_root / args.output_dir,
        plan_id=args.plan_id,
    )


if __name__ == "__main__":
    raise SystemExit(main())
