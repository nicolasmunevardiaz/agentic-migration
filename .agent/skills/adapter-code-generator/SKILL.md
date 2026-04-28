---
name: adapter-code-generator
description: "Generate provider parser and adapter code, fixtures, and local tests from approved provider specs, canonical model specs, and adapter contract reviews for Raw/Bronze to Silver migration."
user-invocable: false
---

# Adapter Code Generator

Use this skill after provider specs, canonical model specs, and adapter contract review are approved. This is a generator skill: it creates implementation artifacts from declared contracts. It should not invent mappings, change model semantics, or bypass Human in the Loop decisions.

Read `metadata/provider_specs/<provider_slug>/<entity>.yaml`, the provider-specialized parser from `src/adapters/`, parser fixtures from `tests/fixtures/`, `metadata/model_specs/bronze/bronze_contract.yaml`, `metadata/model_specs/silver/<entity>.yaml`, `metadata/model_specs/mappings/provider_to_silver_matrix.yaml`, adapter readiness reports, runtime interface contracts when available, and available fixtures. Reuse and extend the provider parser from discovery; do not replace it with a new hidden parser. Generate adapter code that consumes declarative YAML metadata rather than hardcoded provider assumptions.

The generated adapter must preserve source evidence in Bronze, produce Silver according to approved model specs, write quarantine records for invalid rows or files, emit QA evidence hooks, and keep provider, entity, source file, checksum, source row reference, ingestion run, schema version, spec version, and adapter version traceable. It must target runtime-neutral interfaces so the same contracts can be certified locally before a Databricks runtime adapter is generated.

Generate focused fixtures and tests with positive and negative cases. Positive fixtures prove accepted files can parse and map using the provider-specialized parser. Negative fixtures prove malformed files, wrong entity/resource types, missing row keys, missing required fields, unsafe casts, and schema drift are quarantined or stopped according to the approved decision.

Do not silently coerce types, invent missing values, embed local absolute paths, expose raw PII in fixtures, create production jobs, hardcode Databricks workspace paths, bind canonical semantics to Unity Catalog, or generate post-Silver logic. If a mapping, parser, runtime, or dependency decision is uncertain, stop and produce a Human in the Loop question instead of guessing.

Return a concise report with generated paths, impacted provider/entity, assumptions used, tests generated, risks, blocked items, human decisions required, and recommended next action.
