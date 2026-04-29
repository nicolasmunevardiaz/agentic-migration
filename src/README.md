# Source Code Guide

`src/` contains the executable Raw/Bronze -> Silver adapter code. It is intentionally split so provider dialect parsing, canonical mapping, and orchestration do not get mixed together.

## What Is Here

- `src/adapters/`: provider-specific parsers. These read source files using `metadata/provider_specs/<provider>/<entity>.yaml`. They understand dialect details such as FHIR JSON, HL7 XML, X12-like text, CSV quirks, row keys, and source field paths.
- `src/common/`: shared runtime logic. `adapter_runtime.py` builds Bronze records, loads canonical Silver mappings from `metadata/model_specs/silver/*.yaml`, casts values, emits nullable Silver rows, quarantine records, and QA evidence.
- `src/handlers/`: orchestration entrypoints. A handler wires one provider parser to the shared adapter runtime and returns an `AdapterRunResult`.

## Inputs And Outputs

Input starts with a source file plus provider/model metadata:

```text
source file + metadata/provider_specs/<provider>/<entity>.yaml
        -> src/adapters/<provider>.py
        -> parsed values_by_header
        -> src/common/adapter_runtime.py + metadata/model_specs/silver/*.yaml
        -> BronzeRecord, Silver rows, QA evidence, quarantine records
```

Mini example:

```python
from pathlib import Path
from src.handlers.bluestone_adapter import run_bluestone_adapter_for_file

result = run_bluestone_adapter_for_file(
    entity="observations",
    source_file=Path("tests/fixtures/bluestone/observations_message.xml"),
    ingestion_run_id="local-test-run",
)
print(result.silver_rows["observations"][0])
```

## How To Read It

If you need to understand a provider dialect, start in `src/adapters/`. If you need to understand canonical Bronze/Silver behavior, start in `src/common/adapter_runtime.py`. If you need to run a provider end to end, start in `src/handlers/`.

## Validate This Layer

Use `uv`; do not call `python` or `pytest` directly.

```bash
uv run --no-sync pytest tests/adapters
uv run --no-sync pytest tests/adapters/test_bluestone_adapter_runtime.py
uv run --no-sync ruff check src tests/adapters
```

Main test categories here are unit data tests for parsers, integration tests for handler-to-runtime flows, regression tests for provider quirks, and data quality tests for warning/quarantine behavior.
