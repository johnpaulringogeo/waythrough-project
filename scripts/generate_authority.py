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

Safeguard: Spanish pages are validated for missing diacritics before writing. If an
es page's visible text contains a red-flag un-accented Spanish word, generation raises
an error so plain-ASCII Spanish can never ship (mirrors scripts/generate_page.py).
"""
import json
import re
import sys
import glob
import html
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "authorities"
TEMPLATES = ROOT / "templates"

OUT = {
    "en": ROOT / "resources" / "housing-authorities",
    "es": ROOT / "es" / "recursos" / "autoridades-de-vivienda",
}

# ---- Spanish accent guard (same red-flag list as generate_page.py) ----
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


def es_accent_violations(page_html):
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", page_html,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    found = []
    for w in ES_REDFLAGS:
        if re.search(r"\b" + w + r"\b", text, re.IGNORECASE):
            found.append(w)
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


def build_title(m, lang):
    if lang == "en":
        return f"{m['name']}: Section 8 Waitlist Status, Contact & How to Apply | Waythrough"
    return (f"{m['name']}: estado de la lista de espera de Sección 8, contacto y "
            f"cómo solicitar | Waythrough")


def build_description(m, lang):
    if lang == "en":
        return (f"{m['name']} in {m['city']}, {m['state']}: current Section 8 / "
                f"Housing Choice Voucher waiting-list status, phone {m.get('phone','')}, programs offered, "
                f"and how to apply. An independent guide.")
    return (f"{m['name']} en {m['city']}, {m['state']}: estado actual de la lista de espera de "
            f"Sección 8 / Housing Choice Voucher, teléfono {m.get('phone','')}, programas que ofrece "
            f"y cómo solicitar. Una guía independiente.")


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
                "We summarize public information to help you get oriented. For applications "
                "and the most current waiting-list status, always use the official links below."),
            "quick_facts": "Quick Facts",
            "quick_facts_html": (
                f"<strong>Serves:</strong> {m['serves']}<br>\n"
                f'                        <strong>Phone:</strong> <a href="tel:{tel(phone)}">{phone}</a><br>\n'
                f'                        <strong>Official site:</strong> <a href="{off}" target="_blank" rel="noopener">{strip_scheme(off)}</a><br>\n'
                f'                        <strong>Apply:</strong> <a href="{app}" target="_blank" rel="noopener">{short} application page</a><br>\n'
                f"                        <strong>Status last checked:</strong> {m['updated']}"),
            "waitlist_status": "Waiting-List Status",
            "waitlist_intro": ("Waiting lists open and close frequently, so treat the status below as a "
                               "starting point and confirm on the official site before you rely on it."),
            "programs_heading": f"Programs {short} Runs",
            "how_to_apply": "How to Apply",
            "apply_body_html": (
                f'Apply directly through the authority\'s official application page: <a href="{app}" target="_blank" rel="noopener">{strip_scheme(app)}</a>. '
                f'If you have already applied, call <a href="tel:{tel(phone)}">{phone}</a> to verify your position and keep your contact '
                "information current — if the authority cannot reach you when your name comes up, you can be dropped from the list."),
            "new_to_process_html": (
                f'New to the process? Our <a href="{apply_guide}">step-by-step guide to applying for Section 8</a> walks through the whole thing, '
                f'and <a href="{find_pha}">how to find your PHA</a> helps you locate the right authority.'),
            "other_authorities": "Other Authorities Serving This Area",
            "more_local_heading": "More Local Resources",
            "faq_heading": "Frequently Asked Questions",
            "sources": "Sources",
        }
        # More Local Resources sentence
        lead = ("For the full picture of affordable housing in this area — emergency shelter, "
                "rental assistance, tenant rights, and legal aid — see ")
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
            "Resumimos información pública para ayudarle a orientarse. Para solicitudes y el estado "
            "más actualizado de la lista de espera, use siempre los enlaces oficiales de abajo."),
        "quick_facts": "Datos rápidos",
        "quick_facts_html": (
            f"<strong>Sirve a:</strong> {m['serves']}<br>\n"
            f'                        <strong>Teléfono:</strong> <a href="tel:{tel(phone)}">{phone}</a><br>\n'
            f'                        <strong>Sitio oficial:</strong> <a href="{off}" target="_blank" rel="noopener">{strip_scheme(off)}</a><br>\n'
            f'                        <strong>Solicitar:</strong> <a href="{app}" target="_blank" rel="noopener">página de solicitud de {short}</a><br>\n'
            f"                        <strong>Estado verificado por última vez:</strong> {m['updated']}"),
        "waitlist_status": "Estado de la lista de espera",
        "waitlist_intro": ("Las listas de espera abren y cierran con frecuencia, así que tome el estado de abajo "
                           "como un punto de partida y confírmelo en el sitio oficial antes de confiar en él."),
        "programs_heading": f"Programas que administra {short}",
        "how_to_apply": "Cómo solicitar",
        "apply_body_html": (
            f'Solicite directamente a través de la página de solicitud oficial de la autoridad: <a href="{app}" target="_blank" rel="noopener">{strip_scheme(app)}</a>. '
            f'Si ya presentó su solicitud, llame al <a href="tel:{tel(phone)}">{phone}</a> para verificar su posición y mantenga su información '
            "de contacto al día — si la autoridad no puede localizarle cuando le toque su turno, pueden retirarle de la lista."),
        "new_to_process_html": (
            f'¿Nuevo en el proceso? Nuestra <a href="{apply_guide}">guía paso a paso para solicitar la Sección 8</a> le explica todo el trámite, '
            f'y <a href="{find_pha}">cómo encontrar su PHA</a> le ayuda a ubicar la autoridad correcta.'),
        "other_authorities": "Otras autoridades que sirven esta zona",
        "more_local_heading": "Más recursos locales",
        "faq_heading": "Preguntas frecuentes",
        "sources": "Fuentes",
    }
    lead = ("Para el panorama completo de la vivienda asequible en esta zona — refugio de emergencia, "
            "asistencia de alquiler, derechos del inquilino y ayuda legal — vea ")
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
