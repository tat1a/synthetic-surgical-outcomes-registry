# Project state — updated 2026-10-02

Status: published **synthetic portfolio demonstration**; not a finished clinical registry or a clinical publication. The public repository contains the full source, synthetic examples, reports and documentation. GitHub Actions rebuilds and tests on Python 3.10 and 3.12; the validation report records the observed run. The current workflow also checks committed text outputs against a fresh rebuild. Binary SQLite files are tested at the row and rule level, not asserted to be byte-identical across SQLite versions.

Completed: scope and charter; simulation protocol, operational analysis and data-management plans; shared CRF and three modules; field-level dictionary; SQLite schema; seeded synthetic generation; challenge errors with answer key; validation and query export; scripted reconciliation and audit log; aggregate operational HTML dashboard and BI-ready CSV tables; SQL metrics; internal methods review, reviewer packet, traceability matrix, eight tests, negative empty-registry gate, and lock-readiness exercise.

Next if adapted to a **real study**: independent clinical/data-management review of CRF and edit-check rules; choose a single primary procedure module; formalize clinical missing-data, AE coding, source verification, and governance; optional REDCap configuration or Power BI replication. The owner requested a public GitHub portfolio repository **without a license file**. This simulation cannot substitute for clinical, regulatory, statistical, or EDC validation.

Project 2 systematic scoping review is paused while reviewer work is pending. Project 3 MIMIC access is separate. No patient-level material from either project was imported here.
