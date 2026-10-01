"""Generate a deterministic, entirely fictional surgical registry and challenge set."""
import argparse
import csv
from datetime import date, timedelta
import json
from pathlib import Path
import random
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
COHORTS = ('breast', 'nerve', 'wound')
TARGETS = (30, 90, 180, 365)


def iso(day):
    return day.isoformat()


def create_database(path, count=300, seed=20261001):
    if count < 3 or count % 3:
        raise ValueError('participants must be a positive multiple of 3')
    rng = random.Random(seed)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    connection = sqlite3.connect(path)
    connection.execute('PRAGMA foreign_keys = ON')
    connection.executescript((ROOT / 'sql/schema.sql').read_text())
    for index in range(1, count + 1):
        cohort = COHORTS[(index - 1) % 3]
        pid, proc_id = f'SYN-{index:04d}', f'PROC-{index:04d}'
        enrollment = date(2024, 1, 1) + timedelta(days=rng.randint(0, 280))
        operation = enrollment + timedelta(days=rng.randint(0, 20))
        connection.execute('INSERT INTO participants VALUES (?,?,?,?)',
                           (pid, cohort, rng.choice(('18-39','40-59','60+')), iso(enrollment)))
        kind = {'breast': 'breast surgery', 'nerve': 'upper-extremity reconstruction',
                'wound': 'wound coverage'}[cohort]
        connection.execute('INSERT INTO procedures VALUES (?,?,?,?,?)',
                           (proc_id, pid, cohort, iso(operation), kind))
        if cohort == 'breast':
            connection.execute('INSERT INTO breast_module VALUES (?,?,?,?)',
                               (proc_id, rng.choice(('reconstruction','aesthetic')),
                                rng.choice(('left','right','bilateral')), rng.randrange(2)))
        elif cohort == 'nerve':
            connection.execute('INSERT INTO nerve_module VALUES (?,?,?,?)',
                               (proc_id, rng.choice(('plexus','peripheral')),
                                rng.choice(('transfer','graft','primary repair')),
                                rng.choice(('shoulder','elbow','hand'))))
        else:
            connection.execute('INSERT INTO wound_module VALUES (?,?,?,?)',
                               (proc_id, rng.choice(('upper limb','lower limb','trunk')),
                                rng.choice(('local flap','free flap','skin graft')),
                                rng.choice(('small','medium','large'))))
        for day in TARGETS:
            due = operation + timedelta(days=day)
            completed = rng.random() < (0.88 if day < 365 else 0.72)
            visit = due + timedelta(days=rng.randint(-7, 10)) if completed else None
            score = rng.randint(35, 95) if completed else None
            connection.execute('INSERT INTO followups VALUES (?,?,?,?,?,?,?)',
                               (f'FU-{index:04d}-{day}', pid, day, iso(due),
                                'completed' if completed else 'missed',
                                iso(visit) if visit else None, score))
        if rng.random() < 0.16:
            event_day = operation + timedelta(days=rng.randint(1, 80))
            serious = int(rng.random() < 0.10)
            connection.execute('INSERT INTO adverse_events VALUES (?,?,?,?,?,?,?)',
                               (f'AE-{index:04d}', proc_id, iso(event_day),
                                rng.choice(('infection','hematoma','wound dehiscence','other')),
                                rng.choice(('mild','moderate','severe')), serious,
                                iso(event_day + timedelta(days=rng.randint(0, 3))) if serious else None))
    connection.commit()
    connection.close()


def inject_challenge(clean_path, challenge_path, manifest_path):
    """Inject one observable critical issue per case, without breaking SQL constraints."""
    clean_path, challenge_path, manifest_path = map(Path, (clean_path, challenge_path, manifest_path))
    challenge_path.unlink(missing_ok=True)
    source = sqlite3.connect(clean_path)
    target = sqlite3.connect(challenge_path)
    source.backup(target)
    source.close()
    errors = []

    def alter(rule, table, keyfield, key, statement, parameters):
        target.execute(statement, parameters)
        errors.append({'rule_id': rule, 'table': table, 'record_key': key, 'severity': 'critical'})

    # Distinct participants keep challenge cases independently auditable.
    for i in range(1, 4):
        key = f'PROC-{i:04d}'
        alter('CHRONOLOGY', 'procedures', 'procedure_id', key,
              'UPDATE procedures SET procedure_on = ? WHERE procedure_id = ?', ('2020-01-01', key))
    for i in range(4, 7):
        key = f'FU-{i:04d}-90'
        alter('FOLLOWUP_STATUS', 'followups', 'followup_id', key,
              "UPDATE followups SET status = 'completed', visit_on = NULL WHERE followup_id = ?", (key,))
    for i in range(7, 10):
        key = f'FU-{i:04d}-180'
        alter('FOLLOWUP_DUE', 'followups', 'followup_id', key,
              'UPDATE followups SET due_on = ? WHERE followup_id = ?', ('2020-01-01', key))
    for i in range(10, 13):
        key = f'PROC-{i:04d}'
        module = {'breast': 'breast_module', 'nerve': 'nerve_module', 'wound': 'wound_module'}[
            target.execute('SELECT cohort FROM procedures WHERE procedure_id = ?', (key,)).fetchone()[0]]
        alter('MODULE_MISSING', module, 'procedure_id', key,
              f'DELETE FROM {module} WHERE procedure_id = ?', (key,))
    for i in range(13, 16):
        key = f'PROC-{i:04d}'
        alter('COHORT_MISMATCH', 'procedures', 'procedure_id', key,
              'UPDATE procedures SET cohort = ? WHERE procedure_id = ?',
              ('nerve' if (i-1) % 3 != 1 else 'breast', key))
    # Force three valid existing events to be serious but unnotified.
    events = target.execute('SELECT event_id FROM adverse_events WHERE CAST(SUBSTR(procedure_id, 6) AS INTEGER) > 20 ORDER BY event_id LIMIT 3').fetchall()
    if len(events) < 3:
        raise ValueError('challenge requires at least three existing AEs; increase sample size')
    for (key,) in events:
        alter('SAE_NOTIFICATION', 'adverse_events', 'event_id', key,
              'UPDATE adverse_events SET serious = 1, notified_on = NULL WHERE event_id = ?', (key,))
    target.commit()
    target.close()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=('rule_id','table','record_key','severity'))
        writer.writeheader()
        writer.writerows(errors)
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=20261001)
    parser.add_argument('--participants', type=int, default=300)
    args = parser.parse_args()
    clean = ROOT / 'data/registry_clean.sqlite'
    create_database(clean, args.participants, args.seed)
    injected = inject_challenge(clean, ROOT / 'data/registry_challenge.sqlite',
                                ROOT / 'data/injected_errors.csv')
    (ROOT / 'data/generation_manifest.json').write_text(
        json.dumps({'synthetic_only': True, 'seed': args.seed,
                    'participants': args.participants, 'injected_errors': len(injected)}, indent=2) + '\n')
    print(f'Generated {args.participants} synthetic participants; {len(injected)} deliberate critical errors.')


if __name__ == '__main__':
    main()
