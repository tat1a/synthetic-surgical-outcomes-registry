"""Build an operational, explicitly simulated summary from generated reports."""
import csv
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def main():
    clean = json.loads((ROOT / 'reports/clean_validation.json').read_text())
    challenge = json.loads((ROOT / 'reports/challenge_validation.json').read_text())
    reconciled = json.loads((ROOT / 'reports/reconciliation.json').read_text())
    generated = json.loads((ROOT / 'data/generation_manifest.json').read_text())
    with (ROOT / 'data/injected_errors.csv').open(newline='') as handle:
        manifest = list(csv.DictReader(handle))
    detected = {(x['rule_id'], x['record_key']) for x in challenge['issues']}
    matched = sum((x['rule_id'], x['record_key']) in detected for x in manifest)
    with sqlite3.connect(ROOT / 'data/registry_clean.sqlite') as db:
        cohorts = dict(db.execute('SELECT cohort, COUNT(*) FROM participants GROUP BY cohort'))
        complete, total = db.execute("SELECT SUM(status='completed'), COUNT(*) FROM followups").fetchone()
        serious = db.execute('SELECT COUNT(*) FROM adverse_events WHERE serious=1').fetchone()[0]
        ae_count = db.execute('SELECT COUNT(*) FROM adverse_events').fetchone()[0]
    summary = {
        'synthetic_only': True,
        'seed': generated['seed'],
        'cohorts': cohorts,
        'followup_completion': {'completed': complete, 'planned': total,
                                'percentage': round(100 * complete / total, 1)},
        'adverse_events': {'all': ae_count, 'serious': serious},
        'clean_lock_ready_technical_simulation': clean['lock_ready_technical_simulation'],
        'challenge_lock_ready_technical_simulation': challenge['lock_ready_technical_simulation'],
        'reconciled_lock_ready_technical_simulation': reconciled['lock_ready_technical_simulation'],
        'controlled_challenge': {'injected_cases': len(manifest),
                                 'detected_cases': matched,
                                 'detection_percentage': round(100 * matched / len(manifest), 1),
                                 'total_queries_including_cascades': challenge['critical_issues']},
        'reconciliation': {'queries_resolved': reconciled['queries_resolved'],
                           'audit_entries': reconciled['audit_entries'],
                           'remaining_issues': reconciled['remaining_issues']},
        'interpretation': 'Operational simulation only; not clinical outcomes or a real database lock.'
    }
    path = ROOT / 'reports/lock_readiness.json'
    path.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
