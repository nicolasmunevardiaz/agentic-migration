---
name: databricks-rollout-planner
description: "Plan governed Databricks and Unity Catalog rollout for approved Bronze/Silver model specs, quarantine outputs, QA evidence, lineage, permissions, and validation runs."
user-invocable: false
---

# Databricks Rollout Planner

Use this skill when planning Databricks execution, Unity Catalog registration, governed storage locations, validation jobs, or metadata-driven Bronze/Silver implementation. This is a rollout planner skill: it translates approved model, adapter, and QA contracts into a governed Databricks execution plan.

Validate that Databricks is used as the runtime for real data execution and validation after GitHub/Codex checks and human approval. Confirm that Bronze, Silver, quarantine, manifests, YAML specs, and QA evidence have governed locations and can be traced by provider, entity, source file, checksum, row reference, ingestion run, schema version, spec version, and adapter version.

Do not authorize cloud resource creation, production deployment, or direct execution against full-volume data without approval. Do not bypass GitHub PR review or Human in the Loop gates.

Return a concise report with readiness status, Unity Catalog gaps, Databricks validation prerequisites, lineage expectations, permission concerns, and recommended next action.
