from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class NorthCareParseError(ValueError):
    """Raised when a NorthCare X12-like file cannot satisfy its provider spec."""


def load_spec(spec_path: Path | str) -> dict[str, Any]:
    return json.loads(Path(spec_path).read_text())


def parse_northcare_file(
    text_path: Path | str,
    spec_path: Path | str,
) -> list[dict[str, dict[str, str]]]:
    spec = load_spec(spec_path)
    return parse_northcare_text(Path(text_path).read_text(), spec)


def parse_northcare_text(
    text: str,
    spec: dict[str, Any],
) -> list[dict[str, dict[str, str]]]:
    parser_profile = spec["parser_profile"]
    if parser_profile["parser_family"] != "x12_segment_envelope":
        raise NorthCareParseError(
            f"Unsupported parser family: {parser_profile['parser_family']}"
        )

    parser_options = parser_profile["parser_options"]
    segment_terminator = parser_options["segment_terminator"]
    element_separator = parser_options["element_separator"]
    header_segment = parser_options["header_segment"]
    entity_segment = parser_options["entity_segment"]
    comment_prefix = parser_options.get("comment_prefix", "#")

    segments = split_segments(
        text=text,
        segment_terminator=segment_terminator,
        comment_prefix=comment_prefix,
    )
    validate_envelope_segments(segments)

    header_fields = extract_header_fields(
        segments=segments,
        header_segment=header_segment,
        element_separator=element_separator,
    )
    expected_headers = [field["source_header"] for field in spec["mapping"]["fields"]]
    if header_fields != expected_headers:
        raise NorthCareParseError(
            f"HDR fields do not match declared mapping for {spec['source']['entity']}"
        )

    source_row_key = parser_profile["source_row_key"]
    source_to_canonical = {
        field["source_header"]: field["canonical_name"] for field in spec["mapping"]["fields"]
    }
    records = []
    for segment in matching_segments(
        segments=segments,
        entity_segment=entity_segment,
        element_separator=element_separator,
    ):
        values = segment.split(element_separator)
        values_by_header = map_values_by_header(
            values=values,
            header_fields=header_fields,
            entity_segment=entity_segment,
        )
        if not values_by_header[source_row_key].strip():
            raise NorthCareParseError(f"Missing source row key {source_row_key}")

        values_by_canonical = {
            source_to_canonical[source_header]: value
            for source_header, value in values_by_header.items()
        }
        records.append(
            {
                "values_by_header": values_by_header,
                "values_by_canonical": values_by_canonical,
            }
        )

    if not records:
        raise NorthCareParseError(f"Expected entity segment {entity_segment} was not found")

    return records


def split_segments(
    text: str,
    segment_terminator: str,
    comment_prefix: str,
) -> list[str]:
    if segment_terminator not in text:
        raise NorthCareParseError("Malformed NorthCare X12 envelope: missing segment terminator")

    content = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith(comment_prefix)
    )
    return [
        segment.strip()
        for segment in content.split(segment_terminator)
        if segment.strip()
    ]


def validate_envelope_segments(segments: list[str]) -> None:
    segment_names = {segment.split("*", 1)[0] for segment in segments}
    required_segments = {"ISA", "GS", "ST", "HDR", "SE", "GE", "IEA"}
    missing_segments = sorted(required_segments - segment_names)
    if missing_segments:
        raise NorthCareParseError(
            "Malformed NorthCare X12 envelope: missing "
            + ", ".join(missing_segments)
        )


def extract_header_fields(
    segments: list[str],
    header_segment: str,
    element_separator: str,
) -> list[str]:
    for segment in segments:
        values = segment.split(element_separator)
        if values[0] == header_segment:
            return [extract_header_name(value) for value in values[1:]]
    raise NorthCareParseError(f"Expected header segment {header_segment} was not found")


def extract_header_name(header_value: str) -> str:
    if ":" in header_value:
        return header_value.split(":", 1)[1]
    return header_value


def matching_segments(
    segments: list[str],
    entity_segment: str,
    element_separator: str,
) -> list[str]:
    return [
        segment
        for segment in segments
        if segment.split(element_separator, 1)[0] == entity_segment
    ]


def map_values_by_header(
    values: list[str],
    header_fields: list[str],
    entity_segment: str,
) -> dict[str, str]:
    value_count = len(values) - 1
    if value_count != len(header_fields):
        raise NorthCareParseError(
            f"Element count mismatch for {entity_segment}: "
            f"expected {len(header_fields)}, found {value_count}"
        )
    return dict(zip(header_fields, values[1:], strict=True))
