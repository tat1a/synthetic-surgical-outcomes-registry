# Decision log

| Date | Decision | Reason / caveat |
| --- | --- | --- |
| 2026-10-01 | Keep three modules; use wound reconstruction as the third. | Matches the agreed facial-or-wound option and makes a compact initial demonstration. |
| 2026-10-01 | Synthetic adult cohort and no directly identifying fields. | Prevents accidental presentation as real clinical data. |
| 2026-10-01 | Four fixed follow-up milestones and generic 0–100 score. | Tests longitudinal capture without asserting instrument validity. |
| 2026-10-01 | Separate answer-key manifest from validator. | Detectability can be evaluated independently; no hidden direct answer lookup by validator. |
| 2026-10-01 | Use SQL constraints for hard typing and referential integrity; inject errors that pass storage constraints. | Demonstrates edit checks at the application layer while retaining a usable relational schema. |
| 2026-10-01 | Block technical lock for an empty registry or absent demonstration cohort. | A zero-issue empty database must not pass readiness. |
| 2026-10-01 | Publish the completed portfolio package publicly without a license file, subject to final QA. | Explicit owner instruction; no real data and no clinical validity claim. |
