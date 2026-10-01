"""Static Power BI handoff checks; Desktop rendering must be reviewed separately."""

import base64
import csv
import io
import json
from pathlib import Path
import re
import unittest

from src.build_powerbi import MEASURES, SCHEMAS


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "powerbi"
STEM = "Synthetic_Surgical_Registry"


class PowerBIProjectTests(unittest.TestCase):
    def test_embedded_aggregates_match_exports_and_expected_totals(self):
        model = PACKAGE / f"{STEM}.SemanticModel" / "definition" / "tables"
        parsed = {}
        for name, fields in SCHEMAS.items():
            definition = (model / f"{name}.tmdl").read_text(encoding="utf-8")
            match = re.search(r'Binary\.FromText\("([A-Za-z0-9+/=]+)", BinaryEncoding\.Base64\)', definition)
            self.assertIsNotNone(match, name)
            embedded = base64.b64decode(match.group(1)).decode("utf-8")
            source = (ROOT / "reports" / "bi_tables" / f"{name}.csv").read_text(encoding="utf-8-sig")
            self.assertEqual(embedded, source, name)
            parsed[name] = list(csv.DictReader(io.StringIO(embedded)))
            self.assertEqual(set(parsed[name][0]), set(fields))
        self.assertEqual(sum(int(r["participant_count"]) for r in parsed["cohort_counts"]), 300)
        self.assertEqual(sum(int(r["planned"]) for r in parsed["followup_by_cohort"]), 1200)
        self.assertEqual(sum(int(r["completed"]) for r in parsed["followup_by_cohort"]), 1012)
        self.assertEqual(sum(int(r["query_count"]) for r in parsed["challenge_queries_by_rule"]), 30)
        self.assertEqual(sum(int(r["event_count"]) for r in parsed["ae_by_cohort"]), 52)
        self.assertEqual(sum(int(r["serious_count"]) for r in parsed["ae_by_cohort"]), 5)

    def test_visual_fields_exist_and_report_is_aggregate_only(self):
        report = PACKAGE / f"{STEM}.Report" / "definition"
        pages = json.loads((report / "pages" / "pages.json").read_text(encoding="utf-8"))
        self.assertEqual(len(pages["pageOrder"]), 2)
        found = []
        for page in pages["pageOrder"]:
            page_dir = report / "pages" / page
            self.assertTrue((page_dir / "page.json").exists())
            for path in (page_dir / "visuals").glob("*/visual.json"):
                visual = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(visual["name"], path.parent.name)
                self.assertLessEqual(visual["position"]["x"] + visual["position"]["width"], 1280)
                self.assertLessEqual(visual["position"]["y"] + visual["position"]["height"], 720)
                for role in visual["visual"].get("query", {}).get("queryState", {}).values():
                    for item in role.get("projections", []):
                        self.assert_field(item["field"])
                found.append(visual["visual"]["visualType"])
        self.assertGreaterEqual(found.count("cardVisual"), 6)
        self.assertIn("tableEx", found)
        self.assertGreaterEqual(found.count("clusteredBarChart"), 2)

    def assert_field(self, field):
        if "Aggregation" in field:
            return self.assert_field(field["Aggregation"]["Expression"])
        kind, expression = next(iter(field.items()))
        table = expression["Expression"]["SourceRef"]["Entity"]
        self.assertIn(table, SCHEMAS)
        name = expression["Property"]
        self.assertIn(name, MEASURES if kind == "Measure" else SCHEMAS[table])


if __name__ == "__main__":
    unittest.main()
