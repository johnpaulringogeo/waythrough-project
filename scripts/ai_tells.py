#!/usr/bin/env python3
"""Score pages for AI-sounding copy, to pick and verify weekly de-AI batches.

Counts stock phrases and patterns that make text read as machine-written
(filler openers, "not just X but Y", inflated vocabulary, tidy summaries) in
the visible text of each page, English and Spanish. A count is a prompt to
look, not proof: some hits are fine in context.

Usage:
    python scripts/ai_tells.py                    # rank every page, worst first (top 40)
    python scripts/ai_tells.py --all              # rank every page
    python scripts/ai_tells.py FILE [...]         # score these files
    python scripts/ai_tells.py -v FILE [...]      # also list each hit with context
    python scripts/ai_tells.py --total            # one sitewide number (track it over time)

Score = hits per 1,000 words, so long and short pages compare fairly.
The style guide lives in _audit/deai_queue.md.
"""
import html
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EN = [
    # filler openers and signposting
    r"it'?s (important|worth|crucial|essential) (to note|noting|to remember|to understand|to know)",
    r"\bhere'?s (the thing|what you need to know|the short version|the good news|the bottom line|why|how)\b",
    r"\blet'?s (dive|break|take a (closer )?look|explore|walk through)",
    r"\bwhether you'?re\b",
    r"\bin today'?s\b",
    r"\bin (summary|conclusion|short)\b[,:]",
    r"\bthe bottom line\b",
    r"\bat the end of the day\b",
    r"\bthe (good|bad) news is\b",
    r"\bremember[,:] ",
    r"\bkeep in mind\b",
    r"\bbottom line:",
    # contrast formulas
    r"\bnot (just|only) [^.]{1,60}?,? but (also )?",
    r"\bisn'?t (just )?about [^.]{1,60}?[.;,] it'?s about\b",
    r"\bit'?s not [^.]{1,40}?\. it'?s\b",
    r"\bthis isn'?t [^.]{1,40}?\. it'?s\b",
    # inflated vocabulary
    r"\bnavigat(e|ing|es)\b",
    r"\b(crucial|vital|essential|paramount)\b",
    r"\bcomprehensive\b",
    r"\bempower(s|ing|ment)?\b",
    r"\bunlock(s|ing)?\b",
    r"\bseamless(ly)?\b",
    r"\bleverag(e|ing)\b",
    r"\brobust\b",
    r"\bdelve\b",
    r"\bjourney\b",
    r"\blandscape\b",
    r"\bmyriad\b",
    r"\bstreamline(d|s)?\b",
    r"\btailored\b",
    r"\bgame[- ]changer\b",
    r"\bpeace of mind\b",
    r"\bkey (to|role|step|factor|takeaway)s?\b",
    r"\bplays? a (key|crucial|vital|significant) role\b",
    r"\bensur(e|es|ing)\b",
    # stock reassurance
    r"\byou'?re not alone\b",
    r"\bdon'?t (lose hope|give up|panic)\b",
    r"\bevery (situation|case) is (unique|different)\b",
    r"\bknowledge is power\b",
    # rhetorical Q then answer
    r"\bthe answer\?|\bthe result\?|\bthe catch\?|\bwhy\? because\b",
]
ES = [
    r"\bes (importante|fundamental|esencial|crucial|clave) (tener en cuenta|recordar|entender|saber|notar)",
    r"\b(aquí|esto) (está|es) lo que (necesita|necesitas) saber\b",
    r"\bya sea que\b",
    r"\ben (resumen|conclusión)\b",
    r"\bla buena noticia es\b",
    r"\bal final del día\b",
    r"\btenga en cuenta\b|\bten en cuenta\b",
    r"\bno (solo|sólo) [^.]{1,60}?,? sino (también )?",
    r"\bnavegar\b",
    r"\b(crucial|vital|fundamental|esencial)(es)?\b",
    r"\bintegral(es)?\b",
    r"\bempoderar|empoderamiento\b",
    r"\bdesbloquear\b",
    r"\bsin problemas\b",
    r"\brobust[oa]s?\b",
    r"\bviaje\b",
    r"\bpanorama\b",
    r"\bmiríada\b",
    r"\bpersonalizad[oa]s?\b",
    r"\btranquilidad\b",
    r"\bdesempeña un papel\b",
    r"\bgarantizar\b|\basegurar(se)?\b",
    r"\bno est(á|ás) sol[oa]\b",
]
EN_RE = [re.compile(p, re.I) for p in EN]
ES_RE = [re.compile(p, re.I) for p in ES]


def visible(page):
    m = re.search(r'(?is)<main\b.*?</main>', page) or re.search(r'(?is)<body\b.*</body>', page)
    t = m.group(0) if m else page
    t = re.sub(r'(?is)<(script|style|nav|footer)\b.*?</\1>', ' ', t)
    t = re.sub(r'(?s)<!--.*?-->', ' ', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    return ' '.join(html.unescape(t).replace('’', "'").split())


def score(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    t = visible(open(path, encoding='utf-8').read())
    pats = ES_RE if rel.startswith('es/') else EN_RE
    hits = []
    for p in pats:
        for m in p.finditer(t):
            hits.append((m.group(0), t[max(0, m.start() - 50):m.end() + 50]))
    words = max(len(t.split()), 1)
    return rel, len(hits), words, 1000.0 * len(hits) / words, hits


def all_pages():
    r = subprocess.run(['git', '-C', ROOT, 'ls-files', '*.html'], capture_output=True, text=True)
    skip = ('blog/drafts/', '_', 'admin/')
    return [os.path.join(ROOT, f) for f in r.stdout.split('\n') if f and not f.startswith(skip)]


def main(argv):
    verbose = '-v' in argv
    flags = {'-v', '--all', '--total'}
    files = [a for a in argv[1:] if a not in flags]
    rows = [score(f) for f in (files or all_pages())]
    if '--total' in argv:
        hits = sum(r[1] for r in rows); words = sum(r[2] for r in rows)
        print('%d hits in %d words = %.2f per 1,000 words (%d pages)' % (hits, words, 1000.0 * hits / words, len(rows)))
        return 0
    rows.sort(key=lambda r: -r[3])
    if not files and '--all' not in argv:
        rows = rows[:40]
    for rel, n, words, per, hits in rows:
        print('%6.2f  %3d hits  %5d words  %s' % (per, n, words, rel))
        if verbose:
            for h, ctx in hits:
                print('          [%s]  ...%s...' % (h, ctx))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
