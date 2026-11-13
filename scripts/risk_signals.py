#!/usr/bin/env python3
"""Source-conscious financing warnings, shared by SynAct and Isofol.

Verified balance-sheet/contract signals are derived from manually curated
source-linked reports. Headline matches are only *leads for review*, never
automatically verified facts or multipliers in the equity-risk forecast.
"""
from __future__ import annotations
import datetime as dt
import re
from typing import Any

RULES = [
    ("trading_halt", "kritisk", "Handelsstopp / insiderinformation",
     r"handelsstopp(?:ad|ats|ade)?|handeln (?:stoppas|stoppad)|suspension of trading|trading susp(?:ended|ension)|trading halt(?:ed)?|non.disclosure of inside information|icke offentliggjord insiderinformation",
     "Kontrollera börsens ursprungliga marknadsmeddelande och om handeln senare återupptagits. Ett handelsstopp kan ha andra orsaker än kapitalanskaffning."),
    ("liquidity_warning", "kritisk", "Uttalat finansierings- eller likviditetsproblem",
     r"going.concern|likviditetsbrist|otillr[aä]ckligt r[oö]relsekapital|working capital deficit|insufficient (?:working capital|liquidity)|cash shortage|kassan r[aä]cker inte|finansieringsbehov|need for (?:additional |new )?financ|additional (?:equity )?funding (?:is )?required|kapitalbehov",
     "Läs originalrapporten: omfattning, period, befintliga kreditavtal och styrelsens prognos avgör betydelsen."),
    ("deferred_payments", "förhöjd", "Uppskjutna betalningar / anstånd",
     r"uppskjutna betalningar|betalningsanst[aå]nd|f[oö]rl[aä]ngda betalningsvillkor|deferred pay(?:ment|ables)|payment deferral|extended payment terms|betalningsfrist|skjuter upp betalningar|anst[aå]nd till leverant[oö]r",
     "Kontrollera vad som skjutits upp, kostnad, belopp och om det är ett ordinarie kommersiellt villkor."),
    ("new_equity", "kritisk", "Nyemission eller kapitalanskaffning annonserad",
     r"f[oö]retr[aä]desemission|nyemission|riktad emission|riktad nyemission|rights? issue|directed share issue|share issuance|private placement|new share issue|equity offering",
     "Kontrollera om emissionen verkligen är beslutad, endast planerad eller redan genomförd; en emissionsrubrik är inte en framtida prognossignal."),
    ("new_debt", "förhöjd", "Nytt lån / konvertibel finansiering",
     r"konvertibel|convertible financing|convertible loan|finansieringsfacilitet|credit facility|l[aå]nefinansiering|loan facility|new loan|bryggl[aå]n|bridge financing",
     "Läs villkoren: lån kan både förbättra likviditeten och föra med sig ränta, förfall och eventuell utspädning."),
    ("market_stress", "bevakning", "Kraftig kursrörelse / ovanlig handel",
     r"kursras|aktien rasar|kraftigt kursfall|stort kursfall|ovanligt h[oö]g oms[aä]ttning|unusually high (?:trading )?volume|shares plunge|share price plunges",
     "Kursrörelser och stor handel kan ha många orsaker. Verifiera kurs, omsättning och utlösande nyhet; detta är INTE bevis på insiderhandel eller en förestående emission."),
    ("clinical_costs", "bevakning", "Större studie / högre utvecklingskostnad",
     r"cost overrun|costs? increase|higher trial costs|phase iii? study (?:expan|scale)|fas iii?.*(?:ut[oö]k|fler)|expanded clinical trial|klinisk.*(?:f[oö]rdyr|kostnads[oö]k)",
     "Verifiera om studien redan är finansierad och om budget eller tidsplan har ändrats."),
    ("partner_problem", "förhöjd", "Partnerskap eller avtal riskerar att falla bort",
     r"partner(?:ship|avtal).*(?:terminat|upps[aä]g|avslut)|licen[cs](?:e|avtal).*(?:terminat|upps[aä]g|avslut)|terminate(?:d|s)? (?:the )?(?:license|partnership)",
     "Läs avtalet och se om uppsägningen har påverkan på finansiering eller kostnadsdelning."),
]
NEGATIONS = re.compile(
    r"(?:no|not|without|ingen|inget|inte)\s+(?:new |further |ytterligare |nytt )?"
    r"(?:rights? issue|financing|capital need|new share issue|nyemission|emission|kapitalbehov)", re.I
)
RESUMED = re.compile(r"trading resu(?:med|mes)|handeln [aå]teruppt(?:as|agits)|[aå]terupptagen handel|trading resumed", re.I)
OPTION_NOTICE = re.compile(r"\bTO[12]\b|teckningsoptioner|warrants? exercise|optionsinl[oö]sen", re.I)


def _alert(identifier: str, level: str, title: str, detail: str, source: str,
           date: str, status: str, next_step: str, category: str) -> dict[str, str]:
    return {
        "id": identifier, "level": level, "title": title, "detail": detail,
        "source": source, "date": date, "status": status, "next_step": next_step,
        "category": category,
    }


def baseline_signals(model: dict[str, Any], today: dt.date) -> list[dict[str, str]]:
    """Only manually reviewed report figures and documented contract facts."""
    c = model["company"]
    alerts: list[dict[str, str]] = []
    report = c["q3_url"]
    cash = float(c["cash_msek"])
    operating_q3 = float(c["operating_cashflow_q3_msek"])
    months_cash = cash / (-operating_q3 / 3) if operating_q3 < 0 else float("inf")
    if months_cash <= 9:
        alerts.append(_alert(
            "base:quarterly_burn", "förhöjd" if months_cash < 6 else "bevakning",
            "Kassan jämfört med senaste kvartalets förbrukning",
            "Rapporterad kassa motsvarar ungefär %.1f månader av Q3:s operativa "
            "kassaflöde. Det är en bakåtblickande kvot, inte bolagets prognos; "
            "existerande krediter och kommande kostnader ingår inte." % months_cash,
            report, c["reported_at"], "Verifierad siffergrund – tolkning krävs",
            "Jämför med ledningens finansieringsprognos och eventuell tillgänglig kredit.",
            "cash_burn"
        ))
    target = dt.date.fromisoformat(c["cash_runway_proxy"])
    remaining = (target - today).days / 30.4375
    if remaining <= 12:
        alerts.append(_alert(
            "base:runway", "förhöjd" if remaining < 6 else "bevakning",
            "Finansieringshorisonten närmar sig",
            "Omkring %.1f månader till modellens konservativa riktmärke %s. "
            "Det är INTE en verifierad dag då kassan tar slut; bolagets egen "
            "prognos och tidsfaktorn är redan inräknade i riskmodellen."
            % (remaining, target.strftime("%Y-%m-%d")),
            report, today.isoformat(), "Beräknad från verifierad bolagsprognos",
            "Kontrollera ny likviditetsprognos i kommande kvartalsrapport.",
            "runway"
        ))
    if "fenja" in c:
        loan = c["fenja"]
        if today <= dt.date.fromisoformat(loan["maturity_date"]):
            alerts.append(_alert(
                "base:conditional_credit", "bevakning",
                "Villkorad kredit och framtida förfall",
                "SynAct har en Fenja-facilitet, men ett ytterligare uttag är "
                "villkorat och den befintliga finansieringen innebär låne- "
                "och konverteringsvillkor. Outnyttjad kredit är inte kassa.",
                loan["url"], loan["agreement_date"],
                "Verifierade avtalsvillkor – inte en ny händelse",
                "Bevaka nytt uttag, ändrade lånevillkor, förfall och utspädning.",
                "debt"
            ))
    if "warrants" in c:
        warrants = c["warrants"]
        if not warrants.get("outcome_verified", False):
            expiry = dt.date.fromisoformat("2026-11-30")
            delta = (expiry - today).days
            if delta >= -45:
                alert_level = "förhöjd" if delta < -7 else "bevakning"
                alerts.append(_alert(
                    "base:warrant_outcome", alert_level,
                    "TO2: finansieringsutfallet ännu inte verifierat",
                    "TO2-kursen är fastställd till 0,95 kr, men hur många optioner "
                    "som utnyttjas och vilket nettobelopp Isofol faktiskt får "
                    "kan inte fastställas utifrån teckningspriset. "
                    + ("Teckningsperioden har passerat; utfallet bör kontrolleras."
                       if delta < 0 else
                       "Sista nyttjandedag är den 30 november 2026."),
                    warrants["url"], warrants.get("price_decision_date", "2026-11-13"),
                    "Fastställt pris – utfall kräver kontroll",
                    "Granska bolagets slutliga TO2-utfall och uppdatera finansieringsmodellen.",
                    "warrants"
                ))
    report_age = (today - dt.date.fromisoformat(c["report_date"])).days
    if report_age >= 115:
        alerts.append(_alert(
            "base:stale_report", "bevakning",
            "Finansieringsuppgifterna börjar bli gamla",
            "Det har gått %s dagar sedan senaste modellgranskade balansdag. "
            "Ny kvartalsrapport eller finansiering kan ha förändrat läget." % report_age,
            report, today.isoformat(), "Beräknad datastatus",
            "Uppdatera kassa och bolagets finansieringsprognos från en ny originalrapport.",
            "stale_report"
        ))
    return alerts


def headline_signals(items: list[dict[str, Any]], issuer: str,
                     today: dt.date, max_results: int = 8) -> list[dict[str, str]]:
    """News headlines are leads, never verified financing facts."""
    issuer_regex = (r"synact|resomelagon|ap1189|\bSYNACT\b"
                    if issuer == "synact" else
                    r"isofol|arfolitixorin|\bISOFOL\b")
    found: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in sorted(items, key=lambda x: x.get("date", ""), reverse=True):
        if item.get("category") == "jämförelsebolag":
            continue
        title = str(item.get("title", ""))
        if not re.search(issuer_regex, title, re.I):
            continue
        date_raw = str(item.get("date", ""))
        try:
            published = dt.date.fromisoformat(date_raw[:10])
        except ValueError:
            continue
        if (today - published).days not in range(0, 29):
            continue
        if NEGATIONS.search(title):
            continue
        for slug, level, label, pattern, action in RULES:
            if not re.search(pattern, title, re.I):
                continue
            if slug == "trading_halt" and RESUMED.search(title):
                # Trading resumed is a separate important update, not an active suspension.
                slug, level, label, action = (
                    "trading_resumed", "bevakning", "Handeln rapporteras återupptagen",
                    "Kontrollera Nasdaq och läs orsaken till det tidigare handelsstoppet.")
            if slug == "new_equity" and issuer == "isofol" and OPTION_NOTICE.search(title):
                # TO2 exercise was agreed years before the current monitoring window.
                continue
            key = slug + ":" + re.sub(r"[^a-z0-9åäö]+", "", title.casefold())[:90]
            if key in seen:
                continue
            seen.add(key)
            found.append(_alert(
                key, level, label, title, str(item.get("url", "")), date_raw,
                "Rubrikträff – måste granskas", action, slug))
            break
        if len(found) >= max_results:
            break
    return found


def combined_signals(model: dict[str, Any], headlines: list[dict[str, Any]],
                     issuer: str, today: dt.date) -> list[dict[str, str]]:
    return baseline_signals(model, today) + headline_signals(headlines, issuer, today)
