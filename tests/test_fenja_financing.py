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

    def test_cap_based_on_dated_share_price(self):
        c = self.model["company"]
        metrics = fenja_capacity_metrics(c, self.model["calculation"])
        self.assertAlmostEqual(metrics["additional_draw_msek"], 24.31, places=2)
        self.assertAlmostEqual(metrics["max_total_draw_msek"], 74.31, places=2)
        self.assertEqual(metrics["price_as_of"], "2026-11-13")
        self.assertGreater(metrics["fenja_cap_factor"], 1)
        self.assertLess(metrics["fenja_cap_factor"], 1.21)

    def test_full_draw_requires_approximately_a_billion_market_cap(self):
        clone = copy.deepcopy(self.model)
        clone["company"]["fenja"]["market_snapshot"]["price_sek"] = 20
        self.assertEqual(fenja_capacity_metrics(clone["company"], clone["calculation"])["additional_draw_msek"], 50)
        clone["company"]["fenja"]["market_snapshot"]["price_sek"] = 5
        self.assertEqual(fenja_capacity_metrics(clone["company"], clone["calculation"])["additional_draw_msek"], 0)

    def test_risk_weights_capacity_only_once(self):
        c, calculation = self.model["company"], self.model["calculation"]
        metrics = fenja_capacity_metrics(c, calculation)
        inputs = dict(calculation)
        inputs["fenja_cap_factor"] = metrics["fenja_cap_factor"]
        months_left = (dt.date(2027, 10, 1) - dt.date(2026, 11, 15)).days / 30.4375
        self.assertEqual([pct_probability(h, months_left, inputs) for h in (3, 6, 12)],
                         [13.1, 29.8, 63.2])
        prior_inputs = dict(calculation)
        self.assertLess(pct_probability(6, months_left, prior_inputs),
                        pct_probability(6, months_left, inputs))
        # No extra interest/maturity fields enter pct_probability.
        for key in ("annual_minimum_drawn_interest_msek", "maturity_date"):
            self.assertNotIn(key, inputs)

    def test_separate_fenja_warning_categories(self):
        alerts = baseline_signals(self.model, dt.date(2026, 11, 15))
        cats = {a["category"] for a in alerts}
        self.assertTrue({"credit_capacity", "debt_maturity", "debt_cost"}.issubset(cats))
        for a in alerts:
            self.assertTrue(a["source"].startswith("https://"))

if __name__ == "__main__":
    unittest.main()
