# Requirements traceability

| Demonstration requirement | Implementation | Evidence |
| --- | --- | --- |
| Fictional records with repeatable build | `src/generate.py`, seed manifest | Determinism test; generated `data/` files. |
| Cohort-specific capture | `sql/schema.sql`, `docs/CRF_spec.md` | Required module checks; 100 per cohort in summary. |
| Relational referential integrity | Foreign keys in schema; `PRAGMA foreign_key_check` | Challenge and reconciled tests. |
| Longitudinal visits | Follow-up table and generator | 1,200 planned rows; milestone export. |
| AE link and notification check | `adverse_events`, validator | SAE notification rules and query counts. |
| Robust invalid-date handling | `DATE_FORMAT` check | Malformed-date test; no validator crash. |
| Query detection independent of truth key | `src/validate.py` | 18/18 challenge detection test. |
| Scripted discrepancy resolution | `src/reconcile.py` | 30 resolved queries, 48 audit rows; test. |
| Technical lock simulation | `lock_ready_technical_simulation` | Clean/challenge/reconciled reports. |
| Aggregate-only operational display | `src/dashboard.py`, BI exports | Dashboard/aggregate reconciliation tests. |

Passing these tests does not imply regulatory compliance, validated clinical outcomes, security certification, or external clinical review.
