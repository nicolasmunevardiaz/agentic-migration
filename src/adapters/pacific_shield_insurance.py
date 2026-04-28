from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

import yaml


class PacificShieldParseError(ValueError):
    """Raised when a Pacific Shield CSV file cannot satisfy its provider spec."""


def load_spec(spec_path: Path | str) -> dict[str, Any]:
    return yaml.safe_load(Path(spec_path).read_text())


def parse_pacific_shield_file(
    csv_path: Path | str,
    spec_path: Path | str,
) -> list[dict[str, dict[str, Any]]]:
    spec = load_spec(spec_path)
    return parse_pacific_shield_text(Path(csv_path).read_text(), spec)


def parse_pacific_shield_text(
    text: str,
    spec: dict[str, Any],
) -> list[dict[str, dict[str, Any]]]:
    parser_profile = spec["parser_profile"]
    if parser_profile["parser_family"] != "csv_claims_export":
        raise PacificShieldParseError(
            f"Unsupported parser family: {parser_profile['parser_family']}"
        )

    parser_options = parser_profile["parser_options"]
    expected_headers = parser_options["expected_headers"]
    delimiter = parser_options.get("delimiter", ",")
    comment_prefix = parser_options.get("comment_prefix", "#")
    source_row_key = parser_profile["source_row_key"]
    row_key_index = expected_headers.index(source_row_key)
    source_fields = spec["mapping"]["fields"]

    records = []
    for row in csv.reader(io.StringIO(text), delimiter=delimiter):
        if should_skip_csv_row(row, expected_headers, comment_prefix):
            continue
        if looks_like_header_row(row, source_row_key):
            raise PacificShieldParseError(
                f"Unexpected header shape for entity {spec['source']['entity']}"
            )
        if len(row) != len(expected_headers):
            raise PacificShieldParseError(
                f"Malformed CSV row for entity {spec['source']['entity']}: "
                f"expected {len(expected_headers)} columns, found {len(row)}"
            )
        if not row[row_key_index].strip():
            raise PacificShieldParseError(f"Missing source row key {source_row_key}")

        values_by_header = build_values_by_header(expected_headers, row)
        values_by_canonical = {
            field["canonical_name"]: row[field["source_index"]]
            for field in source_fields
        }
        records.append(
            {
                "values_by_header": values_by_header,
                "values_by_canonical": values_by_canonical,
            }
        )

    return records


def should_skip_csv_row(
    row: list[str],
    expected_headers: list[str],
    comment_prefix: str,
) -> bool:
    if not row:
        return True
    first_cell = row[0].strip()
    if not first_cell and len(row) == 1:
        return True
    if first_cell.startswith(comment_prefix):
        return True
    if first_cell.startswith("sep="):
        return True
    return row == expected_headers


def looks_like_header_row(row: list[str], source_row_key: str) -> bool:
    return bool(row and row[0] == source_row_key)


def build_values_by_header(
    expected_headers: list[str],
    row: list[str],
) -> dict[str, str | list[str]]:
    values_by_header: dict[str, str | list[str]] = {}
    for index, source_header in enumerate(expected_headers):
        value = row[index]
        if source_header not in values_by_header:
            values_by_header[source_header] = value
            continue

        existing_value = values_by_header[source_header]
        if isinstance(existing_value, list):
            existing_value.append(value)
        else:
            values_by_header[source_header] = [existing_value, value]
    return values_by_header
