---
name: adapter-contract-reviewer
description: "Review whether provider adapter design can implement approved provider specs and canonical model specs with traceable mappings, quarantine behavior, lineage, and HITL gates."
user-invocable: false
---

# Adapter Contract Reviewer

Use this skill when reviewing whether adapter design can faithfully implement approved provider specs and canonical model specs. This is a reviewer skill: it does not discover provider metadata and does not design the canonical model; it checks that parser choice, mappings, contracts, quarantine behavior, and HITL points are implementable and traceable.

Validate that each adapter consumes declarative YAML metadata instead of hardcoded provider assumptions. Confirm that each spec declares source binding, parser strategy, row key, mapping rules, type handling, lineage fields, quarantine decisions, drift findings, and approval points. Confirm that a provider-specialized parser already exists from discovery, has fixtures and tests, and can be reused by the adapter implementation instead of being reinvented. Confirm that parser and adapter are implementation components inside the Raw/Bronze -> Silver flow, not extra conceptual layers. Confirm that Bronze keeps enough source evidence to reprocess Silver when mappings or schemas change.

Adapter contracts must be runtime-neutral. Review whether the adapter can run through the local runtime interfaces before Databricks rollout: provider parser interface, Bronze writer interface, canonical mapper interface, Silver writer interface, quarantine writer interface, QA evidence writer interface, lineage emitter interface, and runtime adapter interface. Do not approve adapter readiness when Databricks workspace paths, Unity Catalog objects, Lakeflow APIs, bundle layout, or cloud credentials are embedded into the adapter logic.

Do not approve adapter readiness when the provider parser is missing, untested, unable to parse representative provider fixtures, or unable to support local runtime certification. Do not approve silent type coercion, invented values, hardcoded provider paths, hidden row loss, runtime-specific model semantics, or semantic mappings without human approval. Do not introduce post-Silver scope.

Return a concise report with status, impacted provider/entity, YAML spec path, adapter readiness, findings, missing evidence, required human decisions, and recommended next action.
