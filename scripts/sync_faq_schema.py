#!/usr/bin/env python3
"""Make a page's FAQPage JSON-LD match the FAQ readers can see.

For each question in the FAQPage markup, find the matching visible question
(an h2/h3/h4, <summary> or .faq-question whose words overlap at least 60%),
then copy the visible question and answer text into the markup. Markup
questions with no visible twin are dropped; if none are left, the FAQPage
script block is removed. Other JSON-LD blocks and line endings are untouched.

Usage:
    python scripts/sync_faq_schema.py FILE [...]          # dry run: print the plan
    python scripts/sync_faq_schema.py --write FILE [...]  # apply

Pair with scripts/check_faq_schema.py, which finds the pages that need it.
For generated pages (cities, states, authorities, questions) fix the JSON in
data/ instead; this script is for hand-written pages.
"""
import html
import json
import re
import sys

QUESTION_RE = re.compile(
    r'(?is)<(h[234]|summary)\b[^>]*>(.*?)</\1>'
    r'|<div class="faq-question"[^>]*>(.*?)</div>')


def text(fragment):
    t = re.sub(r'(?is)<svg\b.*?</svg>', ' ', fragment)
    t = re.sub(r'(?i)<br\s*/?>', ' ', t)
    t = re.sub(r'(?i)</(p|li|div)>', ' ', t)
    t = re.sub(r'<[^>]+>', '', t)
    return ' '.join(html.unescape(t).split())


def words(s):
    return set(re.findall(r"\w+", s.lower().replace('’', "'")))


def visible_faq(page):
    """[(question, answer, start_offset)] for every visible question."""
    body_at = page.find('<body')
    out = []
    for m in QUESTION_RE.finditer(page, body_at):
        q = text(m.group(2) if m.group(2) is not None else m.group(3))
        if not q.endswith('?') and not q.endswith('?)'):
            continue
        if m.group(3) is not None:  # accordion: answer is the next .faq-answer-inner
            a = re.search(r'(?is)<div class="faq-answer-inner">(.*?)</div>\s*</div>', page[m.end():])
            ans = text(a.group(1)) if a else ''
        elif m.group(1).lower() == 'summary':  # <details><summary>Q</summary> answer </details>
            end = page.find('</details>', m.end())
            ans = text(page[m.end():end]) if end > 0 else ''
        else:  # heading: everything up to the next heading or the end of its container
            rest = page[m.end():]
            stop = re.search(r'(?i)<h[1-4]\b|<nav\b|</(section|article|main|details)>|<div class="(cta-box|related|callout)', rest)
            ans = text(rest[:stop.start() if stop else len(rest)])
        # pages that print "Q: "/"A: " (ES "P: "/"R: ") keep the markup without the prefix
        q = re.sub(r'^(Q|P):\s*', '', q)
        ans = re.sub(r'^(A|R):\s*', '', ans)
        out.append((q, ans))
    return out


def best_match(q, cands):
    qw = words(q)
    best, score = None, 0.0
    for c in cands:
        cw = words(c[0])
        s = len(qw & cw) / max(len(qw | cw), 1)
        if s > score:
            best, score = c, s
    return best if score >= 0.6 else None


def sync(path, write):
    raw = open(path, 'rb').read().decode('utf-8')
    nl = '\r\n' if '\r\n' in raw else '\n'
    page = raw.replace('\r\n', '\n')
    vis = visible_faq(page)
    for m in re.finditer(r'(?is)(<script[^>]*application/ld\+json[^>]*>)(.*?)(</script>)', page):
        try:
            data = json.loads(m.group(2))
        except ValueError:
            continue
        if not (isinstance(data, dict) and data.get('@type') == 'FAQPage'):
            continue
        kept, report = [], []
        for item in data.get('mainEntity', []):
            hit = best_match(item.get('name', ''), vis)
            if not hit or not hit[1]:
                report.append('  DROP  %s' % item.get('name', '')[:90])
                continue
            q, a = hit
            changed = (q != item.get('name')) or (a != item['acceptedAnswer'].get('text'))
            item['name'] = q
            item['acceptedAnswer']['text'] = a
            kept.append(item)
            report.append('  %s  %s' % ('SYNC' if changed else 'ok  ', q[:90]))
        print(path)
        print('\n'.join(report))
        if kept:
            data['mainEntity'] = kept
            # keep the existing layout: blank line after the opening tag, 2-space JSON
            lead = re.match(r'\s*', m.group(2)).group(0)
            trail = re.search(r'\s*$', m.group(2)).group(0)
            new = m.group(1) + lead + json.dumps(data, indent=2, ensure_ascii=False) + trail + m.group(3)
            page = page[:m.start()] + new + page[m.end():]
        else:
            # remove the whole block, including its own line
            s = page.rfind('\n', 0, m.start()) + 1
            e = page.find('\n', m.end()) + 1
            page = page[:s] + page[e:]
            print('  (FAQPage block removed)')
        break
    if write:
        open(path, 'wb').write(page.replace('\n', nl).encode('utf-8'))


def main(argv):
    write = '--write' in argv
    for f in [a for a in argv[1:] if a != '--write']:
        sync(f, write)


if __name__ == '__main__':
    main(sys.argv)
