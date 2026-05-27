#!/usr/bin/env python3
"""Generate city/state pages from JSON data files.

Usage:
    python scripts/generate_page.py data/cities/mesa.json
    python scripts/generate_page.py data/cities/*.json
    python scripts/generate_page.py --all

Writes:
    resources/cities/<slug>.html  (English city)
    es/recursos/ciudades/<slug>.html  (Spanish city)
    resources/states/<slug>.html  (English state)
    es/recursos/estados/<slug>.html  (Spanish state)
"""
import argparse
import glob
import json
import os
import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("ERROR: jinja2 is required. Install with: pip install jinja2 --break-system-packages")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
DATA_DIR = REPO_ROOT / "data"


# Output path layouts and breadcrumb context per (kind, lang).
LAYOUTS = {
    ("city", "en"): {
        "output_path": "resources/cities/{slug}.html",
        "canonical_path": "/resources/cities/{slug}",
        "alt_lang_path": "/es/recursos/ciudades/{slug}",
        "rel_prefix": "../../",
        "home_path": "",
        "resources_path": "resources/",
        "depth": 3,  # ../../images, ../../css, ../../js
        "labels": {
            "home": "Home",
            "resources": "Resources",
            "updated": "Updated",
            "quick_numbers": "Quick numbers to write down:",
            "next_steps": "Next Steps",
            "related_resources": "Related Resources",
        },
        "breadcrumb_position3_name": "{breadcrumb_label}",  # filled from data
    },
    ("city", "es"): {
        "output_path": "es/recursos/ciudades/{slug}.html",
        "canonical_path": "/es/recursos/ciudades/{slug}",
        "alt_lang_path": "/resources/cities/{slug}",
        "rel_prefix": "../../../",
        "home_path": "es/",
        "resources_path": "es/recursos/",
        "depth": 3,
        "labels": {
            "home": "Inicio",
            "resources": "Recursos",
            "updated": "Actualizado",
            "quick_numbers": "Números importantes para anotar:",
            "next_steps": "Próximos pasos",
            "related_resources": "Recursos relacionados",
        },
        "breadcrumb_position3_name": "{breadcrumb_label}",
    },
    ("state", "en"): {
        "output_path": "resources/states/{slug}.html",
        "canonical_path": "/resources/states/{slug}",
        "alt_lang_path": "/es/recursos/estados/{slug}",
        "rel_prefix": "../../",
        "home_path": "",
        "resources_path": "resources/",
        "depth": 3,
        "labels": {
            "home": "Home",
            "resources": "Resources",
            "updated": "Updated",
            "quick_numbers": "Quick numbers to write down:",
            "next_steps": "Next Steps",
            "related_resources": "Related Resources",
        },
        "breadcrumb_position3_name": "State Resources",
        "breadcrumb_position4_name": "{breadcrumb_label}",
    },
    ("state", "es"): {
        "output_path": "es/recursos/estados/{slug}.html",
        "canonical_path": "/es/recursos/estados/{slug}",
        "alt_lang_path": "/resources/states/{slug}",
        "rel_prefix": "../../../",
        "home_path": "es/",
        "resources_path": "es/recursos/",
        "depth": 3,
        "labels": {
            "home": "Inicio",
            "resources": "Recursos",
            "updated": "Actualizado",
            "quick_numbers": "Números importantes para anotar:",
            "next_steps": "Próximos pasos",
            "related_resources": "Recursos relacionados",
        },
        "breadcrumb_position3_name": "Recursos por estado",
        "breadcrumb_position4_name": "{breadcrumb_label}",
    },
}


def build_breadcrumb_json(layout, data, lang):
    """Build the BreadcrumbList JSON-LD with proper indentation."""
    base = f"https://waythroughproject.com{layout['canonical_path'].format(slug='').rsplit('/', 1)[0]}/"
    home_url = "https://waythroughproject.com/" + layout["home_path"]
    resources_url = "https://waythroughproject.com/" + layout["resources_path"]
    items = [
        {"@type": "ListItem", "position": 1, "name": layout["labels"]["home"], "item": home_url},
        {"@type": "ListItem", "position": 2, "name": layout["labels"]["resources"], "item": resources_url},
    ]
    # State pages have 4 levels (Home → Resources → State Resources → <state>)
    if "breadcrumb_position4_name" in layout:
        states_url = f"https://waythroughproject.com{layout['canonical_path'].format(slug='').rsplit('/', 1)[0]}/"
        items.append({
            "@type": "ListItem", "position": 3,
            "name": layout["breadcrumb_position3_name"],
            "item": states_url,
        })
        items.append({
            "@type": "ListItem", "position": 4,
            "name": data.get("breadcrumb_label_long") or data["breadcrumb_label"],
        })
    else:
        items.append({
            "@type": "ListItem", "position": 3,
            "name": data.get("breadcrumb_label_long") or data["breadcrumb_label"],
        })
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }, indent=2, ensure_ascii=False)


def build_faq_json(faqs):
    """Build the FAQPage JSON-LD."""
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": f["a"]},
            }
            for f in faqs
        ],
    }, indent=2, ensure_ascii=False)


def render_one(env, kind, lang, slug, data, layout):
    """Render one language's page for one location."""
    canonical_path = layout["canonical_path"].format(slug=slug)
    alt_lang_path = layout["alt_lang_path"].format(slug=slug)
    output_path = REPO_ROOT / layout["output_path"].format(slug=slug)

    breadcrumb_json = build_breadcrumb_json(layout, data, lang)
    faq_json = build_faq_json(data.get("faqs", [])) if data.get("faqs") else ""

    template = env.get_template("city.html.j2")
    html = template.render(
        data=data,
        lang=lang,
        slug=slug,
        kind=kind,
        canonical_path=canonical_path,
        alt_lang_url=alt_lang_path,
        rel_prefix=layout["rel_prefix"],
        home_path=layout["home_path"],
        resources_path=layout["resources_path"],
        labels=layout["labels"],
        breadcrumb_json=breadcrumb_json,
        faq_json=faq_json,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def process_data_file(env, json_path):
    """Process one JSON data file -> writes EN and ES output."""
    with open(json_path, encoding="utf-8") as f:
        spec = json.load(f)

    slug = spec["slug"]
    kind = spec.get("kind", "city")
    written = []
    for lang in ("en", "es"):
        if lang not in spec:
            continue
        layout = LAYOUTS[(kind, lang)]
        path = render_one(env, kind, lang, slug, spec[lang], layout)
        written.append(path)
    return written


def main():
    parser = argparse.ArgumentParser(description="Generate city/state pages from JSON.")
    parser.add_argument("paths", nargs="*", help="JSON data files to render. Supports glob.")
    parser.add_argument("--all", action="store_true", help="Render every JSON in data/")
    args = parser.parse_args()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
    )

    if args.all:
        json_files = list(DATA_DIR.glob("**/*.json"))
    else:
        json_files = []
        for p in args.paths:
            json_files.extend(Path(f) for f in glob.glob(p))
        if not json_files:
            json_files = [Path(p) for p in args.paths]  # fallback if glob returns []

    if not json_files:
        parser.print_help()
        sys.exit(1)

    total_written = 0
    for jf in json_files:
        try:
            written = process_data_file(env, jf)
            for w in written:
                rel = w.relative_to(REPO_ROOT)
                print(f"  wrote: {rel}")
            total_written += len(written)
        except Exception as e:
            print(f"  ERROR on {jf}: {e}", file=sys.stderr)
            raise

    print(f"\nWrote {total_written} file(s) from {len(json_files)} data file(s).")


if __name__ == "__main__":
    main()
