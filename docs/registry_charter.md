# Registry charter (demonstration protocol)

**Title:** Design and Validation of a Synthetic Clinical Registry for Reconstructive and Aesthetic Surgery Outcomes.

**Purpose:** Show the lifecycle from a protocol concept through case-report forms, relational data capture, edit checks, discrepancy queries, AE reconciliation, and a reproducible database-lock decision. This is a portfolio simulation, not human-subject research and not a claim about treatment effectiveness.

**Unit:** one simulated adult participant, one index procedure, up to four scheduled follow-ups (30, 90, 180, and 365 days). Enrollment target: 300, 100 in each module. Timing and outcome values are invented.

**Modules:** (1) breast reconstruction/aesthetic breast surgery, (2) upper-extremity peripheral nerve reconstruction, (3) wound reconstruction. Shared core holds procedure date, status, and follow-up; module tables hold simplified procedure descriptors. The wound option was selected from the previously agreed “facial or wound” choice for a tractable first version.

**Primary operational indicators:** required-field completeness, visit completion, unresolved critical queries, AE-to-procedure linkage, serious-event reporting reconciliation, and database-lock readiness. Outcome fields serve data-capture demonstrations only. Do not compare simulated cohorts as clinical evidence.

**Source and permissions:** All content is generated from code with a fixed seed. No real records or protected outcome questionnaires. Concepts from CDASH, SDTM, and REDCap guide field organization, but mappings are illustrative and have not been certified against a standard version.

**Lock rule for the exercise:** all critical validation issues resolved, no orphan foreign keys, all serious AE notifications reconciled, and no open critical query. A failed challenge must remain unlocked. A passing clean registry is a technical simulation of readiness, not a real study lock.
