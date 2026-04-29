import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PROVIDER_SLUG = "data_provider_1_aegis_care_network"
DEFAULT_SPEC_ROOT = Path("metadata/provider_specs") / PROVIDER_SLUG


class AegisParseError(ValueError):
    """Raised when an Aegis source bundle does not match its provider spec."""


@dataclass(frozen=True)
class ParsedAegisRecord:
    provider_slug: str
    entity: str
    source_file: str
    source_row_key: str
    values_by_header: dict[str, Any]
    values_by_canonical: dict[str, Any]


def load_aegis_entity_spec(entity: str, spec_root: Path = DEFAULT_SPEC_ROOT) -> dict[str, Any]:
    spec_path = spec_root / f"{entity}.yaml"
    if not spec_path.exists():
        raise AegisParseError(f"Missing Aegis provider spec: {spec_path}")

    spec = yaml.safe_load(spec_path.read_text())
    if not isinstance(spec, dict):
        raise AegisParseError(f"Aegis provider spec is not a mapping: {spec_path}")

    return spec


def resolve_aegis_resource_path(resource: dict[str, Any], path: str) -> Any:
    if path in resource:
        return resource[path]

    current: Any = resource
    try:
        for part in path.split("."):
            if "[" in part:
                name, index_text = part.split("[", 1)
                index = int(index_text.rstrip("]"))
                current = current[name][index]
            else:
                current = current[part]
        return current
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise AegisParseError(f"Missing declared Aegis resource path: {path}") from error


def parse_aegis_entity_file(
    entity: str,
    source_file: Path,
    spec_root: Path = DEFAULT_SPEC_ROOT,
) -> list[ParsedAegisRecord]:
    spec = load_aegis_entity_spec(entity, spec_root)
    return parse_aegis_bundle_with_spec(source_file, spec)


def parse_aegis_bundle_with_spec(
    source_file: Path,
    spec: dict[str, Any],
) -> list[ParsedAegisRecord]:
    parser_profile = spec["parser_profile"]
    parser_options = parser_profile["parser_options"]

    if parser_profile["parser_family"] != "fhir_r4_bundle":
        raise AegisParseError("Aegis parser only supports fhir_r4_bundle specs")

    try:
        source_text = read_aegis_source_text(source_file)
        bundle = json.loads(normalize_aegis_bundle_text(source_text, parser_options))
    except json.JSONDecodeError as error:
        raise AegisParseError(f"Malformed Aegis FHIR bundle JSON in {source_file}") from error
    if bundle.get("resourceType") != "Bundle":
        raise AegisParseError(f"Expected FHIR Bundle in {source_file}")

    resources = [
        entry.get("resource")
        for entry in bundle.get("entry", [])
        if isinstance(entry, dict) and isinstance(entry.get("resource"), dict)
    ]
    if not resources:
        raise AegisParseError(f"No bundle resources found in {source_file}")

    expected_resource_type = parser_options["resource_type"]
    canonical_by_header = {
        field["source_header"]: field["canonical_name"]
        for field in spec["mapping"]["fields"]
    }
    field_paths = parser_options["field_paths"]
    source_row_key = parser_profile["source_row_key"]
    records = []

    for resource in resources:
        if resource.get("resourceType") != expected_resource_type:
            raise AegisParseError(
                f"Expected {expected_resource_type} resource in {source_file}"
            )

        values_by_header = {
            header: resolve_aegis_resource_path(resource, field_path)
            for header, field_path in field_paths.items()
        }
        if not values_by_header.get(source_row_key):
            raise AegisParseError(f"Missing source row key {source_row_key} in {source_file}")

        values_by_canonical = {
            canonical_by_header[header]: value for header, value in values_by_header.items()
        }
        records.append(
            ParsedAegisRecord(
                provider_slug=spec["provider"]["provider_slug"],
                entity=spec["source"]["entity"],
                source_file=str(source_file),
                source_row_key=source_row_key,
                values_by_header=values_by_header,
                values_by_canonical=values_by_canonical,
            )
        )

    return records


def read_aegis_source_text(source_file: Path) -> str:
    raw_bytes = source_file.read_bytes()
    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return raw_bytes.decode("cp1252")


def normalize_aegis_bundle_text(text: str, parser_options: dict[str, Any]) -> str:
    comment_prefix = parser_options.get("comment_prefix", "//")
    cleaned_lines = [
        line for line in text.splitlines() if not line.strip().startswith(comment_prefix)
    ]
    cleaned_text = "\n".join(cleaned_lines).strip()

    export_trailer = parser_options.get("export_trailer")
    if export_trailer and export_trailer in cleaned_text:
        cleaned_text = cleaned_text.split(export_trailer, 1)[0].rstrip()

    first_object_index = cleaned_text.find("{")
    last_object_index = cleaned_text.rfind("}")
    if first_object_index >= 0 and last_object_index >= first_object_index:
        return cleaned_text[first_object_index : last_object_index + 1]

    return cleaned_text
