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

Each page renders its data.faqs as a visible FAQ section AND as FAQPage JSON-LD.
The FAQ text is plain text in the JSON; build_faq_items() below escapes it and
turns only the official targets inside an answer into links, and it refuses any
q/a that carries markup, an HTML entity, an unverified domain or an aggregator.

Safeguard: Spanish (es) pages are validated for missing diacritics before they
are written. If an es page contains a red-flag un-accented Spanish word in its
visible text, generation raises an error so plain-ASCII Spanish can never ship.
The two false positives that scripts/check_spanish.py documents in its own
docstring are exempted narrowly here -- see ES_FALSE_POSITIVES below.
"""
import argparse
import glob
import html
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
            "faq_heading": "Frequently Asked Questions",
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
            "faq_heading": "Preguntas frecuentes",
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
            "faq_heading": "Frequently Asked Questions",
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
            "faq_heading": "Preguntas frecuentes",
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


# ---------------------------------------------------------------------------
# Visible FAQ section (S-FAQ, 2026-09-11).
#
# data.faqs[].q and data.faqs[].a are PLAIN TEXT. The same raw strings go into
# the FAQPage JSON-LD (build_faq_json above), and build_faq_items() derives the
# visible <h3>/<p> copy from them: every text segment is HTML-escaped, and only
# the official targets named inside an answer become links --
#   * bare or www. domains, optional path  -> https link, new tab
#   * US phone numbers, vanity letters too -> tel:+1XXXXXXXXXX (211/311/911 never)
#   * email addresses                      -> mailto:
# so the visible copy and the schema copy cannot drift apart.
#
# It REFUSES (raises) rather than render something wrong:
#   * a q or a containing "<" or ">": FAQ copy is not markup;
#   * a q or a containing an HTML entity (&rsquo;, &amp;, ...): write the character;
#   * a domain missing from FAQ_LINK_TARGETS: fetch it, then record the verdict;
#   * a domain belonging to an aggregator (FAQ_AGGREGATORS), whatever the table says.
# ---------------------------------------------------------------------------

# Every domain token that appears in a FAQ answer, with the href it gets, as
# verified by fetching it on 2026-09-11 (S-FAQ). Keys are the token as written,
# host lower-cased. None = checked and dead (404 / no DNS / broken TLS), so the
# text stays plain until someone fixes the answer. A new domain in any answer
# makes the generator raise until it has been fetched and added here.
FAQ_LINK_TARGETS = {
    "211info.org": "https://211info.org",
    "abqha.org/wait-list": "https://abqha.org/wait-list",
    "applicant.atlantahousing.org": "https://applicant.atlantahousing.org",
    "applyonline.thecha.org": "https://applyonline.thecha.org",
    "boston.myhousing.com": "https://boston.myhousing.com",
    "bostonhousing.org": "https://bostonhousing.org",
    "caaofokc.org": "https://caaofokc.org",
    "cabq.gov/help/rental-assistance": "https://cabq.gov/help/rental-assistance",
    "ccrd.colorado.gov": "https://ccrd.colorado.gov",
    "chicago.gov": "https://chicago.gov",
    "chnhousingpartners.org": "https://chnhousingpartners.org",
    "cmha.net": "https://cmha.net",
    "connect.homeforward.org": "https://connect.homeforward.org",
    "denverhousing.org": "https://denverhousing.org",
    "dhantx.com/applicants": "https://dhantx.com/applicants",
    "doh.colorado.gov/emergency-rental-assistance": "https://doh.colorado.gov/emergency-rental-assistance",
    "encapnebraska.org": "https://encapnebraska.org",
    "erap.dhs.dc.gov": "https://erap.dhs.dc.gov",
    "freeevictionhelp.org": "https://freeevictionhelp.org",
    "fwhs.org": "https://fwhs.org",
    "habc.org": "https://habc.org",
    "hacm.org/programs/housing/apply-for-housing": "https://hacm.org/programs/housing/apply-for-housing",
    "hakc.org": "https://hakc.org",
    "hakc.org/apply-online": "https://hakc.org/apply-online",
    "hatctx.com": "https://hatctx.com",
    "homesa.org": "https://homesa.org",
    "housing.sfgov.org": "https://housing.sfgov.org",
    "housinglink.org": "https://housinglink.org",
    "indyhousing.org": "https://indyhousing.org",
    "jacksonvilleevictiondiversion.org": "https://jacksonvilleevictiondiversion.org",
    "kcba.org": "https://kcba.org",
    "kcmo.gov/city-hall/housing/tenant-resources/assistance-providers-for-tenants": "https://kcmo.gov/city-hall/housing/tenant-resources/assistance-providers-for-tenants",
    "kshousingcorp.org": "https://kshousingcorp.org",
    "las.org": "https://las.org",
    "law.lis.virginia.gov": "https://law.lis.virginia.gov",
    "lawmo.org": "https://lawmo.org",
    "legalaiddc.org": "https://legalaiddc.org",
    "longbeach.gov/haclb/apply": "https://longbeach.gov/haclb/apply",
    "mainehousing.org": "https://mainehousing.org",
    "mass.gov": "https://mass.gov",
    "mass.gov/mcad": "https://mass.gov/mcad",
    "mccr.maryland.gov": "https://mccr.maryland.gov",
    "mdlab.org": "https://mdlab.org",
    "mesaaz.gov/residents/housing": "https://mesaaz.gov/residents/housing",
    "mifa.org/applyonline": "https://mifa.org/applyonline",
    "mn.gov/mdhr": "https://mn.gov/mdhr",  # bot-blocked to scripts, live for people
    "nashville-mdha.org": "https://nashville-mdha.org",
    "oakha.org": "https://oakha.org",
    "ohauthority.org": "https://ohauthority.org",
    "phxhousing.myhousing.com": "https://phxhousing.myhousing.com",
    "planninghcd.cityofomaha.org/for-renters": "https://planninghcd.cityofomaha.org/for-renters",  # bot-blocked to scripts, live for people
    "publichousingapplication.ocd.state.ma.us": "https://publichousingapplication.ocd.state.ma.us",
    "rent-assist.phila.gov": "https://rent-assist.phila.gov",
    "rentful614.com": "https://rentful614.com",
    "rhanc.gov": "https://rhanc.gov",
    "rihousing.com": "https://rihousing.com",
    "sacwaitlist.com": "https://sacwaitlist.com",
    "scchousingauthority.org": "https://scchousingauthority.org",
    "seattlehousing.org": "https://www.seattlehousing.org",  # apex fails TLS (hostname mismatch); www. works
    "sfrb.org": "https://sfrb.org",
    "shelbycountycsa.org": "https://shelbycountycsa.org",
    "shra.org": "https://shra.org",
    "slha.org": "https://slha.org",
    "snvrha.org": "https://snvrha.org",
    "stayhousedla.org": "https://stayhousedla.org",
    "stopmyeviction.org": "https://stopmyeviction.org",
    "waitlistcheck.com": "https://waitlistcheck.com",
    "wichita.gov": "https://wichita.gov",
    "wichita.myhousing.com": "https://wichita.myhousing.com",
    "www.sacwaitlist.com": "https://www.sacwaitlist.com",
    "www.waitlistcheck.com": "https://www.waitlistcheck.com",
    "yourlegalaid.org": "https://yourlegalaid.org",
    "cmhanet.com/HCV/ProspectiveResidents": None,  # 404
    "longbeach.gov/homelessness/RenterAid": None,  # 404
    "mass.gov/raft": None,  # 404
    "metroareacontinuumofcare.org": None,  # DNS failure
    "needlinknashville.org": None,  # DNS failure
    "rent-help.kingcounty.gov": None,  # TLS certificate EXPIRED
    "stlouis-mo.gov/help-stl/request-help-stl": None,  # 404
    "teamkyhherf.ky.gov": None,  # DNS failure
    "trla.org/applyforhelp": None,  # 404 status
    "waitlistcentralri.com": None,  # TLS fails on apex and www.
}

# Never linked, never cited: listing sites that republish PHA data.
FAQ_AGGREGATORS = ("affordablehousingonline.com", "section8waitlist.org", "publichousing.com",
                   "lowincomehousing.us", "gosection8.com")

FAQ_EMAIL_RE = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
FAQ_DOMAIN_RE = re.compile(
    r"(?<![A-Za-z0-9@._%+/-])"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+(?:gov|org|com|net|us|edu|info)"
    r"(?![A-Za-z0-9-])"
    r"(?:/[A-Za-z0-9/_.~%?=&#+-]*)?")
FAQ_PHONE_RE = re.compile(
    r"(?<![A-Za-z0-9-])"
    r"(?:1-)?(?:\(\d{3}\) \d{3}-|\d{3}-\d{3}-|\d{3}\.\d{3}\.)(?:\d{4}|[A-Z]{4})"
    r"(?![A-Za-z0-9])")
FAQ_TRAILING = '.,;)"'   # sentence punctuation after a domain is not part of it
FAQ_ENTITY_RE = re.compile(r"&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")
KEYPAD = {c: d for d, letters in (("2", "ABC"), ("3", "DEF"), ("4", "GHI"), ("5", "JKL"),
                                   ("6", "MNO"), ("7", "PQRS"), ("8", "TUV"), ("9", "WXYZ"))
          for c in letters}


def _faq_host(token):
    return token.split("/", 1)[0].lower()


def _faq_is_aggregator(host):
    host = host[4:] if host.startswith("www.") else host
    return any(host == a or host.endswith("." + a) for a in FAQ_AGGREGATORS)


assert all(v is None or v.startswith("https://") for v in FAQ_LINK_TARGETS.values())
assert not any(_faq_is_aggregator(_faq_host(k)) or (v and _faq_is_aggregator(_faq_host(v[8:])))
               for k, v in FAQ_LINK_TARGETS.items())


def faq_tel(token):
    """'(216) 391-HELP' -> 'tel:+12163914357' (letters map to the phone keypad)."""
    body = token[2:] if token.startswith("1-") else token
    digits = "".join(KEYPAD.get(ch, ch) for ch in body if ch.isalnum())
    if len(digits) != 10 or not digits.isdigit():
        raise ValueError(f"not a 10-digit US phone number: {token!r}")
    return "tel:+1" + digits


def faq_tokens(text):
    """The link tokens inside one answer: [(kind, start, end, token)], in order.
    kind is 'email', 'url' or 'tel'. Emails win over the domain inside them."""
    spans = []

    def free(s, e):
        return all(e <= a or s >= b for _k, a, b, _t in spans)

    for m in FAQ_EMAIL_RE.finditer(text):
        spans.append(("email", m.start(), m.end(), m.group(0)))
    for m in FAQ_DOMAIN_RE.finditer(text):
        tok = m.group(0)
        while tok and tok[-1] in FAQ_TRAILING:
            tok = tok[:-1]
        if free(m.start(), m.start() + len(tok)):
            spans.append(("url", m.start(), m.start() + len(tok), tok))
    for m in FAQ_PHONE_RE.finditer(text):
        if free(m.start(), m.end()):
            spans.append(("tel", m.start(), m.end(), m.group(0)))
    return sorted(spans, key=lambda s: s[1])


def faq_plain_text(where, s):
    """Raise unless s is plain text: no tags, no HTML entities."""
    if "<" in s or ">" in s:
        raise ValueError(f"FAQ {where} must be plain text but contains '<' or '>': {s[:90]!r}")
    for m in FAQ_ENTITY_RE.finditer(s):
        if html.unescape(m.group(0)) != m.group(0):
            raise ValueError(f"FAQ {where} must be plain text but contains the HTML entity "
                             f"{m.group(0)} -- write the character itself")


def faq_anchor(kind, token):
    """HTML for one link token; a verified-dead domain comes back as plain text."""
    text = html.escape(token, quote=False)
    if kind == "email":
        return f'<a href="mailto:{html.escape(token)}">{text}</a>'
    if kind == "tel":
        return f'<a href="{faq_tel(token)}">{text}</a>'
    host = _faq_host(token)
    if _faq_is_aggregator(host):
        raise ValueError(f"FAQ answer links an aggregator ({host}) -- cite the authority's own site")
    key = host + token[len(host):]
    if key not in FAQ_LINK_TARGETS:
        raise ValueError(f"FAQ link target {key!r} has not been verified -- fetch it, then add it "
                         f"to FAQ_LINK_TARGETS in scripts/generate_page.py (None if it is dead)")
    href = FAQ_LINK_TARGETS[key]
    if href is None:
        return text
    return f'<a href="{html.escape(href)}" target="_blank" rel="noopener">{text}</a>'


def build_faq_items(faqs, lang="en"):
    """Visible FAQ copy: [{'q': html, 'a': html}] in JSON order. The question is
    escaped text; the answer is escaped text with its link tokens as anchors."""
    items = []
    for n, f in enumerate(faqs):
        q, a = f["q"], f["a"]
        faq_plain_text(f"{lang}.faqs[{n}].q", q)
        faq_plain_text(f"{lang}.faqs[{n}].a", a)
        out, pos = [], 0
        for kind, s, e, tok in faq_tokens(a):
            out.append(html.escape(a[pos:s], quote=False))
            out.append(faq_anchor(kind, tok))
            pos = e
        out.append(html.escape(a[pos:], quote=False))
        items.append({"q": html.escape(q, quote=False), "a": "".join(out)})
    return items


def render_one(env, kind, lang, slug, data, layout):
    """Render one language's page for one location."""
    canonical_path = layout["canonical_path"].format(slug=slug)
    alt_lang_path = layout["alt_lang_path"].format(slug=slug)
    output_path = REPO_ROOT / layout["output_path"].format(slug=slug)

    breadcrumb_json = build_breadcrumb_json(layout, data, lang)
    faq_json = build_faq_json(data.get("faqs", [])) if data.get("faqs") else ""
    faq_items = build_faq_items(data.get("faqs") or [], lang)

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
        faq_items=faq_items,
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
