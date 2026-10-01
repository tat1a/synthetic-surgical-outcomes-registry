# Portfolio case study: Synthetic Surgical Outcomes Registry

**Purpose.** Demonstrate how a small registry can link procedures and scheduled visits, detect inconsistencies, document queries and assess a technical lock gate.

**Implementation.** The registry uses shared fields and separate breast, nerve and wound modules. Python generates 300 fictional participants with a fixed seed; SQLite enforces keys and allowed values. Validation rules inspect the database without reading the error manifest. A controlled challenge inserts 18 known errors, followed by scripted reconciliation against generated truth.

**Results of the simulation.** The clean database produced zero critical edit-check hits. All 18 injected errors were detected; three incorrect index dates also caused 12 downstream visit-due-date hits, giving 30 query records. After correction against the generated truth, all 30 queries were marked resolved, 48 audit entries captured field or query-status changes, and a technical lock gate passed. An aggregate HTML dashboard displays volume, follow-up capture, error types, and query flow. Five aggregate CSV tables support optional Power BI replication without sharing participant-level rows.

**Scope.** The work covers CRF and data-dictionary design, relational SQL, reproducible Python generation, validation rules, query tracking, longitudinal denominators and aggregate reporting. It does **not** establish clinical outcomes, safety comparisons, real source verification or production EDC validation.

**Next improvement.** Obtain expert review of field definitions and operating rules, choose a narrower clinically grounded module, add a documented missing-data plan, and configure an actual EDC only in an appropriately governed environment.
