"""Regression tests for the site's deterministic financing warning rules."""
import datetime as dt
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from risk_signals import baseline_signals, headline_signals, combined_signals


class TestFinanceAlerts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads((ROOT / "data" / "financing_model.json").read_text(encoding="utf-8"))
        cls.issuer = "isofol" if "warrants" in cls.model["company"] else "synact"
        cls.now = dt.date(2026, 11, 13)

    def item(self, title, date="2026-11-10", category="omvärld"):
        return [{"title": title, "date": date, "source": "Finansnytt",
                 "url": "https://example.org/news", "category": category}]

    def test_known_finance_signals_have_primary_sources(self):
        alerts = baseline_signals(self.model, self.now)
        self.assertTrue(alerts)
        self.assertTrue(all(a["source"].startswith("https://") for a in alerts))
        self.assertTrue(all("Rubrikträff" not in a["status"] for a in alerts))
        self.assertTrue(all(a["id"].startswith("base:") for a in alerts))

    def test_trading_halt_is_high_priority_but_unverified(self):
        alert = headline_signals(self.item(
            self.issuer + " handelsstoppad med hänvisning till insiderinformation"), self.issuer, self.now)
        self.assertEqual(alert[0]["category"], "trading_halt")
        self.assertEqual(alert[0]["level"], "kritisk")
        self.assertIn("granskas", alert[0]["status"])

    def test_resumed_trading_is_not_presented_as_live_halt(self):
        alert = headline_signals(self.item(self.issuer + " handeln återupptas efter handelsstopp"),
                                 self.issuer, self.now)
        self.assertEqual(alert[0]["category"], "trading_resumed")

    def test_unrelated_company_is_excluded(self):
        self.assertEqual(headline_signals(self.item("Cereno handelsstoppad"), self.issuer, self.now), [])

    def test_headline_needs_original_context(self):
        alert = headline_signals(self.item(self.issuer + " skjuter upp betalningar till CRO"),
                                 self.issuer, self.now)
        self.assertEqual(alert[0]["category"], "deferred_payments")
        self.assertIn("Rubrikträff", alert[0]["status"])

    def test_no_emission_negation(self):
        alert = headline_signals(self.item(self.issuer + " ingen nyemission planeras"),
                                 self.issuer, self.now)
        self.assertFalse(any(a["category"] == "new_equity" for a in alert))

    def test_old_alert_expires(self):
        self.assertEqual(headline_signals(
            self.item(self.issuer + " handelsstoppad", "2026-08-01"),
            self.issuer, self.now), [])

    def test_new_equity_is_flagged(self):
        alert = headline_signals(self.item(self.issuer + " aviserar företrädesemission"),
                                 self.issuer, self.now)
        self.assertEqual(alert[0]["category"], "new_equity")

    def test_existing_isofol_options_not_new_equity(self):
        if self.issuer == "isofol":
            alert = headline_signals(self.item("Isofol TO2 teckningsoptioner av serie TO2 fastställts"),
                                     "isofol", self.now)
            self.assertFalse(any(a["category"] == "new_equity" for a in alert))


if __name__ == "__main__":
    unittest.main()
