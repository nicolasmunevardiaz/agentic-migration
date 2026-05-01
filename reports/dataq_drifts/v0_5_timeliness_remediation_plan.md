# V0_5 Timeliness Remediation Plan

Plan id: `DATAQ_TIMELINESS_REMEDIATION_V0_5_2026_04_30`
Category: Timeliness
Contract: `metadata/model_specs/data_quality/contracts/temporal_contract.yaml`
Status: iteration 2 complete; explicit source-row offset remediation applied.

## Scope

This iteration does not infer local time zones or UTC values. It creates the
neutral standardization surface and applies only row-level UTC derivation when
the source temporal value carries an explicit offset or `Z` suffix. Provider
IANA timezone remains a fallback that requires approval before use.

## Implemented dbt Models

| Model | Purpose |
| --- | --- |
| `data_quality.dq_provider_timezone_contract` | Provider timezone registry, currently all `timezone_pending`. |
| `data_quality.dq_standardized_temporal_fields` | Raw temporal values, source-offset detection, local NTZ, UTC, and temporal authority status. |
| `data_quality.dq_timeliness_provider_field_metrics` | Provider/entity/field counts for missing, parsed, timezone pending, timezone approved, local NTZ, and UTC. |
| `data_quality.dq_timeliness_contract_violations` | Must stay empty; catches UTC derivation without approved timezone. |
| `data_quality.dq_timeliness_findings` | Open missing chronology and timezone pending findings. |

## QA Rules

The following must remain true:

- every temporal row appears in `dq_timeliness_provider_field_metrics`;
- `utc_value` may be populated only when `timezone_status in ('offset_derived', 'timezone_approved')`;
- source-row explicit offsets derive UTC without provider timezone inference;
- no provider has `timezone_approved` with null `provider_timezone`;
- provider timezone is never assigned by majority offset or provider name;
- open findings remain visible until source chronology or provider time zones are approved.

## Tests

dbt:

```text
dbt run --select data_quality
dbt test --select data_quality
dbt test --select assert_dataq_standardization_macros
dbt test --select assert_timeliness_no_utc_without_approved_timezone
dbt test --select assert_timeliness_metrics_cover_standardized_fields
```

pytest:

```text
tests/sql/test_dataq_timeliness_standardization.py
```

Expected pytest behavior:

- pass structural contract checks;
- write `artifacts/qa/dataq_timeliness_standardization_audit.jsonl`;
- assert that open timeliness findings still exist.

## Iteration 2 Verification

Applied rule:

```text
if raw temporal value has explicit offset or Z suffix:
    derive local_ntz_value and utc_value from the row value
elif provider has approved IANA timezone:
    derive utc_value from provider timezone
else:
    keep utc_value null and mark timezone_pending
```

Observed PostgreSQL metrics after dbt run:

| Status | Standardization status | Rows |
| --- | --- | ---: |
| `offset_derived` | `standardized_from_source_offset` | 2,232,815 |
| `timezone_pending` | `missing_source_temporal_value` | 3,159,048 |
| `timezone_pending` | `timezone_pending` | 643,057 |

Guardrail:

| Check | Rows |
| --- | ---: |
| UTC without offset-derived or approved timezone authority | 0 |
| Offset-derived rows with UTC | 2,232,815 |
| Offset-derived rows with local NTZ | 2,232,815 |

Remaining findings:

| Finding status | Findings | Affected rows |
| --- | ---: | ---: |
| `open_missing_temporal_value` | 19 | 3,802,105 |

The previous `open_timezone_pending` findings for parsed offset-bearing values
are closed. Remaining findings are missing-source chronology only.

## Next Timeliness Decision Required

HITL/provider approval is still needed for:

- provider IANA timezone per provider only for offsetless values;
- whether business dates should be interpreted as local midnight, date-only
  facts, or event timestamps;
- approved source field for missing encounter, medication, and cost chronology.
