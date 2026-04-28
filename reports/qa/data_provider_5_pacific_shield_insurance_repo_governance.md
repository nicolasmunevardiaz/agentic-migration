# Pacific Shield Insurance Repo Governance Audit

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_5_pacific_shield_insurance`
status: allowed

base_branch: `main`
head_branch: `agentops/01-provider-discovery/pacific-shield`
temporary_branch_deletion_plan: Delete local and remote head branch after PR approval and merge, or after explicit human closure.

## PR Evidence Requirements

- Plan id: `01_provider_discovery_and_specs_plan`
- Provider: `data_provider_5_pacific_shield_insurance`
- Skills used: `provider-spec-generator`, `privacy-governance-reviewer`, `spec-test-generator`, `hitl-escalation-controller`, `repo-governance-auditor`
- Tests run: `uv run pytest tests/specs/test_provider_specs.py`; `uv run pytest tests/adapters`; `uv run pytest`; `uv run ruff check`
- Evidence paths: drift, privacy, HITL, provider QA, repo governance, trace log
- Dependency changes: none
- Databricks impact: none authorized
- Terraform or cloud impact: none authorized
- Rollback notes: revert Pacific Shield metadata, parser, fixtures, tests, reports, and trace log entries from this branch before merge if needed.

## Governance Status

Repo governance audit found complete PR evidence, no dependency changes, no Databricks or Terraform execution, and a scoped temporary branch targeting `main`.

allowed_next_action: `create_pr`
