# data_500k Adapter Load Audit

plan_id: `03_adapter_implementation_and_ci_plan`
scope: `data_500k adapter runtime evidence only`

## Contract

`artifacts/qa/data_500k_adapter_load_audit.jsonl` is the file-level source of truth for local `data_500k` adapter load evidence. It is JSONL, not one large JSON document, so each provider/entity/source file writes one independent JSON record.

The audit is programmatic and reusable. Adapter implementations register runnable provider targets in `src.handlers.data_500k_adapter_audit`; the default command audits every registered target, every default entity, and every source file matching provider spec patterns. Provider-filtered runs are useful for diagnosis, but they do not replace the complete all-target audit required for integration evidence.

## Where The Error Logs Live

The persistent local runtime logs are generated under `artifacts/qa/`:

- `artifacts/qa/data_500k_adapter_load_audit.jsonl`: one JSON record per provider/entity/source file.
- `artifacts/qa/data_500k_adapter_load_audit.md`: compact summary of failures and skips.

These files are intentionally ignored by Git because they are local runtime outputs. They do not copy raw `data_500k` payload values.

## Command

Run:

```bash
uv run --no-sync python -m src.handlers.data_500k_adapter_audit
```

To stamp another plan id into the same reusable audit format:

```bash
uv run --no-sync python -m src.handlers.data_500k_adapter_audit --plan-id 04_local_runtime_and_contract_certification_plan
```

To diagnose only one provider:

```bash
uv run --no-sync python -m src.handlers.data_500k_adapter_audit --provider data_provider_1_aegis_care_network
uv run --no-sync python -m src.handlers.data_500k_adapter_audit --provider data_provider_2_bluestone_health
```

Provider-filtered output is not complete integration evidence; the unfiltered command is the required all-target run.

## Evidence Fields

Each JSONL record includes provider, entity, source file, source checksum, status, decision, error type, message, Bronze record count, Silver entities, Silver row count, quarantine count, QA evidence count, QA decisions, and evidence path.

Allowed skip behavior is only `skip_dataset_absent` when the whole local provider dataset is missing. If `data_500k/<provider>/year=2025/` exists, missing matching files or parser/load errors are `failed` records.
