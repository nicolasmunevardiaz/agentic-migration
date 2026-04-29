from __future__ import annotations

from pathlib import Path

from src.adapters.aegis_care_network import parse_aegis_entity_file
from src.common.adapter_runtime import (
    AdapterRunResult,
    build_bronze_record,
    build_silver_rows,
    build_source_record,
    compute_file_checksum,
    load_provider_canonical_mappings,
    load_yaml,
)

PROVIDER_SLUG = "data_provider_1_aegis_care_network"
DEFAULT_PROVIDER_SPEC_ROOT = Path("metadata/provider_specs") / PROVIDER_SLUG
DEFAULT_MODEL_ROOT = Path("metadata/model_specs")
DEFAULT_EVIDENCE_PATH = "reports/qa/data_provider_1_aegis_care_network_adapter_implementation.md"


def run_aegis_adapter_for_file(
    entity: str,
    source_file: Path,
    ingestion_run_id: str,
    provider_spec_root: Path = DEFAULT_PROVIDER_SPEC_ROOT,
    model_root: Path = DEFAULT_MODEL_ROOT,
    evidence_path: str = DEFAULT_EVIDENCE_PATH,
) -> AdapterRunResult:
    provider_spec = load_yaml(provider_spec_root / f"{entity}.yaml")
    parsed_records = parse_aegis_entity_file(entity, source_file, provider_spec_root)
    canonical_mappings = load_provider_canonical_mappings(model_root, PROVIDER_SLUG)
    source_checksum = compute_file_checksum(source_file)
    result = AdapterRunResult()

    for parsed_record in parsed_records:
        source_record = build_source_record(
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
            if any(
                item.silver_entity == silver_row.silver_entity
                and item.source_row_key_value == source_record.source_row_key_value
                for item in quarantine_records
            ):
                continue
            result.silver_rows.setdefault(silver_row.silver_entity, []).append(
                silver_row.values
            )

    return result
