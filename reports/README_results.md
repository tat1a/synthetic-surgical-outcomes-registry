# Technical validation snapshot

All counts below describe **fabricated data** generated with seed `20261001`. They do not estimate surgical risk, recovery, or effectiveness.

| Indicator | Simulated result |
| --- | ---: |
| Participants | 300 (100 per cohort) |
| Planned follow-up rows | 1,200 |
| Completed follow-ups | 1,012 (84.3%) |
| Adverse-event records | 52 |
| Serious flags | 5 |
| Critical issues, clean database | 0 |
| Deliberately injected critical cases | 18 |
| Injected cases detected by independent rule checks | 18/18 |
| Total challenge queries, including downstream effects | 30 |

The clean dataset passes the **technical simulation** of lock readiness; the challenge dataset is blocked. Changing a procedure date also changes the expected due dates for four visits, which explains 12 additional downstream queries. These are separate discrepancies produced by three root errors, not 12 extra injected errors.

The separate controlled reconciliation corrects the 18 root errors using the generator's truth reference, closes all 30 queries after validation, and records 48 audit entries. These scripted actions are **not** real source-document review or evidence of a validated audit system. Open `operational_dashboard.html` for an aggregate visual summary.

The 18/18 figure is challenge-set recall for six selected rules, not sensitivity in real-world clinical data. Schema constraints, exact visit definitions, source verification, discrepancy resolution, audit trails, access control, and governance require further work before this could resemble a study database.
