---
name: repo-governance-auditor
description: "Audit GitHub governance and PR safety before an agent prepares or creates a pull request, including branch discipline, evidence, tests, dependency safety, forbidden operations, secrets, workflows, Databricks/Terraform guardrails, and human approval requirements."
user-invocable: false
---

# Repo Governance Auditor

Use this skill whenever an agent is preparing a PR, asking to create a PR, reviewing PR readiness, or touching GitHub workflow behavior, branch strategy, secrets, Databricks, Terraform, deployment specs, or CI/CD controls. This is a blocking reviewer skill that decides whether PR creation is safe; it is not a merge, approval, or repository-admin skill.

Read the Technical PRD, `docs/agentops_filesystem_conventions.md`, active plan docs, changed files, available test evidence, HITL records, and trace logs. If GitHub workflow or PR template files exist, review them; if they do not exist, do not create them unless the user explicitly asks.

## Checks

Validate branch discipline, PR evidence, workflow permissions, `uv` usage, dependency cache expectations, dependency safety evidence, forbidden commands, secrets handling, Databricks/Terraform guardrails, protected-branch assumptions, test evidence, and whether the active plan allows the requested change.

The only long-lived branches are `main`, `testing`, and `develop`. Agent branches are temporary work branches and must be scoped, for example `agentops/<plan-id>/<provider-or-scope>` or `governance/<scope>`, when branch creation is explicitly authorized. Agent-created PRs must target `main`; `develop` and `testing` are not valid default PR targets for agent work. If a PR targets anything other than `main`, require an explicit Human in the Loop exception recorded in the PR evidence and return a blocked status unless that exception exists.

Temporary agent branches must have a deletion plan in the PR evidence. After PR approval and merge, or explicit human closure, the temporary head branch must be deleted locally and remotely. This skill may verify and report branch cleanup requirements, but it must not delete branches itself.

PR evidence must include plan id, provider or `all`, skills used, base branch, head branch, branch deletion plan, files changed, tests run, evidence paths, dependency changes, risks, HITL decisions, Databricks impact, and rollback notes. An agent must not claim tests passed or dependency safety without a command transcript, CI check, scanner output, or evidence path. If evidence is complete and the base branch is `main`, this skill may return `allowed_next_action: create_pr`.

## Non-Negotiables

Do not approve PRs, merge PRs, delete branches, change GitHub settings, change branch protections, change secrets, run `gh` commands that mutate repository configuration, run Databricks jobs, apply Terraform, deploy Databricks Asset Bundles, authorize production-impacting actions, or bypass Human in the Loop.

Safe `gh` usage is limited to authentication/status inspection, PR creation after this skill returns `allowed_next_action: create_pr`, PR viewing, PR checks, and CI run inspection. Do not expose `gh` for repository settings, secrets, branch protections, environments, rulesets, project mutation, approvals, or merges. Do not allow broad workflow permissions without explicit human approval. Do not allow direct changes to Databricks or Terraform execution paths from a PR without approval. Do not allow new dependencies with known critical or high vulnerabilities unless a human explicitly approves the exception. Do not allow PR readiness to depend only on agent self-report.

## Output Format

Return a concise report in the chat or active review artifact with governance status, dependency risk status, blocked items, policy violations, missing evidence, risky files, required human approvals, and allowed next action. Keep findings short and technical.
