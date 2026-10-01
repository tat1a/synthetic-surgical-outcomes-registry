# Public portfolio release review — local preparation only

No repository has been published or modified by this packet. Check these items before a public release.

| Review item | Current result | Basis / action |
| --- | --- | --- |
| Patient-level content | Only generated synthetic records | Generation code and fixed seed; no imported external patient datasets. |
| Direct identifiers | No names, contacts, birth dates, sites or chart IDs in schema | Local IDs are `SYN-*`, `PROC-*`, etc. |
| Clinical inference claims | Explicitly disclaimed | README, case study, dashboard and methods documents. |
| Standards conformance | No compliance claimed | Concept-only mapping and official source notes. |
| Determinism | Tested at row level | Same seed produces same generated rows in automated test. |
| Controlled challenge | 18 root errors, all identified | 30 related rule hits include cascading due-date issues. |
| Query history | Scripted, non-EDC | Fixed timestamp and generated truth source are disclosed. |
| Tests | Eight pass locally | Rebuild and test from project root; CI run pending publication. |
| Documentation | Present | Protocol, analysis and data-management plans, CRF, field dictionary, rules, validation report, reviewer packet and handoff. |
| License and repository owner | **Decided** | Owner requested public GitHub under their account with no license file. |

For a public GitHub repository, keep `data/README_SYNTHETIC_ONLY.md` visible and prominently label every analysis output as a simulation. Re-run `python -m src.build` and the test suite immediately before release, then verify the remote repository and CI. A public portfolio release is distinct from clinical or regulatory use.
