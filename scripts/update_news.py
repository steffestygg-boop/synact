"""Fetch public Google News RSS items about SynAct Pharma and resomelagon.
RSS headlines are not independent clinical verification.
"""
import datetime as dt
import email.utils
import json
import pathlib
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUERY = '("SynAct Pharma" OR "resomelagon" OR "AP1189") when:90d'
URL = 'https://news.google.com/rss/search?' + urllib.parse.urlencode(
    {'q': QUERY, 'hl': 'sv', 'gl': 'SE', 'ceid': 'SE:sv'})
req = urllib.request.Request(
    URL, headers={'User-Agent': 'Mozilla/5.0 (compatible; SynActTracker/1.0)'})
with urllib.request.urlopen(req, timeout=25) as response:
    content = response.read()
root = ET.fromstring(content)

items = []
seen = set()
for item in root.findall('./channel/item'):
    title = (item.findtext('title') or '').strip()
    link = (item.findtext('link') or '').strip()
    published = (item.findtext('pubDate') or '').strip()
    source = (item.findtext('source') or '').strip()
    if not title or not link or link in seen:
        continue
    if 'synact' not in title.casefold() and 'resomelagon' not in title.casefold() and 'ap1189' not in title.casefold():
        continue
    seen.add(link)
    try:
        date = email.utils.parsedate_to_datetime(published).astimezone(dt.timezone.utc).date().isoformat()
    except (ValueError, TypeError, IndexError):
        date = ''
    items.append({'title': title, 'url': link, 'date': date, 'source': source})
items.sort(key=lambda item: item['date'], reverse=True)
items = items[:16]
if not items:
    raise RuntimeError('No matching RSS items; preserving existing news data')
payload = {
  'updated_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
  'feed': 'Google News RSS – automatically aggregated headlines, not independently verified',
  'items': items
}
(ROOT / 'data' / 'news.json').write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Saved', len(items), 'SynAct news headlines')
