from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDER_SLUG = "data_provider_5_pacific_shield_insurance"
PROVIDER_ROOT = REPO_ROOT / "metadata/provider_specs" / PROVIDER_SLUG
SILVER_ROOT = REPO_ROOT / "metadata/model_specs/silver"

EXPECTED_SOURCE_ENTITIES = {
    "patients",
    "encounters",
    "conditions",
    "medications",
    "observations",
}
FORBIDDEN_DIRECT_IDENTIFIER_COLUMNS = {
    "MBR_FIRST_NAME",
    "MBR_LAST_NAME",
    "MBR_SSN",
    "PT_FIRST_NM",
    "PT_LAST_NM",
    "SSN_VAL",
}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_pacific_shield_canonical_mappings_reference_existing_provider_fields() -> None:
    provider_fields = {
        path.stem: {
            (field["source_header"], field.get("source_index"))
            for field in load_yaml(path)["mapping"]["fields"]
        }
        for path in PROVIDER_ROOT.glob("*.yaml")
    }

    mapped_source_entities = set()
    for silver_path in SILVER_ROOT.glob("*.yaml"):
        silver_spec = load_yaml(silver_path)
        for column in silver_spec["columns"]:
            for mapping in column["source_mappings"]:
                if mapping["provider_slug"] != PROVIDER_SLUG:
                    continue
                mapped_source_entities.add(mapping["source_entity"])
                assert column["required"] is False
                assert column["nullable"] is True
                if mapping["source_header"] == "__metadata__":
                    continue
                assert (
                    mapping["source_header"],
                    mapping.get("source_index"),
                ) in provider_fields[mapping["source_entity"]], mapping

    assert mapped_source_entities == EXPECTED_SOURCE_ENTITIES


def test_pacific_shield_condition_duplicate_header_mappings_are_position_scoped() -> None:
    mappings = [
        mapping
        for silver_path in SILVER_ROOT.glob("*.yaml")
        for column in load_yaml(silver_path)["columns"]
        for mapping in column["source_mappings"]
        if mapping["provider_slug"] == PROVIDER_SLUG
        and mapping["source_entity"] == "conditions"
        and mapping["source_header"] == "DX_CD"
    ]

    assert {mapping["source_index"] for mapping in mappings} == {2, 5}


def test_pacific_shield_adapter_contract_does_not_promote_direct_identifier_columns() -> None:
    silver_columns = {
        column["name"]
        for silver_path in SILVER_ROOT.glob("*.yaml")
        for column in load_yaml(silver_path)["columns"]
        for mapping in column["source_mappings"]
        if mapping["provider_slug"] == PROVIDER_SLUG
    }

    assert not (silver_columns & FORBIDDEN_DIRECT_IDENTIFIER_COLUMNS)
