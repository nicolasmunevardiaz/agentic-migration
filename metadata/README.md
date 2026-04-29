# Metadata Guide

`metadata/` is the specs-as-code layer. It describes source dialects, canonical models, mappings, runtime profiles, and future deployment specs. Code should consume these files instead of hardcoding provider or model decisions.

## What Is Here

- `provider_specs/`: source contracts from profiling. Each provider/entity YAML declares file type, parser profile, row key, source fields, PII flags, drift notes, and quarantine expectations. Parsers in `src/adapters/` consume these.
- `model_specs/bronze/`: Bronze preservation contract. Today this is validated by tests and governs lineage/source-preservation expectations; adapter runtime builds Bronze records through shared code.
- `model_specs/silver/`: executable canonical Silver contracts. `src/common/adapter_runtime.py` reads these YAMLs to decide Silver entities, columns, source mappings, types, and nullability.
- `model_specs/mappings/`: cross-provider reconciliation matrix. It is the audit table that proves provider fields and Silver columns agree; tests keep it aligned with `silver/*.yaml`.
- `model_specs/impact/`: modeling risks and business-question decision evidence.
- `model_specs/evolution/`: complete versioned model snapshots for Plan 04.5 local PostgreSQL/dbt iterations. Each `V0_N/` folder records the snapshot header, business-question registry version, full PostgreSQL DDL image, rollback target, quality gates, and blocked downstream scope.
- `runtime_specs/` and `deployment_specs/`: planned runtime/deployment contracts for local certification and Databricks rollout.

## Mini Example

```text
metadata/provider_specs/data_provider_2_bluestone_health/observations.yaml
  says OBS_JSON is at OBX.5 in BlueStone HL7 XML

metadata/model_specs/silver/observations.yaml
  says OBS_JSON maps to observation_payload_raw, height_cm, systolic_bp, etc.

src/common/adapter_runtime.py
  loads the Silver YAML and produces nullable canonical observation rows
```

## Rule Of Thumb

Provider specs explain how a source speaks. Silver specs define what the platform produces. The mapping matrix proves those two stories are consistent across providers.

Plan 04.5 model changes should be made through complete `model_specs/evolution/V0_N/` snapshots. If `business_question_profiles.yaml` changes, the active snapshot must record the matching `BQ_V0_N` version and checksum. Do not use ad hoc database patches as the durable model history.

## Validate This Layer

Use `uv`; do not call `python` or `pytest` directly.

```bash
uv run --no-sync pytest tests/specs
uv run --no-sync pytest tests/specs/test_model_specs.py tests/specs/test_provider_to_silver_matrix.py
uv run --no-sync ruff check tests/specs
```

Main test categories here are schema tests for YAML shape, integration tests across provider specs and model specs, reconciliation tests for the mapping matrix, regression tests for canonical drift, and scope-guard tests that block post-Silver behavior.
