"""Generate the reader-question pages and their hub (EN + ES) from data/questions/*.json.

Writes
    resources/questions/<slug>.html                 one answer page per question (English)
    es/recursos/preguntas/<es_slug>.html            its Spanish twin
    resources/questions/index.html                  hub: every question, grouped by topic
    es/recursos/preguntas/index.html                Spanish hub

These answer questions people sent through the site's Ask form (resources/ask.html),
rewritten so nobody can be identified: no names, ages, dates of birth, small towns,
amounts or family details that could point to one person. The original messages never
enter this repo.

JSON shape (one file per question, named <slug>.json):
    {
      "slug": "voucher-expired-waiting-on-inspection",       EN url slug
      "es_slug": "cupon-vencio-esperando-inspeccion",        ES url slug
      "topic": "voucher",                                    key of TOPICS below
      "order": 10,                                           sort order inside the topic
      "related": ["other-slug", ...],                        other question slugs (EN)
      "en": {
        "question":     the anonymized question, as the reader would put it (plain text)
        "title":        <title> WITHOUT " | Waythrough"; with the suffix it must be <= 60
        "description":  meta description, 120-158 characters
        "h1":           the page heading, a plain-language question
        "crumb":        short breadcrumb label (2-4 words)
        "asked":        "July 2026" (month only)
        "updated":      "November 4, 2026"
        "short_answer": 1-3 sentences, plain text
        "body_html":    the answer: <h2>/<h3>/<p>/<ul>/<ol>, 16-space indent not required
        "links":        [{"href": "/resources/guides/x", "label": "...", "note": "..."}]
        "sources":      [{"url": "https://...", "label": "..."}]   primary sources only
      },
      "es": { same keys, in Spanish }
    }

Links: write site paths starting with "/" ("/resources/guides/x", "/es/recursos/guias/y");
they are rewritten to relative links for the page's depth, the way every other page links.

Guards (generation raises): title over 60 with the suffix, description outside 120-158,
a missing key, a related slug that doesn't exist, or a Spanish page with a red-flag
un-accented word (same list and exemptions as generate_authority.py).
"""
import html
import json
import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_authority import es_accent_violations  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "questions"
TEMPLATES = ROOT / "templates"
SITE = "https://waythroughproject.com"
SUFFIX = " | Waythrough"
TITLE_MAX, DESC_MIN, DESC_MAX = 60, 120, 158

OUT = {"en": ROOT / "resources" / "questions", "es": ROOT / "es" / "recursos" / "preguntas"}
URL_DIR = {"en": "/resources/questions/", "es": "/es/recursos/preguntas/"}
KEYS = ("question", "title", "description", "h1", "crumb", "asked", "updated",
        "short_answer", "body_html", "links", "sources")

# Hub order. Labels are the hub's section headings.
TOPICS = [
    ("voucher", "Keeping and using your voucher", "Cómo conservar y usar su cupón"),
    ("applying", "Applying, waitlists and denials", "Solicitudes, listas de espera y rechazos"),
    ("rent", "Rent, income and charges", "Renta, ingresos y cobros"),
    ("repairs", "Repairs and unsafe conditions", "Reparaciones y condiciones inseguras"),
    ("lockouts", "Lockouts, evictions and records", "Cierres, desalojos y antecedentes"),
    ("finding", "Finding a place and moving in", "Cómo encontrar vivienda y mudarse"),
    ("crisis", "Homelessness, safety and emergencies", "Sin hogar, seguridad y emergencias"),
]

T = {
    "en": {
        "home": "Home", "resources": "Resources", "hub_crumb": "Reader Questions",
        "section_label": "Reader Question",
        "question_heading": "The question",
        "privacy_note": "Sent through our Ask a Question form. We removed names, places and other details so no one can be identified.",
        "short_answer": "The short answer",
        "not_legal_advice_html": "<strong>This is general information, not legal advice.</strong> Rules differ by state and by housing authority. For your own situation, talk to your housing authority, a <a href=\"{legal}\">free legal aid office</a>, or call 211.",
        "guides_heading": "Our longer guides on this",
        "related_heading": "Other readers asked",
        "sources": "Sources",
        "ask_cta_html": "Have a question we haven't answered? <a href=\"{ask}\">Ask us</a>, or browse <a href=\"{hub}\">all reader questions</a>.",
        "hub_label": "Community",
        "hub_h1": "Questions Readers Asked Us, Answered",
        "hub_meta": "Updated {updated}",
        "hub_title": "Section 8 & Tenant Questions Readers Asked",
        "hub_description": "Real Section 8, voucher and tenant questions sent to Waythrough, with plain answers: expired vouchers, lockouts, repairs, rent errors and moving.",
        "hub_intro_html": "These are real questions people sent us through our <a href=\"{ask}\">Ask a Question</a> form. We rewrote each one so no one can be identified, then answered it in plain language with links to the rules and to our guides. For general questions, see our <a href=\"{community}\">community answers</a> and <a href=\"{faq}\">FAQ</a>.",
        "hub_urgent_html": "<strong>Need help today?</strong> Call or text 211 for shelter and emergency help. If you are in danger, call 911 or the National Domestic Violence Hotline at 1-800-799-7233.",
        "page_meta": "Asked {asked} · Answered by Matt · Updated {updated}",
    },
    "es": {
        "home": "Inicio", "resources": "Recursos", "hub_crumb": "Preguntas de lectores",
        "section_label": "Pregunta de un lector",
        "question_heading": "La pregunta",
        "privacy_note": "Enviada por nuestro formulario de preguntas. Quitamos nombres, lugares y otros detalles para que nadie pueda ser identificado.",
        "short_answer": "La respuesta corta",
        "not_legal_advice_html": "<strong>Esto es información general, no asesoría legal.</strong> Las reglas cambian según el estado y la autoridad de vivienda. Para su caso, hable con su autoridad de vivienda, con una <a href=\"{legal}\">oficina de ayuda legal gratuita</a> o llame al 211.",
        "guides_heading": "Nuestras guías más completas sobre el tema",
        "related_heading": "Otros lectores preguntaron",
        "sources": "Fuentes",
        "ask_cta_html": "¿Tiene una pregunta que no hemos contestado? <a href=\"{ask}\">Pregúntenos</a> o vea <a href=\"{hub}\">todas las preguntas de lectores</a>.",
        "hub_label": "Comunidad",
        "hub_h1": "Preguntas que nos hicieron los lectores, con respuesta",
        "hub_meta": "Actualizado el {updated}",
        "hub_title": "Preguntas de lectores sobre Sección 8 y renta",
        "hub_description": "Preguntas reales sobre Sección 8, cupones y derechos del inquilino enviadas a Waythrough, con respuestas claras: cupones vencidos, desalojos y reparaciones.",
        "hub_intro_html": "Estas son preguntas reales que la gente nos envió por nuestro <a href=\"{ask}\">formulario de preguntas</a>. Reescribimos cada una para que nadie pueda ser identificado y la contestamos en lenguaje sencillo, con enlaces a las reglas y a nuestras guías. Para preguntas generales, vea nuestras <a href=\"{community}\">respuestas de la comunidad</a> y las <a href=\"{faq}\">preguntas frecuentes</a>.",
        "hub_urgent_html": "<strong>¿Necesita ayuda hoy?</strong> Llame o envíe un mensaje de texto al 211 para refugio y ayuda de emergencia. Si está en peligro, llame al 911 o a la Línea Nacional contra la Violencia Doméstica al 1-800-799-7233.",
        "page_meta": "Pregunta de {asked} · Respondida por Matt · Actualizado el {updated}",
    },
}

PATHS = {
    # All four page kinds sit two (EN) or three (ES) levels below the site root.
    "en": {"rel": "../../", "home": "../../", "resources": "../", "ask": "../ask",
           "community": "../community-answers", "faq": "../faq",
           "legal": "../guides/free-legal-help-for-tenants"},
    "es": {"rel": "../../../", "home": "../../", "resources": "../", "ask": "../preguntar",
           "community": "../respuestas-de-la-comunidad", "faq": "../preguntas-frecuentes",
           "legal": "../guias/ayuda-legal-gratuita-inquilinos"},
}


def site_links(s, rel):
    """href="/x" -> href="<rel>x" (relative, like the rest of the site)."""
    return re.sub(r'href="/(?!/)', 'href="' + rel, s)


def load():
    qs = {}
    for f in sorted(DATA_DIR.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if f.stem != d["slug"]:
            raise ValueError(f"{f.name}: file name must be <slug>.json ({d['slug']})")
        if d["topic"] not in {k for k, _, _ in TOPICS}:
            raise ValueError(f"{d['slug']}: unknown topic {d['topic']!r}")
        for lang in ("en", "es"):
            missing = [k for k in KEYS if k not in d.get(lang, {})]
            if missing:
                raise ValueError(f"{d['slug']} ({lang}): missing {missing}")
            title = d[lang]["title"] + SUFFIX
            if len(title) > TITLE_MAX:
                raise ValueError(f"{d['slug']} ({lang}): title is {len(title)} chars with the suffix, max {TITLE_MAX}")
            n = len(d[lang]["description"])
            if not DESC_MIN <= n <= DESC_MAX:
                raise ValueError(f"{d['slug']} ({lang}): description is {n} chars, want {DESC_MIN}-{DESC_MAX}")
        qs[d["slug"]] = d
    for d in qs.values():
        for r in d.get("related", []):
            if r not in qs:
                raise ValueError(f"{d['slug']}: related slug {r!r} does not exist")
    return qs


def page_slug(d, lang):
    return d["slug"] if lang == "en" else d["es_slug"]


def breadcrumb(lang, name=None, url=None):
    t = T[lang]
    base = SITE + ("/" if lang == "en" else "/es/")
    res = SITE + ("/resources/" if lang == "en" else "/es/recursos/")
    items = [{"@type": "ListItem", "position": 1, "name": t["home"], "item": base},
             {"@type": "ListItem", "position": 2, "name": t["resources"], "item": res}]
    if name:
        items.append({"@type": "ListItem", "position": 3, "name": t["hub_crumb"], "item": SITE + URL_DIR[lang]})
        items.append({"@type": "ListItem", "position": 4, "name": name})
    else:
        items.append({"@type": "ListItem", "position": 3, "name": t["hub_crumb"]})
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                       "itemListElement": items}, indent=2, ensure_ascii=False)


def article(d, lang, url):
    m = d[lang]
    return json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": m["h1"], "description": m["description"], "inLanguage": lang,
        "mainEntityOfPage": url,
        "author": {"@type": "Person", "name": "Matt", "url": SITE + "/author"},
        "publisher": {"@type": "Organization", "name": "Waythrough Project", "url": SITE + "/"},
    }, indent=2, ensure_ascii=False)


def strings(lang, p, **fmt):
    t = dict(T[lang])
    links = dict(ask=p["ask"], hub="./", community=p["community"], faq=p["faq"], legal=p["legal"])
    for k in ("not_legal_advice_html", "ask_cta_html", "hub_intro_html"):
        t[k] = t[k].format(**links)
    fmt = dict({"asked": "", "updated": ""}, **fmt)
    for k in ("page_meta", "hub_meta"):
        t[k] = t[k].format(**fmt)
    return t


def write(dest, page, lang, slug):
    if lang == "es":
        bad = es_accent_violations(page)
        if bad:
            raise ValueError(f"Spanish accent check FAILED for {slug} (es): {bad}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    return dest


def render_all():
    qs = load()
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
    tmpl = env.get_template("question.html.j2")
    written = []
    for lang in ("en", "es"):
        p = PATHS[lang]
        other = "es" if lang == "en" else "en"
        for d in qs.values():
            m = dict(d[lang])
            slug = page_slug(d, lang)
            url = SITE + URL_DIR[lang] + slug
            m["body_html"] = site_links(m["body_html"], p["rel"])
            m["links"] = [dict(l, href=site_links('href="%s"' % l["href"], p["rel"])[6:-1]) for l in m["links"]]
            m["related"] = [{"href": page_slug(qs[r], lang), "h1": qs[r][lang]["h1"]} for r in d.get("related", [])]
            page = tmpl.render(
                page_kind="question", lang=lang, q=m,
                t=strings(lang, p, asked=m["asked"], updated=m["updated"]),
                title=html.escape(m["title"] + SUFFIX, quote=True),
                description=html.escape(m["description"], quote=True),
                canonical_path=URL_DIR[lang] + slug,
                alt_en_url=SITE + URL_DIR["en"] + d["slug"],
                alt_es_url=SITE + URL_DIR["es"] + d["es_slug"],
                rel_prefix=p["rel"], home_href=p["home"], resources_href=p["resources"], hub_href="./",
                breadcrumb_json=breadcrumb(lang, m["crumb"]), article_json=article(d, lang, url),
            )
            written.append(write(OUT[lang] / f"{slug}.html", page, lang, slug))
        # Hub
        groups = []
        for key, en_label, es_label in TOPICS:
            items = sorted((d for d in qs.values() if d["topic"] == key), key=lambda d: (d.get("order", 0), d["slug"]))
            if items:
                groups.append({"label": en_label if lang == "en" else es_label,
                               "entries": [{"href": page_slug(d, lang), "h1": d[lang]["h1"],
                                          "short_answer": d[lang]["short_answer"]} for d in items]})
        newest = max((d[lang]["updated"] for d in qs.values()), key=_date_key(lang))
        t = strings(lang, p, updated=newest)
        page = tmpl.render(
            page_kind="hub", lang=lang, groups=groups, t=t,
            title=html.escape(t["hub_title"] + SUFFIX, quote=True),
            description=html.escape(t["hub_description"], quote=True),
            canonical_path=URL_DIR[lang],
            alt_en_url=SITE + URL_DIR["en"], alt_es_url=SITE + URL_DIR["es"],
            rel_prefix=p["rel"], home_href=p["home"], resources_href=p["resources"], hub_href="./",
            breadcrumb_json=breadcrumb(lang), article_json=None,
        )
        written.append(write(OUT[lang] / "index.html", page, lang, "index"))
    for k in ("hub_title",):
        for lang in ("en", "es"):
            if len(T[lang][k] + SUFFIX) > TITLE_MAX:
                raise ValueError(f"hub title ({lang}) over {TITLE_MAX}")
    return written


EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
             "September", "October", "November", "December"]
ES_MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
             "septiembre", "octubre", "noviembre", "diciembre"]


def _date_key(lang):
    def key(s):
        if lang == "en":
            m = re.match(r"(\w+) (\d+), (\d{4})", s)
            return (int(m.group(3)), EN_MONTHS.index(m.group(1)), int(m.group(2)))
        m = re.match(r"(\d+) de (\w+) de (\d{4})", s)
        return (int(m.group(3)), ES_MONTHS.index(m.group(2)), int(m.group(1)))
    return key


if __name__ == "__main__":
    for w in render_all():
        print("wrote", w)
