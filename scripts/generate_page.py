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
#   * US phone numbers, vanity letters too -> tel:+1XXXXXXXXXX (211/311/911 never
#     here; link_phones() below adds tel:211 for "call 211" / "2-1-1" afterwards)
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
    "211info.org": "https://www.211info.org",
    "abqha.org/how-to-apply": "https://abqha.org/how-to-apply/",  # fetched live 2026-10-15 (AUTH5) in a browser; scripted fetches get a SiteGround bot check
    "abqha.org/wait-list": "https://abqha.org/wait-list",
    "applicant.atlantahousing.org": "https://applicant.atlantahousing.org",
    "applyonline.thecha.org": "https://applyonline.thecha.org",
    "boston.myhousing.com": "https://boston.myhousing.com",
    "bostonhousing.org": "https://bostonhousing.org",
    "caaofokc.org": "https://www.caaofokc.org",
    "cabq.gov/help/rental-assistance": "https://www.cabq.gov/help/rental-assistance",
    "ccrd.colorado.gov": "https://ccrd.colorado.gov",
    "chicago.gov": "https://chicago.gov",
    "chnhousingpartners.org": "https://chnhousingpartners.org",
    "cmha.net": "https://cmha.net",
    "cmhanet.com/apply-housing-waitlist": "https://www.cmhanet.com/apply-housing-waitlist",  # fetched live 2026-09-21 (W-2/3 + X2); replaces cmhanet.com/HCV/ProspectiveResidents
    "connect.homeforward.org": "https://connect.homeforward.org",
    "denverhousing.org": "https://denverhousing.org",
    "dhantx.com/applicants": "https://dhantx.com/applicants",
    "doh.colorado.gov/emergency-rental-assistance": "https://doh.colorado.gov/emergency-rental-assistance",
    "encapnebraska.org": "https://www.encapnebraska.org",
    "erap.dhs.dc.gov": "https://erap.dhs.dc.gov",
    "freeevictionhelp.org": "https://freeevictionhelp.org",
    "fwhs.org": "https://fwhs.org",
    "hano.myhousing.com": "https://hano.myhousing.com",  # fetched live 2026-11-05 (New Orleans set); HANO's applicant portal, says no lists are open
    "habc.org": "https://www.habc.org",
    "hacla.org": "https://www.hacla.org",  # fetched live 2026-10-15 (SEO2); Section 8 page says the list is closed
    "hacm.org/programs/housing/apply-for-housing": "https://hacm.org/programs/housing/apply-for-housing",
    "hacm.org/subsidized": "https://www.hacm.org/subsidized",  # fetched live 2026-10-15 (SEO2); HACM's short link to its open waiting lists page; bot-blocked to scripts, live for people
    "hakc.org": "https://www.hakc.org",
    "cvlas.org": "https://cvlas.org/get-help/",  # fetched live 2026-11-05 (Richmond pages); Central Virginia Legal Aid Society intake page
    "haslcutah.org": "https://haslcutah.org",  # fetched live 2026-11-05 (Salt Lake City pages); haslc.com now redirects to an unrelated St. Louis County site
    "housingconnect.org": "https://housingconnect.org",  # fetched live 2026-11-05 (Salt Lake City pages); Housing Connect, Salt Lake County
    "rrha.com": "https://www.rrha.com",  # fetched live 2026-11-05 (Richmond pages); Richmond Redevelopment and Housing Authority
    "utahca.org": "https://utahca.org/case-management-housing/",  # fetched live 2026-11-05 (Salt Lake City pages); Utah Community Action rent and deposit help
    "hakc.org/apply-online": "https://www.hakc.org/apply-online",
    "hatctx.com": "https://hatctx.com",
    "homesa.org": "https://homesa.org",
    "housing.lacity.gov": "https://housing.lacity.gov",  # fetched live 2026-10-15 (SEO2); LAHD, the City of LA housing department
    "housing.sfgov.org": "https://housing.sfgov.org",
    "housinglink.org": "https://www.housinglink.org",
    "indyhousing.org": "https://www.indyhousing.org",
    "jacksonvilleevictiondiversion.org": "https://jacksonvilleevictiondiversion.org",
    "kcba.org": "https://www.kcba.org",
    "kcmo.gov/city-hall/housing/tenant-resources/assistance-providers-for-tenants": "https://kcmo.gov/city-hall/housing/tenant-resources/assistance-providers-for-tenants",
    "keeppeoplehoused.org": "https://keeppeoplehoused.org",  # fetched live 2026-11-05 (Bay Area guides); BACS Keep People Housed portal, City of Oakland application
    "kshousingcorp.org": "https://kshousingcorp.org",
    "lacounty.gov/prevention": "https://lacounty.gov/prevention/",  # fetched live 2026-10-15 (SEO2); LA County's prevention program list
    "lafairhousing.org": "https://lafairhousing.org",  # fetched live 2026-11-05 (New Orleans set); Louisiana Fair Housing Action Center, eviction defense in Orleans Parish
    "las.org": "https://las.org",
    "law.lis.virginia.gov": "https://law.lis.virginia.gov",
    "lawmo.org": "https://lawmo.org",
    "legalaccessforall.org": "https://www.legalaccessforall.org",  # fetched live 2026-11-05 (Orlando set); Community Legal Services (clsmf.org now redirects here)
    "legalaiddc.org": "https://www.legalaiddc.org",
    "legalhelpmd.org": "https://legalhelpmd.org",  # fetched live 2026-11-03 (Baltimore guide); Maryland Access to Counsel in Evictions intake site
    "longbeach.gov/haclb/apply": "https://longbeach.gov/haclb/apply",
    "longbeach.gov/renteraid": "https://www.longbeach.gov/homelessness/homeless-services/RenterAid/",  # fetched live 2026-09-21 (W-2/3 + X2); the City's own short link, redirects here
    "mainehousing.org": "https://mainehousing.org",
    "mass.gov": "https://mass.gov",
    "mass.gov/mcad": "https://mass.gov/mcad",
    "mass.gov/raft": "https://www.mass.gov/how-to/apply-for-raft-emergency-help-for-housing-costs",  # fetched live 2026-09-21 (W-2/3 + X2): resolves again (redirects to the RAFT how-to page); was None on 2026-09-11
    "mccr.maryland.gov": "https://mccr.maryland.gov",
    "mdlab.org": "https://www.mdlab.org",
    "mesaaz.gov/residents/housing": "https://mesaaz.gov/residents/housing",
    "mifa.org/applyonline": "https://www.mifa.org/applyonline",
    "mn.gov/mdhr": "https://mn.gov/mdhr",  # bot-blocked to scripts, live for people
    "myportal.hacm.org": "https://myportal.hacm.org",  # fetched live 2026-10-15 (SEO2); HACM's RentCafe applicant portal; bot-blocked to scripts, live for people
    "nashville-mdha.org": "https://www.nashville-mdha.org",
    "needlink.org": "https://needlink.org",  # NeedLink Nashville's current site (needlinknashville.org is dead); fetched live 2026-09-11 (NASH)
    "oakha.org": "https://www.oakha.org",
    "oha.myhousing.com": "https://oha.myhousing.com",  # fetched live 2026-11-05 (Orlando set); Orlando Housing Authority's MyHousing portal
    "ohauthority.org": "https://ohauthority.org",
    "phxhousing.myhousing.com": "https://phxhousing.myhousing.com",
    "planninghcd.cityofomaha.org/for-renters": "https://planninghcd.cityofomaha.org/for-renters",  # bot-blocked to scripts, live for people
    "portal.mphaonline.org": "https://portal.mphaonline.org/",  # fetched live 2026-11-03 (AUTH7) in a browser: MPHA's RentCafe applicant portal; scripted fetches get 403
    "publichousingapplication.ocd.state.ma.us": "https://publichousingapplication.ocd.state.ma.us",
    "rent-assist.phila.gov": "https://rent-assist.phila.gov",
    "rentful614.com": "https://www.rentful614.com",
    "rhanc.gov": "https://rhanc.gov",
    "rihousing.com": "https://www.rihousing.com",
    "rooftopnashville.org": "https://www.rooftopnashville.org",  # fetched live 2026-09-11 (NASH); apex redirects to www.
    "sacwaitlist.com": "https://sacwaitlist.com",
    "sahelp.org": "https://sahelp.org",  # The Salvation Army's request system; fetched live 2026-09-11 (NASH)
    "scchousingauthority.org": "https://www.scchousingauthority.org",
    "seattlehousing.org": "https://www.seattlehousing.org",  # apex fails TLS (hostname mismatch); www. works
    "sfrb.org": "https://sfrb.org",
    "shelbycountycsa.org": "https://shelbycountycsa.org",
    "shra.org": "https://www.shra.org",
    "slha.org": "https://www.slha.org",
    "slls.org": "https://slls.org",  # fetched live 2026-11-05 (New Orleans set); Southeast Louisiana Legal Services
    "snvrha.org": "https://www.snvrha.org",
    "stayhousedla.org": "https://www.stayhousedla.org",
    "stlouis-mo.gov/government/departments/human-services/help-stl/request-help-stl.cfm": "https://www.stlouis-mo.gov/government/departments/human-services/help-stl/request-help-stl.cfm",  # fetched live 2026-09-21 (W-2/3 + X2)
    "stopmyeviction.org": "https://www.stopmyeviction.org",
    "thresholdcoc.org/resources": "https://www.thresholdcoc.org/resources",  # fetched live 2026-09-21 (W-2/3 + X2); MACCH renamed itself Threshold CoC
    "trla.org/atc": "https://www.trla.org/atc",  # fetched live 2026-09-21 (W-2/3 + X2); Austin Tenants Council, a TRLA project
    "trla.org/offices": "https://www.trla.org/offices",  # fetched live 2026-09-21 (W-2/3 + X2); TRLA's phone intake lines
    "uwkc.org/renthelp": "https://www.uwkc.org/renthelp/",  # fetched live 2026-09-21 (W-2/3 + X2); Keep King County Housed applications
    "waitlistcheck.com": "https://www.waitlistcheck.com",
    "wichita.gov": "https://www.wichita.gov",
    "wichita.myhousing.com": "https://wichita.myhousing.com",
    "www.sacwaitlist.com": "https://www.sacwaitlist.com",
    "www.waitlist-centralri.com": "https://www.waitlist-centralri.com",  # fetched live 2026-09-21 (W-2/3 + X2); RIHousing's portal (the apex does not connect)
    "www.waitlistcheck.com": "https://www.waitlistcheck.com",
    "yourlegalaid.org": "https://yourlegalaid.org",
    "cmhanet.com/HCV/ProspectiveResidents": None,  # 404
    "longbeach.gov/homelessness/RenterAid": None,  # 404
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


def phone_digits(area, exchange, line):
    """The 10 dialable digits of a US number; keypad letters become digits
    ('414', '895', 'RENT' -> '4148957368'). A longer vanity tail is cut at 10."""
    return "".join(KEYPAD.get(ch, ch) for ch in area + exchange + line)[:10]


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


# ---------------------------------------------------------------------------
# Tap-to-call in the rendered page (mobile audit 2026-11, item 2).
#
# link_phones() runs on the finished HTML of city, state and authority pages
# (scripts/generate_authority.py imports it) and wraps every plain-text US
# phone number inside <main> in <a href="tel:+1XXXXXXXXXX" class="tel-auto">,
# keeping the visible text. The rules are a port of linkifyPhones() in
# js/components.js, so the static links and the JS fallback agree and the JS
# finds nothing left to do on a generated page:
#   * 10 digits with separators: (414) 286-5677, 414-286-5677, 414.286.5677,
#     an optional leading 1 / +1 (1-800-669-9777, 1 (800) 855-7100), and keypad
#     letters ((414) 895-RENT -> tel:+14148957368). Area code and exchange start
#     with 2-9 and the area code is never N11; a dashed/dotted number uses the
#     same separator twice; the number can't touch other letters or digits. So
#     years, ZIPs, dates, dollar amounts, 7-digit fragments and statute or case
#     numbers (RCW 59.18.057, 38-12-1301, 2024-CV-001234) never match.
#   * A number labelled "fax" just before it is left alone.
#   * 211 -> tel:211 when it is clearly a phone reference: "2-1-1" with hyphens,
#     or "211" right after call/dial/text/contact/llame/marque/línea ... or right
#     before at/line/hotline. Never "211 Texas" as a name on its own, "211.org",
#     "211info", "§8-211", "898-211" (a text short code) or "$211".
#   * Never inside <a>, <button>, <script>, <style>, <code>, <pre>, <textarea>,
#     <select>, <option>, <label>, <summary>, <svg>, <noscript>, or any element
#     with data-no-tel / contenteditable; never in attributes; never outside
#     <main> (so never in <head>, <title>, meta tags or JSON-LD).
# ---------------------------------------------------------------------------
TEL_PHONE_RE = re.compile(
    r"(?<![\w$#§@./-])"
    r"((?:\+?1[-.\s ]?)?"
    r"(?:\(([2-9]\d\d)\)(?:[  ]|&nbsp;|&#160;)?|([2-9]\d\d)([-.]))"
    r"([2-9A-Z][0-9A-Z]{2})([-.])([0-9A-Z]{4,7}))"
    r"(?![\w-]|\.\d)", re.ASCII)
TEL_211_RE = re.compile(r"(?<![\w$#§@./-])(2-1-1|211)(?![\w-]|[.,]\d|\.[A-Za-z])", re.ASCII)
TEL_211_BEFORE = re.compile(
    r"\b(?:call|dial|text|calling|dialing|contact|llame|llama|llamar|llamando|marque|marca|"
    r"marcar|marcando|contacte|textee|l[ií]nea)"
    r"(?:\s+(?:or|o)\s+(?:text|textee|env[ií]e un (?:mensaje de )?texto))?\s+(?:(?:al|el|a|to)\s+)?$",
    re.I)
TEL_211_AFTER = re.compile(r"\s+(?:at|line|hotline|helpline)\b", re.I)
TEL_FAX_BEFORE = re.compile(r"\bfax\b\D{0,12}$", re.I)
TEL_SKIP_TAGS = frozenset("a button script style code pre textarea select option label summary "
                          "svg noscript".split())
TEL_RAW_TAGS = frozenset(("script", "style"))
HTML_VOID_TAGS = frozenset("area base br col embed hr img input link meta param source track wbr".split())
HTML_TAG_RE = re.compile(r"<!--.*?-->|<(/?)([A-Za-z][A-Za-z0-9:-]*)((?:\"[^\"]*\"|'[^']*'|[^'\">])*)>", re.S)
TEL_SKIP_ATTR_RE = re.compile(r"(?:^|\s)(?:data-no-tel|contenteditable)(?![\w-])", re.I)


def tel_matches(text, before=""):
    """[(start, end, tel)] for the phone numbers in one raw-HTML text run.
    `before` is the decoded text that precedes it on the page (for context)."""
    found = []
    for m in TEL_PHONE_RE.finditer(text):
        start, end = m.start(1), m.end(1)
        area = m.group(2) or m.group(3)
        sep1, exchange, sep2, line = m.group(4), m.group(5), m.group(6), m.group(7)
        if sep1 and sep1 != sep2:              # 555-555.5555 is not a phone number
            continue
        if area[1:] == "11":                   # N11 is never an area code
            continue
        if not (re.search("[A-Z]", line) or len(line) == 4):
            continue                           # a digits-only last group is exactly 4
        if TEL_FAX_BEFORE.search((before + html.unescape(text[:start]))[-20:]):
            continue
        found.append((start, end, "+1" + phone_digits(area, exchange, line)))
    for m in TEL_211_RE.finditer(text):
        start, end = m.start(1), m.end(1)
        if any(start < e and end > s for s, e, _t in found):
            continue
        if m.group(1) == "211":
            ctx = (before + html.unescape(text[:start]))[-60:]
            if not TEL_211_BEFORE.search(ctx) and not TEL_211_AFTER.match(html.unescape(text[end:])):
                continue
        found.append((start, end, "211"))
    return sorted(found)


def _tel_link_run(text, before):
    out, pos = [], 0
    for start, end, tel in tel_matches(text, before):
        out.append(text[pos:start])
        out.append(f'<a href="tel:{tel}" class="tel-auto">{text[start:end]}</a>')
        pos = end
    out.append(text[pos:])
    return "".join(out)


def link_phones(page_html):
    """Return page_html with plain-text phone numbers inside <main> as tel: links."""
    start = page_html.find("<main")
    stop = page_html.rfind("</main>")
    if start < 0 or stop < start:
        return page_html
    region = page_html[start:stop]
    out, pos, before = [], 0, ""
    skip_tag, skip_depth = None, 0
    while True:
        m = HTML_TAG_RE.search(region, pos)
        text = region[pos:m.start() if m else len(region)]
        if text:
            out.append(_tel_link_run(text, before) if skip_tag is None else text)
            before = (before + html.unescape(text))[-60:]
        if not m:
            break
        tag = m.group(0)
        pos = m.end()
        if tag.startswith("<!--"):
            out.append(tag)
            continue
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        self_closing = name in HTML_VOID_TAGS or attrs.rstrip().endswith("/")
        if not closing and name in TEL_RAW_TAGS:
            # <script>/<style> bodies are not markup: copy through to the close tag.
            close = re.compile(rf"</{name}\s*>", re.I).search(region, pos)
            body_end = close.end() if close else len(region)
            out.append(tag + region[pos:body_end])
            pos = body_end
            continue
        out.append(tag)
        if skip_tag is not None:
            if name == skip_tag and not self_closing:
                skip_depth += -1 if closing else 1
                if skip_depth == 0:
                    skip_tag = None
        elif not closing and not self_closing and (name in TEL_SKIP_TAGS or TEL_SKIP_ATTR_RE.search(attrs)):
            skip_tag, skip_depth = name, 1
    return page_html[:start] + "".join(out) + page_html[stop:]


TITLE_MAX = 60


def render_one(env, kind, lang, slug, data, layout):
    """Render one language's page for one location."""
    # State and city pages: Google truncates titles past ~60 characters and
    # Bing flags anything over 70, so the searcher's words (the city, "Section
    # 8", "rent help") fall off the end. The limit counts the " | Waythrough"
    # suffix. og:title and twitter:title fall back to meta.title in the
    # template; any explicit override has to fit too.
    if kind in ("state", "city"):
        meta = data.get("meta") or {}
        for key in ("title", "og_title", "twitter_title"):
            if meta.get(key) and len(meta[key]) > TITLE_MAX:
                raise ValueError(
                    f"{slug} ({lang}): meta.{key} is {len(meta[key])} characters; "
                    f"{kind} titles must be <= {TITLE_MAX}: {meta[key]!r}"
                )
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
    # Tap-to-call: plain-text phone numbers in <main> become tel: links.
    html = link_phones(html)

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

    if Path(json_path).parent.name == "questions":   # reader Q&A: scripts/generate_questions.py
        return None
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
