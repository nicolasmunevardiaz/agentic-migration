from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = REPO_ROOT / "metadata" / "model_specs"
BRONZE_PATH = MODEL_ROOT / "bronze" / "bronze_contract.yaml"
SILVER_ROOT = MODEL_ROOT / "silver"
PROVIDER_ROOT = REPO_ROOT / "metadata" / "provider_specs"

EXPECTED_SILVER_ENTITIES = {
    "members",
    "coverage_periods",
    "encounters",
    "conditions",
    "medications",
    "observations",
    "cost_records",
}
REQUIRED_LINEAGE_COLUMNS = {
    "provider_slug",
    "source_entity",
    "source_row_id",
    "source_lineage_ref",
}
FORBIDDEN_SILVER_COLUMNS = {
    "FIRST_NAME",
    "LAST_NAME",
    "SSN",
    "MBR_FIRST_NM",
    "MBR_LAST_NM",
    "TAX_ID",
    "SSN_NUM",
    "PATIENT_SSN",
    "MBR_SSN",
}
ALLOWED_TYPES = {"string", "date", "datetime", "decimal", "json_string"}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def source_key(field: dict) -> tuple[str, int | None]:
    return field["source_header"], field.get("source_index")


def provider_field_keys(path_text: str) -> set[tuple[str, int | None]]:
    spec = load_yaml(REPO_ROOT / path_text)
    return {source_key(field) for field in spec["mapping"]["fields"]}


def silver_specs() -> dict[str, dict]:
    return {
        path.stem: load_yaml(path)
        for path in sorted(SILVER_ROOT.glob("*.yaml"))
        if path.name != ".gitkeep"
    }


def all_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for entry in value for item in all_strings(entry)]
    if isinstance(value, dict):
        return [item for entry in value.values() for item in all_strings(entry)]
    return []


def test_bronze_contract_covers_all_provider_specs() -> None:
    bronze = load_yaml(BRONZE_PATH)
    provider_specs = sorted(PROVIDER_ROOT.glob("*/*.yaml"))

    assert bronze["artifact"] == "bronze_contract"
    assert bronze["plan_id"] == "02_canonical_model_and_contracts_plan"
    assert bronze["status"] == "approved"
    assert bronze["provider_scope"] == "all"
    assert len(bronze["source_contracts"]) == len(provider_specs) == 25

    lineage_names = {entry["name"] for entry in bronze["required_lineage_columns"]}
    assert lineage_names >= {
        "provider_slug",
        "provider_name",
        "source_entity",
        "source_row_key_header",
        "source_row_key_value",
        "source_file_pattern",
        "upload_partition",
        "parser_family",
        "schema_version",
        "load_timestamp",
        "quarantine_status",
    }

    contract_paths = {
        REPO_ROOT / contract["provider_spec_path"]
        for contract in bronze["source_contracts"]
    }
    assert contract_paths == set(provider_specs)

    for contract in bronze["source_contracts"]:
        assert contract["source_row_key"]
        assert contract["canonical_row_key"] == "ROW_ID"
        assert contract["parser_family"]
        assert contract["expected_file_patterns"]
        assert contract["fields"]
        assert all(field["required_for_bronze"] for field in contract["fields"])
        for field in contract["fields"]:
            assert field["field_decision_id"]
            assert field["linked_runbook_decision_ids"]


def test_silver_specs_have_required_shape_and_lineage() -> None:
    specs = silver_specs()

    assert set(specs) == EXPECTED_SILVER_ENTITIES

    for entity, spec in specs.items():
        assert spec["entity"] == entity
        assert spec["layer"] == "silver"
        assert spec["plan_id"] == "02_canonical_model_and_contracts_plan"
        assert spec["status"] == "approved"
        assert spec["grain"]
        assert spec["description"]
        assert spec["readiness"]["model_ready"] is True
        assert spec["readiness"]["blocked_reason"] == ""
        assert spec["governance"]["identity_resolution"] == "not_performed"
        assert spec["governance"]["clinical_interpretation"] == "not_performed"
        assert spec["governance"]["financial_interpretation"] == "not_performed"
        assert spec["governance"]["databricks_impact"] == "none"

        columns = {column["name"]: column for column in spec["columns"]}
        assert set(columns) >= REQUIRED_LINEAGE_COLUMNS
        assert not (set(columns) & FORBIDDEN_SILVER_COLUMNS)

        for name, column in columns.items():
            assert column["type"] in ALLOWED_TYPES
            assert isinstance(column["nullable"], bool)
            assert isinstance(column["required"], bool)
            assert column["pii_class"]
            assert column["transform_rule"]
            assert column["source_mappings"], f"{entity}.{name}"
            if name in REQUIRED_LINEAGE_COLUMNS:
                assert column["lineage_required"] is True
                assert column["required"] is True
                assert column["nullable"] is False
            if column["required"]:
                assert column["quarantine_if_invalid"] is True


def test_silver_source_mappings_reference_provider_specs() -> None:
    for entity, spec in silver_specs().items():
        for column in spec["columns"]:
            for mapping in column["source_mappings"]:
                assert not Path(mapping["provider_spec_path"]).is_absolute()
                assert (REPO_ROOT / mapping["provider_spec_path"]).exists()
                if mapping["source_header"] == "__metadata__":
                    assert mapping["field_decision_id"] == "DRIFT-001-lineage-metadata"
                    continue
                assert (
                    mapping["source_header"],
                    mapping.get("source_index"),
                ) in provider_field_keys(mapping["provider_spec_path"]), (
                    entity,
                    column["name"],
                    mapping,
                )


def test_model_specs_do_not_introduce_forbidden_scope_or_sensitive_examples() -> None:
    strings = []
    strings.extend(all_strings(load_yaml(BRONZE_PATH)))
    for spec in silver_specs().values():
        strings.extend(all_strings(spec))

    assert not any(Path(text).is_absolute() for text in strings if "/" in text)
    assert not any("metadata/deployment_specs/databricks/" in text for text in strings)
    assert not any("dashboard" in text.lower() for text in strings)
    assert not any("kpi" in text.lower() for text in strings)
    assert not any(
        "enterprise identity resolution is performed" in text.lower()
        for text in strings
    )
