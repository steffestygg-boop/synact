"""Regression checks for the shared navigation and static company profile."""
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest

from scripts.render_layout import COMPANIES, PageIndex, render

ROOT = Path(__file__).resolve().parents[1]


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.navigation = None
        self.links = {}
        self.ids = []
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'nav':
            self.navigation = attrs.get('aria-label')
            self.links[self.navigation] = []
        if tag == 'a' and self.navigation:
            self.links[self.navigation].append((attrs['href'], attrs.get('aria-current')))
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.assets.append(attrs['href'])
        if tag == 'script' and 'src' in attrs:
            self.assets.append(attrs['src'])

    def handle_endtag(self, tag):
        if tag == 'nav':
            self.navigation = None


class LayoutTests(unittest.TestCase):
    def test_static_navigation_matches_every_section_and_subsection(self):
        page = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(render(), page)
        parsed = PageLinks()
        parsed.feed(page)
        index = PageIndex()
        index.feed(page)
        groups = list(index.groups())
        primary = ['#' + anchor for anchor, _, _ in groups]
        directory = []
        for anchor, _, children in groups:
            directory.append('#' + anchor)
            directory.extend('#' + child for child, _ in children)
        self.assertIn('#milestones-heading', primary)
        self.assertEqual([href for href, _ in parsed.links['Avsnitt på sidan']], primary + directory)
        self.assertEqual(len(set(parsed.ids)), len(parsed.ids))
        for href in directory:
            self.assertIn(href[1:], parsed.ids)
        for asset in parsed.assets:
            self.assertTrue((ROOT / asset).is_file(), asset)

    def test_company_switch_and_official_link(self):
        profile = json.loads((ROOT / 'data/site_profile.json').read_text(encoding='utf-8'))
        page = render()
        parsed = PageLinks()
        parsed.feed(page)
        self.assertEqual(parsed.links['Välj bolag'],
                         [(f'../{slug}/', 'page' if slug == profile['slug'] else None)
                          for slug, _ in COMPANIES])
        self.assertIn(f'class="desk-company-site" href="{profile["official"]}"', page)
        self.assertTrue(profile['official'].startswith('https://'))
        self.assertIn(profile['price_id'], parsed.ids)
        self.assertIn(profile['status_id'], parsed.ids)

    def test_new_section_inherits_a_menu_label_from_its_heading(self):
        index = PageIndex()
        index.feed('<section aria-labelledby="projekt"><h2 id="projekt">Kliniska <em>program</em></h2>'
                   '<details id="studie" data-nav-child="Studien"><summary>Öppna</summary></details></section>')
        self.assertEqual(list(index.groups()), [('projekt', 'Kliniska program', [('studie', 'Studien')])])
