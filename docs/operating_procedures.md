# Simulated data-management operating procedures

## Roles in this exercise

**Generator** creates fictional records and a separate answer key. **Validator** reads only the data tables and raises rule-specific issues. **Data reviewer (scripted)** matches the query log to the challenge and corrects the injected root errors using the generated clean truth. **Lock assessment** reruns checks and rejects unresolved critical issues.

These are software roles, not evidence that a clinical investigator, independent monitor, or medical coder reviewed records. A real implementation would define access permissions, delegated responsibilities, training, and approval signatures.

## Query process

1. Run edit checks on a versioned extract and retain the full output, including rule ID, table, record key, and description.
2. Open discrepancy records without deleting or silently overwriting the underlying observations.
3. Investigate each root error using an authorized source record in real practice. Here, and **only here**, `registry_clean.sqlite` is the fictional truth source.
4. Record corrections with previous and new values, reason, actor, and action time. The example uses a fixed illustrative timestamp, so it cannot establish when a human actually acted.
5. Recheck all rules after corrections. Three incorrect index dates cause 12 further due-date issues; these secondary issues close only when the underlying date is restored and validation passes.
6. Resolve the corresponding query records and retain the audit history. Do not count downstream rule hits as independent originally injected errors.

## Adverse-event check

An event links to a procedure. A serious flag requires a recorded notification date and a notification cannot precede event onset. The example does not apply an actual reporting deadline, regulatory seriousness definition, clinical causality judgment, or coding dictionary. Real AE/SAE handling must follow the applicable protocol, institutional processes, and jurisdiction.

## Technical lock gate

The clean and reconciled databases pass only if all critical edit checks pass and no critical query is open. The challenge fails. In real work, additional gates include source-data verification, authorized medical review, external reconciliation, protocol deviations, sign-offs, access control, freeze/lock privileges, and archival. None of those is established by this simulation.
