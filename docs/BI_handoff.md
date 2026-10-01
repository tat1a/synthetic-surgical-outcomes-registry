# Power BI report — synthetic registry operations

Open [`powerbi/Synthetic_Surgical_Registry.pbip`](../powerbi/Synthetic_Surgical_Registry.pbip) in Power BI Desktop **after downloading the complete `powerbi/` directory**. The `.pbip`, `.Report`, and `.SemanticModel` must stay together. The editable report has two pages: **Registry Operations** (four KPIs, module counts, follow-up completion by target day) and **Data Quality & Queries** (query count, simulated serious flags, rule hits, physical NULL inventory). Save a `.pbix` from Desktop if a single binary deliverable is needed.

The semantic model embeds only five aggregate CSV snapshots from `reports/bi_tables/`, using Base64 text in Power Query. It contains no participant-level records, absolute local paths, credentialed data, or external connection. If source outputs change, run `python -m src.build` followed by `python -m src.build_powerbi`; reopening the PBIP then refreshes from the newly embedded aggregates. Editing a CSV without regenerating the PBIP **does not** update the report. The Python generator and CI verify the source snapshot, JSON structure, references and arithmetic; the PBIP still requires a final open/render check in Power BI Desktop, which is unavailable in the automated Linux environment.

## Interpretation

| Visual | Correct reading |
| --- | --- |
| Participants | 300 generated participants, 100 per surgery module. |
| Follow-up completion | Completed scheduled visits / planned scheduled visits, not functional recovery. The target-day chart sums over all three modules. |
| Event records / serious flags | Invented records for a data-operations exercise, not safety estimates. |
| Rule hits | 30 findings generated from 18 planted root errors, including 12 downstream due-date findings. |
| Physical NULL inventory | Counts absent cells; fields intentionally nullable by design are included. Use the validator for business-rule completeness. |

The aggregate tables remain disconnected in the semantic model. This prevents accidental multiplication of the participant denominator by four follow-up rows. No cross-table cohort slicer is implemented. Rates of adverse events, cross-cohort safety comparisons and clinical treatment effects would be misleading with these invented records.

## Final desktop check

1. Open `Synthetic_Surgical_Registry.pbip` in a current Power BI Desktop release on Windows. Confirm that both pages render without broken fields or query errors.
2. Select **Refresh** and compare the four first-page KPIs with `reports/lock_readiness.json`, `reports/bi_tables/cohort_counts.csv` and `reports/bi_tables/ae_by_cohort.csv` (300 participants; 1,012/1,200 completed = 84.3%; 1,200 planned visits; 52 event records).
3. Confirm the second page shows **30** rule hits and **5** serious flags. Check that rule bars sum to 30 and the four target-day completion values use `SUM(completed)/SUM(planned)`.
4. Confirm no visual claims a patient outcome or clinical comparison. Save the `.pbix` from Desktop only after these checks; the checked-in PBIP is the source of record.
