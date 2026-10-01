import csv
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.generate import create_database, inject_challenge
from src.validate import validate, write_queries
from src.reconcile import reconcile
from src.dashboard import render
from src.export_aggregates import export


@contextmanager
def open_db(path):
    connection = sqlite3.connect(path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


class RegistryTests(unittest.TestCase):
    def test_seed_reproduces_records_and_clean_has_no_critical_issues(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / 'first.sqlite'
            second = Path(directory) / 'second.sqlite'
            create_database(first, 300, 20261001)
            create_database(second, 300, 20261001)
            for table in ('participants','procedures','followups','adverse_events'):
                with open_db(first) as a, open_db(second) as b:
                    self.assertEqual(a.execute(f'SELECT * FROM {table} ORDER BY 1').fetchall(),
                                     b.execute(f'SELECT * FROM {table} ORDER BY 1').fetchall())
            clean = validate(first)
            self.assertEqual(clean['critical_issues'], 0)
            self.assertTrue(clean['lock_ready_technical_simulation'])

    def test_every_injected_critical_case_is_detected_and_blocks_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            clean = Path(directory) / 'clean.sqlite'
            challenge = Path(directory) / 'challenge.sqlite'
            manifest = Path(directory) / 'injected.csv'
            create_database(clean, 300, 20261001)
            inject_challenge(clean, challenge, manifest)
            with manifest.open(newline='') as handle:
                expected = {(row['rule_id'], row['record_key']) for row in csv.DictReader(handle)}
            report = validate(challenge)
            actual = {(row['rule_id'], row['record_key']) for row in report['issues']}
            self.assertEqual(len(expected), 18)
            self.assertTrue(expected <= actual, f'Undetected injected cases: {expected - actual}')
            self.assertFalse(report['lock_ready_technical_simulation'])
            with open_db(challenge) as db:
                self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_query_resolution_has_trace_and_no_open_critical_discrepancies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clean, challenge, reconciled = (root / f'{name}.sqlite' for name in ('clean','challenge','reconciled'))
            manifest, queries = root / 'injected.csv', root / 'queries.csv'
            create_database(clean, 300, 20261001)
            inject_challenge(clean, challenge, manifest)
            write_queries(validate(challenge)['issues'], queries)
            result = reconcile(challenge, clean, manifest, reconciled, queries)
            self.assertEqual(result['root_errors_corrected'], 18)
            self.assertEqual(result['queries_resolved'], 30)
            self.assertEqual(result['audit_entries'], 48)
            self.assertTrue(validate(reconciled)['lock_ready_technical_simulation'])
            with open_db(reconciled) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM discrepancy_queries WHERE query_status='open'").fetchone()[0], 0)
                self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            for table in ('participants', 'procedures', 'breast_module', 'nerve_module',
                          'wound_module', 'followups', 'adverse_events'):
                with open_db(clean) as reference, open_db(reconciled) as restored:
                    self.assertEqual(reference.execute(f'SELECT * FROM {table} ORDER BY 1').fetchall(),
                                     restored.execute(f'SELECT * FROM {table} ORDER BY 1').fetchall())

    def test_dashboard_contains_only_aggregate_operational_fields(self):
        # Build has been run in the packaged workflow; check exported representation.
        output = render().read_text()
        self.assertIn('SYNTHETIC DATA ONLY', output)
        self.assertIn('Follow-up completion', output)
        self.assertNotIn('SYN-0001', output)
        self.assertNotIn('PROC-0001', output)
        self.assertNotIn('https://', output)

    def test_bi_exports_reconcile_with_independent_validation_totals(self):
        stats = export()
        self.assertEqual(stats['followup_planned'], 1200)
        self.assertEqual(stats['challenge_queries'], validate(
            Path(__file__).resolve().parents[1] / 'data/registry_challenge.sqlite')['critical_issues'])
        self.assertEqual(stats['adverse_events'], validate(
            Path(__file__).resolve().parents[1] / 'data/registry_clean.sqlite')['adverse_events'])

    def test_malformed_dates_and_missing_procedure_become_queries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.sqlite'
            create_database(path, 300, 20261001)
            with open_db(path) as db:
                db.execute('PRAGMA foreign_keys=ON')
                db.execute("UPDATE followups SET due_on='2024-02-30' WHERE followup_id='FU-0002-30'")
                db.execute("UPDATE procedures SET procedure_on='bad-date' WHERE procedure_id='PROC-0003'")
                db.execute("DELETE FROM adverse_events WHERE procedure_id='PROC-0001'")
                db.execute("DELETE FROM breast_module WHERE procedure_id='PROC-0001'")
                db.execute("DELETE FROM procedures WHERE procedure_id='PROC-0001'")
            found = {(i['rule_id'], i['record_key']) for i in validate(path)['issues']}
            self.assertIn(('DATE_FORMAT', 'FU-0002-30'), found)
            self.assertIn(('DATE_FORMAT', 'PROC-0003'), found)
            self.assertIn(('PROCEDURE_MISSING', 'SYN-0001'), found)

    def test_open_critical_query_blocks_lock_even_when_data_passes_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'clean_with_open_query.sqlite'
            create_database(path, 300, 20261001)
            with open_db(path) as db:
                db.execute("INSERT INTO discrepancy_queries VALUES ('Q-0001','MANUAL_REVIEW','SYN-0001','critical','open','Pending source review',NULL)")
            report = validate(path)
            self.assertIn('OPEN_CRITICAL_QUERY', report['issues_by_rule'])
            self.assertFalse(report['lock_ready_technical_simulation'])

    def test_empty_registry_cannot_pass_technical_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'empty.sqlite'
            with open_db(path) as db:
                db.executescript((Path(__file__).resolve().parents[1] / 'sql/schema.sql').read_text())
            report = validate(path)
            self.assertIn('EMPTY_REGISTRY', report['issues_by_rule'])
            self.assertFalse(report['lock_ready_technical_simulation'])


if __name__ == '__main__':
    unittest.main()
