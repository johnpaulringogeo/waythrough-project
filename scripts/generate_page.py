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

Safeguard: Spanish (es) pages are validated for missing diacritics before they
are written. If an es page contains a red-flag un-accented Spanish word in its
visible text, generation raises an error so plain-ASCII Spanish can never ship.
The two false positives that scripts/check_spanish.py documents in its own
docstring are exempted narrowly here -- see ES_FALSE_POSITIVES below.
"""
import argparse
import glob
import json
import os
import re
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


# Words that ALWAYS take a diacritic in Spanish (Spanish-only spellings, so they
# won't collide with English text that may appear on a page). If any of these
# show up un-accented in the VISIBLE text of an es page, the page is missing its
# accents and must be fixed before publishing.
ES_REDFLAGS = [
    "informacion", "deposito", "depositos", "seccion", "proteccion",
    "pagina", "paginas", "telefono", "numero", "numeros", "credito", "creditos",
    "energia", "mayoria", "garantia", "dias", "ano", "anos", "dueno", "duenos",
    "duena", "danos", "nino", "ninos", "despues", "segun", "tambien", "ademas",
    "aqui", "alli", "asi", "comision", "division", "articulo", "economica",
    "economico", "energetica", "energetico", "restitucion", "citacion",
    "devolucion", "discriminacion", "reubicacion", "inspeccion", "renovacion",
    "aplicacion", "terminacion", "estabilizacion", "anulacion", "calefaccion",
    "jurisdiccion", "organizacion", "declaracion", "condicion", "situacion",
    "duracion", "comunicacion", "preempcion", "practicamente", "pequeno",
    "pequenos", "pequena", "interes", "cupon", "razon", "habia", "habian",
    "tenia", "limite", "limites", "maximo", "maxima", "minimo",
]


# Documented false positives: spellings that look like a red-flag word but are
# correct as written. These are the two cases scripts/check_spanish.py names in
# its docstring. check_spanish.py only *reports*, so a human can eyeball them
# there; generate_page.py HARD-RAISES, so it has to know them or it blocks
# pages whose Spanish is already correct.
#
#   1. "Division" inside an English proper noun -- "Salvation Army Massachusetts
#      Division", "Division Circle" (a San Francisco Navigation Center). Exempt
#      ONLY when the word is capitalised AND sits directly beside another
#      capitalised word, i.e. it is part of a multi-word English name. Lower-case
#      "division" in Spanish prose, where "division" with an accent is required,
#      is still caught.
#   2. "limite"/"limites" as the VERB after a reflexive clitic -- "no te limites
#      a una sola PHA", "que no se limite a ...". Correctly un-accented, unlike
#      the noun. Safe because a noun can never follow a reflexive clitic, so this
#      cannot mask a missing accent on the noun. NOTE: the bare subjunctive
#      "que limite ..." that check_spanish.py also lists is deliberately NOT
#      exempted -- "que limites de ingresos" is a real un-accented-noun risk, so
#      that one still raises and gets a human look.
ES_FALSE_POSITIVES = [
    re.compile(r"\b[A-Z][\w'\u2019-]*\s+Division\b|\bDivision\s+[A-Z][\w'\u2019-]*"),
    re.compile(r"\b(?:te|se|me|nos|os)\s+limites?\b", re.IGNORECASE),
]


def es_accent_violations(html):
    """Return the sorted list of red-flag un-accented words found in visible
    es text (HTML tags, and therefore href URLs/slugs, are stripped first).

    A hit that falls entirely inside an ES_FALSE_POSITIVES span is correct as
    written and does not count. Every other hit still raises -- this narrows the
    guard, it does not weaken it.
    """
    # Drop <script>/<style> blocks first so JS string literals / URL slugs
    # are not mistaken for un-accented visible Spanish prose.
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    exempt = [m.span() for pat in ES_FALSE_POSITIVES for m in pat.finditer(text)]
    found = []
    for w in ES_REDFLAGS:
        for m in re.finditer(r"\b" + w + r"\b", text, re.IGNORECASE):
            if not any(s <= m.start() and m.end() <= e for s, e in exempt):
                found.append(w)
                break
    return sorted(set(found))


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
            "state_resources": "State Resources",
        },
        "states_path": "resources/states/",
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
            "state_resources": "Recursos por estado",
        },
        "states_path": "es/recursos/estados/",
        "breadcrumb_position3_name": "Recursos por estado",
        "breadcrumb_position4_name": "{breadcrumb_label}",
    },
}

# The only kinds this generator renders; see process_data_file().
KINDS = sorted({kind for kind, _lang in LAYOUTS})


def build_breadcrumb_json(layout, data, lang):
    """Build the BreadcrumbList JSON-LD with proper indentation."""
    base = f"https://waythroughproject.com{layout['canonical_path'].format(slug='').rsplit('/', 1)[0]}/"
    home_url = "https://waythroughproject.com/" + layout["home_path"]
    resources_url = "https://waythroughproject.com/" + layout["resources_path"]
    items = [
        {"@type": "ListItem", "position": 1, "name": layout["labels"]["home"], "item": home_url},
        {"@type": "ListItem", "position": 2, "name": layout["labels"]["resources"], "item": resources_url},
    ]
    # State pages have 4 levels (Home -> Resources -> State Resources -> <state>)
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

    template = env.get_template(f"{kind}.html.j2")
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
        states_path=layout.get("states_path", ""),
        labels=layout["labels"],
        breadcrumb_json=breadcrumb_json,
        faq_json=faq_json,
    )

    # Safeguard: never write a Spanish page that is missing its accents.
    if lang == "es":
        bad = es_accent_violations(html)
        if bad:
            raise ValueError(
                f"Spanish accent check FAILED for {output_path.name}: found un-accented "
                f"word(s) {bad}. Add proper diacritics (a/e/i/o/u accents, n-tilde, "
                f"opening question/exclamation marks) to the 'es' block before generating."
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def process_data_file(env, json_path):
    """Process one JSON data file -> writes EN and ES output.

    Returns None, writing nothing, for a data file whose "kind" this generator
    does not own: data/authorities/*.json is kind="authority" and belongs to
    scripts/generate_authority.py, which renders it with its own accent guard.
    Without this, --all dies on the first authority JSON with a KeyError.
    """
    with open(json_path, encoding="utf-8") as f:
        spec = json.load(f)

    slug = spec["slug"]
    kind = spec.get("kind", "city")
    if kind not in KINDS:
        return None
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
    skipped = []
    for jf in json_files:
        try:
            written = process_data_file(env, jf)
            if written is None:
                skipped.append(jf)
                continue
            for w in written:
                rel = w.relative_to(REPO_ROOT)
                print(f"  wrote: {rel}")
            total_written += len(written)
        except Exception as e:
            print(f"  ERROR on {jf}: {e}", file=sys.stderr)
            raise

    if skipped:
        print(f"\nSkipped {len(skipped)} data file(s) this generator does not own "
              f"-- run scripts/generate_authority.py for those:")
        for jf in skipped:
            print(f"  skipped: {jf}")
    print(f"\nWrote {total_written} file(s) from "
          f"{len(json_files) - len(skipped)} data file(s).")


if __name__ == "__main__":
    main()
