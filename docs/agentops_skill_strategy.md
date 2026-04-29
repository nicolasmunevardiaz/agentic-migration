# AgentOps Skill Strategy

## Purpose

This document defines the first skill set for the Raw/Bronze -> Silver agentic migration. Skills are reusable Markdown instructions stored as `.agent/skills/<skill-name>/SKILL.md`. A skill teaches Codex how to apply domain rules repeatedly; a prompt or plan tells Codex what to do in one execution.

The design borrows the responsibility split from Agentic-Medallion: Planner Agent, Code Generator Agent, Code Reviewer Agent, Executor Agent, and a self-correction loop. We do not copy the notebook-centric implementation. We translate the pattern into enterprise-friendly AgentOps skills, declarative provider specs, GitHub PR gates, local runtime certification, and Databricks/Unity Catalog validation.

## Agentic-Medallion Contrast

Agentic-Medallion is useful because it separates planning, code generation, review, and execution, and because its HITL path creates GitHub PRs before deployment. Its limitation for this migration is that it is more POC than operating model: notebook-heavy, weak package boundaries, limited IaC, and no strong Unity Catalog lineage contract. Our strategy keeps the role separation but makes specs-as-code the center of gravity.

| Agentic-Medallion Role | Our Interpretation | Primary Skill |
|---|---|---|
| Planner Agent | Creates provider/entity YAML specs, resolves drift decisions, canonical model intent, migration risks, and HITL questions | `provider-spec-generator`, `drift-decision-resolver`, `canonical-model-planner` |
| Code Generator Agent | Generates parsers, adapters, fixtures, runtime contracts, and spec tests from approved contracts | `adapter-code-generator`, `local-runtime-harness-planner`, `spec-test-generator` |
| Code Reviewer Agent | Reviews adapter contracts, QA evidence, privacy, dependency safety, lineage, quarantine, scope control, PR governance readiness, and escalation boundaries | `adapter-contract-reviewer`, `qa-evidence-reviewer`, `privacy-governance-reviewer`, `repo-governance-auditor`, `hitl-escalation-controller` |
| Executor Agent | Plans approved local runtime certification and Databricks validation against governed targets | `local-runtime-harness-planner`, `databricks-rollout-planner` |

## Skill Set

The first skill set should remain small, but each skill must have a concrete output. The highest-risk skill is `provider-spec-generator`; it must not stop at a report or YAML-only output. Its DoD is a set of YAML provider/entity specs plus a provider-specialized parser, parser fixtures, and parser tests that can later drive adapter implementation.

Skill names should describe the operating responsibility, not the data layer. Use `generator` when the skill creates a declared artifact, `planner` when it designs a target contract or rollout, and `reviewer` when it validates readiness or evidence. Avoid names like `raw`, `bronze`, or `silver` as the primary identity because they hide what the skill actually does.

| Skill | Purpose | Primary Inputs | Required Output |
|---|---|---|---|
| `provider-spec-generator` | Expert parsing and source profiling skill that reads provider folders and `column_dictionary.md`, detects file/entity structure, standardizes metadata, emits declarative YAML specs, and creates the provider-specialized parser | Provider folders, `column_dictionary.md`, raw file paths, topology PRD | `metadata/provider_specs/<provider_slug>/<entity>.yaml`, `src/adapters/<provider_parser>.py`, parser fixtures, parser tests, provider drift summary, human-review questions |
| `drift-decision-resolver` | Resolves provider drift before canonical modeling by reviewing reports globally, preparing HITL-ready decisions, maintaining the canonical drift decision runbook, and verifying approved decisions are applied | Drift reports, privacy reports, HITL queues, QA reports, provider specs, discovery logs | `reports/hitl/canonical_drift_decision_runbook.md`, applied decision evidence, blockers for unresolved decisions |
| `canonical-model-planner` | Converts provider YAML specs into canonical Bronze/Silver model specs, provider-to-Silver mapping matrices, and modeling impact reports | Provider YAML specs, topology PRD, governance requirements | `metadata/model_specs/bronze/bronze_contract.yaml`, `metadata/model_specs/silver/<entity>.yaml`, `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`, modeling risk report |
| `business-question-profiler` | Reverse-engineers minimum canonical concepts from business questions after provider discovery, proposes provider/entity/field-level solution options with risk/impact, and reduces HITL ambiguity before canonical modeling | `business-request.md`, `.agent/spec_templates/business_question_profile.template.yaml`, provider specs, drift reports, privacy reports, HITL runbooks, QA evidence | `metadata/model_specs/impact/business_question_profiles.yaml`, field-level HITL decision requests, canonical modeling inputs |
| `adapter-contract-reviewer` | Validates adapter design, parser selection, mapping confidence, Bronze contract, Silver contract, lineage, and quarantine | Provider YAML specs, model YAML specs, adapter plan, topology document | Adapter readiness report |
| `adapter-code-generator` | Generates parser/adapter implementation, fixtures, and local tests from approved provider and model specs | Provider YAML specs, model YAML specs, mapping matrix, adapter readiness report | Parser/adapter code, fixtures, implementation tests, generation report |
| `local-runtime-harness-planner` | Defines the cloud-agnostic local runtime profile, runtime adapter interface, QA evidence contract, lineage evidence shape, and dependency approval gates before Databricks rollout | Provider specs, model specs, adapter artifacts, QA evidence, privacy findings, HITL approvals | `metadata/runtime_specs/local/*.yaml`, local runtime certification report, dependency review, runtime validation tests |
| `local-postgres-dbt-modeling-orchestrator` | Operates Plan 04.5 local PostgreSQL and dbt Core model iterations as idempotent CI/CD-style deployments with full model snapshots, rollback, HITL drift write-back, and robust local tests | Bronze contract, Silver specs, provider specs, provider-to-Silver matrix, business-question profiles, local runtime specs, PostgreSQL deploy runbook, local test evidence | `metadata/model_specs/evolution/V0_N/*`, PostgreSQL DDL snapshots, dbt readiness artifacts when approved, local deploy/test evidence, trace entries |
| `qa-evidence-reviewer` | Validates QA families, evidence contract, decisions, rerun behavior, and feedback loop completeness | QA plan, test outputs, evidence files | QA feedback report |
| `spec-test-generator` | Generates Python validators and tests for declarative specs before Databricks execution | PRD test strategy, spec templates, provider/model/deployment specs | `tests/specs/*.py`, validators, spec test report |
| `privacy-governance-reviewer` | Reviews PII/PHI classification, evidence redaction, secrets, dependency safety, permissions, Unity Catalog governance, and approval requirements | Provider specs, model specs, QA evidence, dependency manifests, deployment specs, PR risk report | Privacy/governance/dependency review report |
| `repo-governance-auditor` | Reviews GitHub governance and PR safety before an agent prepares or creates a pull request | Active plan, changed files, test evidence, dependency evidence, HITL records, workflow changes, branch context | Governance readiness findings |
| `hitl-escalation-controller` | Stops uncontrolled iteration and asks for a precise human decision when repeated failures, missing evidence, ambiguous semantics, or scope drift block safe progress | Active plan, trace logs, changed files, test output, reports, HITL records | Concise escalation packet and blocked next action |
| `databricks-rollout-planner` | Validates Databricks execution plan, governed locations, Unity Catalog target design, lineage, permissions, and deployment readiness after local certification | Model YAML specs, adapter readiness, local runtime certification, Databricks specs, UC target plan | Databricks/UC readiness report |

## Raw Discovery YAML Contract

The source specs and provider parser produced by `provider-spec-generator` are the bridge between messy provider exports and scalable adapters. They should be generated per provider/entity, not handwritten ad hoc. Each YAML must include provider identity, source type, upload partition, declared filetype, extension, entity, expected file patterns, parser profile, stable row key, canonical mappings, inferred data types when available, PII flags, relationship hints, known drift, quarantine rules, QA expectations, and `needs_human_review` reasons. The parser must consume those YAML specs and prove that the source profile is executable against fixtures and, when available, sampled local source files.

The five current provider dictionaries already show why this matters. Aegis uses `SRC_ROW`, BlueStone uses `LINE_ID`, NorthCare uses `EXPORT_ID`, ValleyBridge uses `DW_LOAD_SEQ`, and Pacific Shield uses `CLM_SEQ` as the source row key. Filetypes also differ: FHIR-like JSON, HL7 XML, X12-style TXT, and CSV. These differences should become declarative YAML metadata, not hardcoded adapter behavior.

## Declarative Modeling Contract

Provider YAML specs are source contracts, not target model contracts. After provider discovery and before `canonical-model-planner`, `business-question-profiler` must read `business-request.md` and the provider specs/reports to map business questions to decision purpose, grain, provider-specific source language, source evidence, minimum canonical concepts, risk, HITL decisions, solution options, and future Gold candidates. It must also create a provider/entity/field decision matrix so every business-critical source field has a recommended option, alternatives, risk/impact, HITL request, and explicit Plan 02 allowance. Then `drift-decision-resolver` must close or explicitly defer blocking drift decisions in `reports/hitl/canonical_drift_decision_runbook.md`. This prevents canonical modeling from treating scattered discovery findings or analytics wishes as resolved decisions. After that gate, the canonical model layer groups all provider fields by canonical concept, defines Bronze metadata, defines Silver entities, declares required fields and types, records relationship confidence, and produces a provider-to-Silver mapping matrix. It also produces an impact report that explains risks, drift, missing providers, PII exposure, unsafe casts, and HITL decisions.

The output model specs become the input to adapter generation, local runtime certification, and Databricks deployment specs. This prevents each provider dialect or runtime target from shaping the enterprise model by accident.

## Local Runtime Certification Contract

Adapter code must target runtime-neutral interfaces before Databricks rollout. The local runtime harness should validate provider parser output, Bronze preservation, canonical mapping, Silver shape, quarantine records, QA evidence, and lineage evidence using deterministic fixtures and approved local samples. Spark Declarative Pipelines, Delta Lake OSS, OpenLineage, and Marquez are candidate local validation tools, but they must remain HITL-gated dependencies until approved.

Local certification is not Databricks parity. It must not claim to validate Unity Catalog permissions, Lakeflow managed orchestration, Auto CDC behavior, serverless behavior, production performance, cloud IAM, or exact Databricks event logs. Its job is to make the agentic loop fast, cheap, portable, and contract-driven before Databricks certification.

## Local Model Evolution Contract

Plan 04.5 uses `local-postgres-dbt-modeling-orchestrator` after Plan 04 local runtime certification. Its center of gravity is PostgreSQL plus terminal-run QA, with dbt Core used as the preferred local orchestration and test tool after its project layout and profile are approved. The metadata contracts remain primary: dbt must not become an alternate source of truth.

Every material model iteration must create a full snapshot under `metadata/model_specs/evolution/V0_N/`, including a header file, business-question registry version, and versioned PostgreSQL DDL. Plan 04.5 does not maintain backward compatibility by default; rollback means redeploying the previous approved complete snapshot. The skill must update `business_question_profiles.yaml` whenever normalization changes business meaning, version that update as `BQ_V0_N`, and use review/HITL tables rather than private notes for drift decisions. Plan 04.5 is complete only when every business question has tested local SQL output or an explicit HITL-approved deferral.

## Declarative Spec Validation

GitHub CI should validate specs before Databricks execution. Python validators should parse every YAML, check required sections, enforce provider/entity coverage, verify that source mappings reference real provider specs, validate that Silver columns have types and lineage, detect duplicate canonical mappings, detect missing PII flags, reject absolute paths, and ensure deployment specs only reference approved model specs.

Each skill should also name the Python test family that protects its output. `provider-spec-generator` is protected primarily by schema tests, unit data tests, integration tests, reconciliation tests, regression tests, data quality tests over provider specs, and parser behavior tests over provider fixtures. `business-question-profiler` is protected by schema and governance tests over business question profiles, field-level decision records, HITL decision request shape, mapping completeness from question to provider to entity to field to candidate canonical concept, risk classification, HITL requirements, option risk/impact coverage, PII/PHI exposure rules, selected-option consistency, Plan 02 allowance, and deferred Gold candidates. `drift-decision-resolver` is protected by governance and schema checks over the canonical drift decision runbook, required evidence paths, blocking status values, and plan 02 readiness gates. `canonical-model-planner` is protected by schema tests, integration tests, reconciliation tests, and regression tests over model specs and the provider-to-Silver matrix. `adapter-contract-reviewer` and `adapter-code-generator` are protected by unit data tests, integration tests, schema tests, and regression tests over adapter fixtures and provider parser reuse. `local-runtime-harness-planner` is protected by runtime spec schema tests, local profile scope guards, dependency approval checks, lineage evidence shape tests, and QA evidence separation checks. `spec-test-generator` is protected by meta-tests that prove validators fail on invalid fixtures and pass on valid fixtures. `qa-evidence-reviewer` is protected by schema tests and integration tests over QA evidence specs. `privacy-governance-reviewer` is protected by security tests, schema tests, dependency safety checks, and regression tests over privacy flags, redaction rules, secrets checks, package risk, and approval records. `repo-governance-auditor` is protected by governance checks over PR evidence, forbidden operations, workflow permissions, secret handling, dependency evidence, branch discipline, and test evidence. `hitl-escalation-controller` is protected by escalation checks over repeated failures, missing evidence, ambiguous decisions, scope drift, and blocked next actions. `databricks-rollout-planner` is protected by schema tests, integration tests, security tests, and regression tests over deployment specs that reference approved local certification evidence. Business rule tests are scope guards only in this phase: they ensure post-Silver rules do not silently enter Bronze/Silver specs.

## Skill Design Standard

Each skill must include frontmatter with `name`, `description`, and `user-invocable`. The body must include purpose, when to use it, required inputs, required outputs, checks, non-negotiables, DoD, QA expectations, and output format. The checks should use descriptive behavior names, not rule IDs. Every skill output should identify status, impacted provider/entity, evidence path, human decisions required, and recommended next action.

Every skill must follow `docs/agentops_filesystem_conventions.md`. Skills may create or update files only inside the approved global structure for their responsibility. They must not create private agent workspaces, alternate metadata roots, duplicated test folders, or hidden handoff locations.

Every skill must also respect the active plan focus and trace logging rules. During discovery and provider profiling, the active agent is a provider specialist and must work on one provider only, appending concise entries to `logs/provider_discovery/<provider_slug>.md`. During canonical modeling, the active agent becomes a generalist reviewer across providers and appends entries to `logs/canonical_model/canonical_review.md`. Before any PR preparation or creation, the agent must use `repo-governance-auditor` to check PR evidence, forbidden operations, tests, branch discipline, and HITL requirements. If an agent reaches repeated failures, missing evidence, ambiguous semantics, or scope drift, it must use `hitl-escalation-controller` and stop until a human decision or explicit unblock exists. Logs are append-only and must not be purged, deleted, reordered, or rewritten.

## Relationship To Plans

The prompts in `agentic_migration_prompts/` are plan-like work orders. They should invoke these skills by responsibility. `02_raw_discovery_and_schema.md` should use `provider-spec-generator` to produce provider YAML specs. `03_bronze_silver_contracts.md` should use `drift-decision-resolver` first to close blocking drift decisions, then `canonical-model-planner` to create canonical model specs. `01_adapter_topology_planning.md` should use `adapter-contract-reviewer` once model specs exist and `adapter-code-generator` after approval. Local runtime certification should use `local-runtime-harness-planner`, `qa-evidence-reviewer`, `privacy-governance-reviewer`, and `spec-test-generator` before Databricks rollout. Databricks rollout should use `databricks-rollout-planner` only after local certification evidence exists.

## Creation Sequence

Create and harden the skills in this order: first `provider-spec-generator`, then `business-question-profiler`, then `drift-decision-resolver`, then `canonical-model-planner`, then `adapter-contract-reviewer`, then `spec-test-generator`, then `privacy-governance-reviewer`, then `adapter-code-generator`, then `qa-evidence-reviewer`, then `local-runtime-harness-planner`, then `local-postgres-dbt-modeling-orchestrator`, then `databricks-rollout-planner`. This reflects the dependency chain: declarative source specs and drift reports capture source truth; business questions clarify minimum canonical concepts, risk/impact options, and deferred Gold candidates; drift decisions close or defer semantic blockers; resolved decisions drive canonical model specs; model specs drive adapter review; validators and privacy controls protect the contracts; approved contracts drive generated code; generated code drives QA; QA and approved contracts drive local runtime certification; local runtime certification drives local PostgreSQL/dbt model iteration; local model evidence later drives Databricks/Unity Catalog validation.

## Initial Folder Shape

```text
.agent/
  skills/
    provider-spec-generator/
      SKILL.md
    drift-decision-resolver/
      SKILL.md
    canonical-model-planner/
      SKILL.md
    business-question-profiler/
      SKILL.md
    adapter-contract-reviewer/
      SKILL.md
    adapter-code-generator/
      SKILL.md
    qa-evidence-reviewer/
      SKILL.md
    local-runtime-harness-planner/
      SKILL.md
    local-postgres-dbt-modeling-orchestrator/
      SKILL.md
    spec-test-generator/
      SKILL.md
    privacy-governance-reviewer/
      SKILL.md
    databricks-rollout-planner/
      SKILL.md
  spec_templates/
    provider_entity_profile.template.yaml
    business_question_profile.template.yaml
    silver_entity_model.template.yaml
    databricks_deployment_profile.template.yaml
```
