from __future__ import annotations

from pathlib import Path
from typing import Any

from src.adapters.valleybridge_medical import parse_valleybridge_file
from src.common.adapter_runtime import (
    AdapterRunResult,
    SourceRecord,
    build_bronze_record,
    build_silver_rows,
    compute_file_checksum,
    load_provider_canonical_mappings,
    load_yaml,
)

PROVIDER_SLUG = "data_provider_4_valleybridge_medical"
DEFAULT_PROVIDER_SPEC_ROOT = Path("metadata/provider_specs") / PROVIDER_SLUG
DEFAULT_MODEL_ROOT = Path("metadata/model_specs")
DEFAULT_EVIDENCE_PATH = "reports/qa/data_provider_4_valleybridge_medical_adapter_implementation.md"


def run_valleybridge_adapter_for_file(
    entity: str,
    source_file: Path,
    ingestion_run_id: str,
    provider_spec_root: Path = DEFAULT_PROVIDER_SPEC_ROOT,
    model_root: Path = DEFAULT_MODEL_ROOT,
    evidence_path: str = DEFAULT_EVIDENCE_PATH,
) -> AdapterRunResult:
    provider_spec = load_yaml(provider_spec_root / f"{entity}.yaml")
    parsed_records = parse_valleybridge_file(source_file, provider_spec_root / f"{entity}.yaml")
    canonical_mappings = load_provider_canonical_mappings(model_root, PROVIDER_SLUG)
    source_checksum = compute_file_checksum(source_file)
    result = AdapterRunResult()

    for parsed_record in parsed_records:
        source_record = build_valleybridge_source_record(
            parsed_record=parsed_record,
            provider_spec=provider_spec,
            source_file=source_file,
            source_checksum=source_checksum,
        )
        bronze_record = build_bronze_record(
            source_record=source_record,
            provider_spec=provider_spec,
            ingestion_run_id=ingestion_run_id,
        )
        result.bronze_records.append(bronze_record)

        silver_rows, quarantine_records, qa_evidence = build_silver_rows(
            source_record=source_record,
            mappings_by_entity=canonical_mappings,
            source_lineage_ref=bronze_record.source_lineage_ref,
            ingestion_run_id=ingestion_run_id,
            evidence_path=evidence_path,
        )
        result.quarantine_records.extend(quarantine_records)
        result.qa_evidence.extend(qa_evidence)
        for silver_row in silver_rows:
            result.silver_rows.setdefault(silver_row.silver_entity, []).append(
                silver_row.values
            )

    return result


def build_valleybridge_source_record(
    parsed_record: dict[str, dict[str, Any]],
    provider_spec: dict[str, Any],
    source_file: Path,
    source_checksum: str,
) -> SourceRecord:
    source_row_key_header = provider_spec["parser_profile"]["source_row_key"]
    values_by_header = parsed_record["values_by_header"]
    return SourceRecord(
        provider_slug=provider_spec["provider"]["provider_slug"],
        provider_name=provider_spec["provider"]["provider_name"],
        source_entity=provider_spec["source"]["entity"],
        source_file=source_file.as_posix(),
        source_checksum=source_checksum,
        source_row_key_header=source_row_key_header,
        source_row_key_value=str(values_by_header[source_row_key_header]),
        parser_family=provider_spec["parser_profile"]["parser_family"],
        upload_partition=provider_spec["provider"]["upload_partition"],
        schema_version=str(provider_spec["spec_version"]),
        values_by_header=values_by_header,
    )
