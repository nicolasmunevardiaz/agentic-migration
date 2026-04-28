---
name: provider-spec-generator
description: "Create declarative provider/entity YAML specs from raw provider folders, column dictionaries, parser evidence, schema drift, and PII signals."
user-invocable: false
---

# Provider Spec Generator

## Purpose

Use this skill when provider exports and `column_dictionary.md` files must be converted into declarative YAML specs and an executable provider parser. This is a generator skill: it parses source evidence, standardizes metadata, produces provider/entity contracts, and creates the provider-specific parser that downstream modeling and adapter work can trust.

## Operating Focus

Work as a provider specialist. Process exactly one provider per iteration. Do not switch providers, create cross-provider canonical decisions, or work on unrelated plans during the same iteration. Finish, block, or hand off the current provider before starting another provider.

## Required Inputs

Read provider folders under `data_500k/`, every available `column_dictionary.md`, and the current topology or PRD. The known providers are `data_provider_1_aegis_care_network`, `data_provider_2_bluestone_health`, `data_provider_3_northcare_clinics`, `data_provider_4_valleybridge_medical`, and `data_provider_5_pacific_shield_insurance`.

## Required Outputs

Produce one YAML spec per provider/entity under `metadata/provider_specs/<provider_slug>/<entity>.yaml`. Also produce a provider-specific parser under `src/adapters/`, synthetic parser fixtures under `tests/fixtures/`, provider parser tests under `tests/adapters/`, a provider-level drift summary, a human-review queue for ambiguous mappings, missing entities, uncertain parser settings, PII concerns, and relationship risks, and append trace entries to `logs/provider_discovery/<provider_slug>.md`.

## YAML Spec Contract

Each YAML must declare provider identity, source type, upload partition, filetype, file extension, entity, expected file patterns, parser profile, source row key, canonical row key, field mappings, relationship hints, PII classification signals, known drift, quarantine rules, QA expectations, and `needs_human_review` reasons. Use `.agent/spec_templates/provider_entity_profile.template.yaml` as the shape. The parser profile must be executable by the provider parser; do not leave parser details as aspirational documentation.

## Provider Parser Contract

The provider parser is mandatory. It must read the provider's actual file shape or synthetic fixtures that faithfully mirror that shape, consume the generated YAML specs, and emit deterministic records with `values_by_header` and `values_by_canonical`. It must handle provider-specific file format details such as nested structures, flattened keys, delimiters, row grain, status fields, and source row keys. It must fail clearly for malformed files, wrong entity/resource types, unsupported parser profiles, and missing source row keys. It must avoid raw PII in fixtures and logs.

## Checks

Validate that the provider dictionary is parsed into structured metadata rather than copied as prose. Validate that the provider parser can read at least synthetic fixtures for each discovered entity, and local sampled data when available. Detect row-key drift across providers, filetype drift, header-to-canonical mapping drift, duplicate source headers mapping to multiple canonical fields, missing canonical fields, unexpected extra source fields, payer-only entity limitations, and clinical-only entity expectations. Capture whether each entity appears ready for adapter implementation.

## Non-Negotiables

Do not finish provider discovery without an executable provider parser or an explicit HITL blocker. Do not infer final Silver semantics. Do not expose raw PII in examples. Do not hardcode provider paths inside adapter logic. Do not collapse similar fields without evidence. Do not treat file-level failures, row-level failures, and schema ambiguity as the same issue. Do not weaken parser tests to make uncertain parsing pass. Do not purge, delete, reorder, or rewrite trace logs.

## Trace Logging

Append short entries to `logs/provider_discovery/<provider_slug>.md` using the shared format from `docs/agentops_filesystem_conventions.md`. Each entry must include timestamp, plan id, provider slug, skill name, event, artifact path, and one short note. If a log entry is wrong, append a correction entry.

## DoD

The skill is done only when each discovered provider/entity has a YAML spec or an explicit blocked reason, each YAML has a stable parser profile and source-to-canonical mapping section, a provider-specialized parser and parser fixtures exist or a HITL blocker explains why they cannot be produced safely, parser tests prove positive parsing and failure behavior, each drift is recorded with impact, each PII-sensitive field is flagged, each uncertainty is routed to Human in the Loop, and the provider trace log has a completed or blocked entry.

## Output Format

Return a concise report with generated YAML paths, parser path, fixture paths, parser test paths, trace log path, provider/entity readiness, drift findings, PII findings, blocked items, human decisions required, and recommended next action.
