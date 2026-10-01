# Independent review packet — decisions needed before any real-study adaptation

This packet is for a clinician and a clinical data manager. The runnable code is a **synthetic portfolio demonstration**, so review should focus on definitions and workflow, not simulated patient outcomes. Reviewer comments can be entered in a copy of this document; no patient data are required.

## Materials in order

1. `registry_charter.md` — purpose, units, scope and lock concept.
2. `CRF_spec.md` and `data_dictionary.md` — forms and field definitions.
3. `edit_checks.md` and `operating_procedures.md` — rules and query lifecycle.
4. `illustrative_mapping.md` — standards claims and gaps.
5. `../reports/README_results.md` — explicitly simulated QA results.

## High-priority review questions

| Item | Reviewer question | Current state / consequence |
| --- | --- | --- |
| Cohort scope | Should a real study focus on one procedure and a defined population? | Three modules demonstrate architecture but are too broad for a unified clinical endpoint. |
| Eligibility | What age, injury/indication, procedure, site and consent criteria apply? | No real eligibility logic; cannot recruit or interpret outcomes. |
| Index procedure | How are multiple operations, staged reconstruction and revisions represented? | Exactly one procedure; revisions are not modeled. |
| Follow-up | Which timepoints, visit windows and reasons for missed visits are appropriate? | Fixed 30/90/180/365 days and binary status; windows and reasons absent. |
| Outcomes | Which validated, licensed instruments and clinically meaningful endpoints are available? | Generic 0–100 score has no clinical validity. |
| AE/SAE | What seriousness definition, coding, causality, reconciliation and reporting timelines apply? | Simplified flags/terms only; no real regulatory handling. |
| Missingness | Which absent values are expected versus queried, and how are withdrawals handled? | Conditional status checks exist; no withdrawal or imputation policy. |
| Source verification | Who verifies a correction against what authorized record? | Script compares to generator truth; no real source review. |
| Lock authorization | Who signs off, what is the freeze/lock audit process? | Only a technical Boolean gate. |

## Suggested review response

For each row, record **Accept for demonstration / Revise before a real study / Not applicable**, a proposed definition, reviewer role, and date. Do not change the fictional data to imply clinical approval. A real protocol and institutional governance must be established separately.
