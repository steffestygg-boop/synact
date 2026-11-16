"""No-network regression tests for all three Sunday-news dashboards."""
import datetime as dt
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import update_weekly_news as w


class WeeklyDigestTests(unittest.TestCase):
    def test_last_completed_week_on_monday(self):
        sunday = w.week_ending(dt.date(2026, 11, 16))
        self.assertEqual(sunday, dt.date(2026, 11, 15))
        start, end, key, no = w.bounds(sunday)
        self.assertEqual((start.isoformat(), end.isoformat(), key, no),
                         ("2026-11-09", "2026-11-15", "2026-W46", 46))

    def test_sunday_evening_includes_current_week(self):
        self.assertEqual(w.week_ending(dt.date(2026, 11, 22)), dt.date(2026, 11, 22))
        self.assertEqual(w.bounds(dt.date(2026, 11, 22))[2], "2026-W47")

    def test_iso_year_boundary(self):
        self.assertEqual(w.bounds(dt.date(2027, 1, 3))[2], "2026-W53")

    def test_no_future_milestone_treated_as_reported_event(self):
        val = w.event("Planerad fas II 2027", "2026-11-13",
                      "https://example.org/press", "Pressmeddelande")
        self.assertEqual(val["verified"], False)
        self.assertIn("inte fullständigt", val["source_note"])
        self.assertIsNone(w.milestone_date("Q1 2027 · prognos"))

    def test_swedish_milestone_date(self):
        self.assertEqual(w.milestone_date("13 november 2026"), dt.date(2026, 11, 13))
        self.assertEqual(w.milestone_date("4 nov 2026"), dt.date(2026, 11, 4))

    def test_distinguishes_stale_company_report_and_model_snapshot(self):
        current = {
            "risk_3": 12.2, "risk_6": 27.9, "risk_12": 60.4,
            "model_fingerprint": "new", "emission_status": "",
            "alerts": {}, "milestones": {}
        }
        previous = {
            "risk_3": 12.2, "risk_6": 25.6, "risk_12": 56.7,
            "model_fingerprint": "old", "emission_status": "",
            "alerts": {}, "milestones": {}
        }
        found = w.snapshot_changes(current, previous)
        self.assertTrue(any("Barometern" in x["title"] or "Emissionsbarometern" in x["title"]
                            for x in found))
        self.assertFalse(any("rapporterat" in x["title"] for x in found))

    def test_no_future_finance_projections_in_older_week_archive(self):
        current = {
            "risk_3": 12.2, "risk_6": 27.9, "risk_12": 60.4,
            "risk_as_of": "2026-11-16T08:30:00+01:00",
            "emission_status": "aviserad_2026-11-12",
        }
        old, retro = w.visible_finance_snapshot(current, dt.date(2026, 11, 8))
        self.assertTrue(retro)
        self.assertIsNone(old["risk_6"])
        self.assertFalse(old["emission_status"])
        current_week, retro = w.visible_finance_snapshot(current, dt.date(2026, 11, 15))
        self.assertFalse(retro)
        self.assertEqual(current_week["risk_6"], 27.9)

    def test_preserves_source_confidence(self):
        e = w.event("Cereno aviserar emission", "2026-11-12",
                    "https://mfn.se/a/cereno-scientific/sample", "Cereno", True)
        self.assertTrue(e["verified"])
        self.assertIn("källgranskad", e["source_note"])
        rss = w.event("SynAct announces patent", "2026-11-13",
                      "https://news.google.com/rss/articles/abc", "Nyhetskälla")
        self.assertFalse(rss["verified"])

    def test_category_and_event_dedup(self):
        one = w.event("Cereno Scientific planerar företrädesemission om 400 miljoner kronor",
                      "2026-11-12", "https://a.test/event", "Bolaget", True)
        two = w.event("Cereno Scientific planerar företrädesemission om 400 miljoner kronor",
                      "2026-11-12", "https://b.test/event", "Nyhetskälla")
        self.assertTrue(w.similar(one, two))


if __name__ == "__main__":
    unittest.main()
