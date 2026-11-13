#!/usr/bin/env python3
"""Weekly SynAct equity-offering risk update (standard-library only).

The probability curve is an explicitly subjective sensitivity model, not a
statistically estimated frequency. Cash and guidance stay at their last
source-checked figures until reviewed. RSS is discovery, not verification.
"""
from __future__ import annotations

import datetime as dt
import email.utils
import html
import json
import math
import pathlib
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from zoneinfo import ZoneInfo
from risk_signals import combined_signals

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "data" / "financing_model.json"
STATE_PATH = ROOT / "data" / "financing.json"
USER_AGENT = "Mozilla/5.0 (compatible; SynActFinancingMonitor/1.0)"
TIMEZONE = ZoneInfo("Europe/Stockholm")
_FINANCE_RX = re.compile(
    r"f[oö]retr[aä]desemission|riktad(?:e)? (?:ny)?emission|nyemission|"
    r"rights? issue|directed issue|private placement|issue of new shares|"
    r"new share issue|equity financing|capital raise|"
    r"financing facility|funding facility|convertible|"
    r"finansieringsfacilitet|konvertibel|cash runway|"
    r"del[aå]rsrapport|interim report|year.end report|"
    r"cash position|finansiering|likviditet",
    re.I,
)
_ISSUE_RX = re.compile(
    r"f[oö]retr[aä]desemission|riktad(?:e)? (?:ny)?emission|nyemission|"
    r"rights? issue|directed issue|private placement|"
    r"issue of new shares|new share issue|equity offering", re.I
)
_ISSUE_NEGATION = re.compile(r"no (?:planned |new )?(?:rights? issue|share issue)|ingen (?:planerad )?emission", re.I)
_REPORT_RX = re.compile(r"q[1-4] report|interim report|quarterly report|del[aå]rsrapport|year.end report|bokslut", re.I)
_PARTNER_RX = re.compile(r"partnership|licens(?:ing|avtal)|partneravtal|upfront|milestone payment", re.I)
_STUDY_RX = re.compile(r"phase 3|phase iii|fas 3|fas iii|fda|clinical data|studieresultat", re.I)

def load_json(path: pathlib.Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def pct_probability(months: int, months_left: float, inputs: dict, scale: float = 1.0) -> int:
    # The full formula is disclosed next to the graphic on the website.
    proximity = max(.85, min(2.60, 1.0 + 0.10 * (months + 9.0 - months_left)))
    monthly = (inputs["baseline_monthly_hazard"]
               * inputs["clinical_phase3_multiplier"]
               * inputs["credit_dependency_multiplier"]
               * proximity * scale)
    return round(100.0 * (1.0 - math.exp(-months * monthly)), 1)

def fetch_url(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/rss+xml,application/xml,*/*"})
    with urllib.request.urlopen(req, timeout=22) as response:
        return response.read(2_000_000)

def parse_rss(query: str, label: str, limit: int = 35) -> list[dict]:
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": query, "hl": "sv", "gl": "SE", "ceid": "SE:sv"})
    root = ET.fromstring(fetch_url(url))
    found: list[dict] = []
    for item in root.findall("./channel/item")[:limit]:
        title = (item.findtext("title") or "").strip()
        title = html.unescape(title)
        source = (item.findtext("source") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        try:
            published = email.utils.parsedate_to_datetime(pub).astimezone(dt.timezone.utc).date().isoformat()
        except (TypeError, ValueError, IndexError, OverflowError):
            published = ""
        if not title or not link.startswith("https://"):
            continue
        found.append({"title": title, "date": published, "source": source,
                      "url": link, "category": label,
                      "official": label == "bolaget" and
                      ("synactpharma" in source.casefold().replace(" ", "")
                       or "synact pharma" in source.casefold())})
    return found

class PressLinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.href = None
        self.text_parts: list[str] = []
        self.results: list[dict] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.text_parts = []
    def handle_data(self, data: str) -> None:
        if self.href:
            self.text_parts.append(data)
    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self.href:
            return
        title = " ".join(" ".join(self.text_parts).split())
        url = urllib.parse.urljoin("https://www.synactpharma.com", self.href)
        self.href = None
        self.text_parts = []
        if not 20 <= len(title) <= 230 or not url.startswith("https://www.synactpharma.com/"):
            return
        if re.search(r"news-media/news-and-press-releases", url) or re.search(r"investors/financial-reports", url):
            return
        if re.search(r"SynAct|resomelagon|AP1189|finance|financ|study|report|patent|partner|phase", title, re.I):
            self.results.append({"title": title, "date": "", "source": "SynAct Pharma",
                                 "url": url, "category": "officiell lista", "official": True})

def load_official_press_links() -> list[dict]:
    page = "https://www.synactpharma.com/en/news-media/news-and-press-releases/"
    parser = PressLinkParser()
    parser.feed(fetch_url(page).decode("utf-8", "replace"))
    # The company index may not expose dates in HTML; do not infer publication dates.
    return parser.results[:35]

def classification(title: str) -> str:
    if _ISSUE_RX.search(title) and not _ISSUE_NEGATION.search(title):
        return "emission"
    if _REPORT_RX.search(title):
        return "rapport"
    if _FINANCE_RX.search(title):
        return "finansiering"
    if _PARTNER_RX.search(title):
        return "partneravtal"
    if _STUDY_RX.search(title):
        return "kliniskt / regulatoriskt"
    return "övrigt"

def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9åäö]+", "", title.casefold())[:100]

def main() -> None:
    model = load_json(MODEL_PATH)
    old = load_json(STATE_PATH)
    company, calc = model["company"], model["calculation"]
    today = dt.datetime.now(TIMEZONE)
    current_date = today.date()
    report_date = dt.date.fromisoformat(company["report_date"])
    runway_proxy = dt.date.fromisoformat(company["cash_runway_proxy"])
    months_left = (runway_proxy - current_date).days / 30.4375
    bounds = calc["uncertainty_band_monthly_hazard_multiplier"]
    risks = {}
    for n in (3, 6, 12):
        risks["months_" + str(n)] = {
            "percent": pct_probability(n, months_left, calc),
            "low": pct_probability(n, months_left, calc, bounds[0]),
            "high": pct_probability(n, months_left, calc, bounds[1]),
        }
    sources_ok, source_failures, all_items = [], [], []
    feeds = [
        ("bolaget", 'site:synactpharma.com ("SynAct Pharma" OR "resomelagon") when:75d'),
        ("omvärld", '"SynAct Pharma" (emission OR finansiering OR shares OR financing OR partnership OR cash) when:75d'),
        ("jämförelsebolag", '("BioInvent" OR "Cereno Scientific" OR "Alligator Bioscience" OR "Immunovia" OR "Isofol Medical" OR "Active Biotech") ("rights issue" OR "share issue" OR "företrädesemission") when:40d'),
    ]
    # Daily high-signal scan, separate from the weekly probability refresh.
    feeds.extend([
        ("varningssignaler", '"SynAct Pharma" (handelsstopp OR "trading halt" OR suspension OR insiderinformation OR "liquidity" OR "cash shortage" OR "deferred payments" OR "going concern" OR emission OR financing) when:35d'),
        ("börsmeddelanden", 'site:view.news.eu.nasdaq.com "SynAct Pharma" (suspension OR trading OR halt) when:35d'),
    ])
    if "--offline" not in sys.argv:
        for label, query in feeds:
            try:
                all_items.extend(parse_rss(query, label))
                sources_ok.append(label + ": Google News RSS")
            except Exception as err:
                source_failures.append(label + ": " + str(err)[:140])
        try:
            all_items.extend(load_official_press_links())
            sources_ok.append("officiell presslista")
        except Exception as err:
            source_failures.append("officiell presslista: " + str(err)[:140])
    else:
        sources_ok.append("offline-test; inga externa källor kontrollerade")
    seen: set[str] = set()
    unique: list[dict] = []
    for item in sorted(all_items, key=lambda x: x.get("date", ""), reverse=True):
        if item["category"] != "jämförelsebolag" and not re.search(r"synact|resomelagon|ap1189", item["title"], re.I):
            continue
        key = normalize_title(item["title"])
        if not key or key in seen:
            continue
        seen.add(key)
        item["signal"] = classification(item["title"])
        unique.append(item)
    cutoff = dt.date.fromisoformat(model["curated_at"])
    # Dated official announcements only: no inferred dates for press-index entries.
    new_company = [i for i in unique if i["official"] and i.get("date") and
                   i["date"] > cutoff.isoformat() and i["category"] != "jämförelsebolag"]
    issues = [i for i in new_company if i["signal"] == "emission"]
    review = [i for i in new_company if i["signal"] in
              ("emission", "finansiering", "rapport", "partneravtal", "kliniskt / regulatoriskt")]
    new_peers = [i for i in unique if i["category"] == "jämförelsebolag" and
                 i.get("date", "") > cutoff.isoformat() and i["signal"] == "emission"]
    latest_info = [
      "Senast verifierad Q3 2026: 42,4 miljoner kr i kassa 30 september, kvartalets operativa kassaflöde −18,7 miljoner kr.",
      "Fenja: upp till 100 miljoner kr, 50 miljoner kr initialt dragna. Eventuellt nytt uttag under Q4 2026 är villkorat av bland annat börsvärde.",
      "Bolagets prognos från 3 november 2026 är finansiering in i Q4 2027. Närhet till det riktmärket räknas om varje vecka.",
    ]
    if issues:
        latest_info.insert(0, "OBS: Officiell rubrik om ny aktieemission upptäckt; se källan och kontrollera villkoren.")
    elif review:
        latest_info.append("Nya bolagsbesked har upptäckts och visas separat för granskning. Deras ekonomiska effekter har inte gissats från rubriker.")
    if source_failures:
        latest_info.append("En eller flera källor kunde inte kontrolleras. Riskprocenten bygger då på föregående verifierade bolagsuppgifter plus tidens gång.")
    if issues:
        coverage = "emissionsbesked_upptäckt"
    elif not sources_ok or (len(sources_ok) == 1 and "--offline" in sys.argv):
        coverage = "ingen_nätkontroll"
    elif source_failures:
        coverage = "delvis_kontrollerad"
    elif review:
        coverage = "nytt_besked_kräver_granskning"
    else:
        coverage = "källor_kontrollerade_inga_nya_finansfakta"
    payload = {
       "updated_at": today.isoformat(timespec="seconds"),
       "based_on_report": company["report_date"],
       "automated_checked": "--offline" not in sys.argv and bool(sources_ok),
       "coverage_status": coverage,
       "checked_sources": sources_ok,
       "failed_sources": source_failures,
       "days_since_report": (current_date - report_date).days,
       "months_to_company_runway_proxy": round(months_left, 1),
       "methodology_version": model["version"],
       "risk": risks,
       "latest_information": latest_info,
       "latest_items": unique[:14],
       "review_needed": (review + new_peers)[:12],
       "emission_detected": issues[:4],
       "review_warning": ("Detta är en regelstyrd bedömningsmodell, inte ett objektivt förutsagt utfall. "
                          "Tidsfaktorn uppdateras automatiskt. RSS och officiell presslista bevakas "
                          "men rubriker kan varken ersätta rapportläsning eller garantera att alla nyheter "
                          "hittas. Nya villkor, kassavärden och eventuella emissioner måste verifieras "
                          "mot fullständiga originalbesked innan prognosen omkalibreras."),
       "sources": {
          "company_report": company["q3_url"],
          "facility": company["fenja"]["url"],
          "official_feed": model["monitoring"]["official_press"],
       },
    }
    # Verified structural warning signals + unverified news headlines.
    issuer = "synact"
    current_alerts = combined_signals(model, unique, issuer, current_date)
    # Retain recent previously surfaced headlines if an individual RSS endpoint
    # temporarily fails, without describing old headlines as fresh live states.
    existing = {a.get("id"): a for a in current_alerts}
    for earlier in old.get("alerts", []):
        if earlier.get("id", "").startswith("base:") or earlier.get("id") in existing:
            continue
        try:
            age = (current_date - dt.date.fromisoformat(earlier.get("date", "")[:10])).days
        except ValueError:
            continue
        if 0 <= age <= 28:
            existing[earlier["id"]] = earlier
    payload["alerts"] = list(existing.values())[:18]
    payload["alerts_checked_at"] = today.isoformat(timespec="seconds")
    payload["alerts_source_status"] = ("ofullständig nätkontroll" if source_failures
                                     else "inga externa källor kontrollerade" if "--offline" in sys.argv
                                     else "flöden kontrollerade, inte heltäckande")
    if old.get("price_confirmation"):
        payload["price_confirmation"] = old["price_confirmation"]
    if "--signals-only" in sys.argv:
        # The daily job updates warnings, NOT the probability or finance facts.
        daily = dict(old)
        for name in ("alerts", "alerts_checked_at", "alerts_source_status",
                     "checked_sources", "failed_sources", "latest_items"):
            if name in payload:
                daily[name] = payload[name]
        daily["review_needed"] = payload["review_needed"]
        if payload.get("emission_detected"):
            daily["emission_detected"] = payload["emission_detected"]
        STATE_PATH.write_text(json.dumps(daily, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        print("Daily financing warnings:", len(daily["alerts"]), "coverage", daily["alerts_source_status"])
        return
    if "--dry-run" in sys.argv or "--offline" in sys.argv:
        print(json.dumps({"updated_at":payload["updated_at"],
            "coverage_status":coverage,"risk":risks,
            "new_company_releases":len(new_company), "source_failures":source_failures},
            ensure_ascii=False, indent=2))
        return
    STATE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated financing risk:", coverage, "6m", risks["months_6"]["percent"],
          "12m", risks["months_12"]["percent"], "feeds", len(sources_ok),
          "issues", len(issues), "review", len(review))

if __name__ == "__main__":
    main()
