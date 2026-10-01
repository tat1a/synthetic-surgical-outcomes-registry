"""Demonstrate query reconciliation against the generator's synthetic truth.

This is a controlled teaching exercise, not a real source-data verification process.
The clean database is deliberately retained as an answer key; a clinical study
would require human review of authorized source records and documented decisions.
"""
import argparse
import csv
import json
from pathlib import Path
import sqlite3

from src.validate import validate

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {
    'CHRONOLOGY': ('procedures', 'procedure_id', ('procedure_on',)),
    'FOLLOWUP_STATUS': ('followups', 'followup_id', ('status', 'visit_on', 'function_score')),
    'FOLLOWUP_DUE': ('followups', 'followup_id', ('due_on',)),
    'COHORT_MISMATCH': ('procedures', 'procedure_id', ('cohort',)),
    'SAE_NOTIFICATION': ('adverse_events', 'event_id', ('serious', 'notified_on')),
}
STAMP = '2026-10-01T00:00:00Z'  # Fixed, illustrative timestamp for reproducible output.
REASON = 'Simulated reconciliation against generated truth; no real source documents reviewed.'


def reconcile(challenge, clean, manifest, output_db, query_csv):
    challenge, clean, manifest, output_db, query_csv = map(Path,
        (challenge, clean, manifest, output_db, query_csv))
    output_db.parent.mkdir(parents=True, exist_ok=True)
    output_db.unlink(missing_ok=True)
    with sqlite3.connect(challenge) as src, sqlite3.connect(output_db) as dest:
        src.backup(dest)
    with manifest.open(newline='') as handle:
        roots = list(csv.DictReader(handle))
    with query_csv.open(newline='') as handle:
        query_rows = list(csv.DictReader(handle))
    if len(roots) != 18 or len(query_rows) < len(roots):
        raise ValueError('Expected challenge files were not supplied')
    # Ensure the query file corresponds to the unmodified challenge.
    observed = {(i['rule_id'], i['record_key'], i['table']) for i in validate(challenge)['issues']}
    supplied = {(i['rule_id'], i['record_key'], i['table']) for i in query_rows}
    if observed != supplied or len(supplied) != len(query_rows):
        raise ValueError('Query CSV does not match the challenge database')
    with sqlite3.connect(clean) as truth, sqlite3.connect(output_db) as db:
        truth.row_factory = sqlite3.Row
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = ON')
        for row in query_rows:
            db.execute('INSERT INTO discrepancy_queries VALUES (?,?,?,?,?,?,?)',
                       (row['query_id'], row['rule_id'], row['record_key'],
                        row['severity'], 'open', row['description'], None))
        edited_fields = 0
        for root in roots:
            rule, key = root['rule_id'], root['record_key']
            if rule == 'MODULE_MISSING':
                table = root['table']
                if table not in ('breast_module','nerve_module','wound_module'):
                    raise ValueError('Unexpected module table')
                record = truth.execute(f'SELECT * FROM {table} WHERE procedure_id=?', (key,)).fetchone()
                if record is None:
                    raise ValueError('Missing synthetic truth row')
                db.execute(f'INSERT INTO {table} VALUES ({",".join("?" for _ in record)})', tuple(record))
                audit(db, table, key, '<row>', None, json.dumps(dict(record), sort_keys=True))
                edited_fields += 1
            else:
                table, pk, fields = FIELDS[rule]
                reference = truth.execute(f'SELECT * FROM {table} WHERE {pk}=?', (key,)).fetchone()
                target = db.execute(f'SELECT * FROM {table} WHERE {pk}=?', (key,)).fetchone()
                if reference is None or target is None:
                    raise ValueError('Missing synthetic truth or challenge row')
                for field in fields:
                    old, new = target[field], reference[field]
                    if old != new:
                        db.execute(f'UPDATE {table} SET {field}=? WHERE {pk}=?', (new, key))
                        audit(db, table, key, field, old, new)
                        edited_fields += 1
        db.commit()
    remaining = validate(output_db, include_open_queries=False)['issues']
    if remaining:
        raise ValueError(f'Data issues remain: {remaining[:3]}')
    with sqlite3.connect(output_db) as db:
        for row in query_rows:
            db.execute('UPDATE discrepancy_queries SET query_status=?, disposition=? WHERE query_id=?',
                       ('resolved', REASON, row['query_id']))
            audit(db, 'discrepancy_queries', row['query_id'], 'query_status', 'open', 'resolved')
        db.commit()
    result = validate(output_db)
    if result['issues'] or not result['lock_ready_technical_simulation']:
        raise ValueError('Technical lock readiness failed after reconciliation')
    with sqlite3.connect(output_db) as db:
        audit_count = db.execute('SELECT COUNT(*) FROM audit_log').fetchone()[0]
        resolved_count = db.execute("SELECT COUNT(*) FROM discrepancy_queries WHERE query_status='resolved'").fetchone()[0]
    return {'synthetic_only': True, 'root_errors_corrected': len(roots),
            'fields_or_rows_changed': edited_fields, 'queries_resolved': resolved_count,
            'audit_entries': audit_count, 'remaining_issues': 0,
            'lock_ready_technical_simulation': True,
            'source_review': 'Synthetic truth-reference exercise; no actual source-data verification.'}


def audit(db, table, key, field, old, new):
    db.execute('INSERT INTO audit_log (action_utc, actor, table_name, record_key, field_name, old_value, new_value, reason) VALUES (?,?,?,?,?,?,?,?)',
               (STAMP, 'SIMULATED_SOURCE_REVIEW', table, key, field,
                None if old is None else str(old), None if new is None else str(new), REASON))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--challenge', default=str(ROOT / 'data/registry_challenge.sqlite'))
    parser.add_argument('--clean', default=str(ROOT / 'data/registry_clean.sqlite'))
    parser.add_argument('--manifest', default=str(ROOT / 'data/injected_errors.csv'))
    parser.add_argument('--queries', default=str(ROOT / 'reports/challenge_queries.csv'))
    parser.add_argument('--output-db', default=str(ROOT / 'data/registry_reconciled.sqlite'))
    parser.add_argument('--report', default=str(ROOT / 'reports/reconciliation.json'))
    args = parser.parse_args()
    result = reconcile(args.challenge, args.clean, args.manifest, args.output_db, args.queries)
    Path(args.report).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
