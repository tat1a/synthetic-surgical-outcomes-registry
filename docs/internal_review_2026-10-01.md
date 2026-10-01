# Internal methodological review — 2026-10-01

This is a **self-audit of a synthetic portfolio project**, not independent clinical validation. The reviewer packet identifies the judgments requiring clinical/data-management input.

| Finding | Consequence | Action / status |
| --- | --- | --- |
| Invalid calendar dates could stop the validator. | No usable discrepancy query. | Fixed: explicit `DATE_FORMAT` issue and regression test. |
| A participant could have no index procedure without a dedicated check. | An incomplete record might pass some checks. | Fixed: `PROCEDURE_MISSING` rule and test. |
| Follow-up might predate index procedure. | Chronology inconsistency. | Fixed: `FOLLOWUP_CHRONOLOGY` rule. |
| A structurally clean database could still contain an open critical query. | False technical lock readiness. | Confirmed: lock fails; regression test added. |
| The initial dictionary described tables but not every field. | Handoff ambiguity. | Fixed: field-level dictionary with domains and conditional missingness. |
| Three surgical cohorts do not share a defined clinical endpoint. | No meaningful cross-cohort clinical inference. | By design: operational portfolio demonstration only; scope a single cohort before any real study. |
| The function score is invented. | No validated patient-reported or motor outcome. | Prominent limitation; replace only after selecting an appropriate measure and use rights. |
| Fixed event terms and SAE flags lack coding/adjudication. | Cannot represent a real safety reporting system. | Pending clinical/governance design; no real-case claims. |
| Script corrects errors against generated truth with fixed timestamp. | Audit is instructional, not EDC grade. | Labeled in code, dashboard, operating procedure, and case study. |

**Technical checks:** seven automated tests pass; 18/18 controlled injected cases are detected; 30 resulting queries are resolved in a scripted exercise; zero critical issues remain after reconciliation. These are conditional results for this one generated challenge, not prospective performance estimates.
