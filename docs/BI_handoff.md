# Power BI handoff — aggregate operational dashboard

The `reports/bi_tables/` CSVs contain only aggregate or table-level completeness data. They can be loaded into Power BI with **Get data → Text/CSV**. `cohort` is a shared categorical key across the cohort, follow-up, and AE aggregates; rule counts and field completeness are separate QA views. Never sum `participant_count` after joining it to four follow-up milestone rows, or the denominator will be multiplied.

## Suggested page

1. KPI cards: participants from `cohort_counts.csv`; planned and completed visits from `followup_by_cohort.csv`; query count from `challenge_queries_by_rule.csv`.
2. Clustered bars: completion rate by `day_target`, with optional cohort filtering.
3. Horizontal bars: challenge query count by `rule_id`, labeled as **rule hits**, with a note that 18 root errors generated 30 hits.
4. Table: `field_completeness.csv` with `missing` and `rows`, excluding fields intentionally nullable by design when assessing required-field quality.
5. Narrative: synthetic demonstration only, no clinical effect or safety comparison.

## Example DAX measures

Create these measures within their respective imported tables (rename tables in the formulas if Power BI assigns different names):

```DAX
Participants = SUM(cohort_counts[participant_count])
Planned Visits = SUM(followup_by_cohort[planned])
Completed Visits = SUM(followup_by_cohort[completed])
Visit Completion % = DIVIDE([Completed Visits], [Planned Visits])
Challenge Queries = SUM(challenge_queries_by_rule[query_count])
```

Set `Visit Completion %` to percentage format, one decimal. Treat `ae_by_cohort` as a simulation of reconciliation operations; do not make adverse-event rates or cross-cohort safety comparisons from invented data.

`field_completeness.csv` reports physical `NULL` values, not clinical completeness. In particular, missing `visit_on` and `function_score` are expected when `status='missed'`; `notified_on` is not required when `serious=0`. Business-rule completeness should be read from the validator.
