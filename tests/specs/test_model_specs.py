import hashlib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = REPO_ROOT / "metadata" / "model_specs"
BRONZE_PATH = MODEL_ROOT / "bronze" / "bronze_contract.yaml"
SILVER_ROOT = MODEL_ROOT / "silver"
EVOLUTION_ROOT = MODEL_ROOT / "evolution"
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

    for column in bronze["required_lineage_columns"]:
        assert column["required"] is False

    for contract in bronze["source_contracts"]:
        assert contract["source_row_key"]
        assert contract["canonical_row_key"] == "ROW_ID"
        assert contract["parser_family"]
        assert contract["expected_file_patterns"]
        assert contract["fields"]
        assert not any(field["required_for_bronze"] for field in contract["fields"])
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
            assert column["required"] is False
            assert column["nullable"] is True
            assert column["lineage_required"] is False
            assert column["quarantine_if_invalid"] is False


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


def test_model_evolution_snapshots_are_complete_and_local_only() -> None:
    snapshots = sorted(path for path in EVOLUTION_ROOT.glob("V0_*") if path.is_dir())

    assert [path.name for path in snapshots] == ["V0_1", "V0_2"]

    for snapshot_dir in snapshots:
        snapshot = load_yaml(snapshot_dir / "model_snapshot.yaml")
        ddl_path = REPO_ROOT / snapshot["deployment_artifacts"]["postgres_full_ddl"]
        ddl = ddl_path.read_text(encoding="utf-8")
        ddl_upper = ddl.upper()

        assert snapshot["artifact"] == "model_evolution_snapshot"
        assert snapshot["snapshot_id"] == snapshot_dir.name
        assert snapshot["plan_id"] in {
            "04_5_local_data_workbench_and_drift_resolution_plan",
            "04_5_local_data_workbench_and_model_evolution_plan",
        }
        assert snapshot["modeling_scope"]["max_layer_count"] <= 4
        assert snapshot["ci_cd_contract"]["deploy_style"] == "full_snapshot_redeploy"
        assert snapshot["ci_cd_contract"]["compatibility_policy"] == (
            "no_backward_compatibility_required_for_plan_04_5"
        )
        assert snapshot["rollback"]["strategy"] == "redeploy_previous_complete_snapshot"
        assert (
            snapshot["normalization_iteration_rules"][
                "business_question_profiles_are_living_contracts"
            ]
            is True
        )
        assert snapshot["normalization_iteration_rules"]["patch_policy"] == (
            "no_manual_database_patches"
        )
        assert snapshot["guardrails"]["all_execution_local"] is True
        assert (
            snapshot["guardrails"]["no_gold_schema_without_resolved_business_questions"]
            is True
        )
        assert snapshot["iteration_packet_contract"]["status"] in {
            "planned_required_before_next_material_iteration",
            "complete",
        }

        bq_registry = snapshot["business_question_registry"]
        bq_path = REPO_ROOT / bq_registry["profile_path"]
        bq_profile = load_yaml(bq_path)
        bq_checksum = hashlib.sha256(bq_path.read_bytes()).hexdigest()

        assert bq_registry["version_id"] == f"BQ_{snapshot_dir.name}"
        assert bq_registry["profile_sha256"] == bq_checksum
        assert bq_registry["question_count"] == len(
            bq_profile["business_question_profiles"]
        )
        assert bq_registry["field_decision_count"] == len(bq_profile["field_decisions"])
        assert bq_registry["completion_status"] in {
            "plan_02_allowed_not_plan_04_5_complete",
            "plan_04_5_complete_sql_answered",
        }
        assert "tested local SQL outputs" in bq_registry["acceptance_rule"]

        declared_paths = [
            snapshot["source_contracts"]["bronze_contract"],
            snapshot["source_contracts"]["provider_to_silver_matrix"],
            snapshot["source_contracts"]["business_question_profiles"],
            snapshot["business_question_registry"]["profile_path"],
            snapshot["runtime_contracts"]["local_postgres_workbench"],
            snapshot["runtime_contracts"]["local_runtime_profile"],
            snapshot["deployment_artifacts"]["postgres_full_ddl"],
            snapshot["deployment_artifacts"]["deploy_handler"],
            snapshot["deployment_artifacts"]["deploy_runbook"],
            snapshot["iteration_packet_contract"]["packet_path"],
            snapshot["iteration_packet_contract"]["business_question_registry_path"],
            snapshot["iteration_packet_contract"]["db_state_snapshot_path"],
            snapshot["iteration_packet_contract"]["dbt_artifacts_manifest_path"],
            snapshot["iteration_packet_contract"]["lineage_summary_path"],
            snapshot["iteration_packet_contract"]["qa_gate_summary_path"],
            snapshot["iteration_packet_contract"]["rollback_plan_path"],
            *snapshot["source_contracts"]["silver_contracts"],
        ]
        for declared_path in declared_paths:
            assert not Path(declared_path).is_absolute()
            assert (REPO_ROOT / declared_path).exists(), declared_path

        assert "CREATE SCHEMA IF NOT EXISTS" in ddl
        assert '"staging"' in ddl
        assert '"scratch"' in ddl
        assert '"review"' in ddl
        assert '"evidence"' in ddl
        assert '"scratch"."normalization_probe_runs"' in ddl
        assert '"review"."silver_members"' in ddl
        assert '"review"."hitl_decisions"' in ddl
        assert "DROP " not in ddl_upper
        assert "TRUNCATE " not in ddl_upper
        assert "DELETE " not in ddl_upper

        if snapshot_dir.name == "V0_2":
            assert snapshot["rollback"]["current_previous_snapshot"] == "V0_1"
            assert snapshot["dbt_contract"]["approved_adapter"] == "dbt-postgres"
            assert (
                snapshot["normalization_iteration_rules"]["terminal_sql_requirement"][
                    "status"
                ]
                == "satisfied"
            )


def test_model_evolution_iteration_packet_maps_required_feedback() -> None:
    snapshot_dir = EVOLUTION_ROOT / "V0_1"
    packet = load_yaml(snapshot_dir / "iteration_packet.yaml")
    bq_registry = load_yaml(snapshot_dir / "business_question_registry.yaml")
    db_state = load_yaml(snapshot_dir / "db_state_snapshot.yaml")
    dbt_manifest = load_yaml(snapshot_dir / "dbt_artifacts_manifest.yaml")
    lineage = load_yaml(snapshot_dir / "lineage_summary.yaml")
    qa_gate = load_yaml(snapshot_dir / "qa_gate_summary.yaml")
    rollback = load_yaml(snapshot_dir / "rollback_plan.yaml")

    assert packet["artifact"] == "model_iteration_packet"
    assert packet["iteration_id"] == "V0_1"
    assert packet["business_question_registry_version"] == "BQ_V0_1"
    assert packet["feedback_refs"] == {
        "database_feedback": "metadata/model_specs/evolution/V0_1/db_state_snapshot.yaml",
        "dbt_feedback": "metadata/model_specs/evolution/V0_1/dbt_artifacts_manifest.yaml",
        "lineage_feedback": "metadata/model_specs/evolution/V0_1/lineage_summary.yaml",
        "qa_feedback": "metadata/model_specs/evolution/V0_1/qa_gate_summary.yaml",
        "rollback_plan": "metadata/model_specs/evolution/V0_1/rollback_plan.yaml",
    }
    assert packet["normalization_probe_policy"]["default_action_for_strange_data"] == (
        "create_probe_before_semantic_issue"
    )
    assert packet["normalization_probe_policy"]["scratch_schema"] == "scratch"
    assert packet["normalization_probe_policy"]["probe_registry_table"] == (
        "scratch.normalization_probe_runs"
    )
    assert packet["advancement_gate"]["allowed_next_action"] == "continue_iteration"

    assert bq_registry["registry_version"] == "BQ_V0_1"
    assert bq_registry["question_count"] == 16
    assert bq_registry["field_decision_count"] == 205
    assert "tested local SQL output" in bq_registry["completion_rule"]

    assert "row_counts" in db_state["required_feedback"]
    assert "null_rates" in db_state["required_feedback"]
    assert "duplicate_keys" in db_state["required_feedback"]
    assert db_state["privacy_rule"] == (
        "Do not store raw PHI or PII values in this snapshot."
    )

    assert dbt_manifest["dbt_status"] == "not_introduced"
    assert "target/manifest.json" in dbt_manifest["required_artifacts_when_dbt_runs"]
    assert "target/run_results.json" in dbt_manifest["required_artifacts_when_dbt_runs"]
    assert "target/catalog.json" in dbt_manifest["required_artifacts_when_dbt_runs"]

    assert lineage["lineage_backend_status"]["openlineage"].startswith("pending_hitl")
    assert "input_datasets" in lineage["required_feedback_when_approved"]
    assert "output_datasets" in lineage["required_feedback_when_approved"]

    assert set(qa_gate["required_gate_families"]) >= {
        "unit",
        "integration",
        "regression",
        "e2e_local",
        "dbt",
        "sql_answer",
        "rollback",
    }
    assert rollback["rollback_strategy"] == "redeploy_previous_complete_snapshot"
    assert "weakening tests to preserve a broken iteration" in rollback["blocked_actions"]


def test_model_evolution_v0_2_answers_all_business_questions() -> None:
    snapshot_dir = EVOLUTION_ROOT / "V0_2"
    packet = load_yaml(snapshot_dir / "iteration_packet.yaml")
    registry = load_yaml(snapshot_dir / "business_question_registry.yaml")
    sql_evidence = load_yaml(snapshot_dir / "sql_answer_evidence.yaml")
    dbt_manifest = load_yaml(snapshot_dir / "dbt_artifacts_manifest.yaml")

    assert packet["status"] == "complete"
    assert packet["previous_iteration_id"] == "V0_1"
    assert packet["business_question_registry_version"] == "BQ_V0_2"
    assert packet["business_question_progress"]["partial"] == []
    assert packet["business_question_progress"]["unanswered"] == []
    assert packet["business_question_progress"]["deferred_hitl"] == []
    assert len(packet["business_question_progress"]["answered"]) == 16

    assert registry["registry_version"] == "BQ_V0_2"
    assert registry["status"] == "plan_04_5_complete_sql_answered"
    assert registry["question_count"] == 16
    assert registry["field_decision_count"] == 205
    assert len(registry["question_states"]) == 16
    assert all(item["status"] == "answered" for item in registry["question_states"])
    assert all(
        item["sql_output"].startswith("evidence.bq_")
        for item in registry["question_states"]
    )

    assert sql_evidence["artifact"] == "sql_answer_evidence"
    assert sql_evidence["iteration_id"] == "V0_2"
    assert dbt_manifest["approved_adapter"] == "dbt-postgres"
    assert dbt_manifest["project"] == "dbt/dbt_project.yml"
