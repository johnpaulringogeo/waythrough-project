#!/usr/bin/env python3
"""Add guide cards to both guide hubs and keep their "N free housing guides" counts true.

Usage (repo root):
    python scripts/add_hub_cards.py cards.tsv

cards.tsv: one card per line, tab-separated:
    en_slug  en_title  en_desc  es_slug  es_title  es_desc
Cards go at the end of the "Emergency & Crisis" / "Emergencia" section of each hub (after the
last card before the next <h2>), skipping any slug already on the hub. The count in the three
meta lines is then set to the number of cards on the page. Content sessions no longer edit the
hubs; parallel edits there kept colliding, so the PM adds cards after merging.
"""
import html, re, sys

HUBS = {
    'en': ('resources/guides/index.html', 'Emergency & Crisis', r'(\d+) free housing guides'),
    'es': ('es/recursos/guias/index.html', None, r'(\d+) guías gratuitas'),
}

def card(slug, title, desc):
    e = lambda s: html.escape(s, quote=False)
    return ('                        <a href="%s" class="related-item">\n'
            '                            <h3>%s</h3>\n'
            '                            <p>%s</p>\n'
            '                        </a>\n') % (slug, e(title), e(desc))

def insert(path, section_h2, count_re, cards):
    raw = open(path, 'rb').read().decode('utf-8')
    crlf = '\r\n' in raw
    s = raw.replace('\r\n', '\n')
    h2s = [m for m in re.finditer(r'<h2[^>]*>([^<]*)</h2>', s)]
    if section_h2:
        start = next(m for m in h2s if m.group(1).strip() == section_h2)
    else:  # ES hub: find the section holding the existing ES rent-help cards
        anchor = s.index('href="asistencia-renta-emergencia-')
        start = [m for m in h2s if m.start() < anchor][-1]
    nxt = next((m for m in h2s if m.start() > start.start()), None)
    end = nxt.start() if nxt else len(s)
    section = s[start.start():end]
    last = section.rfind('</a>\n')
    assert last != -1, 'no cards in section'
    pos = start.start() + last + len('</a>\n')
    added = 0
    for slug, title, desc in cards:
        if ('href="%s"' % slug) in s:
            print('  already on hub:', slug); continue
        block = card(slug, title, desc)
        s = s[:pos] + block + s[pos:]; pos += len(block); added += 1
    n = s.count('class="related-item"')
    s, k = re.subn(count_re, lambda m: m.group(0).replace(m.group(1), str(n)), s)
    print('%s: +%d cards, count -> %d (%d meta lines)' % (path, added, n, k))
    open(path, 'wb').write((s.replace('\n', '\r\n') if crlf else s).encode('utf-8'))

def main():
    en, es = [], []
    for line in open(sys.argv[1], encoding='utf-8'):
        if not line.strip():
            continue
        f = line.rstrip('\n').split('\t')
        assert len(f) == 6, line
        en.append(tuple(f[0:3])); es.append(tuple(f[3:6]))
    insert(*HUBS['en'], en)
    insert(*HUBS['es'], es)

if __name__ == '__main__':
    main()
