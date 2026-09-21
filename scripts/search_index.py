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
    python scripts/search_index.py refresh --all [--dry-run]    # re-derive stale entries
    python scripts/search_index.py refresh /resources/cities/<slug> ... [--dry-run]

refresh re-derives the title, description and body of entries that already exist,
from the pages as they are now and by the same SECTIONS rules; url, category and
array order never change. Pages get edited after their entry is written (a
retitle, a regenerated city page), so an entry goes stale unless someone
refreshes it. --all covers every entry a SECTIONS row covers and whose category
is that row's category; the rest (state pages, tools, entries filed under
another category) are left as they are and counted in the report.

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


def refresh_entries(index_path, urls=None, write=True):
    """Re-derive title, description and body of existing entries from their pages.

    urls=None refreshes every entry whose url a SECTIONS row covers and whose
    category is that row's category; entries outside SECTIONS or filed under a
    different category are skipped and reported. Given urls, each must already be
    in the index and be covered with a matching category, or ValueError is
    raised. url, category, key order and array order never change, and nothing
    is written unless write is true and at least one entry changed. Returns
    {"changed": [...], "unchanged": [...], "skipped_no_section": [...],
    "skipped_category": [...]} (lists of urls).
    """
    with open(index_path, encoding="utf-8", newline="") as f:
        stored = f.read()
    entries = json.loads(stored)
    if _dumps(entries) != stored:
        raise ValueError("%s does not round-trip through json.dumps(indent=2, "
                         "ensure_ascii=False); refusing to rewrite it" % index_path)
    repo = os.path.dirname(os.path.dirname(os.path.abspath(index_path)))
    position = {}
    for i, e in enumerate(entries):
        if e.get("url") in position:
            raise ValueError("duplicate url in the index: %r" % e.get("url"))
        position[e.get("url")] = i
    if urls is None:
        targets = list(range(len(entries)))
    else:
        absent = [u for u in urls if u not in position]
        if absent:
            raise ValueError("not in the index (use add): %s" % ", ".join(absent))
        targets = [position[u] for u in urls]
    report = {"changed": [], "unchanged": [], "skipped_no_section": [], "skipped_category": []}
    refreshed = [dict(e) for e in entries]
    for i in targets:
        entry = entries[i]
        url = entry["url"]
        try:
            _prefix, category, _start, _decode = section_for(url)
        except ValueError:
            if urls is not None:
                raise
            report["skipped_no_section"].append(url)
            continue
        if category != entry["category"]:
            if urls is not None:
                raise ValueError("%s is filed under %r, not its section's %r; refresh it by hand "
                                 "only after proving the rule for it" % (url, entry["category"], category))
            report["skipped_category"].append(url)
            continue
        derived = derive_entry(os.path.join(repo, repo_path_for(url)), url)
        new = dict(entry)
        for key in ("title", "description", "body"):
            new[key] = derived[key]
        refreshed[i] = new
        report["changed" if new != entry else "unchanged"].append(url)
    # Only title, description and body may differ; everything else stays put.
    if len(refreshed) != len(entries):
        raise AssertionError("entry count changed")
    for old, new in zip(entries, refreshed):
        if list(old) != list(new):
            raise AssertionError("key order changed for %r" % old.get("url"))
        for key in old:
            if key not in ("title", "description", "body") and old[key] != new[key]:
                raise AssertionError("%s changed for %r" % (key, old.get("url")))
        if len(new["body"]) > BODY_CHARS:
            raise AssertionError("body over %d characters for %r" % (BODY_CHARS, new["url"]))
    if write and report["changed"]:
        tmp = index_path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(_dumps(refreshed))
        os.replace(tmp, index_path)
    return report


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
    if len(argv) >= 2 and argv[0] == "refresh":
        args = argv[1:]
        dry = "--dry-run" in args
        args = [a for a in args if a != "--dry-run"]
        if args == ["--all"]:
            urls = None
        elif args and all(a.startswith("/") for a in args):
            urls = args
        else:
            print("usage: search_index.py refresh --all | URL... [--dry-run]", file=sys.stderr)
            return 2
        report = refresh_entries(index_path, urls, write=not dry)
        for url in report["changed"]:
            print(("stale   " if dry else "refreshed ") + url)
        print("%s: %d changed, %d already current, %d outside SECTIONS, %d filed under another category"
              % ("dry run" if dry else "refresh", len(report["changed"]), len(report["unchanged"]),
                 len(report["skipped_no_section"]), len(report["skipped_category"])))
        return 0
    print("usage: search_index.py add URL... | missing | refresh --all | refresh URL... [--dry-run]",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
