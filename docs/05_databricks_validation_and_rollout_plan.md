# Databricks Validation And Rollout Plan

## Status

This plan exists to preserve the repository governance contract, but it is not the active delivery path for the current repository shape.

The active, approved path for this repository is:

```text
data_500k -> adapters/contracts -> PostgreSQL landing.*
```

Anything after `landing.*` belongs to the separate dbt repository.

## Goal

Describe the future, approval-gated path for Databricks validation only after:

1. Local PostgreSQL `landing.*` provisioning is stable.
2. Adapter and contract tests pass.
3. Human approval exists for any Databricks-specific execution.

## Current Boundary

This repository must not use this plan to:

- move the active source-of-truth away from `landing.*`
- reintroduce `review.silver_*` as the dbt source boundary
- create durable post-landing analytical schemas in this repository
- run Databricks jobs, apply Terraform, deploy bundles, or create cloud resources without explicit approval

## Relationship To The Active Flow

The only approved handoff is:

```text
agentic-migration
    ->
PostgreSQL landing.*
    ->
../slalom dbt source('landing', ...)
```

If Databricks validation is ever resumed, it must consume approved contracts and approved local evidence after the `landing` load is already governed and stable.

## Definition Of Ready

Databricks planning should remain blocked until all of the following are true:

- local runtime certification remains green
- `landing.*` is the stable source boundary
- dbt consumption from `landing.*` is documented and validated
- required approvals for cloud execution exist

## Definition Of Done

This plan is complete when it remains available as a governance checkpoint and future planning reference without changing the current repository boundary: this repository stops at `landing.*`.
