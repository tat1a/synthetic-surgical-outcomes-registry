# Data management and reproducibility plan — version 1.0

## Data classification and flow

All records are fictional and generated locally with Python's standard library, seed `20261001`. `src/generate.py` creates `registry_clean.sqlite` and copies it to `registry_challenge.sqlite` before injecting selected errors; `data/injected_errors.csv` is the challenge answer key. `src/validate.py` sees database tables, not that key. `src/reconcile.py` uses the clean database as fictional truth to create `registry_reconciled.sqlite`, a query table and a scripted audit log. Aggregate JSON, CSV and HTML are derived after validation. The retained clean reference makes this a demonstrator with known answers, not a blinded external validation.

## Handling and sharing

The example intentionally has no names, contacts, birth dates, facility IDs, MRNs, free-text narratives, actual patient questionnaires, MIMIC rows, or imported third-party patient records. The `SYN-*` IDs are generated local labels. Do not mix real data into these tables or upload real clinical extracts to the public repository. If a future study uses restricted data, keep source and derived row-level data in an approved environment under its own terms; publish code or suitably reviewed aggregate outputs separately. This project itself requires no credentialed dataset access.

The three SQLite files are included to let reviewers inspect each state; `injected_errors.csv` is openly labelled as an answer key. The browser dashboard and BI tables use aggregate outputs only. Code and generated records are versioned together so users can reproduce exact examples. No license file is included for this public portfolio package, per the project owner's instruction; this document does not grant rights to third-party standards or data.

## Change control and query lifecycle

Field meaning, allowed values and nullability are defined in `docs/data_dictionary.md` and `sql/schema.sql`; edit checks in `docs/edit_checks.md`. Changes to them require an updated decision-log row, code and tests, a full rebuild, and reviewed summary counts. Query IDs identify rule hits, which may include several issues from one root cause. Correction requires a reason, old/new value and actor in the simulated audit table. The fixed `2026-10-01T00:00:00Z` timestamp and scripted actor are illustrative, **not** evidence of actual human action or chronological audit integrity. No investigator sign-off, role-based access, encryption claim, backup policy or institutional retention schedule is implied.

## Quality gates and archive

Run `python -m src.build` and `python -m unittest discover -s tests -v`. Check referential integrity, required modules and visits, dates, AE notification, open critical queries, exact challenge detection, aggregate reconciliation, and the negative empty-registry test. A clean/reconciled state passes only the coded technical gate; the challenge must fail. Keep the manifest, reports and source at one version. The distributable ZIP is a reproducible snapshot, not a regulated source-data archive. A real registry would additionally require governance, privacy/security review, validated EDC processes, source verification, retention, authorized lock sign-offs and controlled amendments.
