# Prespecified operational analysis plan — version 1.0

This plan applies solely to the generated dataset and is executable through `python -m src.build`. All percentages describe simulated capture or rule performance; none estimates clinical outcomes.

| Measure | Numerator | Denominator / definition | Source |
| --- | --- | --- | --- |
| Cohort size | Participants in a named module | All generated participants; modules are mutually exclusive | `participants` |
| Follow-up completion | Rows with `status='completed'` | Four planned rows per participant, also reported by cohort and target day | `followups`, `participants` |
| Field completeness | Non-null rows for a field | Rows in that field's table; conditional interpretation is separate | `reports/bi_tables/field_completeness.csv` |
| AE count | AE rows, and separately rows with `serious=1` | Counts of records, never rates per person or procedure | `adverse_events` |
| Challenge root detection | Injected `(rule_id, record_key)` pairs present in validator output | All pairs in independent challenge manifest (18) | `data/injected_errors.csv`, `reports/challenge_validation.json` |
| Rule hits / queries | Validation issues by rule | All issues in challenge; cascades retained and identified | `reports/challenge_queries.csv` |
| Query resolution | Query rows marked resolved | Query rows opened for the challenge | `discrepancy_queries` in reconciled database |
| Technical lock | Boolean pass only with no critical issues, no open critical query, nonempty registry and all three demonstration cohorts | Evaluated independently on clean, challenge and reconciled states | `reports/*validation.json`, `reports/lock_readiness.json` |

There are 1,200 expected visits by design. Completion is `completed/planned`; a missing scheduled row is also a validation failure and must not silently shrink the planned denominator in a valid build. No complete-case substitution or imputation is used for the invented score. A missed visit's score/date should be null; absent values are a capture feature, not a statement about health. No follow-up windows are specified, so the metric is status-based, not on-time completion. `field_completeness.csv` includes deliberately nullable columns and should not be read as a pass/fail table on its own.

Challenge detection is an exact pair match. An incorrect operation date can raise one chronology issue and four due-date issues; hence 18 root errors produce 30 rule hits. Count each root once for detection. The manifest and clean truth must not be read by the validator. A zero on this controlled challenge is a software check only and cannot characterize false negatives or generalize to clinical data. SQL constraints and validation complement one another; an unexercised rule remains unproven by the 18-case result.

The dashboard and five BI CSV tables display only aggregate operational metrics. The small aggregate AE cells are fictional, so no inference or clinical comparison is appropriate. No p values, confidence intervals, model training, subgroup clinical claims, or statistical hypothesis testing are included. If the schema or generator changes, rebuild all artifacts and revise this plan and the report before presenting new numbers.
