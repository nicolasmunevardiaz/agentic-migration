# Logs Guide

`logs/` contains concise append-only AgentOps trace lines. Logs are for chronology and accountability, not long explanations. Detailed evidence belongs in `reports/`.

## What Is Here

- `provider_discovery/`: one log per provider during source profiling.
- `canonical_model/`: cross-provider canonical modeling and decision application.
- `adapter_implementation/`: one log per provider during Plan 03 adapter work.
- `local_runtime/`: local runtime certification traces.
- `databricks_rollout/`: Databricks rollout planning traces.

## Log Shape

Each entry should stay one line:

```text
YYYY-MM-DDTHH:MM:SS-05:00 | plan=<plan_id> | provider=<slug|all> | skill=<skill> | event=<event> | artifact=<path|none> | note=<short note>
```

Mini example:

```text
2026-04-29T07:38:04-05:00 | plan=03_adapter_implementation_and_ci_plan | provider=data_provider_2_bluestone_health | skill=adapter-code-generator | event=generated | artifact=src/handlers/bluestone_adapter.py | note=Runtime-neutral BlueStone handler maps provider records through canonical model specs.
```

## Rules

Append only. Do not reorder, rewrite, or delete past entries. If something was wrong, add a correction line. Use logs to point at artifacts; use reports to explain evidence.
