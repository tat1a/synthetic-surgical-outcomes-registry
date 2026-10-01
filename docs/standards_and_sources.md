# Standards and source notes (checked 2026-10-01)

This project uses **concepts**, not formally implemented clinical data standards. The references below define the distinctions and give a reviewer a path to verify them.

| Source | Role in this portfolio | What is **not** claimed |
| --- | --- | --- |
| [CDISC CDASH overview](https://www.cdisc.org/standards/foundational/cdash) | Motivates consistent case-report-form collection and traceability. | CRF fields have not been mapped to a named CDASH version or controlled terminology. |
| [CDISC SDTM overview](https://www.cdisc.org/standards/foundational/sdtm) | Explains why a future submission-oriented tabulation layer is distinct from data capture. | SQLite tables are not SDTM domains or regulatory-ready datasets. |
| [REDCap software features](https://projectredcap.org/software/) | Illustrates data-dictionary and branching-logic concepts relevant to future EDC configuration. | No REDCap project, uploadable dictionary, or validated form has been built. |
| [AHRQ registry user guide: data quality](https://www.ncbi.nlm.nih.gov/books/NBK562556/) | Supports a separate data dictionary, validation rules, and registry data-management plan. | The synthetic exercise is not an actual patient registry. |

The names and code lists in `sql/schema.sql` are **locally invented demonstration values**, even when they resemble clinical terms. A real implementation would choose study-specific definitions, qualified terminology, protocol-approved forms, and the relevant dated standard versions before asserting conformance.
