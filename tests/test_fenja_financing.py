"""Regression tests for Fenja capacity, risk weighting and debt warnings."""
import copy
import datetime as dt
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from update_financing import fenja_capacity_metrics, pct_probability
from risk_signals import baseline_signals


class FenjaFacilityRiskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(
            (ROOT / "data" / "financing_model.json").read_text(encoding="utf-8")
        )

    def test_fully_drawn_facility_has_no_remaining_capacity(self):
        c = self.model["company"]
        metrics = fenja_capacity_metrics(c, self.model["calculation"])
        self.assertEqual(metrics["previously_drawn_msek"], 100)
        self.assertEqual(metrics["additional_draw_msek"], 0)
        self.assertEqual(metrics["fenja_cap_factor"], 1)
        self.assertEqual(metrics["annual_minimum_drawn_interest_msek"], 10)
        self.assertEqual(metrics["annual_minimum_undrawn_fee_msek"], 0)
        self.assertFalse(metrics["market_cap_limit_application_verified"])

    def test_price_changes_cannot_reopen_exhausted_facility(self):
        for price in (1, 5, 20, 100):
            clone = copy.deepcopy(self.model)
            clone["company"]["fenja"]["market_snapshot"]["price_sek"] = price
            metrics = fenja_capacity_metrics(clone["company"], clone["calculation"])
            self.assertEqual(metrics["additional_draw_msek"], 0)
            self.assertEqual(metrics["fenja_cap_factor"], 1)

    def test_convertible_notice_does_not_signal_new_cash_share_issue(self):
        from update_financing import classification
        from risk_signals import headline_signals
        title = "SynAct påkallar andra tranchen samt beslutar om en riktad emission av konvertibler till Fenja"
        self.assertEqual(classification(title), "finansiering")
        alerts = headline_signals([{"title": title, "date": "2026-11-18", "url": "https://mfn.se/", "category": "bolaget"}], "synact", dt.date(2026, 11, 18))
        self.assertNotIn("new_equity", {a["category"] for a in alerts})
        self.assertIn("new_debt", {a["category"] for a in alerts})

    def test_neutral_capacity_factor_does_not_add_a_risk_penalty(self):
        calc = dict(self.model["calculation"])
        metrics = fenja_capacity_metrics(self.model["company"], calc)
        neutral = dict(calc, fenja_cap_factor=metrics["fenja_cap_factor"])
        for horizon in (3, 6, 12):
            self.assertEqual(pct_probability(horizon, 10.5, calc),
                             pct_probability(horizon, 10.5, neutral))

    def test_separate_fenja_warning_categories(self):
        alerts = baseline_signals(self.model, dt.date(2026, 11, 15))
        cats = {a["category"] for a in alerts}
        self.assertTrue({"credit_capacity", "debt_maturity", "debt_cost"}.issubset(cats))
        for a in alerts:
            self.assertTrue(a["source"].startswith("https://"))

if __name__ == "__main__":
    unittest.main()
