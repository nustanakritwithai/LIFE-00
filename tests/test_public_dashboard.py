"""Checks for a public-safe, explicitly non-live LIFE-00 dashboard."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]


class IdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])


class TestPublicDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs" / "status.json").read_text(encoding="utf-8"))
        cls.html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    def test_schema(self):
        d = self.data
        self.assertEqual(d["schema_version"], "0.1")
        self.assertEqual(d["snapshot_kind"], "TEMPLATE_ONLY")
        self.assertFalse(d["public_data_approved"])
        self.assertEqual(d["dashboard_status"], "NOT_DEPLOYED")
        self.assertEqual(d["pulse"]["target_interval_minutes"], 5)
        self.assertEqual(d["pulse"]["status"], "NOT_CONFIGURED")
        self.assertIsNone(d["pulse"]["last_heartbeat"])
        self.assertEqual([a["id"] for a in d["agents"]], ["LIFE-00", "LIFE-01"])

    def test_unknown_not_disguised_as_pass(self):
        for agent in self.data["agents"]:
            self.assertEqual(agent["growth_status"], "UNKNOWN")
            self.assertEqual(agent["memory_status"], "UNKNOWN")
            self.assertIsNone(agent["last_cycle"])
            self.assertIsNone(agent["last_checkpoint"])

    def test_no_private_data_in_snapshot(self):
        source = (ROOT / "docs" / "status.json").read_text(encoding="utf-8")
        for forbidden in ("TYPHOON_API_KEY", "OPENAI_API_KEY", "api.opentyphoon.ai", "docs.google.com/document", "Bearer ", "sk-"):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("BEGIN PRIVATE KEY", source)

    def test_html_contract(self):
        parser = IdParser()
        parser.feed(self.html)
        required = {"banner-title", "banner-note", "agents", "notices", "agent-count", "pulse-frequency", "pulse-state"}
        self.assertTrue(required.issubset(parser.ids))
        self.assertIn("UNKNOWN ≠ PASS", self.html)
        self.assertNotRegex(self.html, r'<script[^>]+src="https?://')

    def test_no_public_private_memory_reference(self):
        exposed = self.html + json.dumps(self.data, ensure_ascii=False)
        self.assertNotRegex(exposed, r"https://docs\.google\.com/document/d/")


if __name__ == "__main__":
    unittest.main()
