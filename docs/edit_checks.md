# Edit-check specification, v0.1

| Rule ID | Logic | Severity | Example disposition |
| --- | --- | --- | --- |
| ORPHAN_FK | Referenced parent must exist. | Critical | Resolve source-link mismatch. |
| EMPTY_REGISTRY / COHORT_ABSENT | At least one participant and each of the three demonstration cohorts must exist. | Critical | Recheck extract and intended scope. |
| DATE_FORMAT | Nonempty dates must be valid `YYYY-MM-DD` calendar dates. | Critical | Verify and correct the date; validator must not crash. |
| PROCEDURE_MISSING | Each enrolled participant must have an index procedure. | Critical | Confirm eligibility and complete or reclassify record. |
| CHRONOLOGY | Procedure date must not precede enrollment. | Critical | Verify the source and correct the date with an audit trail. |
| COHORT_MISMATCH | Participant and procedure cohorts must match. | Critical | Resolve classification. |
| MODULE_MISSING / MODULE_WRONG | Exactly the appropriate cohort module must be present. | Critical | Complete or remove the relevant module. |
| VISIT_MISSING | Four follow-up schedule rows are expected. | Critical | Add schedule row, retain missed status if appropriate. |
| FOLLOWUP_DUE | Due date equals procedure date plus target days. | Critical | Recalculate from verified date. |
| FOLLOWUP_CHRONOLOGY | Completed visit date cannot precede the procedure. | Critical | Verify visit date or linked procedure. |
| FOLLOWUP_STATUS | Completed visits require date and score; missed visits have neither. | Critical | Correct status or request missing visit fields. |
| AE_CHRONOLOGY | Event onset cannot precede the index procedure in this simplified registry. | Critical | Verify event association/date. |
| SAE_NOTIFICATION | Serious event must have a notification date. | Critical | Reconcile reporting record. |
| AE_NOTIFICATION_CHRONOLOGY | Notification cannot precede event onset. | Critical | Resolve date discrepancy. |
| OPEN_CRITICAL_QUERY | No open critical query at simulated lock. | Critical | Resolve or document disposition. |

Rules illustrate edit-check mechanics. A real protocol would determine exact windowing, visit status definitions, AE/SAE process, and applicable reporting timelines before data capture. The generated challenge answer key lives in `data/injected_errors.csv`; the validator does not read it.
