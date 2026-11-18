"""Render Mina Aktier's common masthead, section directory and company profile."""
from __future__ import annotations

import argparse
import json
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
COMPANIES = (("isofol", "Isofol"), ("synact", "SynAct"), ("cereno", "Cereno"))


class PageIndex(HTMLParser):
    """Collect sections in reading order. Headings supply default menu labels."""

    def __init__(self):
        super().__init__()
        self.sections = []
        self.stack = []
        self.ids = set()
        self.headings = {}
        self.heading = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        anchor = attrs.get("id")
        if anchor:
            self.ids.add(anchor)
        if tag == "section":
            target = attrs.get("aria-labelledby")
            if not target:
                raise ValueError("Every section needs a heading referenced by aria-labelledby")
            section = {"target": target, "name": attrs.get("data-nav-label"), "children": []}
            self.sections.append(section)
            self.stack.append(section)
        if tag in ("h1", "h2", "h3") and anchor:
            self.heading = anchor
            self.headings[anchor] = []
        if self.stack and "data-nav-child" in attrs:
            if not anchor:
                raise ValueError("A subsection link requires a stable id")
            self.stack[-1]["children"].append((anchor, attrs["data-nav-child"]))

    def handle_data(self, data):
        if self.heading:
            self.headings[self.heading].append(data)

    def handle_endtag(self, tag):
        if tag == "section":
            self.stack.pop()
        if tag in ("h1", "h2", "h3"):
            self.heading = None

    def groups(self):
        seen = set()
        for section in self.sections:
            target = section["target"]
            name = section["name"] or " ".join("".join(self.headings.get(target, [])).split())
            if not name or target not in self.ids:
                raise ValueError("Section has no readable heading at #" + target)
            for key in [target, *(anchor for anchor, _ in section["children"])]:
                if key in seen:
                    raise ValueError("Duplicate section link to #" + key)
                seen.add(key)
            yield target, name, section["children"]


def fill_region(page, region, content):
    start = f"<!-- portfolio:{region} -->"
    end = f"<!-- /portfolio:{region} -->"
    if page.count(start) != 1 or page.count(end) != 1:
        raise ValueError("Missing or duplicate layout region: " + region)
    before, remaining = page.split(start)
    _, after = remaining.split(end)
    return before + start + "\n" + content.rstrip() + "\n" + end + after


def link_to(anchor, label):
    return f'<a href="#{escape(anchor, quote=True)}">{escape(label)}</a>'


def render(root=ROOT):
    profile = json.loads((root / "data/site_profile.json").read_text(encoding="utf-8"))
    safe = {key: escape(value, quote=True) for key, value in profile.items()}
    page = (root / "index.html").read_text(encoding="utf-8")
    template_dir = root / "layout"
    profile_html = Template((template_dir / "profile.html").read_text(encoding="utf-8"))
    page = fill_region(page, "profile", profile_html.substitute(safe))
    index = PageIndex()
    index.feed(page)
    tabs, directory = [], []
    for target, label, children in index.groups():
        parent = link_to(target, label)
        tabs.append(parent)
        nested = "".join(f"<li>{link_to(key, text)}</li>" for key, text in children)
        child_list = f"<ul>{nested}</ul>" if nested else ""
        directory.append(f'<div class="desk-nav-group">{parent}{child_list}</div>')
    companies = []
    for slug, name in COMPANIES:
        current = ' aria-current="page"' if slug == profile["slug"] else ""
        companies.append(f'<a href="../{slug}/"{current}>{name}</a>')
    header_html = Template((template_dir / "masthead.html").read_text(encoding="utf-8"))
    header = header_html.substitute(companies="\n".join(companies), tabs="\n".join(tabs),
                                    directory="\n".join(directory), official=safe["official"])
    return fill_region(page, "masthead", header)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the checked-in page is stale")
    args = parser.parse_args()
    result = render()
    path = ROOT / "index.html"
    if args.check:
        if result != path.read_text(encoding="utf-8"):
            parser.exit(1, "Run python scripts/render_layout.py to update the section menu.\n")
    else:
        path.write_text(result, encoding="utf-8")
