"""Regression tests for synchronized, time-stamped SYNACT stock quote."""
import datetime as dt
import json
import pathlib
import sys
import unittest
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from update_stock_quote import validate_chart, STOCKHOLM, SYMBOL

class SynActQuoteTests(unittest.TestCase):
    def test_valid_quote_has_exchange_timestamp(self):
        now = int(dt.datetime.now(dt.timezone.utc).timestamp())
        item = {"chart": {"result": [{"meta": {
            "symbol": SYMBOL, "currency": "SEK",
            "regularMarketPrice": 14.40, "regularMarketTime": now
        }}]}}
        got = validate_chart(item)
        self.assertEqual(got["price"], 14.40)
        self.assertIn("quote_time", got)
        self.assertIn("fetched_at", got)

    def test_reject_wrong_symbol_currency_and_invalid_price(self):
        now = int(dt.datetime.now(dt.timezone.utc).timestamp())
        for field, value in (("symbol", "AAPL"), ("currency", "USD"),
                             ("regularMarketPrice", 0), ("regularMarketPrice", -1)):
            with self.subTest(field=field, value=value):
                meta = {"symbol": SYMBOL, "currency": "SEK",
                        "regularMarketPrice": 13.22, "regularMarketTime": now}
                meta[field] = value
                with self.assertRaises(ValueError):
                    validate_chart({"chart": {"result": [{"meta": meta}]}})

    def test_reject_stale_quote_and_future_timestamp(self):
        now = int(dt.datetime.now(dt.timezone.utc).timestamp())
        for seconds in (now - 11 * 86400, now + 3600):
            with self.assertRaises(ValueError):
                validate_chart({"chart":{"result":[{"meta":{
                    "symbol": SYMBOL, "currency":"SEK", "regularMarketPrice":14.40,
                    "regularMarketTime":seconds}}]}})

    def test_stock_quote_remains_independent_of_removed_credit_slider(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="synact-shared-price"', html)
        self.assertIn("fetch('./data/stock_quote.json", html)
        self.assertIn("updateStockQuote(price,quote.quote_time", html)
        self.assertNotIn('id="fenja-scenario-price"', html)
        self.assertNotIn('id="fenja-resync-quote"', html)

    def test_quote_loading_never_flashes_undated_fallback_or_goes_backwards(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for marker in (
            'id="synact-shared-price">—',
            "if(stamp<lastQuoteTimestamp)return;",
            "localStorage.setItem(cacheKey,JSON.stringify(quote))",
        ):
            self.assertIn(marker, html)
        self.assertNotIn("updateStockQuote(referPrice,quoteStamp,'historisk referenskurs');", html)

    def test_latest_quote_and_loan_math(self):
        quote = json.loads((ROOT / "data" / "stock_quote.json").read_text(encoding="utf-8"))
        model = json.loads((ROOT / "data" / "financing_model.json").read_text(encoding="utf-8"))
        loan = model["company"]["fenja"]
        price = quote["price"]
        self.assertGreater(price, 0)
        market_cap = price * loan["market_snapshot"]["shares_outstanding"] / 1e6
        available = max(0, min(loan["remaining_nominal_msek"],
                               market_cap * loan["market_cap_limit_fraction"] -
                               loan["already_drawn_gross_msek"]))
        self.assertGreaterEqual(available, 0)
        self.assertLessEqual(available, 50)

if __name__ == "__main__":
    unittest.main()
