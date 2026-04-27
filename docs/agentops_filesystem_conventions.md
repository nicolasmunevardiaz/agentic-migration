# AgentOps Filesystem Conventions

## Purpose

This repository uses one shared filesystem contract for all AgentOps plans and Codex iterations. Agents must not create private folder structures, duplicate conventions, or invent new output roots unless a human explicitly approves the change. Plans orchestrate work; skills provide reusable judgment; all generated artifacts must land in the global structure below.

## Global Structure

```text
.agent/
  skills/
  spec_templates/
data_500k/
docs/
metadata/
  provider_specs/
  model_specs/
    bronze/
    silver/
    mappings/
    impact/
  deployment_specs/
    databricks/
reports/
  drift/
  hitl/
  privacy/
  qa/
logs/
  provider_discovery/
  canonical_model/
  adapter_implementation/
  databricks_rollout/
src/
  adapters/
  common/
  handlers/
tests/
  adapters/
  fixtures/
  specs/
artifacts/
```

## Ownership

`metadata/` contains versioned declarative contracts. Provider specs, model specs, mapping matrices, and deployment specs should be committed when they are reviewable. `reports/` contains versioned human-readable evidence such as drift summaries, HITL queues, QA summaries, privacy reviews, and risk reports. `logs/` contains concise append-only technical trace logs. `src/` contains implementation code only after the relevant specs and approvals exist. `tests/` contains deterministic Python tests and fixtures. `artifacts/` is for local or CI runtime outputs and is ignored by Git except for `.gitkeep`.

## Trace Logs

Trace logs are mandatory for AgentOps work. Logs must be short, technical, and append-only. Agents must append new entries; they must not purge, delete, reorder, or rewrite existing log entries. If an entry is wrong, append a correction entry.

Use one line per event. Each line should follow this shape:

```text
YYYY-MM-DDTHH:MM:SS-05:00 | plan=<plan_id> | provider=<provider_slug|all> | skill=<skill_name> | event=<started|read|generated|validated|blocked|completed> | artifact=<path|none> | note=<short technical note>
```

Discovery and provider profiling must work on exactly one provider at a time. The log file must be `logs/provider_discovery/<provider_slug>.md`. Canonical model review is the first phase that may read all providers together; its log file must be `logs/canonical_model/canonical_review.md` and should use `provider=all` unless a note concerns one provider specifically. Adapter work should log to `logs/adapter_implementation/<provider_slug>.md`. Databricks rollout planning should log to `logs/databricks_rollout/rollout_readiness.md`.

Logs are not long-form reports. Keep notes under one sentence, avoid prose, and link to artifacts instead of repeating their content.

## Python Layout

Shared functions must live under `src/common/`. Handler modules must live under `src/handlers/` and should coordinate orchestration without hiding parsing, validation, file IO, or report generation. Provider-specific adapter code must live under `src/adapters/`. Tests must mirror responsibilities: spec validation in `tests/specs/`, adapter behavior in `tests/adapters/`, and sample inputs or expected outputs in `tests/fixtures/`.

Python must be English-only and executed through `uv`. Use `uv run pytest`, `uv run ruff check`, and `uv run python -m <module>`. Do not use direct `python3`. Function names should self-document behavior. One-line docstrings are allowed only when they add useful intent. Avoid classes unless they clarify domain values; when needed, use `@dataclass`.

## Git Conventions

Empty required directories are kept with `.gitkeep`. Runtime outputs, caches, local environments, Databricks local state, logs, and temporary files are ignored through `.gitignore`. Do not commit secrets, `.env` files, raw sensitive examples, local absolute paths, or generated runtime artifacts from `artifacts/`.

## Agent Permissions

By default, an agent may read repository files, create or update files inside the approved structure, and run local validation with `uv`. An agent must ask for human approval before installing dependencies, using network access, creating cloud resources, applying Terraform, deploying Databricks Asset Bundles, running Databricks jobs, changing GitHub secrets, or executing production-impacting operations.

Multiple agents may work in parallel only when their write scopes are separated. During discovery and provider profiling, parallelism must be provider-isolated and each agent must own exactly one provider. Two agents must not edit the same provider spec, provider log, report, or test file at the same time. Canonical model review is intentionally generalist and may read all provider specs together. Agent handoffs must happen through committed or reviewable files in `metadata/`, `reports/`, `logs/`, `src/`, and `tests/`, not through private local folders.
