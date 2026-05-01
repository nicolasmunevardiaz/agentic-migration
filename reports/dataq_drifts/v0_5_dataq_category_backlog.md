# V0_5 Data Quality Category Backlog

Report id: `DATAQ_CATEGORY_BACKLOG_V0_5_2026_04_30`
Source evidence: `reports/dataq_drifts/v0_5_derived_dataq_drift_matrix.tsv`
and PostgreSQL catalog review of 32 `derived` dbt views.
Scope: evidence and remediation design only. No drift is fixed here.

## Why Category-First

The same data-quality failure appears across several entities. Resolving by
table first would duplicate logic and increase the risk of inconsistent SQL.
This backlog groups drifts by reusable data-quality category first, while each
category still keeps provider, entity, and field evidence.

Operational rule: resolve a data-quality category with one reusable SQL pattern
or macro family, then apply it to the affected provider/entity/field slices.

## Exhaustive Review Coverage

The category pass reviewed all current V0_5 derived entities:

| Entity family | dbt derived views reviewed | Main category surfaces |
| --- | ---: | --- |
| patients | 3 | Completeness, Validity, Consistency |
| coverage | 4 | Completeness, Uniqueness, Validity |
| encounters | 5 | Completeness, Consistency, Timeliness |
| conditions | 5 | Consistency, Validity |
| observations | 3 | Completeness, Validity |
| medications | 7 | Completeness, Consistency, Timeliness |
| cost_records | 5 | Completeness, Consistency, Validity, Timeliness |
| Total | 32 | All category groups |

Catalog evidence: all 32 derived outputs are PostgreSQL views. The schema
contains provider-scoped fields in most analytical outputs, many relationship
columns in fact and summary views, and temporal/numeric columns concentrated in
coverage, encounter, observation, medication, and cost models.

## Category Rollup

| Canonical category | Drift families | Current drift rows | Max severity | Primary resolution mode |
| --- | ---: | ---: | --- | --- |
| Completeness | 5 | 43 | Critical | Required/optional field policy by provider and field |
| Uniqueness | 1 | 5 | High | Deterministic keys and survivor/merge rules |
| Validity | 4 | 15 | Critical | Type, format, domain, and temporal validation macros |
| Accuracy | 2 | 0 direct SQL failures | HITL | External/HITL confirmation before correcting meaning |
| Consistency | 5 | 52 | Critical | Reference, code, and semantic standardization |
| Timeliness | 3 | 10 | Critical | Local/UTC time design plus chronology availability checks |

Counts can overlap because some findings belong to a primary category and a
secondary category. Example: missing `medication_datetime` is Completeness, but
the remediation belongs to Timeliness once a provider-local timestamp source is
approved.

## Recommended Resolution Order

1. **Validity and Timeliness foundation**

   Define canonical date/timestamp handling before fixing fields that depend on
   chronology. For provider-local timestamps, use:

   - `*_raw`: original source value if retained by the source model.
   - `*_local_ts`: parsed provider-local timestamp.
   - `provider_timezone`: IANA time zone or approved provider time zone code.
   - `*_utc_ts`: UTC-normalized timestamp.
   - `*_parse_status`: valid, missing, ambiguous, invalid, or inferred.

   Standard display format for provider-local timestamps should be
   `YYYY-MM-DD HH:MM:SS`. UTC should be produced through an explicit provider
   timezone mapping, not by relying on PostgreSQL session timezone rendering.

2. **Consistency: reference normalization**

   Normalize member, encounter, condition, and medication references before
   completeness or analytical rules depend on joins. Store unresolved references
   in audit/bridge outputs rather than dropping records.

3. **Completeness policy**

   Decide required versus optional fields by provider/entity/field. This avoids
   treating insurance-only provider gaps as clinical defects and avoids forcing
   optional vitals such as BMI to behave like required fields.

4. **Uniqueness and survivor rules**

   Resolve duplicate coverage period keys with deterministic key construction,
   exact-duplicate merge rules, and source-row tiebreakers.

5. **Consistency: code and semantic variants**

   Normalize code punctuation/case/source hints and preserve variant dimensions
   until HITL approves canonical display/meaning.

6. **Accuracy**

   Use SQL to detect suspicious values, but require HITL or authoritative
   source confirmation before changing clinical, financial, or business meaning.

## Category Backlog

### Completeness

| Category drift id | Issue family | Providers | Entities/fields | Evidence | Resolution design | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DQCAT-COMP-001 | Entity availability gap | Pacific Shield | encounters, conditions, observations, medications, cost_records | Pacific has 0 rows in these derived entities while patients and coverage are populated. | Build provider/entity availability rules so missing unsupported entities do not fail as defects. | Open |
| DQCAT-COMP-002 | Missing temporal fields | Aegis, BlueStone, NorthCare, ValleyBridge | encounter_datetime, medication_datetime, cost_date, coverage dates | 10 critical/high nullability drifts across encounter, medication, cost, and coverage outputs. | Apply required/optional policy, then route approved date sources into local/UTC timestamp pattern. | Open |
| DQCAT-COMP-003 | Sparse observation components | Aegis, BlueStone, NorthCare, ValleyBridge | height, weight, BP, pulse, temperature, BMI | 24 component-presence drifts; BMI is the sparsest component. | Keep component completeness flags by provider; do not infer missing clinical vitals. | Open |
| DQCAT-COMP-004 | Missing cost amount | Aegis, BlueStone, NorthCare, ValleyBridge | cost_amount | 4 amount-nullability drifts. | Preserve amount-source dimension and create requiredness rule by cost record type/source field. | Open |
| DQCAT-COMP-005 | Partially unknown coverage periods | all providers | coverage_start_date, coverage_end_date | undated and end-date-only coverage rows across providers. | Separate unknown/open/end-date-only states before computing period duration or enrollment gaps. | Open |

### Uniqueness

| Category drift id | Issue family | Providers | Entities/fields | Evidence | Resolution design | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DQCAT-UNIQ-001 | Duplicate coverage period keys | all providers | provider/member/plan/period key | 5 provider-level duplicate-key drifts; max affected provider is Pacific Shield with 21155 rows. | Generate deterministic period keys, merge exact duplicates, and keep source-row tiebreaker lineage. | Open |

### Validity

| Category drift id | Issue family | Providers | Entities/fields | Evidence | Resolution design | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DQCAT-VAL-001 | Provider-local timestamp standard | all providers with temporal facts | encounter_datetime, medication_datetime, cost_date, observation_datetime, loaded_at | Catalog shows typed date/timestamp columns, but no explicit local timestamp plus UTC pair. | Introduce standard temporal contract in next probe: raw, local, provider timezone, UTC, parse status. | Open |
| DQCAT-VAL-002 | Implausible typed dates | BlueStone, NorthCare, Pacific Shield | birth_date, coverage_start_date, coverage_end_date | 4 temporal-validity drifts. | Add parser/status quarantine for invalid bounds before dimensional publish. | Open |
| DQCAT-VAL-003 | Code/domain format mismatch | BlueStone, NorthCare, ValleyBridge | condition_source_code | 3 provider-level source-code hint mismatches at 100% of condition rows. | Add provider-specific source-code domain mapping and accepted-format tests. | Open |
| DQCAT-VAL-004 | Numeric amount validity | all cost providers | cost_amount | Numeric casts exist and no nonpositive amounts were observed. | Keep guardrail test for positive numeric amounts; no remediation required now. | Monitoring |

### Accuracy

| Category drift id | Issue family | Providers | Entities/fields | Evidence | Resolution design | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DQCAT-ACC-001 | Clinical meaning cannot be corrected by SQL alone | all clinical providers | condition codes, medication codes, vitals | SQL can detect format/consistency issues but cannot prove clinical correctness. | Escalate semantic changes to HITL with examples aggregated by code/provider, not row samples. | Open |
| DQCAT-ACC-002 | Financial meaning cannot be corrected by SQL alone | all cost providers | cost_amount, cost_date, cost source role | Missing dates/amounts and cost source roles affect interpretation. | Require approved business/financial rule before imputing or deriving cost chronology/amounts. | Open |

### Consistency

| Category drift id | Issue family | Providers | Entities/fields | Evidence | Resolution design | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DQCAT-CONS-001 | Orphan member references | all clinical/cost providers | member_reference | Orphan references appear in encounters, conditions, medications, and cost records. | Normalize final reference segment and provider-scoped member keys before joins. | Open |
| DQCAT-CONS-002 | Orphan encounter references | all clinical/cost providers | encounter_reference | Orphan references appear in conditions, medications, and cost records. | Build encounter reference audit bridge; preserve unresolved source references. | Open |
| DQCAT-CONS-003 | Orphan condition references | all medication providers | condition_reference | Medication condition reference drift appears in all clinical providers. | Build condition reference audit bridge after member/encounter normalization. | Open |
| DQCAT-CONS-004 | Code and description variants | all medication providers | medication_source_code, medication_description | 7 semantic-variant drifts; max raw-code variants 4 and description variants 5. | Keep variant dimensions; add canonical-code/description approval workflow. | Open |
| DQCAT-CONS-005 | Conflicting patient demographics | all patient providers | gender, birth_date | Gender conflicts in all providers; birth-date conflicts in BlueStone and Pacific Shield. | Add source precedence/survivor rules and conflict audit outputs. | Open |

### Timeliness

| Category drift id | Issue family | Providers | Entities/fields | Evidence | Resolution design | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DQCAT-TIME-001 | Local time zone missing from temporal contract | all providers | all `*_datetime`, `*_date`, `loaded_at` fields | Current outputs use typed Postgres dates/timestamps but do not expose provider timezone and UTC-normalized pairs for all business timestamps. | Add provider timezone mapping and UTC derivation in a normalization probe. | Open |
| DQCAT-TIME-002 | Chronology unavailable | Aegis, BlueStone, NorthCare, ValleyBridge | encounter_datetime, medication_datetime, cost_date | Several providers have 100% missing chronology for key entities. | Do not infer; require approved source field before deriving month/freshness logic. | Open |
| DQCAT-TIME-003 | Freshness not yet profiled | all providers | loaded_at, source_lineage_ref | This pass mapped data quality, not ingestion SLA freshness. | Add a separate freshness report using max loaded_at and source file lineage by provider/entity. | Open |

## Exhaustive Validation Notes

- The expensive global count across many nested views was started and then
  stopped because the derived layer is view-based and the query did not return
  in a reasonable time. This is itself a useful runtime finding: future
  exhaustive drift validation should run as dbt models/tests or staged audit
  tables rather than one monolithic SQL query.
- The category backlog is built from provider-level aggregate evidence only.
  It intentionally excludes row-level values and PHI/PII examples.
- No V0_5 model behavior, dbt SQL, or PostgreSQL data was changed.

## Next Validation Artifact

The next artifact should be a dbt audit package that materializes category
metrics into tables such as:

- `dq_category_completeness_metrics`
- `dq_category_uniqueness_metrics`
- `dq_category_validity_metrics`
- `dq_category_consistency_metrics`
- `dq_category_timeliness_metrics`

Those tables should be generated from reusable macros and tested with stable
thresholds before any remediation probe begins.
