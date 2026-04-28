# AgentOps Skill Strategy

## Purpose

This document defines the first skill set for the Raw/Bronze -> Silver agentic migration. Skills are reusable Markdown instructions stored as `.agent/skills/<skill-name>/SKILL.md`. A skill teaches Codex how to apply domain rules repeatedly; a prompt or plan tells Codex what to do in one execution.

The design borrows the responsibility split from Agentic-Medallion: Planner Agent, Code Generator Agent, Code Reviewer Agent, Executor Agent, and a self-correction loop. We do not copy the notebook-centric implementation. We translate the pattern into enterprise-friendly AgentOps skills, declarative provider specs, GitHub PR gates, and Databricks/Unity Catalog validation.

## Agentic-Medallion Contrast

Agentic-Medallion is useful because it separates planning, code generation, review, and execution, and because its HITL path creates GitHub PRs before deployment. Its limitation for this migration is that it is more POC than operating model: notebook-heavy, weak package boundaries, limited IaC, and no strong Unity Catalog lineage contract. Our strategy keeps the role separation but makes specs-as-code the center of gravity.

| Agentic-Medallion Role | Our Interpretation | Primary Skill |
|---|---|---|
| Planner Agent | Creates provider/entity YAML specs, canonical model intent, migration risks, and HITL questions | `provider-spec-generator`, `canonical-model-planner` |
| Code Generator Agent | Generates parsers, adapters, fixtures, and spec tests from approved contracts | `adapter-code-generator`, `spec-test-generator` |
| Code Reviewer Agent | Reviews adapter contracts, QA evidence, privacy, dependency safety, lineage, quarantine, scope control, PR governance readiness, and escalation boundaries | `adapter-contract-reviewer`, `qa-evidence-reviewer`, `privacy-governance-reviewer`, `repo-governance-auditor`, `hitl-escalation-controller` |
| Executor Agent | Plans approved Databricks validation against governed targets | `databricks-rollout-planner` |

## Skill Set

The first skill set should remain small, but each skill must have a concrete output. The highest-risk skill is `provider-spec-generator`; it must not stop at a report or YAML-only output. Its DoD is a set of YAML provider/entity specs plus a provider-specialized parser, parser fixtures, and parser tests that can later drive adapter implementation.

Skill names should describe the operating responsibility, not the data layer. Use `generator` when the skill creates a declared artifact, `planner` when it designs a target contract or rollout, and `reviewer` when it validates readiness or evidence. Avoid names like `raw`, `bronze`, or `silver` as the primary identity because they hide what the skill actually does.

| Skill | Purpose | Primary Inputs | Required Output |
|---|---|---|---|
| `provider-spec-generator` | Expert parsing and source profiling skill that reads provider folders and `column_dictionary.md`, detects file/entity structure, standardizes metadata, emits declarative YAML specs, and creates the provider-specialized parser | Provider folders, `column_dictionary.md`, raw file paths, topology PRD | `metadata/provider_specs/<provider_slug>/<entity>.yaml`, `src/adapters/<provider_parser>.py`, parser fixtures, parser tests, provider drift summary, human-review questions |
| `canonical-model-planner` | Converts provider YAML specs into canonical Bronze/Silver model specs, provider-to-Silver mapping matrices, and modeling impact reports | Provider YAML specs, topology PRD, governance requirements | `metadata/model_specs/bronze/bronze_contract.yaml`, `metadata/model_specs/silver/<entity>.yaml`, `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`, modeling risk report |
| `adapter-contract-reviewer` | Validates adapter design, parser selection, mapping confidence, Bronze contract, Silver contract, lineage, and quarantine | Provider YAML specs, model YAML specs, adapter plan, topology document | Adapter readiness report |
| `adapter-code-generator` | Generates parser/adapter implementation, fixtures, and local tests from approved provider and model specs | Provider YAML specs, model YAML specs, mapping matrix, adapter readiness report | Parser/adapter code, fixtures, implementation tests, generation report |
| `qa-evidence-reviewer` | Validates QA families, evidence contract, decisions, rerun behavior, and feedback loop completeness | QA plan, test outputs, evidence files | QA feedback report |
| `spec-test-generator` | Generates Python validators and tests for declarative specs before Databricks execution | PRD test strategy, spec templates, provider/model/deployment specs | `tests/specs/*.py`, validators, spec test report |
| `privacy-governance-reviewer` | Reviews PII/PHI classification, evidence redaction, secrets, dependency safety, permissions, Unity Catalog governance, and approval requirements | Provider specs, model specs, QA evidence, dependency manifests, deployment specs, PR risk report | Privacy/governance/dependency review report |
| `repo-governance-auditor` | Reviews GitHub governance and PR safety before an agent prepares or creates a pull request | Active plan, changed files, test evidence, dependency evidence, HITL records, workflow changes, branch context | Governance readiness findings |
| `hitl-escalation-controller` | Stops uncontrolled iteration and asks for a precise human decision when repeated failures, missing evidence, ambiguous semantics, or scope drift block safe progress | Active plan, trace logs, changed files, test output, reports, HITL records | Concise escalation packet and blocked next action |
| `databricks-rollout-planner` | Validates Databricks execution plan, governed locations, Unity Catalog target design, lineage, permissions, and deployment readiness | Model YAML specs, adapter readiness, Databricks specs, UC target plan | Databricks/UC readiness report |

## Raw Discovery YAML Contract

The source specs and provider parser produced by `provider-spec-generator` are the bridge between messy provider exports and scalable adapters. They should be generated per provider/entity, not handwritten ad hoc. Each YAML must include provider identity, source type, upload partition, declared filetype, extension, entity, expected file patterns, parser profile, stable row key, canonical mappings, inferred data types when available, PII flags, relationship hints, known drift, quarantine rules, QA expectations, and `needs_human_review` reasons. The parser must consume those YAML specs and prove that the source profile is executable against fixtures and, when available, sampled local source files.

The five current provider dictionaries already show why this matters. Aegis uses `SRC_ROW`, BlueStone uses `LINE_ID`, NorthCare uses `EXPORT_ID`, ValleyBridge uses `DW_LOAD_SEQ`, and Pacific Shield uses `CLM_SEQ` as the source row key. Filetypes also differ: FHIR-like JSON, HL7 XML, X12-style TXT, and CSV. These differences should become declarative YAML metadata, not hardcoded adapter behavior.

## Declarative Modeling Contract

Provider YAML specs are source contracts, not target model contracts. The `canonical-model-planner` must create the intermediate canonical model layer before any adapter code or Databricks rollout is generated. This layer groups all provider fields by canonical concept, defines Bronze metadata, defines Silver entities, declares required fields and types, records relationship confidence, and produces a provider-to-Silver mapping matrix. It also produces an impact report that explains risks, drift, missing providers, PII exposure, unsafe casts, and HITL decisions.

The output model specs become the input to adapter generation and Databricks deployment specs. This prevents each provider dialect from shaping the enterprise model by accident.

## Declarative Spec Validation

GitHub CI should validate specs before Databricks execution. Python validators should parse every YAML, check required sections, enforce provider/entity coverage, verify that source mappings reference real provider specs, validate that Silver columns have types and lineage, detect duplicate canonical mappings, detect missing PII flags, reject absolute paths, and ensure deployment specs only reference approved model specs.

Each skill should also name the Python test family that protects its output. `provider-spec-generator` is protected primarily by schema tests, unit data tests, integration tests, reconciliation tests, regression tests, data quality tests over provider specs, and parser behavior tests over provider fixtures. `canonical-model-planner` is protected by schema tests, integration tests, reconciliation tests, and regression tests over model specs and the provider-to-Silver matrix. `adapter-contract-reviewer` and `adapter-code-generator` are protected by unit data tests, integration tests, schema tests, and regression tests over adapter fixtures and provider parser reuse. `spec-test-generator` is protected by meta-tests that prove validators fail on invalid fixtures and pass on valid fixtures. `qa-evidence-reviewer` is protected by schema tests and integration tests over QA evidence specs. `privacy-governance-reviewer` is protected by security tests, schema tests, dependency safety checks, and regression tests over privacy flags, redaction rules, secrets checks, package risk, and approval records. `repo-governance-auditor` is protected by governance checks over PR evidence, forbidden operations, workflow permissions, secret handling, dependency evidence, branch discipline, and test evidence. `hitl-escalation-controller` is protected by escalation checks over repeated failures, missing evidence, ambiguous decisions, scope drift, and blocked next actions. `databricks-rollout-planner` is protected by schema tests, integration tests, security tests, and regression tests over deployment specs. Business rule tests are scope guards only in this phase: they ensure post-Silver rules do not silently enter Bronze/Silver specs.

## Skill Design Standard

Each skill must include frontmatter with `name`, `description`, and `user-invocable`. The body must include purpose, when to use it, required inputs, required outputs, checks, non-negotiables, DoD, QA expectations, and output format. The checks should use descriptive behavior names, not rule IDs. Every skill output should identify status, impacted provider/entity, evidence path, human decisions required, and recommended next action.

Every skill must follow `docs/agentops_filesystem_conventions.md`. Skills may create or update files only inside the approved global structure for their responsibility. They must not create private agent workspaces, alternate metadata roots, duplicated test folders, or hidden handoff locations.

Every skill must also respect the active plan focus and trace logging rules. During discovery and provider profiling, the active agent is a provider specialist and must work on one provider only, appending concise entries to `logs/provider_discovery/<provider_slug>.md`. During canonical modeling, the active agent becomes a generalist reviewer across providers and appends entries to `logs/canonical_model/canonical_review.md`. Before any PR preparation or creation, the agent must use `repo-governance-auditor` to check PR evidence, forbidden operations, tests, branch discipline, and HITL requirements. If an agent reaches repeated failures, missing evidence, ambiguous semantics, or scope drift, it must use `hitl-escalation-controller` and stop until a human decision or explicit unblock exists. Logs are append-only and must not be purged, deleted, reordered, or rewritten.

## Relationship To Plans

The prompts in `agentic_migration_prompts/` are plan-like work orders. They should invoke these skills by responsibility. `02_raw_discovery_and_schema.md` should use `provider-spec-generator` to produce provider YAML specs. `03_bronze_silver_contracts.md` should use `canonical-model-planner` to create canonical model specs. `01_adapter_topology_planning.md` should use `adapter-contract-reviewer` once model specs exist and `adapter-code-generator` after approval. `04_qa_databricks_feedback_loop.md` should use `spec-test-generator`, `qa-evidence-reviewer`, `privacy-governance-reviewer`, and `databricks-rollout-planner`.

## Creation Sequence

Create and harden the skills in this order: first `provider-spec-generator`, then `canonical-model-planner`, then `adapter-contract-reviewer`, then `spec-test-generator`, then `privacy-governance-reviewer`, then `adapter-code-generator`, then `qa-evidence-reviewer`, then `databricks-rollout-planner`. This reflects the dependency chain: declarative source specs drive canonical model specs; model specs drive adapter review; validators and privacy controls protect the contracts; approved contracts drive generated code; generated code drives QA; QA and approved contracts drive Databricks/Unity Catalog validation.

## Initial Folder Shape

```text
.agent/
  skills/
    provider-spec-generator/
      SKILL.md
    canonical-model-planner/
      SKILL.md
    adapter-contract-reviewer/
      SKILL.md
    adapter-code-generator/
      SKILL.md
    qa-evidence-reviewer/
      SKILL.md
    spec-test-generator/
      SKILL.md
    privacy-governance-reviewer/
      SKILL.md
    databricks-rollout-planner/
      SKILL.md
  spec_templates/
    provider_entity_profile.template.yaml
    silver_entity_model.template.yaml
    databricks_deployment_profile.template.yaml
```
