from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ROOT = Path(__file__).resolve().parents[2]
DATAQ_DIR = ROOT / "reports" / "dataq_drifts"
DRIFT_MATRIX = DATAQ_DIR / "v0_5_derived_dataq_drift_matrix.tsv"
CATEGORY_MATRIX = DATAQ_DIR / "v0_5_dataq_category_matrix.tsv"
CATEGORY_BACKLOG = DATAQ_DIR / "v0_5_dataq_category_backlog.md"
DRIFT_REPORT = DATAQ_DIR / "v0_5_derived_dataq_drift_report.md"
TEMPLATE = DATAQ_DIR / "dataq_drift_template.md"

EXPECTED_GRANULAR_HEADERS = [
    "drift_id",
    "provider",
    "entity",
    "field_column",
    "category",
    "total_rows",
    "affected_rows",
    "severity",
    "resolution_hint",
    "status",
]

EXPECTED_CATEGORY_HEADERS = [
    "category_drift_id",
    "canonical_category",
    "issue_family",
    "primary_quality_dimension",
    "secondary_quality_dimension",
    "providers",
    "entities",
    "fields",
    "source_drift_count",
    "max_severity",
    "resolution_pattern",
    "status",
]

EXPECTED_GRANULAR_CATEGORY_COUNTS = {
    "component_presence": 24,
    "nullability": 18,
    "referential_integrity": 32,
    "semantic_variant": 7,
    "standard_format": 8,
    "temporal_validity": 4,
    "uniqueness": 5,
}

EXPECTED_CANONICAL_CATEGORIES = {
    "Accuracy",
    "Completeness",
    "Consistency",
    "Timeliness",
    "Uniqueness",
    "Validity",
}

RESOLUTION_HINT_CATEGORY_COVERAGE = {
    "amount_completeness_flag": "DQCAT-COMP-004",
    "approved_date_source_required": "DQCAT-TIME-002",
    "birth_date_bounds_quarantine": "DQCAT-VAL-002",
    "birth_date_survivor_rule": "DQCAT-CONS-005",
    "code_source_hint_mapping": "DQCAT-VAL-003",
    "component_completeness_flag": "DQCAT-COMP-003",
    "condition_reference_audit_bridge": "DQCAT-CONS-003",
    "date_parser_quarantine": "DQCAT-VAL-002",
    "demographic_survivor_rules": "DQCAT-CONS-005",
    "deterministic_period_key": "DQCAT-UNIQ-001",
    "encounter_reference_audit_bridge": "DQCAT-CONS-002",
    "end_date_only_transition": "DQCAT-COMP-005",
    "medication_code_variant_dimension": "DQCAT-CONS-004",
    "medication_description_variant_dimension": "DQCAT-CONS-004",
    "member_reference_normalization": "DQCAT-CONS-001",
    "provider_gender_precedence": "DQCAT-CONS-005",
    "unknown_period_state": "DQCAT-COMP-005",
}


class DriftMatrixRow(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    drift_id: str
    provider: str
    entity: str
    field_column: str
    category: Literal[
        "component_presence",
        "nullability",
        "referential_integrity",
        "semantic_variant",
        "standard_format",
        "temporal_validity",
        "uniqueness",
    ]
    total_rows: int = Field(ge=0)
    affected_rows: int = Field(ge=0)
    severity: Literal["Critical", "High", "Medium", "Low"]
    resolution_hint: str
    status: Literal["Open", "Monitoring"]

    ID_PREFIXES: ClassVar[tuple[str, ...]] = (
        "DQ-PAT-",
        "DQ-COV-",
        "DQ-ENC-",
        "DQ-CON-",
        "DQ-OBS-",
        "DQ-MED-",
        "DQ-CST-",
    )

    @field_validator("drift_id")
    @classmethod
    def drift_id_has_known_entity_prefix(cls, value: str) -> str:
        if not value.startswith(cls.ID_PREFIXES):
            msg = f"unexpected drift id prefix: {value}"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def affected_rows_do_not_exceed_total_rows(self) -> DriftMatrixRow:
        if self.affected_rows > self.total_rows:
            msg = f"{self.drift_id} has affected_rows > total_rows"
            raise ValueError(msg)
        return self


class CategoryMatrixRow(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    category_drift_id: str
    canonical_category: Literal[
        "Accuracy",
        "Completeness",
        "Consistency",
        "Timeliness",
        "Uniqueness",
        "Validity",
    ]
    issue_family: str
    primary_quality_dimension: Literal[
        "Accuracy",
        "Completeness",
        "Consistency",
        "Timeliness",
        "Uniqueness",
        "Validity",
    ]
    secondary_quality_dimension: Literal[
        "Accuracy",
        "Completeness",
        "Consistency",
        "Timeliness",
        "Uniqueness",
        "Validity",
    ]
    providers: str
    entities: str
    fields: str
    source_drift_count: int = Field(ge=0)
    max_severity: Literal["Critical", "High", "Medium", "Low", "HITL", "Monitoring"]
    resolution_pattern: str
    status: Literal["Open", "Monitoring"]

    @field_validator("category_drift_id")
    @classmethod
    def category_id_has_expected_prefix(cls, value: str) -> str:
        if not value.startswith("DQCAT-"):
            msg = f"unexpected category drift id prefix: {value}"
            raise ValueError(msg)
        return value


def _read_tsv(path: Path, expected_headers: list[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        assert reader.fieldnames == expected_headers
        return list(reader)


def _load_granular_rows() -> list[DriftMatrixRow]:
    return [
        DriftMatrixRow.model_validate(row)
        for row in _read_tsv(DRIFT_MATRIX, EXPECTED_GRANULAR_HEADERS)
    ]


def _load_category_rows() -> list[CategoryMatrixRow]:
    return [
        CategoryMatrixRow.model_validate(row)
        for row in _read_tsv(CATEGORY_MATRIX, EXPECTED_CATEGORY_HEADERS)
    ]


def test_dataq_report_files_exist() -> None:
    for path in (DRIFT_MATRIX, CATEGORY_MATRIX, CATEGORY_BACKLOG, DRIFT_REPORT, TEMPLATE):
        assert path.exists(), f"missing data quality drift artifact: {path}"


def test_granular_drift_matrix_contract() -> None:
    rows = _load_granular_rows()
    assert len(rows) == 98
    assert len({row.drift_id for row in rows}) == len(rows)
    assert Counter(row.category for row in rows) == EXPECTED_GRANULAR_CATEGORY_COUNTS
    assert {row.status for row in rows} == {"Open"}
    assert {row.severity for row in rows} == {"Critical", "High", "Medium", "Low"}


def test_category_matrix_contract() -> None:
    rows = _load_category_rows()
    assert len(rows) == 20
    assert len({row.category_drift_id for row in rows}) == len(rows)
    assert {row.canonical_category for row in rows} == EXPECTED_CANONICAL_CATEGORIES
    assert {row.primary_quality_dimension for row in rows} == EXPECTED_CANONICAL_CATEGORIES
    assert all(row.issue_family for row in rows)
    assert all(row.resolution_pattern for row in rows)


def test_every_granular_resolution_hint_maps_to_category_backlog() -> None:
    granular_rows = _load_granular_rows()
    category_ids = {row.category_drift_id for row in _load_category_rows()}
    missing_hints = {
        row.resolution_hint
        for row in granular_rows
        if row.resolution_hint not in RESOLUTION_HINT_CATEGORY_COVERAGE
    }
    assert not missing_hints

    missing_categories = {
        category_id
        for category_id in RESOLUTION_HINT_CATEGORY_COVERAGE.values()
        if category_id not in category_ids
    }
    assert not missing_categories


def test_backlog_document_references_all_category_ids() -> None:
    backlog_text = CATEGORY_BACKLOG.read_text(encoding="utf-8")
    for row in _load_category_rows():
        assert row.category_drift_id in backlog_text


def test_report_links_to_category_artifacts() -> None:
    report_text = DRIFT_REPORT.read_text(encoding="utf-8")
    assert "v0_5_dataq_category_backlog.md" in report_text
    assert "v0_5_dataq_category_matrix.tsv" in report_text
