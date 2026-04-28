# Technical PRD / AgentOps Operating Spec

## 1. Executive Intent

This specification defines the technical operating model for MediSynth's agentic healthcare data migration. MediSynth must unify five legacy exports from acquired or parallel systems into a governed Databricks platform without losing lineage, quality, security, or human accountability. The program must move quickly, but it must do so with enterprise discipline: AI agents accelerate discovery, specification, code generation, validation, and review while humans retain control over semantics, PII, quality, and promotion.

The target operating model combines AgentOps, Codex skills, specs-as-code, config-as-code, GitHub CI, a portable local runtime certification loop, Databricks, Unity Catalog, and Human in the Loop. AgentOps provides the repeatable pattern of skill + plan + workflow. Codex skills encode reusable migration standards under `.agent/skills/<skill-name>/SKILL.md`. LangChain may provide lightweight tool abstractions where useful. LangGraph may orchestrate stateful multi-agent workflows when migration state, retries, routing, and approvals become complex. LangSmith, MLflow, or OpenTelemetry may capture traces. MCP may expose controlled tools for GitHub, Databricks, Unity Catalog, docs, diagrams, or validation evidence. Spark Declarative Pipelines, Delta Lake OSS, OpenLineage, and Marquez are local validation capabilities behind HITL-approved dependencies. Terraform, Databricks Asset Bundles, Lakeflow/DLT, and dlt-meta are expected implementation capabilities for governed target deployment and validation, not the source of modeling truth.

The migration will cover `data_provider_1_aegis_care_network`, `data_provider_2_bluestone_health`, `data_provider_3_northcare_clinics`, `data_provider_4_valleybridge_medical`, and `data_provider_5_pacific_shield_insurance`. Each provider may have different file formats, schemas, naming conventions, data quality issues, and semantic uncertainty. The system must therefore be adapter-driven, evidence-driven, and approval-driven.

The first governed delivery scope is Raw/Bronze -> Silver, with contracts and canonical models kept cloud-agnostic and with Unity Catalog as the governed Databricks target. The expected end state for this phase is a repeatable agentic workflow that discovers provider files, profiles schemas, designs provider adapters, certifies local Bronze/Silver behavior through portable runtime interfaces, writes quarantine and QA evidence, and then validates governed data assets in Databricks/Unity Catalog. Anything after Silver is intentionally deferred until the provider adapters, lineage, quarantine, QA evidence, local certification, and Unity Catalog governance are stable.

## 2. Scope And Non-Scope

In scope are Raw file discovery, manifests, parsing strategy, provider adapter design, Bronze contracts, Silver contracts, runtime-neutral adapter interfaces, local runtime certification, quarantine behavior, PII handling, dependency safety, lineage, QA evidence, GitHub PR controls, Databricks validation execution, Unity Catalog registration, declarative provider specs, runtime specs, config-as-code, specs-as-code, CI/CD controls, and implementation planning for Terraform, Databricks Asset Bundles, Lakeflow/DLT, and dlt-meta where they reduce operational risk. The system must support fast local planning and validation with Codex plus scalable certification in Databricks.

Out of scope are Gold models, KPI definitions, downstream analytics, dashboards, production promotion, automated identity resolution across providers, automatic clinical code interpretation, and any semantic mapping without human approval. Terraform, Databricks Asset Bundles, Lakeflow/DLT, dlt-meta, LangGraph, LangSmith, and MCP are in scope as technical building blocks for the migration operating model. Creating cloud resources, applying Terraform, deploying Databricks bundles, or running production jobs still requires explicit human approval and environment-specific controls.

## 3. Operating Principle: Three Planes

For a stable agentic migration, the system is separated into three planes.

| Plane | Primary Runtime | Responsibility | Exit Evidence |
|---|---|---|---|
| Control and Generation Plane | Codex, GitHub, skills, specs, CI | Discovery plans, adapter specs, code generation, static QA, PR review, HITL | PR diff, tests, manifests, risk report, approval record |
| Local Runtime Certification Plane | Local Python, Spark Declarative Pipelines when approved, Delta Lake OSS when approved, OpenLineage/Marquez when approved, fixtures, contracts | Fast portable validation of provider adapters, Bronze/Silver contracts, quarantine behavior, QA evidence, and lineage evidence shape | Local runtime specs, local certification report, fixture outputs, local lineage evidence, dependency review |
| Databricks Certification Plane | Databricks Runtime, Lakeflow, Unity Catalog, governed storage, workflows/jobs | Representative target-runtime validation, UC governance, permissions, runtime compatibility, lineage, performance, rollout readiness | Databricks deployment specs, validation run report, QA evidence tables/files, quarantine, UC lineage |

The agent must not jump to Databricks for every generated change. Codex works first in the control plane, producing specs, code, tests, and reviewable artifacts. The local runtime plane certifies that adapters and contracts work through portable interfaces. Databricks is used after local certification, GitHub checks, and human approval are sufficient to justify running against representative target-runtime data.

### 3.1 Control And Generation Plane: GitHub CI Before Databricks

The control plane must validate migration code and migration intent before any Databricks execution. This is the cheaper, faster, reproducible gate connected to Human in the Loop through pull requests. GitHub CI should validate parsers for SQL, notebooks, jobs, and configuration files; unit tests for conversion logic; snapshot tests for generated SQL or generated specs; linting, formatting, and type checks; manifest and configuration validation; migration-rule tests; and security checks for secrets, unsafe permissions, hardcoded paths, destructive operations such as `DROP` or `TRUNCATE`, and unapproved cloud targets.

Every agent-generated PR must explain what changed, which providers/entities/tables are impacted, what risks were introduced, what evidence was produced, and what Databricks validation is expected next. Human approval is based on PR diff, tests, coverage, parser report, migration plan, risk report, manifest, and expected QA checks. A PR that cannot explain its impact is not ready for Databricks.

### 3.1.1 Branch And Pull Request Governance

The only long-lived repository branch is `main`. Agent-created branches are temporary work branches only; they must use a scoped name, must not become permanent integration branches, and must be deleted after the PR is approved and merged or explicitly closed by a human.

All agent-created pull requests must target `main`. Additional integration or validation branches are not part of the default strategy unless a human explicitly records a one-off exception in the PR evidence.

Before creating a PR, the agent must confirm that the base branch is `main`, list the head branch, include branch cleanup notes, and record any branch-policy exception as a Human in the Loop decision. If the target is not `main` and no exception is recorded, `repo-governance-auditor` must block PR creation.

### 3.2 Local Runtime Certification Plane: Portable Before Databricks

The local runtime plane validates functional migration behavior without requiring cloud credentials or remote workspaces. Its role is to prove that provider parsers, adapter interfaces, Bronze preservation, canonical mapping, Silver output shape, quarantine behavior, QA evidence, and lineage evidence can be exercised quickly and cheaply from deterministic fixtures and approved samples.

The local runtime may use Spark Declarative Pipelines, Delta Lake OSS, contracts-as-code, OpenLineage, and Marquez after dependency approval. These tools are local validation capabilities, not enterprise modeling authorities. Local certification must not claim equivalence with Databricks Runtime, Unity Catalog permissions, Lakeflow managed orchestration, Lakeflow Auto CDC, serverless behavior, production performance, cloud IAM, or exact Databricks event logs.

### 3.3 Databricks Certification Plane: Target Runtime After Local Certification

Databricks enters when validation depends on real or representative target-runtime data, Databricks Runtime behavior, Lakeflow behavior, Unity Catalog permissions, runtime configuration, UC lineage, governed storage, or scalable execution. This plane must perform source profiling, Bronze/Silver data quality checks, source-to-target reconciliation, row counts, null-rate checks, duplicate checks, schema drift detection, CDC correctness where applicable, performance and cost benchmarks, Unity Catalog lineage validation, Lakeflow/DLT validation if used, comparison between legacy outputs and new outputs when available, and progressive testing from sampled data to larger volumes.

This QA belongs in Databricks because it depends on the actual execution engine, data permissions, Unity Catalog metadata, storage layout, runtime behavior, and lineage system tables. It must run first in dev or validation environments, not production.

### 3.4 Databricks Readiness Gate

Databricks validation is allowed only after the PR has passed parser/conversion checks, local unit tests, local runtime certification, static compilation or syntax checks, valid deployment/spec configuration, generated migration plan, human approval, and a versioned CI artifact containing code, tests, manifest, expected checks, local certification evidence, and risk report. This gate prevents the agent from using Databricks as an expensive debugging loop.

### 3.5 Orchestration Responsibilities

The system should not use one orchestrator for everything. GitHub Actions orchestrates CI and PR gates. Local runtime certification orchestrates deterministic fixture and contract checks without cloud credentials. Databricks Workflows or Lakeflow Jobs orchestrate target-runtime validation after approval. Codex plus skills performs local planning, editing, generation, and PR preparation. LangGraph may later orchestrate multi-step migration state, routing, retries, evaluations, and HITL checkpoints. MLflow, LangSmith, or OpenTelemetry may be used for agent tracing if approved. OpenLineage/Marquez may provide local lineage evidence when approved; Unity Catalog system tables provide target-runtime lineage and auditability.

## 4. Agentic Architecture

Codex is the primary implementation and planning agent. It reads skills, specs, provider topology, and prompts; then it edits files, produces artifacts, and runs local verification. Skills live under `.agent/skills/<skill-name>/SKILL.md` and encode reusable domain rules. Plans live as Markdown prompts or task specs and declare DoR, DoD, QA, scope, and expected outputs.

LangChain may be used as a lightweight integration layer for tools, retrieval, and structured agent utilities when it makes the implementation more robust. LangGraph is the preferred candidate for a later stateful migration orchestrator when the workflow needs persistent state per provider, table, file, adapter, approval, retry, and validation run. LangSmith, MLflow, or OpenTelemetry may be used for traceability of agent decisions and tool calls when security review approves the telemetry path. MCP may expose controlled tools for Databricks, GitHub, filesystem, documentation, Unity Catalog metadata, diagrams, or validation reports. MCP tools must be permission-scoped and must not bypass PR/HITL gates.

The reference projects are directional, not controlling. `snowflake-agentops-lunch-and-learn` provides the skill + plan + workflow pattern. Agentic-Medallion is useful as a conceptual reference for agent roles and HITL PRs, but it is not enterprise-ready enough to copy as-is. Databricks Labs `dlt-meta` is a strong implementation reference for specs-as-code and metadata-driven Bronze/Silver pipelines. Databricks Asset Bundles are the expected packaging and deployment mechanism when Databricks jobs/pipelines are promoted beyond local planning. Terraform is the expected infrastructure-as-code mechanism for governed environments once the architecture is approved.

The initial role model is intentionally small but complete enough to move from planning into implementation. A Discovery Agent profiles sources and produces inventory plus migration evidence. A Parser/Evaluator Agent parses source structures, classifies complexity, detects incompatibilities, and proposes Bronze/Silver strategy. A Codegen Agent generates adapter code, declarative specs, Python validators, fixtures, tests, and data quality checks only after contracts are clear. A Governance Reviewer evaluates PII/PHI, redaction, secrets, Unity Catalog permissions, and approval records. A Code Reviewer Agent evaluates PRs for correctness, safety, lineage, QA evidence, and scope control. An Executor Agent may run approved Databricks validation jobs, but must not bypass GitHub CI or human approval.

## 5. Declarative Specs

The migration should prefer declarative specs over hardcoded provider logic. Each provider/entity should be representable by a YAML or JSON profile that declares source file patterns, format, parser options, expected fields, target Bronze/Silver entity, mapping confidence, quarantine behavior, lineage requirements, and QA expectations.

A provider spec is not a replacement for code. It is the contract that lets agents and humans discuss the same thing. Code should implement shared parser and adapter behavior; specs should declare provider differences. If a provider requires custom cleanup, the spec should name that requirement and link to the adapter implementation.

The system must separate source contracts, model contracts, and deployment contracts. Provider/entity YAMLs are source contracts; they describe how each provider speaks. They are not the canonical model. Canonical Bronze/Silver model YAMLs are model contracts; they define what the platform will standardize and govern. Databricks/Lakeflow/DLT/dlt-meta YAMLs are deployment contracts; they define how approved model contracts are rolled out.

### 5.1 Declarative Layer Contract

| Layer | Purpose | Inputs | Outputs | Owner Skill |
|---|---|---|---|---|
| Provider Source Specs | Capture provider/entity dialects, parser profile, row key, source fields, canonical hints, PII signals, drift, quarantine expectations, and executable provider parser behavior | `data_500k/**/column_dictionary.md`, raw file paths, topology PRD | `metadata/provider_specs/<provider_slug>/<entity>.yaml`, `src/adapters/<provider_parser>.py`, parser fixtures/tests, drift summary, HITL queue | `provider-spec-generator` |
| Drift Decision Runbook | Resolve or explicitly defer blocking drift, privacy, relationship, status, parser-contract, and payload decisions before canonical modeling starts | Provider specs, drift reports, privacy reports, HITL queues, QA evidence | `reports/hitl/canonical_drift_decision_runbook.md`, applied decision evidence, plan 02 blockers | `drift-decision-resolver` |
| Canonical Model Specs | Convert provider source evidence into shared Bronze/Silver contracts, canonical entities, types, required fields, lineage, keys, mappings, and modeling risks | Provider specs, topology PRD, governance requirements, drift decision runbook | `metadata/model_specs/bronze/bronze_contract.yaml`, `metadata/model_specs/silver/<entity>.yaml`, `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`, `metadata/model_specs/impact/modeling_risk_report.md` | `canonical-model-planner` |
| Adapter Implementation Specs | Define how parser and adapter code consumes provider specs and writes Bronze/Silver/quarantine according to approved model specs through runtime-neutral interfaces | Provider specs, model specs, adapter design | Adapter readiness report, parser/adapter task plan, implementation fixtures | `adapter-contract-reviewer` |
| Adapter Code Artifacts | Generate parser/adapter code, local fixtures, and implementation tests from approved contracts | Provider specs, model specs, mapping matrix, adapter readiness report | Parser code, adapter code, fixtures, local tests, generation report | `adapter-code-generator` |
| Local Runtime Specs | Define local runtime profiles, interface contracts, local lineage evidence shape, dependency gates, and local certification commands | Provider specs, model specs, adapter artifacts, QA evidence, HITL approvals | `metadata/runtime_specs/local/*.yaml`, local runtime certification report, dependency review, runtime validation tests | `local-runtime-harness-planner` |
| Spec Validation Artifacts | Generate Python tests and validators that protect declarative contracts in GitHub CI | PRD test strategy, spec templates, provider/model/deployment specs | `tests/specs/*.py`, validator helpers, spec test report | `spec-test-generator` |
| Privacy And Governance Review | Validate PII/PHI classification, evidence redaction, secrets, permissions, governed targets, and HITL approvals | Provider specs, model specs, QA evidence, deployment specs, PR risk report | Privacy/governance review report, blockers, approval queue | `privacy-governance-reviewer` |
| Databricks Deployment Specs | Convert approved model specs and local certification evidence into Databricks execution configuration, governed locations, Unity Catalog objects, expectations, jobs, bundles, or dlt-meta dataflowspecs | Model specs, adapter readiness, local runtime certification, QA plan, environment strategy | `metadata/deployment_specs/databricks/*.yaml`, Lakeflow/DLT/dlt-meta specs, Databricks Asset Bundle config, UC rollout plan | `databricks-rollout-planner` |

### 5.2 Provider Specs Are Inputs, Not The Model

The provider specs explain source dialects. For example, the row key may be `SRC_ROW` for Aegis, `LINE_ID` for BlueStone, `EXPORT_ID` for NorthCare, `DW_LOAD_SEQ` for ValleyBridge, and `CLM_SEQ` for Pacific Shield. These are source facts. The canonical model spec decides that all of them map to `ROW_ID`, how that value is typed, whether it is required in Bronze and Silver, and how it participates in lineage and reconciliation.

The modeling layer must aggregate source evidence by canonical concept. It should show which source headers map to a Silver column, which providers support the column, which providers drift, which types are safe, which fields are PII, which relationships are reliable, and which decisions require Human in the Loop. This layer prevents a single provider's dialect from accidentally becoming the enterprise model.

### 5.3 Python Validation For Declarative Specs

Before Databricks execution, GitHub CI must validate all declarative files with Python. The initial validators should check YAML parseability, required keys, provider/entity coverage, unique provider/entity/entity-field combinations, mapping completeness, canonical field consistency, PII flags for sensitive fields, row-key presence, allowed parser families, allowed QA decisions, no hardcoded absolute paths, no unapproved post-Silver targets, and cross-layer referential integrity from provider specs to model specs to deployment specs.

The validation suite should include at least `validate_provider_specs.py`, `validate_model_specs.py`, `validate_deployment_specs.py`, and `validate_spec_lineage.py`. These scripts should fail fast with actionable messages and should emit a machine-readable report for PR review. Snapshot tests should protect generated YAML shape so agent iterations do not silently change the contract.

### 5.4 Test Strategy By Declarative Layer

Each declarative layer requires different Python tests because each layer owns a different kind of risk. Unit tests prove the smallest rule or parser works. Integration tests prove two adjacent spec layers agree. End-to-end/system tests prove the full spec chain can drive a sample Raw/Bronze -> Silver run. Data quality tests prove technical quality assumptions are represented. Schema tests prove the declarative files obey their contract. Regression tests protect generated specs from accidental drift. Reconciliation tests prove counts and mappings remain balanced across layers. Business rule tests are limited in this phase: they may verify that unapproved post-Silver rules are absent or explicitly marked as future/HITL, but they must not validate KPIs or analytics outcomes.

| Declarative Layer | Most Appropriate Python Tests | What The Tests Validate | Example Test File |
|---|---|---|---|
| Provider Source Specs | Schema tests, unit data tests, integration tests, reconciliation tests, regression tests, data quality tests, parser behavior tests | YAML shape, required provider/entity fields, parser family, source row key, source-to-canonical hints, PII flags, allowed file extensions, dictionary coverage, no raw PII examples, executable provider parser behavior over fixtures | `tests/specs/test_provider_specs.py`, `tests/adapters/test_<provider>_parser.py` |
| Canonical Model Specs | Schema tests, integration tests, data quality tests, reconciliation tests, regression tests | Silver entity shape, column types, nullability, lineage columns, required fields, key candidates, provider coverage, source mappings reference existing provider specs, unsafe casts require HITL | `tests/specs/test_model_specs.py` |
| Provider-To-Silver Mapping Matrix | Integration tests, reconciliation tests, regression tests | Every model column maps to at least one approved source or approved lineage field, every provider mapping references valid source headers, no duplicate conflicting mappings, unsupported providers are explicitly marked | `tests/specs/test_provider_to_silver_matrix.py` |
| Adapter Implementation Specs | Unit data tests, integration tests, schema tests, regression tests | Parser profile is implementable, adapter consumes declarative YAML, quarantine behavior exists for invalid casts/missing required fields, fixtures cover positive and negative cases | `tests/specs/test_adapter_specs.py` |
| QA Evidence Specs | Schema tests, integration tests, regression tests | Required evidence fields exist, allowed decisions are `stop_pipeline`, `quarantine_data`, `warn`, every test links to provider/entity/model/deployment context, evidence paths are deterministic | `tests/specs/test_qa_evidence_specs.py` |
| Local Runtime Specs | Schema tests, integration tests, lineage evidence shape tests, scope guard tests, regression tests | Runtime profile references approved contracts, local paths are constrained to `artifacts/`, dependency approvals are explicit, local QA says `local_validated`, Databricks-only secrets and workspace paths are absent | `tests/specs/test_local_runtime_specs.py` |
| Databricks Deployment Specs | Schema tests, integration tests, security tests, regression tests | Deployment spec references approved model specs and local certification evidence, Unity Catalog catalog/schema/table targets are declared, no hardcoded local paths, no production execution without approval, DAB/Lakeflow/DLT/dlt-meta references are coherent | `tests/specs/test_deployment_specs.py` |
| Full Spec Chain | End-to-end/system tests, reconciliation tests, regression tests | Provider specs -> model specs -> adapter specs -> deployment specs can be resolved as one graph; no missing references; sample provider/entity can produce a deterministic dry-run plan | `tests/specs/test_spec_chain_system.py` |
| Business Rules | Scope guard tests, schema tests | Post-Silver KPI/analytics rules are absent, deferred, or explicitly marked out-of-scope/HITL; no business rule silently changes Bronze/Silver semantics | `tests/specs/test_business_rule_scope.py` |

The first CI gate should run these tests without Databricks. They should operate on YAML, small fixtures, and generated metadata only. Databricks validation starts after these tests pass and a human approves the PR.

The minimum spec families are source profiles, parser profiles, adapter mapping specs, Bronze contract specs, Silver contract specs, provider-to-Silver mapping matrices, quarantine specs, QA evidence specs, local runtime specs, deployment specs, and human approval records.

## 6. Responsibilities

| Component | Responsibility |
|---|---|
| Codex | Plans, edits, generates specs/code/tests/docs, runs local checks, prepares PR-ready artifacts |
| Skills | Encode reusable domain rules for discovery, modeling, adapters, Bronze/Silver contracts, local runtime certification, QA, PII, and Databricks validation |
| GitHub CI | Runs static validation, unit tests, fixture tests, security checks, spec validation, and PR evidence checks |
| Human Reviewer | Approves source coverage, uncertain mappings, PII classification, ambiguous types, Silver contracts, and Databricks execution |
| Local Runtime | Executes fast fixture/sample validation through runtime-neutral interfaces, local Delta/Spark capabilities when approved, and local lineage evidence when approved |
| Databricks | Executes representative and scalable target-runtime validation, materializes Bronze/Silver, stores Delta outputs, validates permissions and Unity Catalog lineage |
| Unity Catalog | Governs datasets, permissions, lineage, tables, volumes, schemas, and auditability |
| Terraform | Infrastructure-as-code for approved Databricks/cloud resources and environment separation |
| Databricks Asset Bundles | Versioned packaging and deployment of Databricks jobs, pipelines, and configuration |
| Lakeflow/DLT/dlt-meta | Metadata-driven Bronze/Silver pipeline implementation option using declarative specs |
| LangGraph | Stateful multi-step orchestrator for migration workflows when the simple Codex loop is insufficient |
| LangChain | Lightweight tool and integration layer when it improves robustness without adding unnecessary complexity |
| LangSmith / MLflow / OpenTelemetry | Traceability for agent decisions, tools, retries, and validation runs when approved |
| MCP | Controlled tool access layer for GitHub, Databricks, Unity Catalog, docs, diagrams, and evidence |

## 6.1 Validation Split

| Validation | GitHub CI | Databricks |
|---|---:|---:|
| SQL, notebook, job, and config parsing | Required | Optional |
| Conversion logic unit tests | Required | Optional unless target-runtime behavior is required |
| Generated SQL/spec snapshot tests | Required | Optional |
| Linting, formatting, and type checks | Required | Optional |
| Manifest and declarative spec validation | Required | Optional |
| Security checks for secrets, hardcoded paths, unsafe permissions, `DROP`, `TRUNCATE` | Required | Optional runtime confirmation |
| PR impact report and migration plan validation | Required | No |
| Data quality over fixtures and approved local samples | Required | Optional follow-up |
| Data quality over representative or real target-runtime data | No | Required |
| Source-to-target reconciliation | Fixture/local sample | Required |
| Row counts, null rates, duplicate checks | Fixture/local sample | Required |
| Schema drift over actual sources | Partial/local sample | Required |
| CDC correctness | Static/spec partial | Required when CDC applies |
| Performance and cost benchmark | No | Required before scale-up |
| Unity Catalog permissions and lineage | No | Required |
| Lakeflow/DLT pipeline validation | Static/spec partial | Required when used |

## 7. Required Skills

The initial AgentOps skill set should be small, precise, and complete enough to move from specs into implementation. The recommended v1 skills are `provider-spec-generator`, `drift-decision-resolver`, `canonical-model-planner`, `adapter-contract-reviewer`, `adapter-code-generator`, `local-runtime-harness-planner`, `spec-test-generator`, `privacy-governance-reviewer`, `qa-evidence-reviewer`, `repo-governance-auditor`, `hitl-escalation-controller`, and `databricks-rollout-planner`.

Skill names must describe operating responsibility instead of layer ownership. `generator` means the skill creates a durable declarative artifact, `planner` means it designs a target contract or rollout, and `reviewer` means it validates readiness, evidence, or implementation risk. The layer still appears inside the skill contract, but it should not be the primary name because names like Raw, Bronze, or Silver are too broad to explain what the skill does.

The skill strategy is documented separately in `docs/agentops_skill_strategy.md`. Skills must be written as reusable Markdown instructions and stored as `.agent/skills/<skill-name>/SKILL.md`. They must tell Codex when to use them, what to check, what not to do, and what output format to produce.

All plans and skills must follow the shared filesystem contract in `docs/agentops_filesystem_conventions.md`. Agents must write to the approved global structure for `metadata/`, `reports/`, `src/`, `tests/`, and `artifacts/`; they must not create private agent-specific output roots.

Agent work must be traceable through concise append-only technical logs under `logs/`. Discovery and provider profiling must operate on one provider at a time, with the agent acting as a specialist for the active provider and writing to `logs/provider_discovery/<provider_slug>.md`. Canonical modeling is the first generalist phase that may review all providers together, writing to `logs/canonical_model/canonical_review.md`. Logs must include timestamp, plan, provider, skill, event, artifact, and a short note; agents must append corrections instead of deleting or rewriting history.

Before an agent prepares or creates a PR, it must use `repo-governance-auditor` to check PR evidence, branch discipline, forbidden operations, workflow permissions, secrets handling, dependency safety evidence, test evidence, and HITL requirements. This skill must verify that the PR targets `main`, that `main` is the only long-lived branch, and that the temporary head branch has a documented deletion plan after PR approval and merge or explicit closure. This skill must not create PRs, mutate GitHub settings, change secrets, run Databricks, apply Terraform, approve PRs, or merge changes.

Any new or changed package must be reviewed by `privacy-governance-reviewer` for supportability, known vulnerability risk, lockfile discipline, dependency confusion or typosquatting risk, and human-approved exceptions. Agents must not install or approve packages with known critical or high vulnerabilities without explicit HITL approval and mitigation.

If an agent reaches repeated failed attempts, missing source evidence, ambiguous semantics, unclear test failures, or scope drift, it must use `hitl-escalation-controller` to stop the flow and request a specific human decision. The agent must not continue by guessing, weakening tests, inventing mappings, or changing governance posture.

## 8. QA And Gates

QA is the feedback loop, not a naming taxonomy. The approved test families are unit tests de datos, integration tests, end-to-end/system tests, data quality tests, schema tests, regression tests, and reconciliation tests. Each check must produce evidence with test name, family, stage, provider, entity, source file, checksum, expected value, observed value, failure count, decision, and evidence path.

GitHub CI validates code and specs before target-runtime data execution. It should run parser tests, adapter fixture tests, local runtime spec tests, schema/spec validation, static SQL/Python checks, generated artifact checks, security scans for secrets or dangerous operations, and PR risk reports. Local runtime certification validates portable behavior against fixtures and approved local samples. Databricks validates target-runtime behavior against representative data after approval. It should run profiling, Bronze/Silver data quality checks, reconciliation, schema drift detection, quarantine summaries, performance checks, permissions checks, and Unity Catalog lineage validation.

The valid QA decisions are `stop_pipeline`, `quarantine_data`, and `warn`. A `stop_pipeline` decision blocks the current run. `quarantine_data` isolates a file or row and allows valid data to continue. `warn` allows continuation but requires visible evidence.

## 9. Local Runtime, Databricks, And Unity Catalog Requirements

Contracts and canonical models are the source of truth. The local runtime is the fast certification loop for functional correctness and portability. Databricks is the governed target runtime for representative validation and execution. Bronze, Silver, quarantine, QA evidence, and manifests must be stored in governed locations when running in Databricks and later registered or exposed through Unity Catalog. Tables and volumes must be designed so provider, entity, source file, source checksum, source row reference, ingestion run, adapter version, and schema version remain traceable.

Unity Catalog is the Databricks governance target. The migration must be able to answer which provider, file, adapter version, and run produced a Silver record both in local certification evidence and in Databricks validation evidence. The platform must also support permissions, auditability, and lineage inspection. If Spark Declarative Pipelines, Delta Lake OSS, OpenLineage, Marquez, dlt-meta, Databricks Asset Bundles, or Lakeflow Declarative Pipelines are used later, their specs must remain versioned in Git and reviewed through the same PR/HITL process.

## 10. Human In The Loop

Human approval is required when a decision changes data meaning or governance posture. Required approval points are source coverage, field mappings with low confidence, ambiguous types, identifiers with leading zeros, PII classification, quarantine rules, Silver required columns, candidate keys, local runtime dependency installation, Docker/Marquez usage, OpenLineage transport, and Databricks validation execution. Approval records must include owner, decision, date, evidence path, impacted provider/entity, environment, and next action.

The agent may recommend, summarize, and prepare review packets. It must not silently approve mappings, infer identity resolution, downgrade PII classification, or promote data beyond Silver.

## 11. Acceptance Criteria

This PRD is satisfied when the repository contains the operating spec, the skill strategy, a minimal `.agent/skills/` structure, compact plan prompts for the five planning tasks, and a clear path from provider discovery to local runtime certification to Unity Catalog-governed Silver validation. The team must be able to explain what happens in GitHub, what happens locally, what happens in Databricks, what requires human approval, what is out of scope, and how QA evidence drives the next iteration.
