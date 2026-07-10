#!/usr/bin/env python3
"""Generate housing-authority pages from data/authorities/<slug>.json.

Usage:
    python scripts/generate_authority.py                # render every authority
    python scripts/generate_authority.py data/authorities/milwaukee-hacm.json

Writes English pages to resources/housing-authorities/<slug>.html.
Mirrors the approach of generate_page.py (Jinja2 template + JSON data).
"""
import json
import sys
import glob
import html
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "authorities"
OUT_DIR = ROOT / "resources" / "housing-authorities"
TEMPLATES = ROOT / "templates"
REL_PREFIX = "../../"


def build_breadcrumb_json(data):
    name = data.get("short_name") or data["name"]
    obj = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://waythroughproject.com/"},
            {"@type": "ListItem", "position": 2, "name": "Resources", "item": "https://waythroughproject.com/resources/"},
            {"@type": "ListItem", "position": 3, "name": "Housing Authorities", "item": "https://waythroughproject.com/resources/housing-authorities/"},
            {"@type": "ListItem", "position": 4, "name": name},
        ],
    }
    return json.dumps(obj, indent=2, ensure_ascii=False)


def build_gov_json(data):
    obj = {
        "@context": "https://schema.org",
        "@type": "GovernmentOffice",
        "name": data.get("schema_name") or data["name"],
        "telephone": data.get("phone", ""),
        "url": data.get("official_url", ""),
        "areaServed": data.get("serves", ""),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": data.get("city", ""),
            "addressRegion": data.get("state", ""),
            "addressCountry": "US",
        },
    }
    return json.dumps(obj, indent=2, ensure_ascii=False)


def build_faq_json(data):
    faqs = data.get("faqs") or []
    if not faqs:
        return ""
    obj = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faqs
        ],
    }
    return json.dumps(obj, indent=2, ensure_ascii=False)


def build_title(data):
    return f"{data['name']}: Section 8 Waitlist Status, Contact & How to Apply | Waythrough"


def build_description(data):
    return (f"{data['name']} in {data['city']}, {data['state']}: current Section 8 / "
            f"Housing Choice Voucher waiting-list status, phone {data.get('phone','')}, programs offered, "
            f"and how to apply. An independent guide.")


def render(env, data):
    slug = data["slug"]
    tmpl = env.get_template("authority.html.j2")
    out = tmpl.render(
        data=data,
        title=html.escape(build_title(data), quote=True),
        description=html.escape(build_description(data), quote=True),
        canonical_path=f"/resources/housing-authorities/{slug}",
        rel_prefix=REL_PREFIX,
        breadcrumb_json=build_breadcrumb_json(data),
        gov_json=build_gov_json(data),
        faq_json=build_faq_json(data),
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / f"{slug}.html"
    dest.write_text(out, encoding="utf-8")
    return dest


def main():
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), trim_blocks=False, lstrip_blocks=False)
    args = sys.argv[1:]
    if args:
        files = []
        for a in args:
            files.extend(glob.glob(a))
        files = files or args
    else:
        files = sorted(str(p) for p in DATA_DIR.glob("*.json"))
    written = []
    for f in files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        written.append(str(render(env, data)))
    for w in written:
        print(f"wrote {w}")
    print(f"done: {len(written)} authority page(s)")


if __name__ == "__main__":
    main()
