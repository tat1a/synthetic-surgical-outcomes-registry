# Case-report form specification, v0.1

## Enrollment / index procedure

Record simulated subject ID, cohort, age band, index procedure date, and procedure type. No patient identifiers, exact age, birth date, site, physician, or source-chart text. Exactly one module record is required for each index procedure and its cohort must match the parent record.

## Procedure modules

- Breast: intent (reconstruction/aesthetic), laterality (left/right/bilateral), and implant use (yes/no).
- Nerve: injury level (plexus/peripheral), repair technique (transfer/graft/primary repair), and target function (shoulder/elbow/hand).
- Wound: region (upper limb/lower limb/trunk), coverage (local flap/free flap/skin graft), and defect size category (small/medium/large).

## Follow-up

Create four planned visits per participant at days 30, 90, 180, 365. Capture due date and status (completed/missed). For completed visits capture visit date and a generic function score on a 0–100 simulation scale; for missed visits both remain empty. This score is a **synthetic demonstration variable**, not a named validated PRO instrument.

## Adverse event / notification

Capture simulated event ID, associated procedure, onset date, severity (mild/moderate/severe), serious flag, event term from a limited list, and notification date if serious. A serious event missing a notification date creates a reconciliation query. No real reporting to an IRB, sponsor, or regulator is performed.

## Discrepancy management

Each issue has a stable rule and record key, criticality, open/resolved status, and a disposition. The example challenge intentionally leaves queries open; the clean simulation has none. No automatic imputation or silent correction.

The separate reconciliation exercise copies the **generated truth** into the challenge database after matching all queries to the current data. It records old/new field values, an illustrative actor and timestamp, and a clearly labeled simulated disposition. It does not represent source document verification, clinician adjudication, or an operational EDC audit trail.
