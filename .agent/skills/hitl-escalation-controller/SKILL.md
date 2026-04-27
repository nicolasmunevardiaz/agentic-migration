---
name: hitl-escalation-controller
description: "Stop uncontrolled agent iteration and escalate to Human in the Loop when repeated failures, missing evidence, ambiguous semantics, scope drift, or risky decisions require a concise human decision before continuing."
user-invocable: false
---

# HITL Escalation Controller

Use this skill when an agent is repeating failed attempts, lacks required evidence, faces ambiguous data semantics, sees conflicting specs, risks scope drift, or needs a human decision before continuing. This is a stop-and-escalate control skill, not a generator or reviewer.

## Trigger Conditions

Escalate when the same provider, spec, test, adapter, PR, or Databricks readiness task has failed three times; the same error appears twice without a new diagnosis; required source information is missing; a decision changes semantics, PII/PHI classification, mappings, permissions, quarantine behavior, or Databricks execution; tests fail for unclear reasons; the active plan scope starts drifting; or the agent would need to guess to proceed.

## Required Inputs

Read the active plan, relevant skill output, changed files, trace logs, test output, reports, and any HITL records. Use the append-only logs to count attempts and identify whether the current failure is new, repeated, or unresolved.

## Non-Negotiables

Do not force progress by inventing mappings, approving semantics, weakening tests, downgrading PII/PHI, changing governance posture, bypassing QA, or creating broad speculative edits. Do not continue after escalation until a human decision or explicit unblock condition exists.

## Escalation Output

Return a concise escalation packet with `status`, `reason`, `active_plan`, `provider`, `artifact`, `failed_attempts`, `last_error`, `question_for_human`, `recommended_option`, `options`, `evidence`, and `blocked_next_action`. Keep the question specific enough that a human can answer quickly.

## Trace Logging

Append a short log entry using the active plan's trace path with `event=blocked` or `event=hitl_requested`. When a human decision is received, append `event=resumed` before continuing. Logs are append-only; do not purge, delete, reorder, or rewrite entries.

## Output Format

Use this compact shape:

```yaml
status: blocked
reason: missing_human_decision
active_plan: "<plan_id>"
provider: "<provider_slug|all>"
artifact: "<path>"
failed_attempts: 3
last_error: "<short technical error>"
question_for_human: "<specific decision needed>"
recommended_option: "<option>"
options:
  - "<option>"
  - "<option>"
  - "<option>"
evidence:
  - "<path>"
blocked_next_action: "<what must not continue>"
```
