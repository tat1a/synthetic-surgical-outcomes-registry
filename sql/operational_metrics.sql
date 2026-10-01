-- Run against data/registry_clean.sqlite. All rows are synthetic.
-- Cohort volume (participant-level denominator)
SELECT cohort, COUNT(*) AS participants
FROM participants
GROUP BY cohort ORDER BY cohort;

-- Visit completion by milestone (scheduled-visit denominator)
SELECT day_target, COUNT(*) AS scheduled,
       SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) AS completed,
       ROUND(100.0 * SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) / COUNT(*), 1) AS completion_pct
FROM followups GROUP BY day_target ORDER BY day_target;

-- Serious AE reconciliation (event-level denominator)
SELECT COUNT(*) AS serious_events,
       SUM(CASE WHEN notified_on IS NULL THEN 1 ELSE 0 END) AS unnotified_serious_events
FROM adverse_events WHERE serious=1;

-- Run against data/registry_reconciled.sqlite after the demonstration.
SELECT query_status, COUNT(*) AS query_count
FROM discrepancy_queries GROUP BY query_status;
