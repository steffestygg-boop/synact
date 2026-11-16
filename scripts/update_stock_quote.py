#!/usr/bin/env python3
"""Refresh the same sourced SYNACT quote used by the stock tile and Fenja slider.

Yahoo's chart endpoint is unofficial and can fail. Never silently publish a
fetched-at timestamp as though it were the timestamp of the exchange quote.
This task intentionally does not rewrite the equity-risk probability model:
that model's dated snapshot is separately audited.
"""
from __future__ import annotations
import datetime as dt
import json
import math
import pathlib
import sys
import urllib.request
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "stock_quote.json"
SYMBOL = "SYNACT.ST"
URLS = [
    "https://query1.finance.yahoo.com/v8/finance/chart/SYNACT.ST?range=5d&interval=5m",
    "https://query2.finance.yahoo.com/v8/finance/chart/SYNACT.ST?range=5d&interval=1d",
]
STOCKHOLM = ZoneInfo("Europe/Stockholm")

def validate_chart(payload: dict) -> dict:
    chart = payload.get("chart", {})
    result = chart.get("result")
    if not isinstance(result, list) or not result:
        raise ValueError("Missing chart result")
    node = result[0]
    meta = node.get("meta") or {}
    if meta.get("currency") != "SEK":
        raise ValueError("Expected SEK, got " + str(meta.get("currency")))
    symbol = str(meta.get("symbol", "")).upper()
    if symbol and symbol != SYMBOL:
        raise ValueError("Wrong symbol " + symbol)
    price = meta.get("regularMarketPrice")
    quote_time = meta.get("regularMarketTime")
    if not isinstance(price, (int, float)) or not math.isfinite(price) or not 0 < price < 10000:
        raise ValueError("No reliable market price")
    if not isinstance(quote_time, (float, int)) or quote_time <= 0:
        # Last valid chart bar is a fallback only when regularMarketTime missing.
        timestamps = node.get("timestamp") or []
        if not timestamps:
            raise ValueError("No source timestamp")
        quote_time = timestamps[-1]
    quoted = dt.datetime.fromtimestamp(quote_time, STOCKHOLM)
    now = dt.datetime.now(STOCKHOLM)
    if quoted > now + dt.timedelta(minutes=10):
        raise ValueError("Source quote time is in the future")
    if quoted < now - dt.timedelta(days=10):
        raise ValueError("Quote too old to publish")
    return {
        "symbol": SYMBOL,
        "currency": "SEK",
        "price": round(float(price), 4),
        "quote_time": quoted.isoformat(timespec="seconds"),
        "fetched_at": now.isoformat(timespec="seconds"),
        "source": "Yahoo Finance chart / Nasdaq Stockholm",
        "source_url": "https://finance.yahoo.com/quote/SYNACT.ST/",
        "delayed": True,
        "source_note": "Extern, potentiellt fördröjd marknadskurs. Tidpunkten är kursens källtidsstämpel; kontrollera alltid tidsstämpeln."
    }

def download():
    issues = []
    for url in URLS:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; SynactQuoteSync/1.0)",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=18) as res:
                obj = json.loads(res.read(600_000))
            return validate_chart(obj)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            issues.append(str(exc)[:130])
    raise RuntimeError("All market quote endpoints failed: " + "; ".join(issues))

def main():
    if "--check-only" in sys.argv:
        fixture = {
            "chart":{"result":[{
                "meta":{"currency":"SEK","symbol":SYMBOL,
                        "regularMarketPrice":13.22,
                        "regularMarketTime":int(dt.datetime.now(dt.timezone.utc).timestamp())}
            }]}
        }
        valid = validate_chart(fixture)
        assert valid["price"] == 13.22
        assert valid["symbol"] == SYMBOL
        print("Quote validation passed")
        return
    quote = download()
    previous = {}
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    # Don't create commits every 20 minutes when the market quote hasn't moved:
    # mark the source quote's own timestamp, not the scheduled job's runtime.
    if (previous.get("price") == quote["price"] and
            previous.get("quote_time") == quote["quote_time"] and
            previous.get("source") == quote["source"]):
        print("No new quote, keeping previously published timestamp")
        return
    OUTPUT.write_text(json.dumps(quote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated", quote["symbol"], quote["price"], quote["quote_time"])

if __name__ == "__main__":
    main()
