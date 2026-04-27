# Aegis Care Network Repo Governance Audit

Provider: `data_provider_1_aegis_care_network`
Plan: `01_provider_discovery_and_specs_plan`
Branch: `agentops/01-provider-discovery/aegis`
Target branch: `develop`

## Governance Status

Status: `allowed`
Allowed next action: `create_pr`

## Evidence

- Provider specs: `metadata/provider_specs/data_provider_1_aegis_care_network/`
- Drift report: `reports/drift/data_provider_1_aegis_care_network.md`
- Privacy and dependency review: `reports/privacy/data_provider_1_aegis_care_network.md`
- HITL queue: `reports/hitl/data_provider_1_aegis_care_network.md`
- QA report: `reports/qa/data_provider_1_aegis_care_network_provider_specs.md`
- Trace log: `logs/provider_discovery/data_provider_1_aegis_care_network.md`

## Tests

- `uv run pytest tests/specs/test_provider_specs.py`: 9 passed.
- `uv run pytest tests/adapters/test_aegis_care_network_parser.py`: 3 passed.
- `uv run pytest`: 15 passed.
- `uv run ruff check`: passed.

## Checks

- Branch follows `agentops/<plan-id>/<provider-or-scope>` convention.
- Scope is limited to Aegis provider discovery artifacts, specialized Aegis parser, provider and adapter tests, and approved `PyYAML` dependency update.
- No Databricks, Terraform, GitHub settings, secrets, PR approval, or merge actions were performed.
- `data_500k/` remains untracked and source values are not copied into reports or specs.
- HITL decisions are recorded and adapter readiness remains blocked pending human review.

## Blockers

- No blocker for PR creation.
- Adapter implementation remains blocked by HITL decisions in `reports/hitl/data_provider_1_aegis_care_network.md`.
