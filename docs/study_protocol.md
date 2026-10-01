# Simulation design record — version 1.0 (2026-10-01)

This design record was written alongside the completed portfolio simulation. It documents the implemented methods and was **not** prospectively registered before data generation or analysis.

## Identity and purpose

**Title:** Design and Validation of a Synthetic Clinical Registry for Reconstructive and Aesthetic Surgery Outcomes. This is a methods and clinical data-management portfolio exercise. Its objective is to show that a specified fictional registry can be generated, checked, queried, corrected against its generator truth, and summarized reproducibly. It is **not** a clinical observational study, a trial, an actual patient registry, or evidence that a procedure works or is safe.

## Design and population

The design is a deterministic software simulation with a clean data state, a deliberately corrupted challenge state, and a reconciled state. The units are fictional participant, index procedure, scheduled follow-up, and adverse-event record. The generator makes 300 adult-labelled participant records, 100 each in breast surgery, upper-extremity nerve reconstruction, and wound reconstruction. These modules demonstrate extensibility, not mutually comparable clinical populations. No real patient is enrolled; the age bands and all event/outcome values are invented. There is no sampling frame, recruitment, consent process, observed exposure, or external patient-level source.

Each participant has one index procedure and four expected follow-up rows targeted at 30, 90, 180 and 365 days after it. A visit is completed or missed. Completed visits receive an invented 0–100 `function_score`; this is not a validated questionnaire or interpretable clinical endpoint. Adverse-event terms, severity and serious flags are simplified demonstration fields. No actual causality, incidence, risk, reporting deadline, or SAE adjudication is represented. The generation settings and full field definitions are in `data/generation_manifest.json` and `docs/data_dictionary.md`.

## Operational objectives implemented in this version

1. Verify row counts, cohort structure, link integrity, expected follow-ups, dates, conditional fields, and open critical queries against the rule list in `docs/edit_checks.md`.
2. Detect all 18 code-defined root errors inserted into a copy of the clean dataset. The validator must not consult the answer key.
3. Document root-error counts separately from additional rule hits caused by an upstream error.
4. Restore the challenge using the generator's clean truth reference, retain simulated audit entries, rerun validation, and assess the technical lock gate.
5. Produce aggregate operational tables and a dashboard without exposing row-level data in visual outputs.

## Workflow and endpoints

The fixed-seed generator writes three SQLite states. The validator applies documented edit checks to the clean and challenge states; the challenge answer key is used only to evaluate detection and to drive an explicitly scripted resolution exercise. The primary technical endpoints are (a) zero critical edit-check issues on the clean state, (b) detection of each injected `(rule_id, record_key)` pair, and (c) zero residual critical checks and zero open critical queries after reconciliation. Secondary operational descriptors are cohort counts, follow-up completion with scheduled rows as denominator, adverse-event record counts, query counts by rule, and audit-entry count. There are no clinical hypotheses or effect estimates.

## Analysis and interpretation

`docs/analysis_plan.md` fixes numerator and denominator definitions. No tests of significance, treatment comparisons, missing-data imputation, risk prediction, or causal claims are planned. A 100% detection fraction refers only to the six deliberately exercised rule families in this specific challenge, not diagnostic sensitivity across untested errors. The clean database serves as simulation truth and is not an authorized medical source. A passing technical gate must never be described as a real database lock or independent monitoring approval.

## Ethics, provenance and dissemination

This artifact contains generated records only; it has no human participants, PHI, clinical source documents, or imported MIMIC/FDA individual records. No IRB review or exemption determination has been sought or claimed for this exercise. A future study using real people or data needs its own institutional and data-use determinations before work begins. The public package may include the synthetic SQLite examples and an aggregate dashboard, plainly labelled as such. See `docs/data_management_plan.md` for handling rules and `docs/standards_and_sources.md` for conceptual sources.

## Deviations and limitations

The 300 and 18 sizes, cohort mix, event rates, visits, and scores are generator choices rather than estimates from clinical literature. One procedure per participant, fixed timepoints, limited AE vocabulary, no visit windows, no validated outcome instrument, no data-entry interface, and no real source verification constrain transfer to practice. Independent clinical/data-management review and a narrower clinical question would be required before any real-study adaptation. Changes to the simulation should update the decision log, tests, and validation report together.
