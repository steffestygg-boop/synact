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


    def test_clickable_weekly_news_modal_is_present(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        html += (ROOT / "assets" / "week.js").read_text(encoding="utf-8")
        for marker in ("id=\"weekly-event-overlay\"", "id=\"weekly-event-title\"",
                       "id=\"weekly-event-facts\"", "id=\"weekly-event-links\"",
                       "button.addEventListener('click',()=>openEvent(it,button))",
                       "event.key==='Escape'"):
            self.assertIn(marker, html)
        self.assertIn("id=\"weekly-history\"", html)

    def test_curated_event_facts_survive_regeneration(self):
        curated = w.read_json(w.DATA / "weekly_event_details.json", {}).get("by_title", {})
        self.assertTrue(curated)
        title = sorted(curated)[0]
        info = curated[title]
        original = w.event(title, "2026-11-13", info["source_url"], "Bolagskälla")
        updated = w.enrich_events([original])
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0]["summary"], info["summary"])
        self.assertTrue(updated[0]["details"])
        self.assertTrue(updated[0]["key_facts"])
        self.assertTrue(updated[0]["editorial_verified"])
        self.assertNotIn("Rapporterad kassa och historiskt kassaflöde är inte", updated[0]["summary"])

    def test_abg_value_change_is_specific(self):
        if w.ISSUER != "isofol":
            return
        e = w.event("ABG höjer efter Q3", "2026-11-15",
                    "https://cr.abgsc.com/foretag/isofol-medical/example", "ABG", True)
        data = w.enrich_events([e])[0]
        self.assertIn("1,80", data["summary"])
        self.assertIn("2,10", data["summary"])
        self.assertIn("10,50", data["summary"])
        self.assertIn("11,00", data["summary"])

    def test_mfn_publisher_listing_parser(self):
        slug = {"isofol": "isofol-medical",
                "synact": "synact-pharma",
                "cereno": "cereno-scientific"}[w.ISSUER]
        sample = (
            '<div>2026-11-16 07:00:00 '
            '<a href="/a/' + slug + '/test-svensk">'
            + w.CONFIG[w.ISSUER]["name"] + ' meddelar styrelseförändring</a>'
            ' 2026-11-16 07:00:00 '
            '<a href="/a/' + slug + '/test-english">'
            + w.CONFIG[w.ISSUER]["name"] + ' announces board update</a></div>'
        )
        parser = w.MFNListingParser(slug)
        parser.feed(sample)
        self.assertEqual(len(parser.entries), 2)
        self.assertTrue(all(url.startswith("https://mfn.se/a/"+slug+"/")
                            for _, _, url in parser.entries))
        self.assertTrue(all(date.startswith("2026-11-16") for date, _, _ in parser.entries))

    def test_original_mfn_event_wins_over_syndicated_mirror(self):
        slug = {"isofol": "isofol-medical",
                "synact": "synact-pharma",
                "cereno": "cereno-scientific"}[w.ISSUER]
        publisher = w.event("Bolaget meddelar ny styrelse", "2026-11-16",
                            "https://mfn.se/a/"+slug+"/styrelse",
                            "MFN · bolagets pressmeddelande",
                            False, "bolagsflöde")
        mirror = w.event("Bolaget meddelar ny styrelse - MFN", "2026-11-16",
                         "https://news.google.com/rss/articles/example",
                         "MFN", False, "rubrik")
        enriched = w.enrich_events([publisher, mirror])
        self.assertEqual(len(enriched), 1)
        self.assertEqual(enriched[0]["origin"], "bolagsflöde")

    def test_iso_week_boundary_monday_to_sunday(self):
        monday = dt.date(2026, 11, 16)
        sunday = monday + dt.timedelta(days=6-monday.weekday())
        begin, end, week, week_no = w.bounds(sunday)
        self.assertEqual(begin, dt.date(2026,11,16))
        self.assertEqual(end, dt.date(2026,11,22))
        self.assertEqual(week, "2026-W47")

    def test_schedule_handles_daylight_saving_independent_of_start_delay(self):
        from zoneinfo import ZoneInfo
        zone = ZoneInfo("Europe/Stockholm")
        for day, expected_utc_hour in ((dt.date(2026,11,17),8),
                                       (dt.date(2026,7,15),7)):
            nine_local = dt.datetime.combine(day,dt.time(9,0),tzinfo=zone)
            self.assertEqual(nine_local.astimezone(dt.timezone.utc).hour,
                             expected_utc_hour)
        workflow = (ROOT / ".github" / "workflows" / "weekly-news.yml").read_text(encoding="utf-8")
        self.assertIn("cron: '0 7 * * *'",workflow)
        self.assertIn("cron: '0 8 * * *'",workflow)
        self.assertIn("cron: '0 14 * * 1-5'",workflow)
        self.assertIn("--scheduled-cron",workflow)

    def test_issuer_archive_has_no_generic_event_descriptions(self):
        archive = w.read_json(w.OUTPUT, {})
        self.assertTrue(archive.get("weeks"))
        generic = ("Rapporterad kassa och historiskt kassaflöde är inte",
                   "Finansieringsvillkor och möjlig utspädning behöver",
                   "Nyhetsrubriken återges med källa")
        for week in archive["weeks"]:
            for event in week.get("events", []):
                self.assertFalse(any(x in event.get("summary", "") for x in generic))

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
