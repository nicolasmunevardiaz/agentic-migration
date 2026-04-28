from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ValleyBridgeParseError(ValueError):
    """Raised when a ValleyBridge FHIR STU3 file cannot satisfy its provider spec."""


def load_spec(spec_path: Path | str) -> dict[str, Any]:
    return json.loads(Path(spec_path).read_text())


def parse_valleybridge_file(
    json_path: Path | str,
    spec_path: Path | str,
) -> list[dict[str, dict[str, str]]]:
    spec = load_spec(spec_path)
    json_text = decode_source_bytes(Path(json_path).read_bytes(), spec)
    return parse_valleybridge_text(json_text, spec)


def parse_valleybridge_text(
    text: str,
    spec: dict[str, Any],
) -> list[dict[str, dict[str, str]]]:
    parser_profile = spec["parser_profile"]
    if parser_profile["parser_family"] != "fhir_stu3_bundle_with_comments":
        raise ValleyBridgeParseError(
            f"Unsupported parser family: {parser_profile['parser_family']}"
        )

    parser_options = parser_profile["parser_options"]
    cleaned_text = strip_comment_lines(
        text=text,
        comment_prefix=parser_options.get("comment_prefix", "#"),
    )
    try:
        bundle = json.loads(cleaned_text)
    except json.JSONDecodeError as error:
        raise ValleyBridgeParseError(f"Malformed ValleyBridge FHIR JSON: {error}") from error

    if bundle.get("resourceType") != "Bundle":
        raise ValleyBridgeParseError("Expected FHIR Bundle resourceType")

    entries = bundle.get("entry")
    if not isinstance(entries, list) or not entries:
        raise ValleyBridgeParseError("Expected Bundle entries were not found")

    expected_resource_type = parser_options["resource_type"]
    source_row_key = parser_profile["source_row_key"]
    field_paths = parser_options["field_paths"]
    source_to_canonical = {
        field["source_header"]: field["canonical_name"] for field in spec["mapping"]["fields"]
    }

    records = []
    for entry in entries:
        resource = entry.get("resource") if isinstance(entry, dict) else None
        if not isinstance(resource, dict):
            raise ValleyBridgeParseError("Expected Bundle entry resource object")
        if resource.get("resourceType") != expected_resource_type:
            raise ValleyBridgeParseError(
                f"Expected resourceType {expected_resource_type}, "
                f"found {resource.get('resourceType')}"
            )

        values_by_header = {
            source_header: stringify_source_value(
                resolve_required_path(resource=resource, field_path=field_path)
            )
            for source_header, field_path in field_paths.items()
        }
        if not values_by_header[source_row_key].strip():
            raise ValleyBridgeParseError(f"Missing source row key {source_row_key}")

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

    return records


def decode_source_bytes(raw_bytes: bytes, spec: dict[str, Any]) -> str:
    encoding_candidates = spec["parser_profile"]["parser_options"].get(
        "encoding_candidates",
        ["utf-8"],
    )
    errors = []
    for encoding in encoding_candidates:
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError as error:
            errors.append(f"{encoding}: {error.reason}")
    raise ValleyBridgeParseError(
        "Unable to decode ValleyBridge source bytes with declared encodings: "
        + "; ".join(errors)
    )


def strip_comment_lines(text: str, comment_prefix: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.strip().startswith(comment_prefix)
    )


def resolve_required_path(resource: dict[str, Any], field_path: str) -> Any:
    if field_path in resource:
        return resource[field_path]

    try:
        current: Any = resource
        for part in field_path.split("."):
            if "[" in part:
                name, index_text = part.split("[", 1)
                index = int(index_text.rstrip("]"))
                current = current[name][index]
            else:
                current = current[part]
    except (KeyError, IndexError, TypeError) as error:
        raise ValleyBridgeParseError(f"Missing declared field path: {field_path}") from error

    if current is None:
        raise ValleyBridgeParseError(f"Missing declared field path: {field_path}")
    return current


def stringify_source_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return ""
    if isinstance(value, int | float):
        return str(value)
    return json.dumps(value, sort_keys=True)
