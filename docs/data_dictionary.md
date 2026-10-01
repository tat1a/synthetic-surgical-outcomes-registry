# Data dictionary, v0.1

Required fields use SQLite `NOT NULL`; foreign keys and allowed values are in `sql/schema.sql`. All dates are ISO `YYYY-MM-DD` in a fictional 2024–2025 timeline.

| Table | Key / link | Captured fields | Notes |
| --- | --- | --- | --- |
| participants | participant_id | cohort, age_band, enrolled_on | IDs generated `SYN-NNNN`; age band only. |
| procedures | procedure_id; participant_id unique FK | cohort, procedure_on, procedure_type | One index procedure per participant. |
| breast_module | procedure_id FK | intent, laterality, implant_used | One row for breast cohort. |
| nerve_module | procedure_id FK | injury_level, technique, target_function | One row for nerve cohort. |
| wound_module | procedure_id FK | region, coverage, defect_size | One row for wound cohort. |
| followups | followup_id; participant_id FK | day_target, due_on, status, visit_on, function_score | Exactly four planned time points; nullable date/score for missed visits. |
| adverse_events | event_id; procedure_id FK | event_on, term, severity, serious, notified_on | SAE notification is simulated; missing notification flagged. |
| discrepancy_queries | query_id | rule_id, record_key, severity, query_status, description, disposition | A tracking structure; CSV output is the exercise query log. |
| audit_log | audit_id | action_utc, actor, table_name, record_key, field_name, old_value, new_value, reason | Demonstration trace for scripted reconciliation; not an EDC-grade audit system. |

`function_score` is an invented 0–100 capture field, not an MRC grade, PROMIS measure, BREAST-Q, or other licensed/validated instrument. The dictionary is a minimal demonstration, not a definitive clinical CRF.

## Field-level capture specification

`Required` below means physically required by the schema; conditional business requirements are in the edit checks. IDs are synthetic local keys, not medical-record identifiers.

| Table.field | Type | Required / allowed | Meaning or derivation |
| --- | --- | --- | --- |
| participants.participant_id | Text | Yes; unique | Generated `SYN-NNNN` identifier. |
| participants.cohort | Text | Yes; breast, nerve, wound | Registry module. |
| participants.age_band | Text | Yes; 18-39, 40-59, 60+ | Coarse fabricated age group. |
| participants.enrolled_on | Date text | Yes; ISO date | Simulated enrollment date. |
| procedures.procedure_id | Text | Yes; unique | Generated `PROC-NNNN` identifier. |
| procedures.participant_id | Text | Yes; unique FK | One index procedure per participant. |
| procedures.cohort | Text | Yes; three module values | Must equal participant cohort. |
| procedures.procedure_on | Date text | Yes; ISO date | Index operation date; on/after enrollment. |
| procedures.procedure_type | Text | Yes | Broad synthetic descriptor, not coded nomenclature. |
| breast_module.procedure_id | Text | Yes; FK, unique | Breast module link. |
| breast_module.intent | Text | Yes; reconstruction, aesthetic | Simplified surgical intent. |
| breast_module.laterality | Text | Yes; left, right, bilateral | Simplified side. |
| breast_module.implant_used | Integer | Yes; 0 or 1 | Binary fabricated procedure field. |
| nerve_module.procedure_id | Text | Yes; FK, unique | Nerve module link. |
| nerve_module.injury_level | Text | Yes; plexus, peripheral | Broad injury category. |
| nerve_module.technique | Text | Yes; transfer, graft, primary repair | Broad reconstruction technique. |
| nerve_module.target_function | Text | Yes; shoulder, elbow, hand | Broad target region/function. |
| wound_module.procedure_id | Text | Yes; FK, unique | Wound module link. |
| wound_module.region | Text | Yes; upper limb, lower limb, trunk | Broad anatomical region. |
| wound_module.coverage | Text | Yes; local flap, free flap, skin graft | Broad coverage category. |
| wound_module.defect_size | Text | Yes; small, medium, large | Arbitrary demonstration group; no thresholds defined. |
| followups.followup_id | Text | Yes; unique | Generated visit identifier. |
| followups.participant_id | Text | Yes; FK | Participant link. |
| followups.day_target | Integer | Yes; 30, 90, 180, 365 | Scheduled day relative to procedure. |
| followups.due_on | Date text | Yes; ISO date | Procedure date + day_target. |
| followups.status | Text | Yes; completed, missed | Simplified visit status. |
| followups.visit_on | Date text | Conditional | Required for completed, absent for missed. |
| followups.function_score | Integer | Conditional; 0–100 | Invented illustrative score; required for completed. |
| adverse_events.event_id | Text | Yes; unique | Generated event key. |
| adverse_events.procedure_id | Text | Yes; FK | Linked index procedure. |
| adverse_events.event_on | Date text | Yes; ISO date | Simulated onset. |
| adverse_events.term | Text | Yes; infection, hematoma, wound dehiscence, other | Simplified nonstandard term. |
| adverse_events.severity | Text | Yes; mild, moderate, severe | Separate concept from seriousness. |
| adverse_events.serious | Integer | Yes; 0 or 1 | Demonstration flag, not a clinical adjudication. |
| adverse_events.notified_on | Date text | Conditional | Required if serious; must not precede onset. |
| discrepancy_queries.query_id | Text | Yes; unique | Rule-hit identifier. |
| discrepancy_queries.rule_id | Text | Yes | Stable rule code. |
| discrepancy_queries.record_key | Text | Yes | Key of affected record. |
| discrepancy_queries.severity | Text | Yes; critical, major, minor | Operational priority. |
| discrepancy_queries.query_status | Text | Yes; open, resolved | Exercise workflow state. |
| discrepancy_queries.description | Text | Yes | Rule explanation. |
| discrepancy_queries.disposition | Text | Optional | Simulated resolution explanation. |
| audit_log.audit_id | Integer | Yes; auto key | Audit event key. |
| audit_log.action_utc | Date-time text | Yes | Fixed illustrative timestamp, not real activity time. |
| audit_log.actor | Text | Yes | Scripted actor label. |
| audit_log.table_name | Text | Yes | Affected table. |
| audit_log.record_key | Text | Yes | Affected record. |
| audit_log.field_name | Text | Yes | Changed field or row marker. |
| audit_log.old_value | Text | Optional | Prior value when available. |
| audit_log.new_value | Text | Optional | Resulting value when available. |
| audit_log.reason | Text | Yes | Reason for simulated correction. |
