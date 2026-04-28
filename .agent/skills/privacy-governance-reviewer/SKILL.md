---
name: privacy-governance-reviewer
description: "Review healthcare privacy, PII/PHI classification, evidence redaction, secrets, dependency safety, Unity Catalog governance, permissions, and Human in the Loop approval requirements for migration specs and artifacts."
user-invocable: false
---

# Privacy Governance Reviewer

Use this skill when provider specs, model specs, adapter code, QA evidence, deployment specs, dependency changes, or PR plans touch sensitive healthcare data, identifiers, permissions, secrets, packages, or governed Databricks/Unity Catalog assets. This is a reviewer skill: it validates governance posture and approval requirements.

Respect the active plan focus. During provider discovery and profiling, review exactly one provider at a time and append trace entries to that provider's log. During canonical review, evaluate all provider specs together and append entries to the canonical review log.

Read provider specs, model specs, QA evidence contracts, local runtime specs, Databricks deployment specs, dependency manifests, lockfiles, PR risk reports, and any generated fixtures or examples. Confirm that PII/PHI fields are flagged, sensitive examples are redacted or synthetic, lineage and audit fields are present, Unity Catalog targets are governed when Databricks is in scope, permissions are explicit enough for review, and dependencies are justified and supportable.

Validate that secrets are not committed, local absolute paths are not embedded, QA evidence does not leak raw sensitive values, and approval records exist for PII classification, masking/redaction expectations, ambiguous identifiers, Silver required fields, quarantine rules, local runtime dependency installation, Docker/Marquez usage, OpenLineage transport, Databricks execution, and dependency risk exceptions.

## Dependency Safety

Review any new or changed package before approval. The package must have a clear migration purpose, come from an approved ecosystem source, use a maintained version, avoid end-of-life runtimes, and be represented in the lockfile when a lockfile exists. Prefer stable or LTS-supported versions over prerelease, abandoned, unmaintained, or obscure packages.

If dependency scanning is available, require evidence from the configured scanner before approving the change. Block or escalate packages with known critical or high vulnerabilities, suspicious maintainers, unclear licensing, dependency confusion risk, typosquatting risk, unpinned install instructions, or broad transitive dependency risk. If the package is necessary despite a warning, require Human in the Loop approval with risk, mitigation, and planned remediation.

Do not downgrade PII/PHI classification, approve semantic mappings, grant permissions, authorize cloud execution, start Docker services, install local runtime dependencies, or approve risky dependencies without evidence. Do not allow privacy, governance, or dependency risk decisions to be hidden inside adapter logic. Governance decisions must be visible in specs, QA evidence, Human in the Loop records, and concise append-only trace logs.

Return a concise report with privacy status, dependency risk status, impacted provider/entity/table, sensitive fields, package concerns, evidence issues, permission concerns, required approvals, blockers, and recommended next action.
