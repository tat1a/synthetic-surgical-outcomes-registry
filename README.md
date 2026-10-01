# Synthetic Surgical Outcomes Registry

[![Rebuild and validate](https://github.com/tat1a/synthetic-surgical-outcomes-registry/actions/workflows/ci.yml/badge.svg)](https://github.com/tat1a/synthetic-surgical-outcomes-registry/actions/workflows/ci.yml)

A portfolio demonstration of clinical data management for breast surgery, peripheral nerve reconstruction, and wound reconstruction. **Every record is generated; no real patient data or PHI is used.** Numbers and clinical patterns in this repository are simulation outputs, not medical evidence.

The complete project package covers a simulation design record, analysis specification and data-management plan, CRF specification, relational schema, deterministic generation of 300 fictional participants, independent validation rules, a controlled error challenge, query log, scripted reconciliation with audit entries, a technical lock-readiness report, and an aggregate HTML dashboard. It uses CDASH and SDTM ideas as design references; it is not a CDISC compliant submission or a validated EDC system.

## At a glance

| Demonstration | Generated result | Interpretation |
| --- | ---: | --- |
| Fictional participants | 300 (100 per module) | Fixed-seed simulated records |
| Planned / completed visits | 1,200 / 1,012 | Simulated data-capture completeness: 84.3% |
| Deliberate root errors detected | 18 / 18 | Only the selected, known challenge cases |
| Discrepancy queries | 30 | Includes 12 downstream due-date issues |
| Scripted query resolutions | 30 / 30 | Checked against generator truth, without source review |

The [validation report](docs/validation_report.md), [case study](reports/portfolio_case_study.md), and [aggregate dashboard](reports/operational_dashboard.html) show the methods and outputs. The dashboard is a standalone HTML file to download or open locally; GitHub's code preview does not execute it.

## Run

Python 3.10+; no third-party packages. From the project directory:

```bash
python -m src.build
python -m unittest discover -s tests -v
```

Generated data are written to `data/`; the clean database represents valid records, while the challenge database has deliberate errors. `data/injected_errors.csv` is the answer key. Validation checks are applied to both independently. The reconciled database and audit log demonstrate documented resolution against generated truth. Open `reports/operational_dashboard.html` locally for an aggregate view. `reports/bi_tables/` contains aggregate CSVs for optional Power BI work; see `docs/BI_handoff.md`. `reports/lock_readiness.json` records the synthetic exercise outcome.

## Structure

- `docs/`: protocol, analysis and data-management plans, charter, dictionary, CRF, edit checks, validation report, decisions, and limitations.
- `sql/schema.sql`: core and cohort module tables with keys and constraints.
- `src/`: generator, validator, controlled reconciliation, summary, dashboard, and build runner.
- `data/`: generated synthetic SQLite files, error answer key, and seed manifest.
- `reports/`: machine-readable validation, query, reconciliation, and aggregate HTML outputs.

No names, addresses, dates of birth, chart numbers, source medical records, or actual outcome instruments are included. IDs are local simulated identifiers. Start with [`docs/study_protocol.md`](docs/study_protocol.md), [`docs/analysis_plan.md`](docs/analysis_plan.md), and [`docs/validation_report.md`](docs/validation_report.md); then consult [`PROJECT_STATE.md`](PROJECT_STATE.md) before extending or presenting the project.

The [internal methods review](docs/internal_review_2026-10-01.md) is a self-audit; the [reviewer packet](docs/reviewer_packet.md) isolates clinical and governance decisions that remain open. [Standards and source notes](docs/standards_and_sources.md) distinguish conceptual references from implemented conformance.

## Reuse and scope

No license file is provided. The repository is shared as a reviewable portfolio example. This project does not contain MIMIC data; future studies using credentialed data are separate and must follow their own access terms. Do not replace the simulated rows with real patient data in a public copy.
