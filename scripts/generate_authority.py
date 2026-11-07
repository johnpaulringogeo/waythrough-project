#!/usr/bin/env python3
"""Generate housing-authority pages (English + Spanish) from data/authorities/<slug>.json.

Usage:
    python scripts/generate_authority.py                # render every authority (EN+ES)
    python scripts/generate_authority.py data/authorities/milwaukee-hacm.json

Writes:
    resources/housing-authorities/<slug>.html                  (English)
    es/recursos/autoridades-de-vivienda/<slug>.html            (Spanish, only if the JSON has an "es" block)

Each JSON keeps its English content at the top level (unchanged) and, optionally, a
localized "es" block that overrides the translatable fields (serves, updated, intro,
programs, waitlists, also_serving, faqs, sources). Shared fields (name, short_name,
phone, URLs, city/state, slugs) are inherited by the Spanish page.

Titles: "title_name" is the name people search (e.g. "HACLA", "MDHA Nashville",
"Denver Housing Authority"); it feeds a compact <title> pattern (TITLE_PATTERNS)
that is always <= 60 characters, and the meta description pattern
(DESC_PATTERNS, 140-158 characters). The full legal "name" stays in the H1 and
body. An "es" block may set its own "title_name". Optional "meta_title" /
"meta_description" override the default <title> and meta description for an
intent the pattern can't carry (Denver's lottery, CHA's phone number); when set
at the top level they must also be set in "es". Generation raises if any title
is over 60 characters or any description is over 158.

Optional "status_check_html" replaces the How to Apply sentence "If you have already applied,
call <phone> to verify your position ..." for authorities where that advice is wrong (status
by email only, an unranked lottery list). Like meta_title, a top-level one needs an es twin.

Safeguard: Spanish pages are validated for missing diacritics before writing. If an
es page's visible text contains a red-flag un-accented Spanish word, generation raises
an error so plain-ASCII Spanish can never ship (mirrors scripts/generate_page.py,
including its ES_FALSE_POSITIVES exemptions).
"""
import json
import re
import sys
import glob
import html
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_page import link_phones  # noqa: E402  (tap-to-call, same rules as js/components.js)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "authorities"
TEMPLATES = ROOT / "templates"

OUT = {
    "en": ROOT / "resources" / "housing-authorities",
    "es": ROOT / "es" / "recursos" / "autoridades-de-vivienda",
}

# ---- Spanish accent guard (same red-flag list and exemptions as generate_page.py) ----
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
# correct as written. Ported from scripts/generate_page.py (commit cce6b99) so
# both generators make the same call. These are the two cases that
# scripts/check_spanish.py names in its docstring. check_spanish.py only
# *reports*, so a human can eyeball them there; this generator HARD-RAISES, so
# it has to know them or it blocks pages whose Spanish is already correct.
#
#   1. "Division" inside an English proper noun -- "Salvation Army Massachusetts
#      Division", "Division Circle" (a San Francisco Navigation Center). Exempt
#      ONLY when the word is capitalised AND sits directly beside another
#      capitalised word, i.e. it is part of a multi-word English name. Lower-case
#      "division" in Spanish prose, where the accented spelling is required, is
#      still caught.
#   2. "limite"/"limites" as the VERB after a reflexive clitic -- "no te limites
#      a una sola PHA", "que no se limite a ...". Correctly un-accented, unlike
#      the noun. Safe because a noun can never follow a reflexive clitic, so this
#      cannot mask a missing accent on the noun. NOTE: the bare subjunctive
#      "que limite ..." that check_spanish.py also lists is deliberately NOT
#      exempted -- "que limites de ingresos" is a real un-accented-noun risk, so
#      that one still raises and gets a human look.
ES_FALSE_POSITIVES = [
    re.compile(r"\b[A-Z][\w'’-]*\s+Division\b|\bDivision\s+[A-Z][\w'’-]*"),
    re.compile(r"\b(?:te|se|me|nos|os)\s+limites?\b", re.IGNORECASE),
]


def es_accent_violations(page_html):
    """Return the sorted red-flag un-accented words found in visible es text.

    A hit that falls entirely inside an ES_FALSE_POSITIVES span is correct as
    written and does not count. Every other hit still raises -- this narrows the
    guard, it does not weaken it.
    """
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", page_html,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    exempt = [m.span() for pat in ES_FALSE_POSITIVES for m in pat.finditer(text)]
    found = []
    for w in ES_REDFLAGS:
        for m in re.finditer(r"\b" + w + r"\b", text, re.IGNORECASE):
            if not any(st <= m.start() and m.end() <= en for st, en in exempt):
                found.append(w)
                break
    return sorted(set(found))


def strip_scheme(url):
    return url.replace("https://", "").replace("http://", "")


def tel(phone):
    return re.sub(r"[()\s-]", "", phone)


def merged_for(data, lang):
    m = {k: v for k, v in data.items() if k != "es"}
    if lang == "es" and isinstance(data.get("es"), dict):
        m.update(data["es"])
    return m


def paths_for(lang, slug):
    if lang == "en":
        rel = "../../"
        return {
            "rel_prefix": rel,
            "home_href": rel,
            "resources_href": rel + "resources/",
            "guides_base": rel + "resources/guides/",
            "cities_base": rel + "resources/cities/",
            "states_base": rel + "resources/states/",
            "apply_guide": "how-to-apply-section-8",
            "find_pha": "how-to-find-your-pha",
            "canonical_path": f"/resources/housing-authorities/{slug}",
        }
    rel = "../../../"
    return {
        "rel_prefix": rel,
        "home_href": rel + "es/",
        "resources_href": rel + "es/recursos/",
        "guides_base": rel + "es/recursos/guias/",
        "cities_base": rel + "es/recursos/ciudades/",
        "states_base": rel + "es/recursos/estados/",
        "apply_guide": "como-solicitar-seccion-8",
        "find_pha": "como-encontrar-tu-pha",
        "canonical_path": f"/es/recursos/autoridades-de-vivienda/{slug}",
    }


# Google cuts titles off at about 60 characters and Bing flags anything over 70,
# so the words a searcher typed ("waitlist", "apply", the city) fall off the end.
# The full legal name stays in the H1 and the body; the <title> uses
# "title_name", the name people actually search (an acronym plus city, or the
# common name). The first pattern that fits TITLE_MAX wins, longest first.
TITLE_MAX = 60
DESC_MIN, DESC_MAX = 140, 158

TITLE_PATTERNS = {
    "en": [
        "{n} Section 8 Waitlist: Status & How to Apply | Waythrough",
        "{n} Section 8 Waitlist & How to Apply | Waythrough",
        "{n} Section 8 Waitlist & How to Apply",
        "{n} Section 8 Waitlist",
    ],
    "es": [
        "Lista de espera Sección 8 de {n}: estado y cómo solicitar",
        "Lista de espera Sección 8 de {n} y cómo solicitar",
        "{n}: lista de espera Sección 8 y solicitud",
        "{n}: lista de espera Sección 8",
    ],
}

# Meta description candidates in order of preference (the dated ones first):
# the first one that lands in DESC_MIN..DESC_MAX wins; otherwise the longest
# one that is <= DESC_MAX.
DESC_PATTERNS = {
    "en": [
        "{n} in {c}, {s}: Section 8 waitlist status (checked {u}), phone {ph}, programs offered and how to apply. An independent guide.",
        "{n} in {c}, {s}: Section 8 waitlist status (checked {u}), phone {ph}, programs and how to apply. An independent guide.",
        "{n} in {c}, {s}: Section 8 waitlist status (checked {u}), phone {ph}, programs and how to apply.",
        "{n} in {c}, {s}: Section 8 waitlist status, phone {ph}, programs offered and how to apply. An independent guide.",
        "{n} in {c}, {s}: Section 8 waitlist status, phone {ph}, programs and how to apply. An independent guide.",
        "{n} in {c}, {s}: Section 8 waitlist status, phone {ph}, programs and how to apply.",
    ],
    "es": [
        "{n} en {c}, {s}: estado de la lista de espera de Sección 8 (verificado {ue}), teléfono {ph}, programas y cómo solicitar. Guía independiente.",
        "{n} en {c}, {s}: lista de espera de Sección 8 (verificada {ue}), teléfono {ph}, programas y cómo solicitar. Guía independiente.",
        "{n} en {c}, {s}: lista de espera de Sección 8 (verificada {ue}), teléfono {ph}, programas y cómo solicitar.",
        "{n} en {c}, {s}: estado de la lista de espera de Sección 8, teléfono {ph}, programas que ofrece y cómo solicitar. Guía independiente.",
        "{n} en {c}, {s}: estado de la lista de espera de Sección 8, teléfono {ph}, programas y cómo solicitar. Guía independiente.",
        "{n} en {c}, {s}: lista de espera de Sección 8, teléfono {ph}, programas que ofrece y cómo solicitar. Guía independiente.",
        "{n} en {c}, {s}: lista de espera de Sección 8, teléfono {ph}, programas y cómo solicitar. Guía independiente.",
        "{n} en {c}, {s}: lista de espera de Sección 8, teléfono {ph}, programas y cómo solicitar.",
    ],
}


def title_name(m):
    return m.get("title_name") or m.get("short_name") or m["name"]


def build_title(m, lang):
    # Optional per-page override: "meta_title" at the top level (EN) and in the
    # "es" block (ES). render() refuses an EN override without an ES one, so the
    # Spanish page can never inherit an English title.
    if m.get("meta_title"):
        title = m["meta_title"]
    else:
        n = title_name(m)
        title = next((p.format(n=n) for p in TITLE_PATTERNS[lang]
                      if len(p.format(n=n)) <= TITLE_MAX), None)
        if title is None:
            raise ValueError(f"{m['slug']} ({lang}): title_name {n!r} is too long for any "
                             f"title pattern; shorten it or set meta_title")
    if len(title) > TITLE_MAX:
        raise ValueError(f"{m['slug']} ({lang}): title is {len(title)} characters, "
                         f"max {TITLE_MAX}: {title!r}")
    return title


def build_description(m, lang):
    if m.get("meta_description"):
        desc = m["meta_description"]
    else:
        fields = dict(n=title_name(m), c=m["city"], s=m["state"],
                      ph=m.get("phone", ""), u=m["updated"],
                      # "el 15 de octubre de 2026" but "en mayo de 2026"
                      ue=("el " if m["updated"][:1].isdigit() else "en ") + m["updated"])
        cands = [p.format(**fields) for p in DESC_PATTERNS[lang]]
        fits = [d for d in cands if len(d) <= DESC_MAX]
        desc = next((d for d in fits if len(d) >= DESC_MIN),
                    max(fits, key=len) if fits else cands[-1])
    if len(desc) > DESC_MAX:
        raise ValueError(f"{m['slug']} ({lang}): meta description is {len(desc)} characters, "
                         f"max {DESC_MAX}: {desc!r}")
    return desc


def build_strings(m, lang, p):
    short = m.get("short_name") or m["name"]
    off = m.get("official_url", "")
    app = m.get("apply_url", "")
    phone = m.get("phone", "")
    apply_guide = f'{p["guides_base"]}{p["apply_guide"]}'
    find_pha = f'{p["guides_base"]}{p["find_pha"]}'

    if lang == "en":
        t = {
            "home": "Home", "resources": "Resources", "authorities": "Housing Authorities",
            "section_label": "Housing Authority",
            "page_meta": f"Serves {m['serves']} · Last checked {m['updated']}",
            "independent_html": (
                f"<strong>Waythrough is an independent resource, not {short}.</strong> "
                "This is a summary of public information. To apply, or to check the current "
                "waiting-list status, use the official links below."),
            "quick_facts": "Quick Facts",
            "quick_facts_html": (
                f"<strong>Serves:</strong> {m['serves']}<br>\n"
                f'                        <strong>Phone:</strong> <a href="tel:{tel(phone)}">{phone}</a><br>\n'
                f'                        <strong>Official site:</strong> <a href="{off}" target="_blank" rel="noopener">{strip_scheme(off)}</a><br>\n'
                f'                        <strong>Apply:</strong> <a href="{app}" target="_blank" rel="noopener">{short} application page</a><br>\n'
                f"                        <strong>Status last checked:</strong> {m['updated']}"),
            "waitlist_status": "Waiting-List Status",
            "waitlist_intro": ("Waiting lists open and close often. The status below is what we found the last "
                               "time we checked; confirm it on the official site before you count on it."),
            "programs_heading": f"Programs {short} Runs",
            "how_to_apply": "How to Apply",
            "apply_body_html": (
                f'Apply on the authority\'s own application page: <a href="{app}" target="_blank" rel="noopener">{strip_scheme(app)}</a>. '
                + (m.get("status_check_html") or
                   f'If you already applied, call <a href="tel:{tel(phone)}">{phone}</a> to check your place on the list, and give them '
                   "your new phone number or address every time it changes. If they can't reach you when your name comes up, they can drop you from the list.")),
            "new_to_process_html": (
                f'If this is your first time applying, our <a href="{apply_guide}">step-by-step guide to applying for Section 8</a> covers each stage, '
                f'and <a href="{find_pha}">how to find your PHA</a> shows which authority covers where you live.'),
            "other_authorities": "Other Authorities Serving This Area",
            "more_local_heading": "More Local Resources",
            "faq_heading": "Frequently Asked Questions",
            "sources": "Sources",
        }
        # More Local Resources sentence
        lead = "For emergency shelter, rental assistance, tenant rights, and legal aid in this area, see "
        if m.get("city_slug"):
            frag = f'our <a href="{p["cities_base"]}{m["city_slug"]}">{m["city"]} housing resources</a> page'
            if m.get("state_slug"):
                frag += f' and our <a href="{p["states_base"]}{m["state_slug"]}">{m["state"]} state resources</a>'
        elif m.get("state_slug"):
            frag = f'our <a href="{p["states_base"]}{m["state_slug"]}">{m["state"]} state resources</a>'
        else:
            frag = "your local city and state resources"
        t["more_local_html"] = lead + frag + "."
        return t

    # ---- Spanish ----
    t = {
        "home": "Inicio", "resources": "Recursos", "authorities": "Autoridades de Vivienda",
        "section_label": "Autoridad de Vivienda",
        "page_meta": f"Sirve a {m['serves']} · Última verificación: {m['updated']}",
        "independent_html": (
            f"<strong>Waythrough es un recurso independiente, no es {short}.</strong> "
            "Esto es un resumen de información pública. Para presentar una solicitud o consultar el estado "
            "actual de la lista de espera, use los enlaces oficiales de abajo."),
        "quick_facts": "Datos rápidos",
        "quick_facts_html": (
            f"<strong>Sirve a:</strong> {m['serves']}<br>\n"
            f'                        <strong>Teléfono:</strong> <a href="tel:{tel(phone)}">{phone}</a><br>\n'
            f'                        <strong>Sitio oficial:</strong> <a href="{off}" target="_blank" rel="noopener">{strip_scheme(off)}</a><br>\n'
            f'                        <strong>Solicitar:</strong> <a href="{app}" target="_blank" rel="noopener">página de solicitud de {short}</a><br>\n'
            f"                        <strong>Estado verificado por última vez:</strong> {m['updated']}"),
        "waitlist_status": "Estado de la lista de espera",
        "waitlist_intro": ("Las listas de espera abren y cierran a menudo. El estado de abajo es lo que encontramos "
                           "la última vez que lo verificamos; confírmelo en el sitio oficial antes de contar con él."),
        "programs_heading": f"Programas que administra {short}",
        "how_to_apply": "Cómo solicitar",
        "apply_body_html": (
            f'Presente su solicitud en la página oficial de la autoridad: <a href="{app}" target="_blank" rel="noopener">{strip_scheme(app)}</a>. '
            + (m.get("status_check_html") or
               f'Si ya presentó su solicitud, llame al <a href="tel:{tel(phone)}">{phone}</a> para saber en qué lugar de la lista está, y avíseles '
               "cada vez que cambie de teléfono o de dirección. Si no logran localizarle cuando le toque su turno, pueden sacarle de la lista.")),
        "new_to_process_html": (
            f'Si es la primera vez que solicita, nuestra <a href="{apply_guide}">guía paso a paso para solicitar la Sección 8</a> explica cada etapa, '
            f'y <a href="{find_pha}">cómo encontrar su PHA</a> le muestra qué autoridad cubre la zona donde vive.'),
        "other_authorities": "Otras autoridades que sirven esta zona",
        "more_local_heading": "Más recursos locales",
        "faq_heading": "Preguntas frecuentes",
        "sources": "Fuentes",
    }
    lead = "Para refugio de emergencia, asistencia de alquiler, derechos del inquilino y ayuda legal en esta zona, vea "
    if m.get("city_slug"):
        frag = f'nuestra página de <a href="{p["cities_base"]}{m["city_slug"]}">recursos de vivienda de {m["city"]}</a>'
        if m.get("state_slug"):
            frag += f' y nuestros <a href="{p["states_base"]}{m["state_slug"]}">recursos del estado de {m["state"]}</a>'
    elif m.get("state_slug"):
        frag = f'nuestros <a href="{p["states_base"]}{m["state_slug"]}">recursos del estado de {m["state"]}</a>'
    else:
        frag = "los recursos de su ciudad y estado"
    t["more_local_html"] = lead + frag + "."
    return t


def breadcrumb_json(m, lang, slug):
    if lang == "en":
        names = ["Home", "Resources", "Housing Authorities"]
        base = "https://waythroughproject.com/"
        hub = base + "resources/housing-authorities/"
        res = base + "resources/"
    else:
        names = ["Inicio", "Recursos", "Autoridades de Vivienda"]
        base = "https://waythroughproject.com/"
        hub = base + "es/recursos/autoridades-de-vivienda/"
        res = base + "es/recursos/"
    name = m.get("short_name") or m["name"]
    obj = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": names[0], "item": base},
            {"@type": "ListItem", "position": 2, "name": names[1], "item": res},
            {"@type": "ListItem", "position": 3, "name": names[2], "item": hub},
            {"@type": "ListItem", "position": 4, "name": name},
        ],
    }
    return json.dumps(obj, indent=2, ensure_ascii=False)


def gov_json(m):
    obj = {
        "@context": "https://schema.org",
        "@type": "GovernmentOffice",
        "name": m.get("schema_name") or m["name"],
        "telephone": m.get("phone", ""),
        "url": m.get("official_url", ""),
        "areaServed": m.get("serves", ""),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": m.get("city", ""),
            "addressRegion": m.get("state", ""),
            "addressCountry": "US",
        },
    }
    return json.dumps(obj, indent=2, ensure_ascii=False)


def faq_json(m):
    faqs = m.get("faqs") or []
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


def render(env, data, lang, stage_dir=None):
    slug = data["slug"]
    if lang == "es":
        for k in ("meta_title", "meta_description", "status_check_html"):
            if data.get(k) and not data["es"].get(k):
                raise ValueError(f"{slug}: top-level {k} needs an es.{k} too")
    m = merged_for(data, lang)
    p = paths_for(lang, slug)
    tmpl = env.get_template("authority.html.j2")
    page = tmpl.render(
        data=m,
        lang=lang,
        t=build_strings(m, lang, p),
        title=html.escape(build_title(m, lang), quote=True),
        description=html.escape(build_description(m, lang), quote=True),
        canonical_path=p["canonical_path"],
        alt_en_url=f"https://waythroughproject.com/resources/housing-authorities/{slug}",
        alt_es_url=f"https://waythroughproject.com/es/recursos/autoridades-de-vivienda/{slug}",
        rel_prefix=p["rel_prefix"],
        home_href=p["home_href"],
        resources_href=p["resources_href"],
        breadcrumb_json=breadcrumb_json(m, lang, slug),
        gov_json=gov_json(m),
        faq_json=faq_json(m),
    )
    # Tap-to-call: plain-text phone numbers in <main> (Quick Facts, body, FAQ) become tel: links.
    page = link_phones(page)
    if lang == "es":
        bad = es_accent_violations(page)
        if bad:
            raise ValueError(f"Spanish accent check FAILED for {slug} (es): {bad}")
    dest = OUT[lang] / f"{slug}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    if stage_dir:
        rel = dest.relative_to(ROOT)
        sd = Path(stage_dir) / rel
        sd.parent.mkdir(parents=True, exist_ok=True)
        sd.write_text(page, encoding="utf-8")
    return dest


def main():
    import os
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), trim_blocks=False, lstrip_blocks=False)
    stage_dir = os.environ.get("STAGE_DIR")
    args = sys.argv[1:]
    if args:
        files = []
        for a in args:
            files.extend(glob.glob(a))
        files = files or args
    else:
        files = sorted(str(pp) for pp in DATA_DIR.glob("*.json"))
    written = []
    for f in files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        for lang in ("en", "es"):
            if lang == "es" and not isinstance(data.get("es"), dict):
                continue
            written.append(str(render(env, data, lang, stage_dir)))
    for w in written:
        print(f"wrote {w}")
    print(f"done: {len(written)} authority page(s)")


if __name__ == "__main__":
    main()
