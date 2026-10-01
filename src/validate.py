"""Independent registry edit checks and simulated lock-readiness assessment."""
import argparse
import csv
from datetime import date, timedelta
import json
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('breast', 'nerve', 'wound')
TARGETS = (30, 90, 180, 365)


def validate(path, include_open_queries=True):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    issues = []

    def issue(rule, table, key, description, severity='critical'):
        issues.append({'rule_id': rule, 'table': table, 'record_key': key,
                       'severity': severity, 'description': description})

    def parsed_day(value, table, key, field):
        if value is None or re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) is None:
            issue('DATE_FORMAT', table, key, f'{field} must be a valid ISO calendar date')
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            issue('DATE_FORMAT', table, key, f'{field} must be a valid ISO calendar date')
            return None

    for row in connection.execute('PRAGMA foreign_key_check'):
        issue('ORPHAN_FK', row['table'], str(row['rowid']), 'Foreign key has no parent')
    participants = {r['participant_id']: r for r in connection.execute('SELECT * FROM participants')}
    procedures = {r['procedure_id']: r for r in connection.execute('SELECT * FROM procedures')}
    if not participants:
        issue('EMPTY_REGISTRY', 'participants', '<registry>', 'No participants were captured')
    else:
        for cohort in MODULES:
            if not any(person['cohort'] == cohort for person in participants.values()):
                issue('COHORT_ABSENT', 'participants', cohort, 'Expected demonstration cohort absent')
    enrollment_dates = {key: parsed_day(row['enrolled_on'], 'participants', key, 'enrolled_on')
                        for key, row in participants.items()}
    module_ids = {name: {r[0] for r in connection.execute(f'SELECT procedure_id FROM {name}_module')}
                  for name in MODULES}
    operation_dates = {}
    for key, row in procedures.items():
        operation = parsed_day(row['procedure_on'], 'procedures', key, 'procedure_on')
        operation_dates[key] = operation
        person = participants.get(row['participant_id'])
        if person is None:
            continue  # FK rule covers this.
        enrollment = enrollment_dates[person['participant_id']]
        if operation and enrollment and operation < enrollment:
            issue('CHRONOLOGY', 'procedures', key, 'Procedure precedes enrollment')
        if row['cohort'] != person['cohort']:
            issue('COHORT_MISMATCH', 'procedures', key, 'Procedure cohort differs from participant')
        for module in MODULES:
            if module == person['cohort'] and key not in module_ids[module]:
                issue('MODULE_MISSING', module + '_module', key, 'Required cohort module absent')
            if module != person['cohort'] and key in module_ids[module]:
                issue('MODULE_WRONG', module + '_module', key, 'Unexpected cohort module')
    followups = list(connection.execute('SELECT * FROM followups'))
    by_participant = {r['participant_id']: r for r in procedures.values()}
    seen = {(r['participant_id'], r['day_target']) for r in followups}
    for person in participants.values():
        if person['participant_id'] not in by_participant:
            issue('PROCEDURE_MISSING', 'participants', person['participant_id'],
                  'Participant has no index procedure')
        for target in TARGETS:
            if (person['participant_id'], target) not in seen:
                issue('VISIT_MISSING', 'followups', f"{person['participant_id']}:{target}",
                      'Expected follow-up row absent')
    for row in followups:
        key = row['followup_id']
        due_recorded = parsed_day(row['due_on'], 'followups', key, 'due_on')
        visit_recorded = (parsed_day(row['visit_on'], 'followups', key, 'visit_on')
                          if row['visit_on'] is not None else None)
        operation = by_participant.get(row['participant_id'])
        if operation is None:
            continue
        operation_day = operation_dates[operation['procedure_id']]
        if operation_day and due_recorded and due_recorded != operation_day + timedelta(days=row['day_target']):
            issue('FOLLOWUP_DUE', 'followups', key, 'Due date does not equal procedure date plus target days')
        if operation_day and visit_recorded and visit_recorded < operation_day:
            issue('FOLLOWUP_CHRONOLOGY', 'followups', key, 'Visit precedes index procedure')
        if row['status'] == 'completed' and (row['visit_on'] is None or row['function_score'] is None):
            issue('FOLLOWUP_STATUS', 'followups', key, 'Completed visit lacks visit date or score')
        elif row['status'] == 'missed' and (row['visit_on'] is not None or row['function_score'] is not None):
            issue('FOLLOWUP_STATUS', 'followups', key, 'Missed visit contains a date or score')
    events = list(connection.execute('SELECT * FROM adverse_events'))
    for row in events:
        key = row['event_id']
        event_day = parsed_day(row['event_on'], 'adverse_events', key, 'event_on')
        notified_day = (parsed_day(row['notified_on'], 'adverse_events', key, 'notified_on')
                        if row['notified_on'] is not None else None)
        procedure = procedures.get(row['procedure_id'])
        operation_day = operation_dates[procedure['procedure_id']] if procedure else None
        if operation_day and event_day and event_day < operation_day:
            issue('AE_CHRONOLOGY', 'adverse_events', key, 'AE precedes procedure')
        if row['serious'] and not row['notified_on']:
            issue('SAE_NOTIFICATION', 'adverse_events', key, 'Serious AE has no notification date')
        if notified_day and event_day and notified_day < event_day:
            issue('AE_NOTIFICATION_CHRONOLOGY', 'adverse_events', key, 'Notification precedes AE')
    if include_open_queries:
        queries = list(connection.execute('SELECT * FROM discrepancy_queries'))
        for q in queries:
            if q['severity'] == 'critical' and q['query_status'] == 'open':
                issue('OPEN_CRITICAL_QUERY', 'discrepancy_queries', q['query_id'], 'Critical query remains open')
    connection.close()
    issues.sort(key=lambda x: (x['rule_id'], x['record_key'], x['table']))
    by_rule = {}
    for item in issues:
        by_rule[item['rule_id']] = by_rule.get(item['rule_id'], 0) + 1
    return {'synthetic_only': True, 'participants': len(participants),
            'procedures': len(procedures), 'followups': len(followups),
            'adverse_events': len(events), 'critical_issues': len(issues),
            'issues_by_rule': by_rule, 'lock_ready_technical_simulation': len(issues) == 0,
            'issues': issues}


def write_queries(issues, output):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=('query_id','rule_id','table','record_key',
                                                     'severity','query_status','description','disposition'))
        writer.writeheader()
        for number, item in enumerate(issues, 1):
            writer.writerow({'query_id': f'Q-{number:04d}', **item,
                             'query_status': 'open', 'disposition': ''})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--queries')
    args = parser.parse_args()
    report = validate(args.database)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n')
    if args.queries:
        write_queries(report['issues'], args.queries)
    print(f"{report['participants']} synthetic participants; {report['critical_issues']} critical issues; "
          f"technical lock ready: {report['lock_ready_technical_simulation']}")


if __name__ == '__main__':
    main()
