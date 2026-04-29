from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


class BlueStoneParseError(ValueError):
    """Raised when a BlueStone HL7 XML file cannot satisfy its provider spec."""


def load_spec(spec_path: Path | str) -> dict[str, Any]:
    return json.loads(Path(spec_path).read_text())


def parse_file(xml_path: Path | str, spec_path: Path | str) -> list[dict[str, dict[str, str]]]:
    spec = load_spec(spec_path)
    return parse_xml_text(read_bluestone_xml_text(Path(xml_path)), spec)


def parse_xml_text(xml_text: str, spec: dict[str, Any]) -> list[dict[str, dict[str, str]]]:
    parser_profile = spec["parser_profile"]
    if parser_profile["parser_family"] != "hl7_v2_xml_messages":
        raise BlueStoneParseError(
            f"Unsupported parser family: {parser_profile['parser_family']}"
        )

    parser_options = parser_profile["parser_options"]
    expected_root_tag = parser_options["root_tag"]
    try:
        root = ET.fromstring(normalize_xml_document_text(xml_text, expected_root_tag))
    except ET.ParseError as error:
        raise BlueStoneParseError(f"Malformed BlueStone HL7 XML: {error}") from error

    if local_name(root.tag) != expected_root_tag:
        raise BlueStoneParseError(
            f"Expected root tag {expected_root_tag}, found {local_name(root.tag)}"
        )

    message_segment = parser_options["message_segment"]
    messages = [child for child in root if local_name(child.tag) == message_segment]
    if not messages:
        raise BlueStoneParseError(f"Expected message segment {message_segment} was not found")

    source_row_key = parser_profile["source_row_key"]
    field_paths = parser_options["field_paths"]
    source_to_canonical = {
        field["source_header"]: field["canonical_name"] for field in spec["mapping"]["fields"]
    }

    records = []
    for message in messages:
        values_by_header = {
            source_header: extract_required_text(message, field_path)
            for source_header, field_path in field_paths.items()
        }
        if not values_by_header[source_row_key]:
            raise BlueStoneParseError(f"Missing source row key {source_row_key}")

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


def read_bluestone_xml_text(xml_path: Path) -> str:
    raw_bytes = xml_path.read_bytes()
    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return raw_bytes.decode("cp1252")


def normalize_xml_document_text(xml_text: str, root_tag: str) -> str:
    stripped_text = xml_text.lstrip()
    declaration_index = stripped_text.find("<?xml")
    if declaration_index > 0:
        stripped_text = stripped_text[declaration_index:]

    closing_tag = f"</{root_tag}>"
    closing_index = stripped_text.rfind(closing_tag)
    if closing_index >= 0:
        return stripped_text[: closing_index + len(closing_tag)]

    return stripped_text


def extract_required_text(message: ET.Element, field_path: str) -> str:
    child = find_direct_child_by_local_name(message, field_path)
    if child is None:
        raise BlueStoneParseError(f"Missing declared field path: {field_path}")
    return "".join(child.itertext()).strip()


def find_direct_child_by_local_name(element: ET.Element, name: str) -> ET.Element | None:
    for child in element:
        if local_name(child.tag) == name:
            return child
    return None


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag
