# Plan 04.5 Local Data Workbench And Model Evolution

## Purpose

Plan 04.5 turns Plan 04 local runtime certification into a repeatable local modeling workbench. The plan owns PostgreSQL, dbt Core, local tests, model evolution snapshots, drift resolution, HITL write-back, and the iterative path from Silver normalization to business-question SQL outputs.

This is not a loose Markdown note. It is the active operating plan for local model evolution after Plan 04. It must be propagated through the PRD, filesystem conventions, skill strategy, model registry, tests, and trace logs.

## Scope

The plan is local-only and uses PostgreSQL as the HITL review database. dbt Core is the preferred local SQL orchestration and testing tool for material normalization iterations once its project layout, profiles, and tests are declared. Spark/Delta remain optional validation tools documented in `docs/local_runtime_macos_requirements.md`, not the modeling authority for Plan 04.5.

The plan starts from approved Bronze/Silver contracts and iterates toward tested SQL that answers every business question in `metadata/model_specs/impact/business_question_profiles.yaml`. Local Gold candidates may be introduced only when they are derived from resolved business questions and protected by dbt/PostgreSQL tests. Gold is not provider-driven and is not a Databricks production serving model in this plan.

Plan 04.5 reads:

- `metadata/provider_specs/**`
- `metadata/model_specs/bronze/bronze_contract.yaml`
- `metadata/model_specs/silver/**`
- `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`
- `metadata/model_specs/impact/business_question_profiles.yaml`
- `metadata/runtime_specs/local/**`
- `src/**`
- `tests/**`

Plan 04.5 writes only to approved repository roots: `metadata/`, `docs/`, `.agent/skills/`, `src/`, `tests/`, `reports/`, and `logs/`.

## Required Templates

Plan 04.5 agents must use these templates when creating new iteration evidence:

- `.agent/spec_templates/model_iteration_packet.template.yaml`
- `.agent/spec_templates/normalization_probe.template.yaml`
- `.agent/spec_templates/semantic_discovery_issue.template.yaml`

The iteration packet template prevents partial handoffs. The normalization probe template is the default response to strange data: decompose, test, measure, and decide. The semantic discovery issue template is reserved for ambiguity, high risk, or HITL-required cases that remain after a probe or cannot safely be probed.

## Authority And Source Of Truth

The modeling authority order is:

1. Business question intent in `metadata/model_specs/impact/business_question_profiles.yaml`.
2. Provider evidence in `metadata/provider_specs/**`.
3. Bronze/Silver contracts in `metadata/model_specs/bronze/` and `metadata/model_specs/silver/`.
4. Runtime/deploy contracts in `metadata/runtime_specs/local/`.
5. Versioned model snapshots in `metadata/model_specs/evolution/V0_N/`.
6. Generated SQL/dbt artifacts and PostgreSQL deployments.

PostgreSQL and dbt execute the model; they do not replace metadata as the durable source of truth.

## Central Model Registry

Every material modeling iteration must create a complete snapshot under:

```text
metadata/model_specs/evolution/V0_N/
```

Each snapshot must include:

- `model_snapshot.yaml`: header, scope, source contracts, quality gates, rollback, and guardrails.
- `postgres_schema.sql`: complete PostgreSQL DDL image generated from declarative contracts.
- `business_question_registry`: the exact `business_question_profiles.yaml` version used by the snapshot, including version id, checksum, question count, field decision count, and completion status.
- `iteration_packet.yaml`: exhaustive state packet that tells the next agent iteration what changed, what failed, what passed, what data evidence exists, what rollback target is safe, and which business questions advanced.
- Optional later files for dbt manifests, local Gold SQL, normalization specs, and query answer specs when dbt is approved for that iteration.

The pipeline does not maintain backward compatibility during Plan 04.5. Instead, every material change is a clean full-snapshot redeploy with complete tests. Rollback means redeploying the previous approved `V0_N` snapshot, not hand-editing tables.

Whenever `business_question_profiles.yaml` changes, the active model snapshot must record a new `BQ_V0_N` registry version. A model snapshot is incomplete if it cannot identify which business-question version it implements.

## Iteration Packet Contract

Every material Plan 04.5 iteration must leave an iteration packet under the active snapshot folder:

```text
metadata/model_specs/evolution/V0_N/iteration_packet.yaml
metadata/model_specs/evolution/V0_N/business_question_registry.yaml
metadata/model_specs/evolution/V0_N/db_state_snapshot.yaml
metadata/model_specs/evolution/V0_N/dbt_artifacts_manifest.yaml
metadata/model_specs/evolution/V0_N/lineage_summary.yaml
metadata/model_specs/evolution/V0_N/qa_gate_summary.yaml
metadata/model_specs/evolution/V0_N/rollback_plan.yaml
```

The files may start as planned metadata before dbt/OpenLineage are approved, but their absence must block promotion to the next major model iteration once data loading or dbt execution begins.

The iteration packet must include:

- `iteration_id`: active `V0_N` snapshot id.
- `previous_iteration_id`: rollback target or `none`.
- `business_question_registry_version`: active `BQ_V0_N`.
- `change_intent`: business question, drift domain, entity, table, or test gap being addressed.
- `metadata_inputs`: provider specs, Bronze/Silver specs, runtime specs, model snapshots, and HITL records read.
- `database_feedback`: PostgreSQL schemas, tables, columns, types, constraints, indexes, row counts, null rates, domain value summaries, failed casts, duplicate keys, orphan relationships, empty-table checks, and checksums or fingerprints.
- `dbt_feedback`: `manifest.json`, `run_results.json`, `catalog.json`, compiled SQL, model statuses, test statuses, execution timing, and changed node list when dbt is introduced.
- `lineage_feedback`: dbt `ref()`/`source()` graph, OpenLineage event paths when approved, input datasets, output datasets, run/job ids, and SQL or source-code facets when emitted.
- `qa_feedback`: unit, integration, regression, e2e, dbt, SQL-answer, data quality, reconciliation, and rollback checks.
- `hitl_feedback`: pending, applied, rejected, or deferred decisions from `review.hitl_decisions` and related evidence paths.
- `business_question_progress`: state of each affected question as `unanswered`, `partial`, `answered`, or `deferred_hitl`.
- `next_action`: `continue_iteration`, `rollback`, `request_hitl`, `create_pr`, or `stop`.

An agent may pass to the next iteration only when the packet can answer: which business question improved, which model changed, which SQL proves it, what broke, what data evidence supports the decision, what tests passed, what HITL decision is still needed, and how to restore the last stable snapshot.

## Real-Time Feedback Loop

Plan 04.5 should feel interactive, but it must stay auditable. The feedback loop is:

1. PostgreSQL feedback after every deploy, load, dbt run, rollback, or HITL edit.
2. dbt artifact feedback after every dbt parse, compile, run, test, build, or docs generation.
3. OpenLineage/Marquez feedback after runs only when HITL has approved lineage emission and local services.
4. Business-question feedback after SQL-answer tests compare observed outputs to expected grain and acceptance criteria.

PostgreSQL is the immediate read/write source for HITL review. dbt artifacts are the authoritative execution metadata for model graph, test result, compiled SQL, and catalog/schema evidence. OpenLineage and Marquez are lineage observers, not modeling authorities.

## DoR

- Local PostgreSQL database exists and is reachable from terminal.
- `docs/local_postgres_workbench_deploy.md` dry-run works.
- Current model snapshot exists under `metadata/model_specs/evolution/V0_N/`.
- Bronze, Silver, provider-to-Silver matrix, business-question profiles, model evolution snapshots, and local runtime specs pass spec tests.
- dbt Core usage has a declared local-only project/profile strategy before dbt models are introduced.
- HITL has approved any dependency or service start required for the iteration.
- No production data, cloud jobs, Terraform, bundles, or Databricks execution are required.

## Execution Model

All validation and correction happens through terminal-driven CI/CD-style commands. The high-level sequence is:

1. Update declarative metadata first.
2. Version the active business-question registry when `business_question_profiles.yaml` changes.
3. Generate or update the full model snapshot and PostgreSQL DDL.
4. Create or refresh `iteration_packet.yaml`.
5. Run dry-run deploy.
6. Apply to local PostgreSQL only after HITL approval.
7. Capture `db_state_snapshot.yaml`.
8. Load local fixture or approved sample data into staging/review tables.
9. Run dbt/PostgreSQL normalization and tests when dbt is approved for the iteration.
10. Capture `dbt_artifacts_manifest.yaml` and dbt target artifact references.
11. Capture `lineage_summary.yaml` when OpenLineage/Marquez is approved.
12. Run unit, integration, regression, and e2e checks.
13. Record drift results in `review.drift_*`.
14. Let HITL update `review.hitl_decisions` through DBeaver or SQL.
15. Update `business_question_profiles.yaml` when a normalization decision changes business meaning.
16. Add or update SQL that answers each resolved business question.
17. Write `qa_gate_summary.yaml` and `rollback_plan.yaml`.
18. Append trace evidence and prepare PR only after tests pass.

## Normalization Depth

Plan 04.5 is intentionally iterative. A business question may require multiple depth levels:

- Field-level cleanup: type, nullability, enum, code, date, and unit normalization.
- Entity-level reconciliation: row grain, source lineage, duplicate handling, relationship confidence, and sparse field behavior.
- Cross-provider normalization: provider-specific semantics mapped into common Silver concepts.
- Local Gold/query layer: dbt/PostgreSQL SQL that answers resolved business questions from normalized Silver or approved local Gold candidates.

The agent must resolve data field by field, column by column, entity by entity, provider by provider. It must not apply one-off SQL patches outside the deploy/test pipeline.

## Chaotic Discovery Guardrails

The agent should expect disorder. If it discovers nested data inside scalar-looking columns, source fields that belong to another entity, mixed grain, duplicate keys, orphan relationships, unsafe casts, unit/code ambiguity, temporal ambiguity, PII/PHI exposure, or sparse unmapped fields, it should first decompose the problem into a normalization probe unless the risk is clearly unsafe.

The default flow is:

1. Isolate the smallest provider/entity/field slice that shows the problem.
2. State a normalization hypothesis.
3. Create a scratch transition table or temp table to evaluate the hypothesis.
4. Measure counts, nulls, domains, failed casts, duplicate keys, orphan relationships, nested payload counts, and entity mismatch counts.
5. Compare the probe output to the target business question and Silver contract.
6. Promote the change into the next `V0_N` snapshot only when tests and evidence support it.
7. Create a semantic discovery issue only when meaning, ownership, privacy, or business impact remains ambiguous.

Allowed actions are intentionally bounded:

- Preserve the source value in Bronze or review tables.
- Quarantine the affected rows or fields.
- Map to an existing Silver column only when provider/model specs support it.
- Create scratch or temp transition tables to evaluate candidate normalizations.
- Propose a new review table, Silver column, or entity through a new `V0_N` snapshot after probe evidence exists.
- Request HITL when semantics, privacy, clinical meaning, financial meaning, or entity ownership is ambiguous.
- Roll back when the active iteration breaks a previously answered business question or violates a registry contract.

Forbidden actions:

- Treat scratch probes as durable model history.
- Promote probe SQL without tests, metrics, and snapshot updates.
- Silently flatten nested payloads into unrelated columns without probe evidence.
- Move data to another entity without evidence and HITL when ownership is unclear.
- Drop fields because they are sparse or inconvenient.
- Coerce dates, codes, units, identifiers, or money values without tests and evidence.
- Patch PostgreSQL manually without updating the snapshot, DDL, tests, and iteration packet.

## Normalization Probe Contract

Normalization probes are encouraged. They let the agent be bold without being reckless. A probe may create temporary tables or timestamped `scratch` schema transition tables to evaluate a candidate normalization before changing durable model contracts.

Each probe must record:

- `probe_id`, `iteration_id`, and related business question ids
- provider, source entity, source fields, target entity candidate, and target fields candidate
- normalization hypothesis
- scratch table or temp table used
- SQL or handler path that created the probe
- metrics before and after the transformation
- pass/fail result against business-question and Silver-contract expectations
- decision: `promote_to_snapshot`, `revise_probe`, `quarantine`, `request_hitl`, or `rollback`

Promotion from probe to model requires updating the relevant metadata, DDL, tests, iteration packet, and rollback plan. A probe that fails is useful evidence; it should narrow the next step rather than automatically stop the plan.

## Quality Metrics

Each material iteration must report these metrics in `qa_gate_summary.yaml` or referenced evidence:

- business questions answered, partial, unanswered, and HITL-deferred
- source-to-Bronze row counts by provider/entity
- Bronze-to-review/Silver row counts by entity
- rejected, quarantined, and warning counts
- null rates for business-critical fields
- accepted-value coverage for statuses, gender, coverage, codes, and other domains
- duplicate key counts and candidate-key stability
- orphan relationship counts
- failed cast counts
- nested payload detection counts
- entity mismatch counts
- unmapped or sparse field counts
- dbt model/test pass, fail, warn, skip counts when dbt is introduced
- regression count against the previous approved snapshot
- rollback dry-run status when rollback is applicable

The minimum acceptable state to advance is not "all metrics are perfect." It is "all metric movement is explained, tested, and tied to a business question, HITL deferral, or rollback decision."

## dbt And PostgreSQL Requirements

PostgreSQL is the local read/write workbench and HITL interaction layer. dbt Core is the expected local mechanism for repeatable SQL model execution, model tests, documentation, and regression checks once its project is declared.

dbt work must remain local and metadata-aligned:

- dbt models must be derived from Bronze/Silver/model evolution contracts.
- dbt tests must cover accepted values, not-null expectations where approved, relationships, uniqueness, row-count reconciliation, and business-question SQL outputs.
- dbt artifacts must be captured by path and checksum after every material run.
- `manifest.json` must be used to inspect model graph, sources, refs, compiled SQL, tests, exposures, and semantic resources when present.
- `run_results.json` must be used to inspect execution status, failures, timing, and executed nodes.
- `catalog.json` must be used to inspect database-observed schemas, columns, types, and descriptions after docs generation.
- dbt must not encode hidden source-of-truth decisions that are absent from metadata.
- PostgreSQL deploys must remain idempotent and rollbackable through complete snapshots.

## Advancement Gate

Before moving from `V0_N` to `V0_N+1`, the agent must validate the active iteration packet. Advancement is blocked when any of these are missing:

- active snapshot id and previous rollback target
- active `BQ_V0_N` registry version and checksum
- PostgreSQL state snapshot
- dbt artifact manifest once dbt is introduced
- lineage summary when lineage emission is approved
- QA gate summary
- rollback plan
- business-question progress state
- HITL status for unresolved semantic or data-quality decisions

The agent must choose one next action:

- `continue_iteration`: tests pass enough to perform the next planned normalization step.
- `rollback`: the active model is fractured or a regression breaks a previously answered business question.
- `request_hitl`: semantics, data quality, dependency use, or service start require human approval.
- `create_pr`: the snapshot is stable, QA has passed, and governance permits review.
- `stop`: required evidence is missing or repeated failures would require weakening checks.

## DoD

Plan 04.5 is complete only when all of the following are true:

- Every business question in `business_question_profiles.yaml` is resolved with tested local SQL output, or has an explicit HITL-approved deferral.
- The active `V0_N` snapshot is complete and internally documented.
- The active snapshot records the exact `BQ_V0_N` business-question registry version it implements.
- The active snapshot includes a complete iteration packet and related feedback summaries.
- PostgreSQL deploy is idempotent and verified.
- dbt/PostgreSQL normalization tests pass for the active model iteration when dbt is introduced.
- Bronze contract, Silver contracts, runtime specs, business-question profiles, model snapshots, and generated SQL remain aligned.
- Drift tables and HITL decisions can explain every normalization change.
- Tests cover schema, integration, regression, local e2e deploy behavior, and SQL outputs for business questions.
- Rollback path to the previous approved snapshot is explicit and stable.
- No Databricks parity claim, production dependency, cloud deployment, or unapproved serving model is introduced.
