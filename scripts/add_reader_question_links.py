#!/usr/bin/env python3
"""Add a "Readers asked" box to every hand-written page that a reader-question page links to.

Reads data/questions/*.json. For each page in a question's `links` (EN and ES separately), the
page gets a box listing up to MAX questions that point at it, linking to the answer pages. The box
sits between <!-- reader-questions:start --> / <!-- reader-questions:end --> markers, so re-running
replaces it (idempotent). Run it after adding or editing questions.

Generated pages (city, state, authority) are skipped: their generators would overwrite the box.

Usage (repo root):  python scripts/add_reader_question_links.py [--dry-run]
"""
import glob, html, json, os, posixpath, re, sys

MAX = 4
SKIP_PREFIXES = ('resources/cities/', 'resources/states/', 'resources/housing-authorities/',
                 'es/recursos/ciudades/', 'es/recursos/estados/', 'es/recursos/autoridades-de-vivienda/',
                 'resources/questions/', 'es/recursos/preguntas/')
TEXT = {
    'en': ('Readers asked', 'See all reader questions', '/resources/questions/'),
    'es': ('Preguntas de lectores', 'Ver todas las preguntas de lectores', '/es/recursos/preguntas/'),
}
START, END = '<!-- reader-questions:start -->', '<!-- reader-questions:end -->'
ANCHORS = [r'^[ \t]*<section class="related-resources"', r'^[ \t]*<div class="cta-box"',
           r'^[ \t]*</article>', r'^[ \t]*</main>']


def page_file(url_path):
    p = url_path.split('#')[0].lstrip('/')
    for cand in (p + '.html', p.rstrip('/') + '/index.html', p):
        if os.path.isfile(cand):
            return cand
    return None


def collect():
    """{(lang, file): [(order, question_h1, question_url)]}"""
    targets = {}
    for f in sorted(glob.glob('data/questions/*.json')):
        d = json.load(open(f, encoding='utf-8'))
        for lang in ('en', 'es'):
            q = d[lang]
            url = TEXT[lang][2] + (d['slug'] if lang == 'en' else d['es_slug'])
            for link in q.get('links', []):
                href = link['href']
                if not href.startswith('/'):
                    continue
                fp = page_file(href)
                if not fp or fp.startswith(SKIP_PREFIXES):
                    continue
                lst = targets.setdefault((lang, fp), [])
                if all(u != url for _, _, u in lst):
                    lst.append((d.get('order', 999), q.get('h1') or q['question'], url))
    return targets


def served_dir(fp):
    """Directory the page is served from (clean URLs: a/b.html -> /a/, a/index.html -> /a/)."""
    return '/' + posixpath.dirname(fp)


def block(lang, fp, items, indent):
    h, more, hub = TEXT[lang]
    base = served_dir(fp)
    rel = lambda u: posixpath.relpath(u.rstrip('/'), base) + ('/' if u.endswith('/') else '')
    lines = [indent + START,
             indent + '<div class="callout">',
             indent + '    <h2>%s</h2>' % h,
             indent + '    <ul>']
    for _, q, u in sorted(items)[:MAX]:
        lines.append(indent + '        <li><a href="%s">%s</a></li>' % (rel(u), html.escape(q, quote=False)))
    lines += [indent + '    </ul>',
              indent + '    <p><a href="%s">%s</a></p>' % (rel(hub), more),
              indent + '</div>',
              indent + END]
    return lines


def apply(fp, lang, items, dry):
    raw = open(fp, 'rb').read().decode('utf-8')
    nl = '\r\n' if '\r\n' in raw else '\n'
    s = raw.replace('\r\n', '\n')
    s = re.sub(r'^[ \t]*' + re.escape(START) + r'.*?' + re.escape(END) + r'\n\n?', '', s, flags=re.S | re.M)
    for pat in ANCHORS:
        m = re.search(pat, s, re.M)
        if m:
            break
    else:
        return 'NO ANCHOR'
    indent = re.match(r'[ \t]*', s[m.start():]).group(0)
    new = s[:m.start()] + '\n'.join(block(lang, fp, items, indent)) + '\n\n' + s[m.start():]
    if new == raw.replace('\r\n', '\n'):
        return 'unchanged'
    if not dry:
        open(fp, 'wb').write(new.replace('\n', nl).encode('utf-8'))
    return 'ok (%d, before %s)' % (min(len(items), MAX), pat.split('<')[-1][:30])


def main():
    dry = '--dry-run' in sys.argv
    for (lang, fp), items in sorted(collect().items(), key=lambda x: x[0][1]):
        print('%-60s %s' % (fp, apply(fp, lang, items, dry)))


if __name__ == '__main__':
    main()
