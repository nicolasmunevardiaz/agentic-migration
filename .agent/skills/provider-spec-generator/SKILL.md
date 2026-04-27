---
name: provider-spec-generator
description: "Create declarative provider/entity YAML specs from raw provider folders, column dictionaries, parser evidence, schema drift, and PII signals."
user-invocable: false
---

# Provider Spec Generator

## Purpose

Use this skill when provider exports and `column_dictionary.md` files must be converted into declarative YAML specs. This is a generator skill: it parses source evidence, standardizes metadata, and produces provider/entity contracts that downstream modeling and adapter work can consume.

## Operating Focus

Work as a provider specialist. Process exactly one provider per iteration. Do not switch providers, create cross-provider canonical decisions, or work on unrelated plans during the same iteration. Finish, block, or hand off the current provider before starting another provider.

## Required Inputs

Read provider folders under `data_500k/`, every available `column_dictionary.md`, and the current topology or PRD. The known providers are `data_provider_1_aegis_care_network`, `data_provider_2_bluestone_health`, `data_provider_3_northcare_clinics`, `data_provider_4_valleybridge_medical`, and `data_provider_5_pacific_shield_insurance`.

## Required Outputs

Produce one YAML spec per provider/entity under `metadata/provider_specs/<provider_slug>/<entity>.yaml`. Also produce a provider-level drift summary, a human-review queue for ambiguous mappings, missing entities, uncertain parser settings, PII concerns, and relationship risks, and append trace entries to `logs/provider_discovery/<provider_slug>.md`.

## YAML Spec Contract

Each YAML must declare provider identity, source type, upload partition, filetype, file extension, entity, expected file patterns, parser profile, source row key, canonical row key, field mappings, relationship hints, PII classification signals, known drift, quarantine rules, QA expectations, and `needs_human_review` reasons. Use `.agent/spec_templates/provider_entity_profile.template.yaml` as the shape.

## Checks

Validate that the provider dictionary is parsed into structured metadata rather than copied as prose. Detect row-key drift across providers, filetype drift, header-to-canonical mapping drift, duplicate source headers mapping to multiple canonical fields, missing canonical fields, unexpected extra source fields, payer-only entity limitations, and clinical-only entity expectations. Capture whether each entity appears ready for adapter implementation.

## Non-Negotiables

Do not infer final Silver semantics. Do not expose raw PII in examples. Do not hardcode provider paths inside adapter logic. Do not collapse similar fields without evidence. Do not treat file-level failures, row-level failures, and schema ambiguity as the same issue. Do not purge, delete, reorder, or rewrite trace logs.

## Trace Logging

Append short entries to `logs/provider_discovery/<provider_slug>.md` using the shared format from `docs/agentops_filesystem_conventions.md`. Each entry must include timestamp, plan id, provider slug, skill name, event, artifact path, and one short note. If a log entry is wrong, append a correction entry.

## DoD

The skill is done only when each discovered provider/entity has a YAML spec or an explicit blocked reason, each YAML has a stable parser profile and source-to-canonical mapping section, each drift is recorded with impact, each PII-sensitive field is flagged, each uncertainty is routed to Human in the Loop, and the provider trace log has a completed or blocked entry.

## Output Format

Return a concise report with generated YAML paths, trace log path, provider/entity readiness, drift findings, PII findings, blocked items, human decisions required, and recommended next action.
