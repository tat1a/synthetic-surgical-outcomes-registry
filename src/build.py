"""One-command rebuild of the portfolio simulation and its aggregate dashboard."""
import json

from src import dashboard, export_aggregates, generate, reconcile, summarize, validate

ROOT = generate.ROOT


def main():
    seed, participants = 20261001, 300
    clean = ROOT / 'data/registry_clean.sqlite'
    challenge = ROOT / 'data/registry_challenge.sqlite'
    generated = ROOT / 'data/injected_errors.csv'
    queries = ROOT / 'reports/challenge_queries.csv'
    generate.create_database(clean, participants, seed)
    roots = generate.inject_challenge(clean, challenge, generated)
    (ROOT / 'data/generation_manifest.json').write_text(
        json.dumps({'synthetic_only': True, 'seed': seed,
                    'participants': participants, 'injected_errors': len(roots)}, indent=2) + '\n')
    reports = {}
    for name, database in (('clean', clean), ('challenge', challenge)):
        report = validate.validate(database)
        reports[name] = report
        (ROOT / f'reports/{name}_validation.json').write_text(json.dumps(report, indent=2) + '\n')
        if name == 'challenge':
            validate.write_queries(report['issues'], queries)
    detected = {(item['rule_id'], item['record_key']) for item in reports['challenge']['issues']}
    expected = {(item['rule_id'], item['record_key']) for item in roots}
    if (not reports['clean']['lock_ready_technical_simulation'] or
            reports['challenge']['lock_ready_technical_simulation'] or
            not expected <= detected):
        raise RuntimeError('Synthetic registry QA gate failed; inspect validation reports')
    result = reconcile.reconcile(challenge, clean, generated,
                                 ROOT / 'data/registry_reconciled.sqlite', queries)
    (ROOT / 'reports/reconciliation.json').write_text(json.dumps(result, indent=2) + '\n')
    summarize.main()
    export_aggregates.export()
    dashboard.render()
    print('Built synthetic registry, validation reports, reconciliation trail, and dashboard.')


if __name__ == '__main__':
    main()
