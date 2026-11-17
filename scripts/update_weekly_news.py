#!/usr/bin/env python3
"""Sunday-evening source-based weekly digest for Isofol, SynAct and Cereno.

Only extract facts from dated, traceable titles and reviewed local site data.
A feed headline is never presented as a verified full-article summary.
The previous week is retained permanently; comparison figures are snapshots.
No third-party Python packages or API credentials are required.
"""
from __future__ import annotations

import argparse
import os
import datetime as dt
import email.utils
import hashlib
import json
import pathlib
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "weekly_news.json"
ISSUER = ROOT.name.lower()
LOCAL_TZ = ZoneInfo("Europe/Stockholm")

CONFIG = {
    "synact": {
        "name": "SynAct Pharma",
        "queries": ['"SynAct Pharma" OR resomelagon when:21d',
                    '"SynAct Pharma" (patent OR studie OR emission OR avtal OR finansiering) when:21d'],
        "aliases": ("synact", "resomelagon", "ap1189"),
    },
    "isofol": {
        "name": "Isofol Medical",
        "queries": ['"Isofol Medical" OR arfolitixorin when:21d',
                    '"Isofol Medical" (fas OR TO2 OR studie OR finansiering OR topline) when:21d'],
        "aliases": ("isofol", "arfolitixorin"),
    },
    "cereno": {
        "name": "Cereno Scientific",
        "queries": ['"Cereno Scientific" OR "Cereno CS1" OR "Cereno CS014" when:21d',
                    '"Cereno Scientific" (emission OR handelsstopp OR EPIMODE OR finansiering) when:21d'],
        "aliases": ("cereno", "epimode", "cs014", "cs585"),
    },
}
CATEGORIES = [
    ("Handelsstopp", r"handelsstopp|handeln återuppt|trading halt|trading susp"),
    ("Emission och finansiering", r"emission|units?|teckningsoption|to2\b|to1\b|finansier|kredit|låne|loan|fenja|likviditet|capital raise|rights issue"),
    ("Studie och resultat", r"fas [123ivb]+|phase [123ivb]+|studie|clinical|trial|patient|rekryter|doser|top.?line|resov|respi|effekt|endpoint"),
    ("Regulatoriskt och patent", r"fda|ema|regulator|godkän|patent|allowance|myndighet|ind\b"),
    ("Partner och avtal", r"partner|licens|hipolabor|samarbete|deal|commercial"),
    ("Rapport och ekonomi", r"delårsrapport|kvartal|q[1234]\b|financial results|interim report|rörelseresultat|förlust"),
    ("Analys och marknad", r"analys|riktkurs|kursras|börsvärde|redeye|edison|abg|research|aktiens|aktien"),
]
SWEDISH_MONTHS = {
    "jan": 1, "januari": 1, "feb": 2, "februari": 2, "mar": 3, "mars": 3,
    "apr": 4, "april": 4, "maj": 5, "jun": 6, "juni": 6,
    "jul": 7, "juli": 7, "aug": 8, "augusti": 8, "sep": 9, "september": 9,
    "okt": 10, "oktober": 10, "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}
IGNORE = {"och", "med", "från", "till", "för", "the", "and", "from", "of", "i", "om", "en", "ett",
          "sina", "sin", "efter", "har", "skall", "ska", "bolaget", "scientific", "pharma", "medical"}
USER_AGENT = "Mozilla/5.0 (compatible; InvestorWeeklyDigest/1.0; source-attributed)"

def read_json(path: pathlib.Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback

def week_ending(day: dt.date) -> dt.date:
    """Return Sunday of last completed/closing ISO week, using Stockholm date."""
    return day if day.weekday() == 6 else day - dt.timedelta(days=day.weekday() + 1)

def bounds(sunday: dt.date):
    start = sunday - dt.timedelta(days=6)
    iso = sunday.isocalendar()
    return start, sunday, f"{iso.year}-W{iso.week:02d}", iso.week

def iso_date(text: str):
    try:
        return dt.date.fromisoformat(str(text)[:10])
    except (ValueError, TypeError):
        return None

def milestone_date(text):
    val = iso_date(text)
    if val:
        return val
    s = str(text).lower()
    match = re.search(r"\b(\d{1,2})\s+([a-zåäö]+)\s+(20\d\d)\b", s)
    if not match:
        return None
    month = SWEDISH_MONTHS.get(match.group(2))
    if not month:
        return None
    try:
        return dt.date(int(match.group(3)), month, int(match.group(1)))
    except ValueError:
        return None

def normalize(text):
    s = re.sub(r"[\s–—-]+(?:biostock|börsvärlden|affärsvärlden|di|synact pharma|isofol medical|cereno scientific)$", "", str(text).strip(), flags=re.I)
    return re.sub(r"\s+", " ", s).strip(" –-")

def word_tokens(title):
    x = re.findall(r"[a-zåäö0-9]{3,}", title.casefold())
    return {t for t in x if t not in IGNORE}

def category(title):
    for label, pattern in CATEGORIES:
        if re.search(pattern, title, re.I):
            return label
    return "Övrigt"

def event_priority(event):
    score = {
        "Handelsstopp": 115, "Emission och finansiering": 106,
        "Studie och resultat": 92, "Regulatoriskt och patent": 84,
        "Partner och avtal": 81, "Rapport och ekonomi": 73,
        "Analys och marknad": 45, "Övrigt": 40,
    }.get(event["category"], 30)
    if event.get("verified"):
        score += 12
    if event.get("origin") == "milstolpe":
        score += 6
    # Resumed trading is important, but an issuer's new funding announcement
    # normally merits greater prominence in the short editorial lead.
    title = event.get("title", "").casefold()
    if "återupptas" in title or "handelsstopp hävs" in title:
        score -= 33
    if event["category"] == "Emission och finansiering" and (
            "400 mkr" in title or "miljoner" in title or "företrädesemission" in title):
        score += 22
    return score

def similar(a, b):
    if a.get("category") != b.get("category"):
        return False
    aa = iso_date(a.get("date")), iso_date(b.get("date"))
    if not all(aa) or abs((aa[0] - aa[1]).days) > 2:
        return False
    ta, tb = word_tokens(a["title"]), word_tokens(b["title"])
    if not ta or not tb:
        return False
    return len(ta & tb) / min(len(ta), len(tb)) >= .73

def event(title, date, url, source, verified=False, origin="rubrik"):
    title = normalize(title)
    if not title or not url or not str(url).startswith("https://") or not iso_date(date):
        return None
    kind = category(title)
    return {
        "date": str(date)[:10], "title": title[:220],
        "category": kind, "summary": "",
        "source": str(source or "Källa okänd")[:100], "url": url,
        "verified": bool(verified), "origin": origin,
        "source_note": "Manuellt källgranskad post" if verified else
                       "Automatiskt insamlad rubrik – originalartikeln har inte fullständigt faktagranskats",
    }

def rss_events(queries, first, last):
    found, errors = [], []
    for query in queries:
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
            "q": query, "hl": "sv", "gl": "SE", "ceid": "SE:sv"})
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=22) as reply:
                root = ET.fromstring(reply.read(2_000_000))
            for node in root.findall("./channel/item"):
                title = (node.findtext("title") or "").strip()
                link = (node.findtext("link") or "").strip()
                pub = (node.findtext("pubDate") or "").strip()
                try:
                    date = email.utils.parsedate_to_datetime(pub).astimezone(LOCAL_TZ).date()
                except (TypeError, ValueError, IndexError):
                    continue
                if not first <= date <= last:
                    continue
                source = (node.findtext("source") or "Google News").strip()
                e = event(title, date.isoformat(), link, source)
                if e:
                    found.append(e)
        except (TimeoutError, OSError, ET.ParseError, ValueError) as exc:
            errors.append("RSS-sökning kunde inte läsas: " + str(exc)[:110])
    return found, errors

def issuer_matches(item, conf):
    if item.get("verified") or item.get("origin") == "milstolpe":
        return True
    full = (str(item.get("title", "")) + " " + str(item.get("source", ""))).lower()
    return any(alias in full for alias in conf["aliases"])

def load_milestones():
    data = read_json(DATA / "milestones.json", {})
    if isinstance(data, dict) and isinstance(data.get("milestones"), list):
        return data["milestones"]
    try:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        match = re.search(r"const milestones\s*=\s*(\[[\s\S]*?\]);", html)
        return json.loads(match.group(1)) if match else []
    except (OSError, ValueError):
        return []

def milestones_snapshot():
    snapshot = {}
    for m in load_milestones():
        title = str(m.get("title", ""))
        if not title:
            continue
        # Same milestone title remains a stable identity across quarter and date shifts.
        snapshot[title] = {
            "date": str(m.get("date", "")),
            "status": str(m.get("status", "")),
            "period": str(m.get("col", m.get("era", ""))),
            "url": str(m.get("url", "")),
        }
    return snapshot

def collect_events(start, end, config, finance):
    events, errors = rss_events(config["queries"], start, end)
    local_news = read_json(DATA / "news.json", {})
    candidates = list(local_news.get("items", []))
    for item in finance.get("latest_items", []):
        if item.get("category") == "jämförelsebolag":
            continue
        candidates.append(item)
    for item in candidates:
        day = iso_date(item.get("date"))
        if not day or not start <= day <= end:
            continue
        e = event(item.get("title"), day.isoformat(), item.get("url"),
                  item.get("source", "Nyhetskälla"), item.get("verified", False),
                  "källgranskad" if item.get("verified", False) else "rubrik")
        if e:
            events.append(e)
    # Completed dated milestones are also traceable original-source events.
    for m in load_milestones():
        if m.get("status") != "done":
            continue
        day = milestone_date(m.get("date", ""))
        if not day or not start <= day <= end:
            continue
        e = event(m.get("title", ""), day.isoformat(), m.get("url", ""),
                  "Dokumenterad milstolpe", True, "milstolpe")
        if e:
            events.append(e)
    # Cereno's dated financial warning panel includes reviewed issuer disclosures.
    if ISSUER == "cereno":
        for a in finance.get("alerts", []):
            day = iso_date(a.get("date"))
            if not day or not start <= day <= end:
                continue
            verified = ("Verifierat" in str(a.get("status", "")) or
                        "Källjämförelse" in str(a.get("status", "")))
            if not verified:
                continue
            e = event(a.get("title"), day.isoformat(), a.get("source", ""),
                      "Bolagsbesked / finansieringsanalys", True, "källgranskad")
            if e:
                e["summary"] = str(a.get("detail", ""))[:330] or e["summary"]
                events.append(e)
    events = [e for e in events if issuer_matches(e, config)]
    events.sort(key=lambda e: (int(e.get("verified", False)), event_priority(e), e["date"]), reverse=True)
    deduped = []
    seen_url = set()
    for e in events:
        if e["url"] in seen_url:
            continue
        if any(similar(e, prev) for prev in deduped):
            continue
        seen_url.add(e["url"])
        deduped.append(e)
    deduped.sort(key=lambda e: (e["date"], event_priority(e)), reverse=True)
    return deduped, 0, errors

def snapshot_financing(model, finance):
    risks = finance.get("risk") or {}
    if ISSUER == "cereno":
        relevant_model = {"issue": model.get("issue"), "fenja": model.get("fenja"),
                          "scenario": model.get("scenario")}
    else:
        relevant_model = {"calculation": model.get("calculation"), "company": model.get("company")}
    signature = hashlib.sha256(json.dumps(relevant_model, ensure_ascii=False,
                                            sort_keys=True).encode()).hexdigest()[:16]
    alerts = {}
    for item in finance.get("alerts", []):
        if item.get("id") or item.get("title"):
            alerts[str(item.get("id") or item.get("title"))] = {
                "title": item.get("title", ""), "level": item.get("level", ""),
                "source": item.get("source", ""),
            }
    return {
        "risk_3": risks.get("months_3", {}).get("percent"),
        "risk_6": risks.get("months_6", {}).get("percent"),
        "risk_12": risks.get("months_12", {}).get("percent"),
        "risk_as_of": str(finance.get("updated_at", "")),
        "model_version": str(model.get("version", "")),
        "model_fingerprint": signature,
        "emission_status": str(finance.get("emission_status", "")),
        "alerts": alerts,
        "milestones": milestones_snapshot(),
    }

def snapshot_changes(now, prev):
    if not prev:
        return []
    changes = []
    risks_changed = any(
        isinstance(now.get("risk_" + k), (int, float)) and
        isinstance(prev.get("risk_" + k), (int, float)) and
        abs(now["risk_" + k] - prev["risk_" + k]) >= .05 for k in ("3", "6", "12"))
    if risks_changed:
        details = []
        for k in ("3", "6", "12"):
            x, y = now.get("risk_" + k), prev.get("risk_" + k)
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                continue
            delta = round(x-y, 1)
            details.append(f"{k} mån {x:.1f} % ({delta:+.1f} procentenheter)")
        if details:
            changes.append({"title": "Emissionsbarometern uppdaterad",
              "detail": "Jämfört med förra veckoutgåvan: " + "; ".join(details).replace(".", ",") + ".",
              "kind": "finansiering"})
    if now.get("model_fingerprint") != prev.get("model_fingerprint"):
        title = "Konkurs- och finansieringsantaganden justerade" if ISSUER == "cereno" else "Emissionsbarometerns grundantaganden reviderade"
        changes.append({"title": title,
           "detail": "Källdata eller modellantaganden har ändrats sedan förra veckoutgåvan. Läs modellens metodavsnitt för vad uppdateringen innebär; ändringen ska inte automatiskt tolkas som ett nytt bolagsbesked.",
           "kind": "modell"})
    if now.get("emission_status") != prev.get("emission_status") and now.get("emission_status"):
        changes.append({"title": "Emissionsstatus förändrad",
          "detail": "Nuvarande status: " + now["emission_status"] + ". Kontrollera bolagets originalbesked för beslut, villkor och utfall.",
          "kind": "finansiering"})
    old_alerts, new_alerts = prev.get("alerts", {}), now.get("alerts", {})
    for k in new_alerts.keys() - old_alerts.keys():
        a = new_alerts[k]
        changes.append({"title": "Ny finansieringsvarning: " + a.get("title", ""),
          "detail": "Prioritet: " + a.get("level", "bevakning") + ". Läs varningsrutan och dess källa innan slutsatser dras.",
          "kind": "varning", "url": a.get("source", "")})
    old_ms, new_ms = prev.get("milestones", {}), now.get("milestones", {})
    for title in new_ms.keys() & old_ms.keys():
        if new_ms[title] == old_ms[title]:
            continue
        cur, old = new_ms[title], old_ms[title]
        if cur.get("date") == old.get("date") and cur.get("status") == old.get("status") and cur.get("period") == old.get("period"):
            continue
        changes.append({"title": "Milstolpe uppdaterad: " + title,
          "detail": "Tidigare: " + old.get("date", "?") + ". Nu: " + cur.get("date", "?") + ". " +
                    ("Ändrad status: " + cur.get("status", "") + "." if cur.get("status") != old.get("status") else "Kvartalsplaceringen eller tidsbedömningen har justerats."),
          "kind": "milstolpe", "url": cur.get("url", "")})
    for title in new_ms.keys() - old_ms.keys():
        cur = new_ms[title]
        changes.append({"title": "Milstolpe tillagd: " + title,
           "detail": "Placerad: " + cur.get("date", "datum saknas") + " (" +
                     ("genomförd" if cur.get("status") == "done" else "planerad") + ").",
           "kind": "milstolpe", "url": cur.get("url", "")})
    return changes[:16]

def intro_text(items, updates):
    if not items and not updates:
        return "Inga daterade nya händelser hittades i de källflöden som kunde läsas. Det betyder inte att ingenting har hänt."
    highlights = [item for item in items if item.get("verified")]
    ranked = highlights if highlights else items
    lead = max(ranked, key=event_priority) if ranked else None
    if lead:
        prefix = "Veckans tydligaste källanknutna besked" if lead.get("verified") else "En framträdande nyhetsrubrik"
        summary = f"{prefix}: {lead['title']}."
        if not lead.get("verified"):
            summary += " Innehållet i artikeln behöver kontrolleras mot originalkällan."
    else:
        summary = "Veckans uppdateringar gäller främst analys och bevakade nyckeltal."
    if updates:
        summary += " Dessutom finns " + str(len(updates)) + " noterade förändringar i sidans finansieringsanalys eller milstolpar."
    return summary

def visible_finance_snapshot(current, sunday):
    """Do not project a new risk model backward into an older archived week."""
    dated = iso_date(current.get("risk_as_of"))
    too_new = bool(dated and dated > sunday + dt.timedelta(days=2))
    return {
        "risk_3": None if too_new else current.get("risk_3"),
        "risk_6": None if too_new else current.get("risk_6"),
        "risk_12": None if too_new else current.get("risk_12"),
        "risk_as_of": None if too_new else current.get("risk_as_of"),
        "emission_status": "" if too_new else current.get("emission_status"),
        "explanation": (
            "Ingen verifierad historisk riskmodell finns för denna efterhandsrekonstruerade vecka. "
            "Senare modellvärden eller emissionsbesked visas inte bakåt i tiden."
            if too_new else
            "Lägesbild vid sammanställningen, inte ett påstående om att "
            "siffrorna offentliggjordes denna vecka."
        ),
    }, too_new


def enrich_events(events):
    """Attach factual, source-attributed information; omit generic boilerplate."""
    curated = read_json(DATA / "weekly_event_details.json", {}).get("by_title", {})
    curated_new_titles = {v.get("title"): v for v in curated.values() if v.get("title")}
    milestone_map = {m.get("title"): m for m in load_milestones() if m.get("title")}
    result = []
    for raw in events:
        entry = dict(raw)
        original_title = entry.get("title", "")
        info = curated.get(original_title) or curated_new_titles.get(original_title)
        milestone = milestone_map.get(original_title)
        if info:
            entry["title"] = info.get("title", original_title)
            entry["summary"] = info.get("summary", "")
            entry["details"] = info.get("details", "")
            entry["importance"] = info.get("importance", "")
            entry["key_facts"] = list(info.get("key_facts", []))[:9]
            primary = info.get("source_url")
            if primary and primary.startswith("https://"):
                if entry.get("url") and entry["url"] != primary:
                    entry["additional_source_url"] = entry["url"]
                entry["url"] = primary
            entry["editorial_verified"] = True
        elif milestone:
            entry["summary"] = str(milestone.get("body", "")).strip()
            entry["details"] = str(milestone.get("meaning", "")).strip()
            entry["importance"] = ""
            entry["key_facts"] = []
            entry["editorial_verified"] = True
        else:
            entry["summary"] = ""
            entry["details"] = ""
            entry["importance"] = ""
            entry["key_facts"] = []
            entry["editorial_verified"] = False
        result.append(entry)
    # Two separately syndicated headlines about a single issuer announcement
    # should become one well-sourced story, not repetitive cards.
    compact, duplicates = [], set()
    for e in sorted(result, key=lambda x: (
          int(x.get("verified", False)), int(x.get("editorial_verified", False)),
          event_priority(x)), reverse=True):
        key = (e["date"], e.get("url"))
        if key in duplicates:
            continue
        duplicates.add(key)
        compact.append(e)
    compact.sort(key=lambda e: (e["date"], event_priority(e)), reverse=True)
    return compact


def create_edition(sunday, current, existing, headlines, errors, omitted):
    start, end, week_id, week_num = bounds(sunday)
    older_id = (start - dt.timedelta(days=1)).isocalendar()
    previous_key = f"{older_id.year}-W{older_id.week:02d}"
    prev = next((x for x in existing if x.get("id") == previous_key), None)
    prior_snapshot = prev.get("snapshot") if prev else None
    visible, reconstructed = visible_finance_snapshot(current, sunday)
    headlines = enrich_events(headlines)
    updates = [] if reconstructed else snapshot_changes(current, prior_snapshot)
    # Do not use future model values to retroactively describe earlier weeks.
    return {
        "id": week_id, "week": week_num, "year": end.isocalendar().year,
        "start": start.isoformat(), "end": end.isoformat(),
        "generated_at": dt.datetime.now(LOCAL_TZ).isoformat(timespec="seconds"),
        "intro": intro_text(headlines, updates),
        "events": headlines, "updates": updates,
        "omitted_events": omitted,
        "finance_snapshot": visible,
        "snapshot": {} if reconstructed else current,
        "sources_checked": ["lokal bevakningsfil", "nyhetssökningar via Google News RSS",
                            "daterade milstolpar", "finansierings- och riskdata"],
        "source_errors": errors,
        "note": "Automatiskt sammanställda rubriker och källgranskade dataposter; inte fulltextbevakning av all nyhetsrapportering. Endast uttryckligen källgranskade poster markeras verifierade.",
    }

def weekly_stock_change(start, today, previous=None):
    """Last Friday close -> latest available close, using Yahoo daily chart.
    Missing or stale quotes are never represented as fresh changes.
    """
    symbols = {"isofol": "ISOFOL.ST", "synact": "SYNACT.ST", "cereno": "CRNO-B.ST"}
    symbol = symbols[ISSUER]
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + symbol + "?range=1mo&interval=1d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.load(response)["chart"]["result"][0]
        times = data["timestamp"]
        closes = data["indicators"]["quote"][0]["close"]
        observations = [(dt.datetime.fromtimestamp(t, LOCAL_TZ).date(), float(c)) for t,c in zip(times, closes) if c is not None]
        observations.sort()
        baseline = next(((d,p) for d,p in reversed(observations) if d < start), None)
        latest = next(((d,p) for d,p in reversed(observations) if start <= d <= today), None)
        if not baseline or not latest:
            raise ValueError("No comparable daily closes for this week")
        d0,p0 = baseline
        d1,p1 = latest
        return {"symbol": symbol, "baseline_date": d0.isoformat(), "baseline": round(p0,4),
                "latest_date": d1.isoformat(), "latest": round(p1,4),
                "change_sek": round(p1-p0,4), "change_percent": round((p1/p0-1)*100,2),
                "source_url": "https://finance.yahoo.com/quote/"+symbol+"/history/",
                "note": "Jämfört med föregående handelsveckas sista stängningskurs. Fördröjda dagsstängningar, inte realtid."}
    except Exception as exc:
        print("Stock quote unavailable:", exc)
        return previous if previous else {"unavailable": True, "note": "Kursförändring saknas: jämförbara verifierbara dagsstängningar kunde inte hämtas."}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scheduled", action="store_true", help="Run only at 09:00 Europe/Stockholm")
    ap.add_argument("--offline", action="store_true", help="Generate from existing data without RSS")
    ap.add_argument("--backfill", type=int, default=0, help="Number of previous Sundays, including latest")
    ap.add_argument("--date", help="Local date YYYY-MM-DD (for reproducible tests)")
    args = ap.parse_args()
    if ISSUER not in CONFIG:
        raise RuntimeError("Unknown repository slug " + ISSUER)
    if args.scheduled and dt.datetime.now(LOCAL_TZ).hour != 9:
        print("Outside Stockholm 09:00, skipping duplicate UTC schedule")
        return
    local_now = iso_date(args.date) if args.date else dt.datetime.now(LOCAL_TZ).date()
    if not local_now:
        raise ValueError("Invalid --date")
    target = local_now
    old_data = read_json(OUTPUT, {"weeks": []})
    editions = [e for e in old_data.get("weeks", []) if isinstance(e, dict) and e.get("id")]
    known = {e["id"]: e for e in editions}
    finance = read_json(DATA / "financing.json", {})
    model = read_json(DATA / "financing_model.json", {})
    current = snapshot_financing(model, finance)
    count = max(1, min(3, args.backfill or (2 if not editions else 1)))
    # Generate the older week first so snapshots/archives remain chronological.
    for offset in range(count-1, -1, -1):
        sunday = target - dt.timedelta(days=7*offset)
        begin, end, week_id, week_num = bounds(sunday)
        if offset == 0:
            begin = local_now - dt.timedelta(days=6)
            end = local_now
        headlines, omitted, errors = collect_local(begin, end, CONFIG[ISSUER], finance) if args.offline else collect_events(begin, end, CONFIG[ISSUER], finance)
        edition = create_edition(sunday, current, list(known.values()), headlines, errors, omitted)
        if offset == 0:
            edition["start"] = begin.isoformat()
            edition["end"] = end.isoformat()
        previous = known.get(week_id, {})
        # Preserve previously discovered items when refreshing the current week.
        old_events = previous.get("events", []) if isinstance(previous, dict) else []
        by_key = {(e.get("date"), e.get("url") or e.get("title")): e for e in old_events}
        for e in edition["events"]:
            key = (e.get("date"), e.get("url") or e.get("title"))
            by_key[key] = e
        edition["events"] = sorted(by_key.values(), key=lambda e: e.get("date", ""), reverse=True)
        edition["stock_change"] = weekly_stock_change(begin, local_now, previous.get("stock_change") if isinstance(previous, dict) else None)
        known[week_id] = edition
    weeks = sorted(known.values(), key=lambda e: e["id"], reverse=True)
    payload = {
        "version": 1, "company": CONFIG[ISSUER]["name"],
        "timezone": "Europe/Stockholm",
        "schedule": "Varje dag kl. 09:00 Europe/Stockholm; ny ISO-vecka från måndag",
        "updated_at": dt.datetime.now(LOCAL_TZ).isoformat(timespec="seconds"),
        "latest_week": weeks[0]["id"] if weeks else None, "weeks": weeks
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Weekly digest", ISSUER, "latest", payload["latest_week"],
          "weeks", len(weeks), "events", len(weeks[0]["events"]) if weeks else 0)

def collect_local(start, end, config, finance):
    # A strict no-network mode for offline tests.
    saved = read_json(DATA / "news.json", {})
    source = list(saved.get("items", [])) + [x for x in finance.get("latest_items", [])
                                               if x.get("category") != "jämförelsebolag"]
    events = []
    for x in source:
        day = iso_date(x.get("date"))
        if day is None or not start <= day <= end:
            continue
        e = event(x.get("title"), day.isoformat(), x.get("url"), x.get("source"),
                  x.get("verified", False))
        if e and issuer_matches(e, config):
            events.append(e)
    for m in load_milestones():
        day = milestone_date(m.get("date", ""))
        if m.get("status") == "done" and day and start <= day <= end:
            e = event(m.get("title", ""), day.isoformat(), m.get("url", ""), "Källbelagd milstolpe", True, "milstolpe")
            if e:
                events.append(e)
    if ISSUER == "cereno":
        for a in finance.get("alerts", []):
            day = iso_date(a.get("date"))
            verified = ("Verifierat" in str(a.get("status", "")) or "Källjämförelse" in str(a.get("status", "")))
            if day and start <= day <= end and verified:
                e = event(a.get("title"), day.isoformat(), a.get("source", ""), "Finansieringsanalys", True, "källgranskad")
                if e:
                    e["summary"] = str(a.get("detail", ""))[:330] or e["summary"]
                    events.append(e)
    events.sort(key=lambda e: (int(e["verified"]), event_priority(e), e["date"]), reverse=True)
    result, seen = [], set()
    for e in events:
        if e["url"] in seen or any(similar(e, x) for x in result):
            continue
        result.append(e)
        seen.add(e["url"])
    result.sort(key=lambda e: (e["date"], event_priority(e)), reverse=True)
    return result, 0, ["Nätkontroll avstängd"]

if __name__ == "__main__":
    main()
