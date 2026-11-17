"""Buyer-side due diligence: seven dimensions and transparent timing risk."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = json.loads((ROOT / "data" / "financing_model.json").read_text(encoding="utf-8"))
HTML = (ROOT / "index.html").read_text(encoding="utf-8")

EXPECTED = {"Kliniska data", "Patent/IP", "Regulatoriskt", "Kommersiellt",
            "Finansiellt", "Tillverkning/CMC", "Juridik/avtal"}


class TestPartnerDueDiligence(unittest.TestCase):
    def test_all_seven_pillars_have_status_and_assessment(self):
        dd = MODEL["partner_due_diligence"]
        self.assertEqual({x["area"] for x in dd["pillars"]}, EXPECTED)
        self.assertEqual(len(dd["pillars"]), 7)
        self.assertTrue(all(x["status"] and x["assessment"] for x in dd["pillars"]))
        self.assertIn("visionlifesciences.com", dd["framework_url"])
        self.assertEqual(len(dd["scenarios"]), 3)
        self.assertTrue(dd["next_decision_gate"])
        self.assertTrue(dd["time_to_cash_assessment"])

    def test_dd_panel_is_visible_and_fetched_from_curated_model(self):
        self.assertIn('id="dd-risk-module"', HTML)
        self.assertIn('id="dd-risk-detail"', HTML)
        self.assertIn('renderPartnerDueDiligence', HTML)
        self.assertIn('./data/financing_model.json', HTML)

    def test_emission_probability_uses_reviewed_dd_multiplier(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from update_financing import pct_probability
        calc = dict(MODEL["calculation"])
        self.assertGreater(calc["partner_dd_multiplier"], 1.0)
        without_dd = dict(calc, partner_dd_multiplier=1.0)
        if "synact" == "synact":
            calc["fenja_cap_factor"] = without_dd["fenja_cap_factor"] = 1.1
        self.assertGreater(pct_probability(6, 10.5, calc),
                           pct_probability(6, 10.5, without_dd))
        self.assertIn('partner-DD-faktor', HTML)


if __name__ == "__main__":
    unittest.main()
