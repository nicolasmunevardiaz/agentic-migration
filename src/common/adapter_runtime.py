from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import yaml

ADAPTER_VERSION = "0.1.0"
DEFAULT_SCHEMA_VERSION = "0.1"
SENSITIVE_RAW_VALUE_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(ssn|tax)[-_][a-z0-9-]+\b", re.IGNORECASE),
    re.compile(r"\bsynthetic-ssn\b", re.IGNORECASE),
)


class AdapterRuntimeError(ValueError):
    """Raised when runtime-neutral adapter contracts cannot be satisfied."""


@dataclass(frozen=True)
class CanonicalColumnMapping:
    silver_entity: str
    silver_column: str
    source_entity: str
    source_header: str
    source_index: int | None
    target_type: str
    required: bool
    nullable: bool
    provider_spec_path: str
    field_decision_id: str


@dataclass(frozen=True)
class SourceRecord:
    provider_slug: str
    provider_name: str
    source_entity: str
    source_file: str
    source_checksum: str
    source_row_key_header: str
    source_row_key_value: str
    parser_family: str
    upload_partition: str
    schema_version: str
    values_by_header: dict[str, Any]
    values_by_position: dict[int, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BronzeRecord:
    provider_slug: str
    provider_name: str
    source_entity: str
    source_file: str
    source_checksum: str
    source_row_key_header: str
    source_row_key_value: str
    source_file_pattern: str
    upload_partition: str
    parser_family: str
    schema_version: str
    adapter_version: str
    ingestion_run_id: str
    source_lineage_ref: str
    quarantine_status: str
    values_by_header: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_slug": self.provider_slug,
            "provider_name": self.provider_name,
            "source_entity": self.source_entity,
            "source_file": self.source_file,
            "source_checksum": self.source_checksum,
            "source_row_key_header": self.source_row_key_header,
            "source_row_key_value": self.source_row_key_value,
            "source_file_pattern": self.source_file_pattern,
            "upload_partition": self.upload_partition,
            "parser_family": self.parser_family,
            "schema_version": self.schema_version,
            "adapter_version": self.adapter_version,
            "ingestion_run_id": self.ingestion_run_id,
            "source_lineage_ref": self.source_lineage_ref,
            "quarantine_status": self.quarantine_status,
            "values_by_header": self.values_by_header,
        }


@dataclass(frozen=True)
class SilverRow:
    silver_entity: str
    values: dict[str, Any]


@dataclass(frozen=True)
class QuarantineRecord:
    provider_slug: str
    source_entity: str
    silver_entity: str
    source_file: str
    source_checksum: str
    source_row_key_value: str
    column_name: str
    decision: str
    reason: str
    evidence_path: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class QAEvidenceRecord:
    test_name: str
    family: str
    stage: str
    provider: str
    entity: str
    source_file: str
    checksum: str
    expected_value: str
    observed_value: str
    failure_count: int
    decision: str
    evidence_path: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class AdapterRunResult:
    bronze_records: list[BronzeRecord] = field(default_factory=list)
    silver_rows: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    quarantine_records: list[QuarantineRecord] = field(default_factory=list)
    qa_evidence: list[QAEvidenceRecord] = field(default_factory=list)


def load_yaml(path: Path) -> dict[str, Any]:
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        raise AdapterRuntimeError(f"YAML document must be a mapping: {path}")
    return content


def compute_file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def build_lineage_ref(
    provider_slug: str,
    source_entity: str,
    source_file: str,
    source_checksum: str,
    source_row_key_value: str,
) -> str:
    raw_value = "|".join(
        [provider_slug, source_entity, source_file, source_checksum, source_row_key_value]
    )
    return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()


def load_provider_canonical_mappings(
    model_root: Path,
    provider_slug: str,
) -> dict[str, list[CanonicalColumnMapping]]:
    mappings: dict[str, list[CanonicalColumnMapping]] = {}
    silver_root = model_root / "silver"
    for silver_path in sorted(silver_root.glob("*.yaml")):
        silver_spec = load_yaml(silver_path)
        silver_entity = silver_spec["entity"]
        for column in silver_spec["columns"]:
            for source_mapping in column["source_mappings"]:
                if source_mapping["provider_slug"] != provider_slug:
                    continue
                source_entity = source_mapping["source_entity"]
                mappings.setdefault(source_entity, []).append(
                    CanonicalColumnMapping(
                        silver_entity=silver_entity,
                        silver_column=column["name"],
                        source_entity=source_entity,
                        source_header=source_mapping["source_header"],
                        source_index=source_mapping.get("source_index"),
                        target_type=column["type"],
                        required=column["required"],
                        nullable=column["nullable"],
                        provider_spec_path=source_mapping["provider_spec_path"],
                        field_decision_id=source_mapping["field_decision_id"],
                    )
                )
    return mappings


def build_source_record(
    parsed_record: Any,
    provider_spec: dict[str, Any],
    source_file: Path,
    source_checksum: str,
) -> SourceRecord:
    source_row_key_header = provider_spec["parser_profile"]["source_row_key"]
    source_row_key_value = str(parsed_record.values_by_header[source_row_key_header])
    return SourceRecord(
        provider_slug=provider_spec["provider"]["provider_slug"],
        provider_name=provider_spec["provider"]["provider_name"],
        source_entity=provider_spec["source"]["entity"],
        source_file=source_file.as_posix(),
        source_checksum=source_checksum,
        source_row_key_header=source_row_key_header,
        source_row_key_value=source_row_key_value,
        parser_family=provider_spec["parser_profile"]["parser_family"],
        upload_partition=provider_spec["provider"]["upload_partition"],
        schema_version=str(provider_spec.get("spec_version", DEFAULT_SCHEMA_VERSION)),
        values_by_header=parsed_record.values_by_header,
        values_by_position=build_values_by_position(
            parsed_record.values_by_header,
            provider_spec["parser_profile"]["parser_options"].get("expected_headers", []),
        ),
    )


def build_values_by_position(
    values_by_header: dict[str, Any],
    expected_headers: list[str],
) -> dict[int, Any]:
    values_by_position: dict[int, Any] = {}
    duplicate_offsets: dict[str, int] = {}
    for index, header in enumerate(expected_headers):
        raw_value = values_by_header.get(header)
        if isinstance(raw_value, list):
            offset = duplicate_offsets.get(header, 0)
            values_by_position[index] = raw_value[offset] if offset < len(raw_value) else None
            duplicate_offsets[header] = offset + 1
        else:
            values_by_position[index] = raw_value
    return values_by_position


def build_bronze_record(
    source_record: SourceRecord,
    provider_spec: dict[str, Any],
    ingestion_run_id: str,
) -> BronzeRecord:
    source_lineage_ref = build_lineage_ref(
        source_record.provider_slug,
        source_record.source_entity,
        source_record.source_file,
        source_record.source_checksum,
        source_record.source_row_key_value,
    )
    return BronzeRecord(
        provider_slug=source_record.provider_slug,
        provider_name=source_record.provider_name,
        source_entity=source_record.source_entity,
        source_file=source_record.source_file,
        source_checksum=source_record.source_checksum,
        source_row_key_header=source_record.source_row_key_header,
        source_row_key_value=source_record.source_row_key_value,
        source_file_pattern=provider_spec["source"]["expected_file_patterns"][0],
        upload_partition=source_record.upload_partition,
        parser_family=source_record.parser_family,
        schema_version=source_record.schema_version,
        adapter_version=ADAPTER_VERSION,
        ingestion_run_id=ingestion_run_id,
        source_lineage_ref=source_lineage_ref,
        quarantine_status="accepted",
        values_by_header=source_record.values_by_header,
    )


def build_silver_rows(
    source_record: SourceRecord,
    mappings_by_entity: dict[str, list[CanonicalColumnMapping]],
    source_lineage_ref: str,
    ingestion_run_id: str,
    evidence_path: str,
) -> tuple[list[SilverRow], list[QuarantineRecord], list[QAEvidenceRecord]]:
    rows_by_silver_entity: dict[str, dict[str, Any]] = {}
    quarantine_records: list[QuarantineRecord] = []
    qa_evidence: list[QAEvidenceRecord] = []

    for mapping in mappings_by_entity.get(source_record.source_entity, []):
        rows_by_silver_entity.setdefault(
            mapping.silver_entity,
            {
                "adapter_version": ADAPTER_VERSION,
                "ingestion_run_id": ingestion_run_id,
                "source_checksum": source_record.source_checksum,
            },
        )
        raw_value = resolve_raw_value(source_record, mapping, source_lineage_ref)
        value, warning = cast_canonical_value(mapping, raw_value)
        if warning:
            qa_evidence.append(
                build_qa_record(
                    source_record,
                    mapping,
                    expected_value="valid optional canonical value",
                    observed_value=warning,
                    failure_count=1,
                    decision="warn",
                    evidence_path=evidence_path,
                )
            )

        if value is None and mapping.required:
            reason = f"Required canonical field {mapping.silver_column} is missing or invalid"
            quarantine_records.append(
                QuarantineRecord(
                    provider_slug=source_record.provider_slug,
                    source_entity=source_record.source_entity,
                    silver_entity=mapping.silver_entity,
                    source_file=source_record.source_file,
                    source_checksum=source_record.source_checksum,
                    source_row_key_value=source_record.source_row_key_value,
                    column_name=mapping.silver_column,
                    decision="quarantine_data",
                    reason=reason,
                    evidence_path=evidence_path,
                )
            )
            qa_evidence.append(
                build_qa_record(
                    source_record,
                    mapping,
                    expected_value="required canonical value",
                    observed_value="missing_or_invalid",
                    failure_count=1,
                    decision="quarantine_data",
                    evidence_path=evidence_path,
                )
            )
            continue

        rows_by_silver_entity[mapping.silver_entity][mapping.silver_column] = value

    silver_rows = [
        SilverRow(silver_entity=silver_entity, values=values)
        for silver_entity, values in sorted(rows_by_silver_entity.items())
    ]
    return silver_rows, quarantine_records, qa_evidence


def resolve_raw_value(
    source_record: SourceRecord,
    mapping: CanonicalColumnMapping,
    source_lineage_ref: str,
) -> Any:
    if mapping.source_header == "__metadata__":
        metadata_values = {
            "provider_slug": source_record.provider_slug,
            "source_entity": source_record.source_entity,
            "source_lineage_ref": source_lineage_ref,
        }
        return metadata_values.get(mapping.silver_column)

    if mapping.silver_column == "source_row_id":
        return source_record.source_row_key_value

    if mapping.source_index is not None and source_record.values_by_position:
        return source_record.values_by_position.get(mapping.source_index)

    return source_record.values_by_header.get(mapping.source_header)


def cast_canonical_value(
    mapping: CanonicalColumnMapping,
    raw_value: Any,
) -> tuple[Any, str | None]:
    if raw_value in (None, ""):
        return None, None

    if mapping.silver_column == "record_status":
        return normalize_status(raw_value), None
    if mapping.silver_column == "coverage_status":
        return normalize_coverage_status(raw_value), None
    if mapping.silver_column in {"height_cm", "weight_kg", "systolic_bp"}:
        return extract_observation_measure(raw_value, mapping.silver_column)

    try:
        if mapping.target_type == "string":
            return str(raw_value), None
        if mapping.target_type == "date":
            return parse_date(raw_value), None
        if mapping.target_type == "datetime":
            return parse_datetime(raw_value), None
        if mapping.target_type == "decimal":
            return str(Decimal(str(raw_value))), None
        if mapping.target_type == "json_string":
            return parse_json_string(raw_value), None
    except (ValueError, InvalidOperation, TypeError) as error:
        if mapping.required:
            return None, str(error)
        return None, f"optional cast failed for {mapping.silver_column}"

    raise AdapterRuntimeError(f"Unsupported canonical type: {mapping.target_type}")


def normalize_status(raw_value: Any) -> str:
    if isinstance(raw_value, bool):
        return "active" if raw_value else "inactive"
    text = str(raw_value).strip().lower()
    status_map = {
        "1": "active",
        "0": "inactive",
        "true": "active",
        "false": "inactive",
        "active": "active",
        "inactive": "inactive",
        "final": "final",
        "completed": "completed",
        "stopped": "inactive",
        "cancelled": "inactive",
        "entered-in-error": "error",
    }
    return status_map.get(text, "unknown")


def normalize_coverage_status(raw_value: Any) -> str:
    if isinstance(raw_value, bool):
        return "COVERED" if raw_value else "OUT_OF_COVERAGE"
    text = str(raw_value).strip().upper()
    coverage_map = {
        "1": "COVERED",
        "TRUE": "COVERED",
        "ACTIVE": "COVERED",
        "COVERED": "COVERED",
        "0": "OUT_OF_COVERAGE",
        "FALSE": "OUT_OF_COVERAGE",
        "INACTIVE": "OUT_OF_COVERAGE",
        "TERMED": "OUT_OF_COVERAGE",
        "OUT_OF_COVERAGE": "OUT_OF_COVERAGE",
        "UNINSURED": "UNINSURED",
    }
    return coverage_map.get(text, "UNKNOWN")


def parse_date(raw_value: Any) -> str:
    if isinstance(raw_value, date) and not isinstance(raw_value, datetime):
        return raw_value.isoformat()
    text = str(raw_value).strip()
    return date.fromisoformat(text[:10]).isoformat()


def parse_datetime(raw_value: Any) -> str:
    if isinstance(raw_value, datetime):
        return raw_value.isoformat()
    text = str(raw_value).strip()
    if len(text) == 10:
        return datetime.fromisoformat(f"{text}T00:00:00").isoformat()
    return datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat()


def parse_json_string(raw_value: Any) -> str:
    if not isinstance(raw_value, str):
        raise TypeError("JSON source value must be a string")
    json.loads(raw_value)
    return raw_value


def extract_observation_measure(
    raw_value: Any,
    silver_column: str,
) -> tuple[str | None, str | None]:
    try:
        payload = json.loads(str(raw_value))
    except json.JSONDecodeError:
        return None, f"optional observation payload parse failed for {silver_column}"

    value = None
    if silver_column == "height_cm":
        value = payload.get("height_cm")
        if value is None and isinstance(payload.get("height"), dict):
            value = payload["height"].get("value")
    elif silver_column == "weight_kg":
        value = payload.get("weight_kg")
        if value is None and isinstance(payload.get("weight"), dict):
            value = payload["weight"].get("value")
    elif silver_column == "systolic_bp":
        value = payload.get("systolic_bp")
        if value is None and isinstance(payload.get("blood_pressure"), dict):
            value = payload["blood_pressure"].get("systolic")

    if value in (None, ""):
        return None, None
    try:
        return str(Decimal(str(value))), None
    except (InvalidOperation, ValueError):
        return None, f"optional observation measure cast failed for {silver_column}"


def build_qa_record(
    source_record: SourceRecord,
    mapping: CanonicalColumnMapping,
    expected_value: str,
    observed_value: str,
    failure_count: int,
    decision: str,
    evidence_path: str,
) -> QAEvidenceRecord:
    return QAEvidenceRecord(
        test_name=f"{mapping.silver_entity}.{mapping.silver_column}",
        family="data_quality",
        stage="adapter_implementation",
        provider=source_record.provider_slug,
        entity=source_record.source_entity,
        source_file=source_record.source_file,
        checksum=source_record.source_checksum,
        expected_value=expected_value,
        observed_value=observed_value,
        failure_count=failure_count,
        decision=decision,
        evidence_path=evidence_path,
    )


def evidence_contains_sensitive_raw_value(evidence: list[QAEvidenceRecord]) -> bool:
    for item in evidence:
        evidence_text = " ".join(
            [item.expected_value, item.observed_value, item.source_file]
        )
        if any(pattern.search(evidence_text) for pattern in SENSITIVE_RAW_VALUE_PATTERNS):
            return True
    return False
