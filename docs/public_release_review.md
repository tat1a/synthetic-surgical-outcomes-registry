# Public portfolio release review — updated 2026-10-02

This review applies to the published repository and the matching local 51-file package. Repository tree hashes were compared with local files before this update. The new workflow change requires a fresh remote CI check after publication; a local pass alone is insufficient evidence of a complete remote release.

| Review item | Current result | Basis / action |
| --- | --- | --- |
| Patient-level content | Only generated synthetic records | Generation code and fixed seed; no imported external patient datasets. |
| Direct identifiers | No names, contacts, birth dates, sites or chart IDs in schema | Local IDs are `SYN-*`, `PROC-*`, etc. |
| Clinical inference claims | Explicitly disclaimed | README, case study, dashboard and methods documents. |
| Standards conformance | No compliance claimed | Concept-only mapping and official source notes. |
| Determinism | Tested at row level | Same seed produces same generated rows in automated test. |
| Controlled challenge | 18 root errors, all identified | 30 related rule hits include cascading due-date issues. |
| Query history | Scripted, non-EDC | Fixed timestamp and generated truth source are disclosed. |
| Tests | Eight pass locally; remote Python 3.10/3.12 passed in run #4 | [Observed run](https://github.com/tat1a/synthetic-surgical-outcomes-registry/actions/runs/36933647259). New text-output reproducibility gate awaits its first remote run. |
| Documentation | Present | Protocol, analysis and data-management plans, CRF, field dictionary, rules, validation report, reviewer packet and handoff. |
| License and repository owner | **Decided** | Owner requested public GitHub under their account with no license file. |

Keep `data/README_SYNTHETIC_ONLY.md` visible and prominently label every analysis output as a simulation. Re-run `python -m src.build` and the test suite before publishing a revision, then verify the remote repository and CI. A public portfolio release is distinct from clinical or regulatory use.
