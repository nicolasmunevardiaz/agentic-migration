# NorthCare Clinics Repo Governance Audit

plan_id: `01_provider_discovery_and_specs_plan`
provider: `data_provider_3_northcare_clinics`
status: passed
allowed_next_action: create_pr

## Branch Discipline

- Base branch: `main`.
- Head branch: `agentops-01-provider-discovery-northcare-clinics`.
- Requested scoped branch with slashes could not be created under local sandboxed git refs, so a hyphenated temporary branch was used.
- Branch deletion plan: delete the temporary local and remote head branch after PR approval and merge or explicit human closure.

## Evidence Reviewed

- Provider specs: `metadata/provider_specs/data_provider_3_northcare_clinics/`.
- Parser: `src/adapters/northcare_clinics.py`.
- Fixtures: `tests/fixtures/northcare/`.
- Parser tests: `tests/adapters/test_northcare_clinics_parser.py`.
- Drift report: `reports/drift/data_provider_3_northcare_clinics.md`.
- Privacy report: `reports/privacy/data_provider_3_northcare_clinics.md`.
- HITL queue: `reports/hitl/data_provider_3_northcare_clinics.md`.
- QA evidence: `reports/qa/data_provider_3_northcare_clinics_provider_specs.md`.

## Test Evidence

- `uv run pytest tests/specs/test_provider_specs.py`: passed, 9 tests.
- `uv run pytest tests/adapters/test_northcare_clinics_parser.py`: passed, 14 tests.
- `uv run pytest tests/adapters`: passed, 28 tests.
- `uv run pytest`: passed, 49 tests.
- `uv run ruff check`: passed.

## Findings

- Dependency risk status: pass; no new dependencies or lockfile changes.
- Secret handling: pass; no secrets, credentials, or local absolute paths added.
- Raw data handling: pass; fixtures are synthetic and raw `data_500k/` files remain untracked.
- Databricks/Terraform guardrail: pass; no cloud, Databricks, Terraform, deployment, or production-impacting action was performed.
- HITL status: non-blocking queue exists for PII/PHI, relationship hints, observation payload handling, medication price handling, and parser-profile drift.

## Required PR Evidence

The PR body must include plan id, provider, skills used, base branch, head branch, branch deletion plan, files changed, tests run, evidence paths, risks, HITL decisions, Databricks impact, and rollback notes.
