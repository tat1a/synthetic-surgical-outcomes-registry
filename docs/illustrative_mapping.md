# Illustrative standards mapping — conceptual only

The schema is a compact relational design for a portfolio exercise. The crosswalk below helps explain why fields were grouped; it **does not** imply conformance to a CDISC implementation guide, controlled terminology release, or regulatory submission package.

| Local content | Conceptual research-data domain | Important gap |
| --- | --- | --- |
| participants | Subject-level identity/demography | No site, consent, eligibility, or study identifier hierarchy. |
| procedures + cohort modules | Intervention / procedure exposure | No formally defined treatment coding, protocol visits, or device traceability. |
| followups | Visits and generic functional observation | Score is invented and not a validated assessment instrument. |
| adverse_events | Adverse-event capture | No clinical seriousness criteria, relationship, outcome, MedDRA coding, or reporting workflow. |
| discrepancy_queries + audit_log | Operational data cleaning | Fixed actor/time in a scripted simulation; no immutable validated audit trail. |

The electronic case-report form specification is platform neutral. Moving it into REDCap or another EDC requires local field configuration, field-level logic testing, governance, user-access design, and human validation.
