---
name: databricks-rollout-planner
description: "Plan governed Databricks and Unity Catalog rollout for approved Bronze/Silver model specs, local runtime certification evidence, quarantine outputs, QA evidence, lineage, permissions, and validation runs."
user-invocable: false
---

# Databricks Rollout Planner

Use this skill when planning Databricks execution, Unity Catalog registration, governed storage locations, validation jobs, or metadata-driven Bronze/Silver implementation after local runtime certification exists. This is a rollout planner skill: it translates approved model, adapter, local certification, and QA contracts into a governed Databricks execution plan.

Validate that Databricks is used as the target runtime for representative data execution and validation after local runtime certification, GitHub/Codex checks, and human approval. Confirm that Bronze, Silver, quarantine, manifests, YAML specs, local certification evidence, and QA evidence have governed locations and can be traced by provider, entity, source file, checksum, row reference, ingestion run, schema version, spec version, and adapter version.

Confirm that Databricks deployment specs consume runtime-neutral contracts and approved local certification outputs instead of redefining provider parsing, canonical modeling, or Silver semantics. Treat Lakeflow, Unity Catalog, Databricks Asset Bundles, and Databricks Runtime behavior as target-runtime certification concerns.

Do not authorize cloud resource creation, production deployment, bundle deployment, or direct execution against full-volume data without approval. Do not use Databricks as the first place to discover basic parser, schema, mapping, quarantine, or local lineage-shape errors. Do not bypass GitHub PR review or Human in the Loop gates.

Return a concise report with readiness status, Unity Catalog gaps, Databricks validation prerequisites, lineage expectations, permission concerns, and recommended next action.
