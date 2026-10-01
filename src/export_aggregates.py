"""Export small, patient-free operational tables suitable for BI practice."""
import csv
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/bi_tables'


def write(name, headers, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def export():
    with sqlite3.connect(ROOT / 'data/registry_clean.sqlite') as db:
        counts = list(db.execute('SELECT cohort, COUNT(*) FROM participants GROUP BY cohort ORDER BY cohort'))
        visits = list(db.execute("""
            SELECT p.cohort, f.day_target, COUNT(*) AS planned,
                   SUM(CASE WHEN f.status='completed' THEN 1 ELSE 0 END) AS completed,
                   SUM(CASE WHEN f.status='missed' THEN 1 ELSE 0 END) AS missed
            FROM followups f JOIN participants p USING(participant_id)
            GROUP BY p.cohort, f.day_target ORDER BY p.cohort, f.day_target
        """))
        events = list(db.execute("""
            SELECT p.cohort, COUNT(a.event_id) AS events,
                   COALESCE(SUM(CASE WHEN a.serious=1 THEN 1 ELSE 0 END),0) AS serious,
                   COALESCE(SUM(CASE WHEN a.serious=1 AND a.notified_on IS NULL THEN 1 ELSE 0 END),0) AS unnotified_serious
            FROM participants p JOIN procedures pr USING(participant_id)
            LEFT JOIN adverse_events a ON a.procedure_id=pr.procedure_id
            GROUP BY p.cohort ORDER BY p.cohort
        """))
        completeness = []
        for table in ('participants','procedures','breast_module','nerve_module','wound_module','followups','adverse_events'):
            columns = [r[1] for r in db.execute(f'PRAGMA table_info({table})')]
            total = db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            for col in columns:
                # Table and column names only come from fixed local schema.
                present = db.execute(f'SELECT COUNT(*) FROM {table} WHERE {col} IS NOT NULL').fetchone()[0]
                completeness.append((table, col, present, total, total-present))
    with (ROOT / 'reports/challenge_queries.csv').open(newline='') as handle:
        queries = list(csv.DictReader(handle))
    query_groups = {}
    for q in queries:
        query_groups[q['rule_id']] = query_groups.get(q['rule_id'], 0) + 1
    write('cohort_counts.csv', ('cohort','participant_count'), counts)
    write('followup_by_cohort.csv', ('cohort','day_target','planned','completed','missed'), visits)
    write('ae_by_cohort.csv', ('cohort','event_count','serious_count','unnotified_serious_count'), events)
    write('challenge_queries_by_rule.csv', ('rule_id','query_count'), sorted(query_groups.items()))
    write('field_completeness.csv', ('table_name','field_name','nonmissing','rows','missing'), completeness)
    return {'cohorts': len(counts), 'followup_groups': len(visits),
            'followup_planned': sum(r[2] for r in visits),
            'followup_completed': sum(r[3] for r in visits),
            'adverse_events': sum(r[1] for r in events),
            'challenge_queries': sum(query_groups.values())}


if __name__ == '__main__':
    print(export())
