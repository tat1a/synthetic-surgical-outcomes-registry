"""Generate a portable PBIP snapshot from the public aggregate CSV exports.

The report contains no row-level participant data. Regenerate after src.build.
Power BI Desktop is required to open, render, and export the project as PBIX.
"""

import base64
import csv
import io
import json
from pathlib import Path
import shutil
import uuid


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "powerbi"
NAME = "Synthetic_Surgical_Registry"
MODEL = OUT / f"{NAME}.SemanticModel"
REPORT = OUT / f"{NAME}.Report"
SAMPLE_THEME = None  # The PBIR uses the default Power BI theme.
SCHEMAS = {
    "cohort_counts": {"cohort": "text", "participant_count": "int64"},
    "followup_by_cohort": {"cohort": "text", "day_target": "int64", "planned": "int64", "completed": "int64", "missed": "int64"},
    "ae_by_cohort": {"cohort": "text", "event_count": "int64", "serious_count": "int64", "unnotified_serious_count": "int64"},
    "challenge_queries_by_rule": {"rule_id": "text", "query_count": "int64"},
    "field_completeness": {"table_name": "text", "field_name": "text", "nonmissing": "int64", "rows": "int64", "missing": "int64"},
}
MEASURES = {
    "Participants": ("SUM(cohort_counts[participant_count])", "#,0"),
    "Planned Visits": ("SUM(followup_by_cohort[planned])", "#,0"),
    "Completed Visits": ("SUM(followup_by_cohort[completed])", "#,0"),
    "Follow-up Completion": ("DIVIDE([Completed Visits], [Planned Visits])", "0.0%;-0.0%;0.0%"),
    "Challenge Queries": ("SUM(challenge_queries_by_rule[query_count])", "#,0"),
    "Event Records": ("SUM(ae_by_cohort[event_count])", "#,0"),
    "Serious Event Flags": ("SUM(ae_by_cohort[serious_count])", "#,0"),
    "Missing Cells": ("SUM(field_completeness[missing])", "#,0"),
}


def tag(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "synthetic-surgical-registry/pbip/" + name))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def literal(value):
    return {"expr": {"Literal": {"Value": "'" + value.replace("'", "''") + "'"}}}


def source(table, field, measure=False, aggregate=False):
    expression = {"SourceRef": {"Entity": table}}
    node = {"Measure" if measure else "Column": {"Expression": expression, "Property": field}}
    if aggregate:
        node = {"Aggregation": {"Expression": node, "Function": 0}}
    return node


def projection(table, field, measure=False, aggregate=False):
    q = f"{table}.{field}"
    if aggregate:
        q = f"Sum({q})"
    return {"field": source(table, field, measure, aggregate), "queryRef": q, "nativeQueryRef": field}


def visual(page, visual_name, visual_type, x, y, w, h, query=None, title=None, order=1):
    visual_obj = {"visualType": visual_type}
    if query:
        visual_obj["query"] = {"queryState": query}
    if title:
        visual_obj["visualContainerObjects"] = {"title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": literal(title)}}]}
    obj = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": visual_name,
        "position": {"x": x, "y": y, "z": order, "height": h, "width": w, "tabOrder": order},
        "visual": visual_obj,
    }
    write_json(REPORT / "definition" / "pages" / page / "visuals" / visual_name / "visual.json", obj)


def textbox(page, name, content, x, y, w, h, size=14, color="#17283D", bold=False, order=1):
    visual(page, name, "textbox", x, y, w, h, order=order)
    path = REPORT / "definition" / "pages" / page / "visuals" / name / "visual.json"
    obj = json.loads(path.read_text())
    obj["visual"]["objects"] = {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": content, "textStyle": {"fontSize": f"{size}pt", "fontWeight": "bold" if bold else "normal", "color": color}}]}]}}]}
    write_json(path, obj)


def table_definition(name, fields, raw):
    header = next(csv.reader(io.StringIO(raw)))
    if header != list(fields):
        raise ValueError(f"Aggregate schema drift in {name}: {header}")
    encoded = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    cols = []
    for col, kind in fields.items():
        column = [f"\tcolumn {col}", f"\t\tdataType: {kind}", f"\t\tlineageTag: {tag(name + '/' + col)}", f"\t\tsourceColumn: {col}"]
        if kind == "int64":
            column.extend(["\t\tformatString: #,0", "\t\tsummarizeBy: none"])
        cols.append("\n".join(column))
    transforms = ", ".join('{"' + col + '", ' + ("Int64.Type" if kind == "int64" else "type text") + '}' for col, kind in fields.items())
    steps = [
        "let",
        f'    Source = Csv.Document(Binary.FromText("{encoded}", BinaryEncoding.Base64), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        f'    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {{{transforms}}})',
        "in",
        '    #"Changed Type"',
    ]
    source_m = "\n".join("\t\t\t\t" + s for s in steps)
    text = f"table {name}\n\tlineageTag: {tag(name)}\n\n" + "\n\n".join(cols) + f"\n\n\tpartition {name} = m\n\t\tmode: import\n\t\tsource =\n{source_m}\n\n\tannotation PBI_ResultType = Table\n"
    return text


def build_model():
    d = MODEL / "definition"
    d.mkdir(parents=True, exist_ok=True)
    write_json(MODEL / "definition.pbism", {"version": "4.2", "settings": {}})
    (d / "database.tmdl").write_text("database\n\tcompatibilityLevel: 1606\n", encoding="utf-8")
    model = "model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\n"
    model += "annotation PBI_QueryOrder = " + json.dumps(list(SCHEMAS)) + "\n\n"
    model += "\n".join("ref table " + name for name in SCHEMAS) + "\n\nref cultureInfo en-US\n"
    (d / "model.tmdl").write_text(model, encoding="utf-8")
    culture = d / "cultures" / "en-US.tmdl"
    culture.parent.mkdir(exist_ok=True)
    culture.write_text("cultureInfo en-US\n", encoding="utf-8")
    for name, fields in SCHEMAS.items():
        raw = (ROOT / "reports" / "bi_tables" / f"{name}.csv").read_text(encoding="utf-8-sig")
        text = table_definition(name, fields, raw)
        if name == "cohort_counts":
            measures = []
            for label, (dax, fmt) in MEASURES.items():
                measures.append(f"\tmeasure '{label}' = {dax}\n\t\tformatString: {fmt}\n\t\tlineageTag: {tag('measure/' + label)}")
            text = text.replace("\tpartition cohort_counts", "\n\n".join(measures) + "\n\n\tpartition cohort_counts")
        path = d / "tables" / f"{name}.tmdl"
        path.parent.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8")


def build_report():
    write_json(OUT / f"{NAME}.pbip", {"version": "1.0", "artifacts": [{"report": {"path": f"{NAME}.Report"}}], "settings": {"enableAutoRecovery": True}})
    write_json(REPORT / "definition.pbir", {"version": "4.0", "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}}})
    d = REPORT / "definition"
    write_json(d / "version.json", {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    write_json(d / "report.json", {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json", "settings": {"useEnhancedTooltips": False}})
    pages = ["operations", "data_quality"]
    write_json(d / "pages" / "pages.json", {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json", "pageOrder": pages, "activePageName": pages[0]})
    for page, label in [(pages[0], "Registry Operations"), (pages[1], "Data Quality & Queries")]:
        write_json(d / "pages" / page / "page.json", {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json", "name": page, "displayName": label, "displayOption": "FitToPage", "height": 720, "width": 1280})
    p = pages[0]
    textbox(p, "title", "SURGICAL OUTCOMES REGISTRY  /  OPERATIONS", 40, 22, 1180, 52, 23, bold=True)
    textbox(p, "subtitle", "Synthetic portfolio demonstration · 300 fictional participants · operational metrics only", 42, 76, 1170, 35, 12, "#607185")
    for i, (label, measure) in enumerate([("Simulated participants", "Participants"), ("Follow-up completed", "Follow-up Completion"), ("Scheduled visits", "Planned Visits"), ("Event records", "Event Records")]):
        x = 40 + i * 305
        visual(p, f"kpi_{i}", "cardVisual", x, 130, 280, 120, {"Data": {"projections": [projection("cohort_counts", measure, measure=True)]}}, label, 10 + i)
    visual(p, "cohorts", "clusteredBarChart", 40, 286, 570, 330, {"Category": {"projections": [projection("cohort_counts", "cohort")]}, "Y": {"projections": [projection("cohort_counts", "participant_count", aggregate=True)]}}, "Participants by module", 20)
    visual(p, "visits", "clusteredColumnChart", 645, 286, 590, 330, {"Category": {"projections": [projection("followup_by_cohort", "day_target")]}, "Y": {"projections": [projection("cohort_counts", "Follow-up Completion", measure=True)]}}, "Completion by follow-up day", 21)
    textbox(p, "foot", "Completion reflects simulated data capture, not clinical recovery. No real patients or outcome comparisons.", 42, 645, 1170, 40, 11, "#607185")
    p = pages[1]
    textbox(p, "title", "DATA QUALITY  /  CONTROLLED CHALLENGE", 40, 22, 1180, 52, 23, bold=True)
    textbox(p, "subtitle", "18 deliberately injected root errors generated 30 rule hits; reconciliation is scripted against synthetic truth.", 42, 76, 1180, 42, 12, "#607185")
    for i, (label, measure) in enumerate([("Rule hits", "Challenge Queries"), ("Serious event flags", "Serious Event Flags")]):
        visual(p, f"quality_kpi_{i}", "cardVisual", 40 + i * 305, 138, 280, 112, {"Data": {"projections": [projection("cohort_counts", measure, measure=True)]}}, label, 10 + i)
    visual(p, "rules", "clusteredBarChart", 40, 285, 570, 330, {"Category": {"projections": [projection("challenge_queries_by_rule", "rule_id")]}, "Y": {"projections": [projection("challenge_queries_by_rule", "query_count", aggregate=True)]}}, "Rule hits by validation check", 20)
    columns = [projection("field_completeness", c, aggregate=c in ("nonmissing", "rows", "missing")) for c in SCHEMAS["field_completeness"]]
    visual(p, "completeness", "tableEx", 645, 285, 590, 330, {"Values": {"projections": columns}}, "Physical NULLs by field", 21)
    textbox(p, "foot", "Physical NULLs include intentionally optional fields. The validator, not this table, assesses business-rule completeness.", 42, 645, 1170, 40, 11, "#607185")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    build_model()
    build_report()
    print(f"Generated {OUT / (NAME + '.pbip')}")


if __name__ == "__main__":
    main()
