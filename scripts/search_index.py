#!/usr/bin/env python3
"""
Site-search entries for js/search-index.json, derived the way the existing ones were.

js/components.js scores every entry's title, description and body against the
visitor's query, so a page with no entry cannot be found by site search. This
module is the one place an entry is derived and inserted: the weekly blog
publisher (.github/scripts/publish-draft.py) calls it for each post it
publishes, and a session adding pages can call it by hand:

    python scripts/search_index.py add /resources/guides/<slug> /es/recursos/guias/<slug>
    python scripts/search_index.py missing      # sitemap URLs with no entry; exit 1 if any

Entry shape, key order as in the file:

    title        the page's <title>, character references decoded
    description  the page's <meta name="description">, decoded
    url          the clean path: "/" + repo path minus ".html"; index.html -> "<dir>/"
    category     the category the section's existing entries use (SECTIONS)
    body         the first 300 characters of the page's visible text (scripts,
                 styles and comments removed, tags replaced by a space,
                 whitespace collapsed), starting where the section's existing
                 entries start and decoded the way they are (SECTIONS)

The index has been built by different hands over time, and the sections differ:
English pages start at the top of the document, so the <title> text leads the
body; Spanish pages start at <main>; English blog posts and city pages keep
character references as written (&middot;), while guides, authority pages and
every Spanish section decode them. SECTIONS records each section's rule. Each
rule was proven (2026-09-16, before any entry was added with it) by regenerating
existing entries of that section byte-for-byte from their live HTML. Add a
section only with the same proof.

The file is written as json.dumps(entries, indent=2, ensure_ascii=False) with no
trailing newline, which is exactly how it is stored; insert_entry refuses to
rewrite a file that does not round-trip that way. A new entry goes directly
after the last entry with the same category and language. js/search-index.json
is served with a one-hour Cache-Control (see _headers), so an edit reaches every
visitor within the hour; no cache-busting query or components.js bump is needed.
"""

import html
import json
import os
import re
import sys

BODY_CHARS = 300
KEYS = ("title", "description", "url", "category", "body")

# (url prefix, category, where the body text starts, decode character references)
SECTIONS = (
    ("/blog/posts/", "Blog", "document", False),
    ("/es/blog/posts/", "Blog", "main", True),
    ("/resources/guides/", "Guide", "document", True),
    ("/resources/housing-authorities/", "Guide", "document", True),
    ("/es/recursos/guias/", "Guías", "main", True),
    ("/es/recursos/autoridades-de-vivienda/", "Guías", "main", True),
    ("/resources/cities/", "City", "document", False),
    ("/es/recursos/ciudades/", "Recursos de Ciudades", "main", True),
)


def section_for(url):
    """The SECTIONS row covering url (longest prefix wins); ValueError if none."""
    rows = [row for row in SECTIONS if url.startswith(row[0])]
    if not rows:
        raise ValueError("no search-index section covers %s; add one to SECTIONS "
                         "only after proving it against existing entries" % url)
    return max(rows, key=lambda row: len(row[0]))


def repo_path_for(url):
    """Repo-relative HTML file for a clean url ("/" -> index.html)."""
    if not url.startswith("/") or url.endswith(".html"):
        raise ValueError("url must be a clean root-relative path: %r" % url)
    return (url[1:] + "index.html") if url.endswith("/") else (url[1:] + ".html")


def visible_text(page_html, start):
    """Whitespace-collapsed visible text of a page, from the document top or from <main>."""
    text = re.sub(r"<script\b.*?</script>", " ", page_html, flags=re.S | re.I)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    if start == "main":
        m = re.search(r"<main\b[^>]*>", text, flags=re.I)
        if not m:
            raise ValueError("page has no <main> element")
        text = text[m.end():]
    elif start != "document":
        raise ValueError("unknown start %r" % start)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def derive_entry(html_path, url):
    """Build the search-index entry for the page at html_path, served at url."""
    expected = repo_path_for(url)
    if not os.path.normpath(html_path).replace(os.sep, "/").endswith(expected):
        raise ValueError("%s is not the file for %s (expected .../%s)" % (html_path, url, expected))
    _prefix, category, start, decode = section_for(url)
    with open(html_path, encoding="utf-8", newline="") as f:
        page = f.read()
    title = re.search(r"<title>(.*?)</title>", page, flags=re.S | re.I)
    desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', page, flags=re.I)
    if not title or not desc:
        raise ValueError("%s has no <title> or no meta description" % html_path)
    body = visible_text(page, start)
    if decode:
        body = html.unescape(body)
    return {
        "title": html.unescape(title.group(1)),
        "description": html.unescape(desc.group(1)),
        "url": url,
        "category": category,
        "body": body[:BODY_CHARS],
    }


def _dumps(entries):
    return json.dumps(entries, indent=2, ensure_ascii=False)


def _is_spanish(url):
    return url == "/es/" or url.startswith("/es/")


def insert_entry(index_path, entry):
    """Insert entry after the last entry of its category and language.

    Returns True if it was added, False if an entry for its url already exists
    (nothing is written, so re-running is safe).
    """
    if tuple(entry) != KEYS or not all(isinstance(entry[k], str) for k in KEYS):
        raise ValueError("entry must have exactly the string keys %s, in that order" % (KEYS,))
    if len(entry["body"]) > BODY_CHARS or not entry["url"].startswith("/") or entry["url"].startswith("//"):
        raise ValueError("malformed entry for %r" % entry["url"])
    with open(index_path, encoding="utf-8", newline="") as f:
        stored = f.read()
    entries = json.loads(stored)
    if _dumps(entries) != stored:
        raise ValueError("%s does not round-trip through json.dumps(indent=2, "
                         "ensure_ascii=False); refusing to rewrite it" % index_path)
    if any(e.get("url") == entry["url"] for e in entries):
        return False
    spanish = _is_spanish(entry["url"])
    at = len(entries)
    for i, e in enumerate(entries):
        if e.get("category") == entry["category"] and _is_spanish(e.get("url", "")) == spanish:
            at = i + 1
    entries.insert(at, dict(entry))
    tmp = index_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(_dumps(entries))
    os.replace(tmp, index_path)
    return True


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    repo = _repo_root()
    index_path = os.path.join(repo, "js", "search-index.json")
    if len(argv) >= 2 and argv[0] == "add":
        for url in argv[1:]:
            entry = derive_entry(os.path.join(repo, repo_path_for(url)), url)
            print(("added   " if insert_entry(index_path, entry) else "present ") + url)
        return 0
    if argv == ["missing"]:
        with open(os.path.join(repo, "sitemap.xml"), encoding="utf-8") as f:
            locs = re.findall(r"<loc>https://waythroughproject\.com([^<]*)</loc>", f.read())
        with open(index_path, encoding="utf-8") as f:
            have = {e["url"] for e in json.load(f)}
        gaps = [u for u in locs if u not in have]
        for u in gaps:
            print(u)
        return 1 if gaps else 0
    print("usage: search_index.py add URL... | missing", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
