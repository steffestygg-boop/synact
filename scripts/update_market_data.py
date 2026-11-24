"""Refresh sourced market figures in the stock section during the news run."""
from datetime import datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

COMPANY = "SynAct Pharma"
NORDNET = "https://www.nordnet.se/aktier/kurser/syn-act-pharma-synact-xsto"
OWNERS = "https://www.borskollen.se/aktie/synact-pharma"
FI = "https://www.fi.se/sv/vara-register/fis-marknadsregister/blankning/register/"
today = datetime.now(ZoneInfo("Europe/Stockholm")).date().isoformat()


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.skip = False
        if tag == "tr":
            self.parts.append("|")

    def handle_data(self, text):
        if not self.skip and text.strip():
            self.parts.append(text.strip())


def fetch(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "sv-SE"})
    with urlopen(req, timeout=25) as response:
        parser = VisibleText()
        parser.feed(response.read().decode("utf-8"))
    return " ".join(" ".join(parser.parts).split())


def number(text, label):
    match = re.search(label + r"\s*:?\s*(\d{1,3}(?:[ ,]\d{3})+|\d+)(?![\d,])", text, re.I)
    if not match:
        raise ValueError("Missing " + label)
    return int(re.sub(r"\D", "", match[1]))


def refresh(page):
    for url, keys in [(NORDNET, ["shares"]), (OWNERS, ["Avanza", "Nordnet"]), (FI, ["short"])]:
        try:
            content = fetch(url)
        except (OSError, ValueError) as exc:
            print("Source unavailable:", url, exc)
            content = ""
        for key in keys:
            try:
                date = today
                if key == "short":
                    row = re.search(re.escape(COMPANY) + r"\s+AB(?:\s*\(publ\))?\s+[A-Z0-9]{20}\s+(\d{4}-\d{2}-\d{2})\s+(\d+(?:[.,]\d+)?)\s*(?:%|\|)", content, re.I)
                    if not row:
                        raise ValueError("Register row unavailable")
                    date, value = row.groups()
                    value = value.replace(".", ",") + " %"
                    source = "FI · position " + date
                else:
                    if COMPANY.lower() not in content.lower():
                        raise ValueError("Issuer unavailable")
                    label = "Antal aktier" if key == "shares" else "Antal ägare " + key
                    count = number(content, label)
                    if count <= 0:
                        raise ValueError("Unexpected count")
                    value = f"{count:,}".replace(",", " ")
                    source = "Nordnet / FactSet" if key == "shares" else key + " · Börskollen"
                html = f'<strong>{value}</strong><a href="{escape(url)}" target="_blank" rel="noopener">{source} · avläst {today}</a>'
            except ValueError as exc:
                print(key, exc)
                html = None
            pattern = rf"(<!-- market:{key} -->)(.*?)(<!-- /market:{key} -->)"
            def replace(match):
                previous = match[2].split('<small class="market-missing">')[0]
                missing = f'<small class="market-missing">Ny uppgift saknas vid kontroll {today}</small>'
                return match[1] + (html if html else previous + missing) + match[3]
            page, matches = re.subn(pattern, replace, page, flags=re.S)
            if matches != 1:
                raise ValueError("Missing market field: " + key)
    return page


if __name__ == "__main__":
    path = Path("index.html")
    path.write_text(refresh(path.read_text(encoding="utf-8")), encoding="utf-8")
