#!/usr/bin/env python3
"""Check that FAQPage JSON-LD matches the FAQ readers can see on the page.

Google's rule for FAQ structured data: every question and answer in the markup
must also be visible on the page. This flags, per page:

  * a JSON-LD question whose text is not visible on the page, and
  * a JSON-LD answer whose words mostly are not visible (under 80% of its
    5-word phrases appear in the visible text).

Usage:
    python scripts/check_faq_schema.py              # every tracked .html outside blog/drafts/
    python scripts/check_faq_schema.py FILE [...]   # just these files
    python scripts/check_faq_schema.py -v ...       # also print each failing question

Exit 0 = all match, 1 = mismatches found.
"""
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANSWER_MIN = 0.80
N = 5


def norm(s):
    s = html.unescape(s)
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace(' ', ' ')
    s = re.sub(r"[^\w$%']+", ' ', s.lower())
    return ' '.join(s.split())


def visible_text(page):
    body = re.sub(r'(?is)<head\b.*?</head>', ' ', page)
    body = re.sub(r'(?is)<(script|style|noscript)\b.*?</\1>', ' ', body)
    body = re.sub(r'(?s)<!--.*?-->', ' ', body)
    body = re.sub(r'<[^>]+>', ' ', body)
    return ' ' + norm(body) + ' '


def faq_entries(page):
    out = []
    for block in re.findall(r'(?is)<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        items = data if isinstance(data, list) else data.get('@graph', [data])
        for d in items:
            if isinstance(d, dict) and d.get('@type') == 'FAQPage':
                for q in d.get('mainEntity', []):
                    a = q.get('acceptedAnswer', {})
                    a = a[0] if isinstance(a, list) else a
                    out.append((q.get('name', ''), re.sub(r'<[^>]+>', ' ', a.get('text', ''))))
    return out


def ngram_cover(answer, vis):
    w = norm(answer).split()
    if len(w) < N:
        return 1.0 if (' ' + ' '.join(w) + ' ') in vis else 0.0
    grams = [' '.join(w[i:i + N]) for i in range(len(w) - N + 1)]
    return sum((' ' + g + ' ') in vis for g in grams) / len(grams)


def check(path):
    page = open(path, encoding='utf-8').read()
    entries = faq_entries(page)
    if not entries:
        return None, []
    vis = visible_text(page)
    bad = []
    for q, a in entries:
        qv = (' ' + norm(q) + ' ') in vis
        cov = ngram_cover(a, vis)
        if not qv or cov < ANSWER_MIN:
            bad.append((q, qv, cov))
    return len(entries), bad


def files_from_git():
    r = subprocess.run(['git', '-C', ROOT, 'ls-files', '*.html'], capture_output=True, text=True)
    return [os.path.join(ROOT, f) for f in r.stdout.split('\n')
            if f and not f.startswith('blog/drafts/')]


def main(argv):
    verbose = '-v' in argv
    args = [a for a in argv[1:] if a != '-v']
    files = args or files_from_git()
    pages = failing = entries_bad = 0
    for f in sorted(files):
        n, bad = check(f)
        if n is None:
            continue
        pages += 1
        if bad:
            failing += 1
            entries_bad += len(bad)
            print('%s: %d of %d FAQ entries not visible' % (os.path.relpath(f, ROOT).replace(os.sep, '/'), len(bad), n))
            if verbose:
                for q, qv, cov in bad:
                    print('    [%s q, %3d%% a] %s' % ('ok ' if qv else 'NO ', cov * 100, q[:90]))
    print('%d pages with FAQ markup, %d mismatched, %d entries' % (pages, failing, entries_bad))
    return 1 if failing else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
