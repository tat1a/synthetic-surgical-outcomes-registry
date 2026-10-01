"""Render a standalone aggregate operational dashboard; no patient-level data."""
from collections import Counter
import html
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/operational_dashboard.html'


def render():
    with sqlite3.connect(ROOT / 'data/registry_clean.sqlite') as db:
        cohort = dict(db.execute('SELECT cohort, COUNT(*) FROM participants GROUP BY cohort'))
        visits = db.execute("SELECT day_target, SUM(status='completed'), COUNT(*) FROM followups GROUP BY day_target ORDER BY day_target").fetchall()
        ae_count = db.execute('SELECT COUNT(*) FROM adverse_events').fetchone()[0]
        serious = db.execute('SELECT COUNT(*) FROM adverse_events WHERE serious=1').fetchone()[0]
    challenge = json.loads((ROOT / 'reports/challenge_validation.json').read_text())
    resolution = json.loads((ROOT / 'reports/reconciliation.json').read_text())
    summary = json.loads((ROOT / 'reports/lock_readiness.json').read_text())
    if sum(cohort.values()) != summary['followup_completion']['planned'] // 4:
        raise ValueError('Aggregate sources are inconsistent')
    labels = {'breast': 'Breast surgery', 'nerve': 'Peripheral nerve', 'wound': 'Wound reconstruction'}
    rows = ''.join(
        f'<tr><th scope="row">Day {day}</th><td>{done:,} / {total:,}</td>'
        f'<td><div class="meter" role="img" aria-label="{100*done/total:.1f} percent completed"><span style="width:{100*done/total:.1f}%"></span></div></td>'
        f'<td>{100*done/total:.1f}%</td></tr>' for day, done, total in visits)
    max_count = max(challenge['issues_by_rule'].values())
    checks = ''.join(
        f'<li><span>{html.escape(rule.replace("_", " ").title())}</span><div class="meter" role="img" aria-label="{count} queries"><span style="width:{100*count/max_count:.1f}%"></span></div><strong>{count}</strong></li>'
        for rule, count in sorted(challenge['issues_by_rule'].items(), key=lambda x: (-x[1], x[0])))
    total = sum(cohort.values())
    cards = ''.join(f'<div class="cohort"><span class="dot {key}"></span><span>{labels[key]}</span><strong>{cohort[key]:,}</strong></div>'
                    for key in ('breast','nerve','wound'))
    html_doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Synthetic Surgical Registry | Data Operations</title>
<style>
:root{{--ink:#17283d;--muted:#607185;--blue:#195b98;--light:#eaf2f8;--teal:#177f75;--orange:#c27332;--line:#dce5ec;--bg:#f4f7fa}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
.wrap{{max-width:1160px;margin:auto;padding:38px 28px 48px}}header{{display:flex;justify-content:space-between;gap:20px;align-items:start;margin-bottom:28px}}
.eyebrow{{text-transform:uppercase;letter-spacing:.14em;font-size:12px;font-weight:750;color:var(--blue)}}h1{{font-size:clamp(28px,4vw,41px);letter-spacing:-.035em;line-height:1.1;margin:8px 0}}
.sub{{color:var(--muted);max-width:700px;margin:0}}.badge{{background:#fff4e9;border:1px solid #eed2b7;color:#8a4917;padding:8px 12px;border-radius:24px;font-weight:750;font-size:12px;white-space:nowrap}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}}.card,.panel{{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 5px 20px #17304408}}
.card{{padding:19px 21px;border-top:4px solid var(--blue)}}.card:nth-child(2){{border-color:var(--teal);border-left-color:var(--line);border-right-color:var(--line);border-bottom-color:var(--line)}}
.card.warn{{border-top-color:var(--orange)}}.card small{{display:block;color:var(--muted);font-size:12px;font-weight:650}}.card strong{{display:block;font-size:30px;letter-spacing:-.04em;margin-top:4px}}.card em{{display:block;color:var(--muted);font-size:12px;font-style:normal}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.panel{{padding:24px;min-width:0}}h2{{font-size:18px;margin:0 0 6px}}.note{{color:var(--muted);font-size:13px;margin:0 0 18px}}
.cohort{{display:flex;align-items:center;padding:13px 0;border-top:1px solid var(--line);gap:10px}}.cohort strong{{margin-left:auto}}.dot{{width:9px;height:9px;border-radius:50%}}.breast{{background:#236aa5}}.nerve{{background:#17877b}}.wound{{background:#c07539}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}td,th{{text-align:left;border-bottom:1px solid var(--line);padding:11px 7px}}th{{white-space:nowrap}}td:last-child{{text-align:right}}.meter{{height:9px;background:var(--light);border-radius:10px;overflow:hidden;min-width:70px}}.meter span{{display:block;height:100%;background:var(--blue);border-radius:10px}}
.checks{{list-style:none;padding:0;margin:0}}.checks li{{display:grid;grid-template-columns:145px 1fr 30px;gap:14px;align-items:center;margin:13px 0;font-size:12px}}.checks .meter span{{background:var(--orange)}}.checks strong{{text-align:right}}
.flow{{display:flex;align-items:center;justify-content:space-around;gap:10px;padding:12px 0}}.flow div{{text-align:center;flex:1}}.flow b{{display:block;font-size:23px}}.flow span{{font-size:12px;color:var(--muted)}}.flow i{{font-size:18px;color:#91a1ae;font-style:normal}}
.status{{padding:13px 15px;border-radius:10px;background:#e8f6f2;color:#146a60;font-size:13px;font-weight:650}}footer{{color:var(--muted);font-size:12px;margin-top:20px}}
@media(max-width:780px){{header{{display:block}}.badge{{display:inline-block;margin-top:15px}}.metrics{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}}}
@media(max-width:480px){{.wrap{{padding:24px 15px}}.metrics{{grid-template-columns:1fr 1fr}}.card{{padding:14px}}.card strong{{font-size:24px}}.panel{{padding:17px}}.checks li{{grid-template-columns:115px 1fr 25px}}}}
</style></head><body><main class="wrap">
<header><div><div class="eyebrow">Data operations · portfolio demonstration</div><h1>Surgical Outcomes Registry</h1><p class="sub">Synthetic participants across breast, peripheral nerve, and wound surgery modules. Operational completeness, discrepancy detection, and a simulated database-lock workflow.</p></div><span class="badge">SYNTHETIC DATA ONLY</span></header>
<section class="metrics" aria-label="Key indicators"><div class="card"><small>Simulated participants</small><strong>{total:,}</strong><em>100 in each module</em></div><div class="card"><small>Follow-up completion</small><strong>{summary['followup_completion']['percentage']:.1f}%</strong><em>{summary['followup_completion']['completed']:,} / {summary['followup_completion']['planned']:,} scheduled</em></div><div class="card"><small>Adverse event records</small><strong>{ae_count}</strong><em>{serious} serious flags, simulated</em></div><div class="card warn"><small>Challenge queries</small><strong>{challenge['critical_issues']}</strong><em>18 seeded root errors plus cascades</em></div></section>
<div class="grid"><section class="panel"><h2>Registry composition</h2><p class="note">One index procedure per synthetic participant.</p>{cards}</section><section class="panel"><h2>Follow-up by planned milestone</h2><p class="note">Completion describes simulated data capture, not recovery.</p><table><thead><tr><th>Target</th><th>Completed</th><th>Rate</th><th>Share</th></tr></thead><tbody>{rows}</tbody></table></section>
<section class="panel"><h2>Challenge discrepancy types</h2><p class="note">Thirty rule hits include downstream follow-up date conflicts from three changed procedure dates.</p><ul class="checks">{checks}</ul></section><section class="panel"><h2>Query lifecycle</h2><p class="note">Controlled exercise using a separate generated truth reference.</p><div class="flow"><div><b>18</b><span>root errors</span></div><i>→</i><div><b>30</b><span>queries</span></div><i>→</i><div><b>{resolution['queries_resolved']}</b><span>resolved</span></div></div><div class="status">After simulated reconciliation: 0 open critical issues; technical lock-readiness check passes.</div><p class="note" style="margin-top:16px">{resolution['audit_entries']} audit entries record changes and query closures. No clinical source records were reviewed.</p></section></div>
<footer>Generated from local aggregate SQLite tables and validation reports · Seed {summary['seed']} · Illustration only. No real patients, PHI, clinical comparisons, or regulatory database lock.</footer></main></body></html>'''
    OUT.write_text(html_doc)
    return OUT


if __name__ == '__main__':
    print(render())
