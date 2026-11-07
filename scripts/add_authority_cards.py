"""Add housing-authority cards to the authority hubs and the find-your-PHA guides (EN + ES).

Parallel authority sessions never edit these four files (their append-at-the-end edits always
conflict); each writes a `_auth_cards.tsv` instead and the PM runs this after merging.

Usage: python scripts/add_authority_cards.py cards.tsv [more.tsv ...]

TSV, no header, tab-separated, one row per authority:
  slug  en_hub_title  en_hub_desc  es_hub_title  es_hub_desc  state_en  state_es  city_label  phone  official_url

- Hubs (resources/housing-authorities/index.html, es/recursos/autoridades-de-vivienda/index.html):
  the card is appended to the end of the directory list.
- Find-your-PHA guides: the entry goes under its state heading, sorted by city; a missing state
  heading is created in alphabetical order (before the "Not listed here?" section).
- Section 8 trackers (EN + ES): a card is appended to the "authority guides" list.
- The "directory of N authorities" count in the EN guide's descriptions is set to the number of
  authority pages on disk.
Rows whose slug is already present are skipped, so re-running is safe. Line endings are kept.
"""
import glob
import html
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB_EN = 'resources/housing-authorities/index.html'
HUB_ES = 'es/recursos/autoridades-de-vivienda/index.html'
PHA_EN = 'resources/guides/how-to-find-your-pha.html'
PHA_ES = 'es/recursos/guias/como-encontrar-tu-pha.html'
TRK_EN = 'resources/tools/section-8-tracker.html'
TRK_ES = 'es/recursos/herramientas/rastreador-section-8.html'
COLS = ['slug', 'en_title', 'en_desc', 'es_title', 'es_desc', 'state_en', 'state_es', 'city', 'phone', 'url']


def read(p):
    raw = open(os.path.join(ROOT, p), 'rb').read().decode('utf-8')
    return raw.replace('\r\n', '\n'), ('\r\n' if '\r\n' in raw else '\n')


def write(p, s, nl):
    open(os.path.join(ROOT, p), 'wb').write(s.replace('\n', nl).encode('utf-8'))


def esc(s):
    return html.escape(s, quote=False)


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c)).lower()


def add_hub(p, rows, lang):
    s, nl = read(p)
    end = '                    </div>\n                </section>'
    assert s.count(end) == 1, p + ': directory list end not found'
    cards = ''
    for r in rows:
        if 'href="%s"' % r['slug'] in s:
            print('  skip (present)', p, r['slug']); continue
        cards += ('                        <a href="%s" class="related-item">\n'
                  '                            <h3>%s</h3>\n'
                  '                            <p>%s</p>\n'
                  '                        </a>\n') % (r['slug'], esc(r[lang + '_title']), esc(r[lang + '_desc']))
    write(p, s.replace(end, cards + end), nl)


def add_pha(p, rows, lang):
    s, nl = read(p)
    # Indentation differs between the EN and ES guides; take it from the first state heading.
    m = re.search(r'\n( *)<h3 class="section-label" style="font-size:0.75rem; margin:28px 0 14px;">', s)
    ind = m.group(1)
    head_re = re.compile(r'^' + ind + r'<h3 class="section-label" style="font-size:0.75rem; margin:28px 0 14px;">(.*?)</h3>\n', re.M)
    prefix = '../housing-authorities/' if lang == 'en' else '../autoridades-de-vivienda/'
    site = 'Official site' if lang == 'en' else 'Sitio oficial'
    for r in rows:
        if prefix + r['slug'] + '"' in s:
            print('  skip (present)', p, r['slug']); continue
        item = ('%s    <div class="related-item">\n'
                '%s        <h3><a href="%s%s">%s</a></h3>\n'
                '%s        <p>%s &middot; <span style="white-space:nowrap">%s</span> &middot; <a href="%s">%s</a></p>\n'
                '%s    </div>\n') % (ind, ind, prefix, r['slug'], esc(r[lang + '_title']), ind, esc(r['city']),
                                    esc(r['phone']), esc(r['url']), site, ind)
        state = r['state_' + lang]
        heads = list(head_re.finditer(s))
        states = [h for h in heads if not h.group(1).endswith('?')]
        hit = [h for h in states if h.group(1) == state]
        if hit:
            # Insert among the state's items, sorted by city label.
            start = hit[0].end()
            close = s.index('\n' + ind + '</div>\n', start) + 1
            block = s[start:close]
            items = re.findall(r'^' + ind + r'    <div class="related-item">\n.*?^' + ind + r'    </div>\n', block, re.M | re.S)
            items.append(item)
            items.sort(key=lambda it: fold(re.search(r'<p>(.*?) &middot;', it).group(1)))
            new_block = ind + '<div class="related-list">\n' + ''.join(items)
            assert block.startswith(ind + '<div class="related-list">\n'), p + ': unexpected block for ' + state
            s = s[:start] + new_block + s[close:]
        else:
            after = [h for h in states if fold(h.group(1)) > fold(state)]
            at = (after[0] if after else [h for h in heads if h.group(1).endswith('?')][0]).start()
            section = ('%s<h3 class="section-label" style="font-size:0.75rem; margin:28px 0 14px;">%s</h3>\n'
                       '%s<div class="related-list">\n%s%s</div>\n') % (ind, esc(state), ind, item, ind)
            s = s[:at] + section + s[at:]
    write(p, s, nl)


def add_tracker(p, rows, lang):
    # The trackers' "Authority guides" card list, closed by the "Browse the full ... directory" link.
    s, nl = read(p)
    end = '                </div>\n                <p style="margin-top:1rem;"><a href="../%s/">' % (
        'housing-authorities' if lang == 'en' else 'autoridades-de-vivienda')
    assert s.count(end) == 1, p + ': authority card list end not found'
    prefix = '../housing-authorities/' if lang == 'en' else '../autoridades-de-vivienda/'
    cards = ''
    for r in rows:
        if prefix + r['slug'] + '"' in s:
            print('  skip (present)', p, r['slug']); continue
        if lang == 'en':
            m = re.search(r'\(([A-Z]{2,})\)\s*$', r['en_title'])
            desc = esc(r['city']) + (' (%s)' % m.group(1) if m else '') + ': waiting-list status, contact, and how to apply.'
        else:
            desc = esc(r['city']) + ': estado de la lista de espera, contacto y cómo aplicar.'
        cards += ('                    <a href="%s%s" class="related-item">\n'
                  '                        <h3>%s</h3>\n'
                  '                        <p>%s</p>\n'
                  '                    </a>\n') % (prefix, r['slug'], esc(r[lang + '_title']), desc)
    s = s.replace(end, cards + end)
    n = s.count('<a href="' + prefix) - s.count('<a href="' + prefix + '"')
    s = re.sub(r'<span class="summary-count">\d+ (guides|guías)</span>', lambda m: '<span class="summary-count">%d %s</span>' % (n, m.group(1)), s)
    write(p, s, nl)


def set_count(p):
    n = len(glob.glob(os.path.join(ROOT, 'resources/housing-authorities/*.html'))) - 1  # minus index
    s, nl = read(p)
    s2 = re.sub(r'directory of \d+ authorities', 'directory of %d authorities' % n, s)
    write(p, s2, nl)
    print('  count ->', n, p)


def main():
    rows = []
    for f in sys.argv[1:]:
        for ln in open(f, encoding='utf-8'):
            ln = ln.rstrip('\r\n')
            if not ln.strip():
                continue
            parts = ln.split('\t')
            assert len(parts) == len(COLS), '%s: expected %d columns, got %d: %s' % (f, len(COLS), len(parts), ln[:60])
            rows.append(dict(zip(COLS, [x.strip() for x in parts])))
    for r in rows:
        for lang, d in (('en', 'resources/housing-authorities/'), ('es', 'es/recursos/autoridades-de-vivienda/')):
            assert os.path.exists(os.path.join(ROOT, d + r['slug'] + '.html')), 'missing page ' + d + r['slug']
    add_hub(HUB_EN, rows, 'en')
    add_hub(HUB_ES, rows, 'es')
    add_pha(PHA_EN, rows, 'en')
    add_pha(PHA_ES, rows, 'es')
    add_tracker(TRK_EN, rows, 'en')
    add_tracker(TRK_ES, rows, 'es')
    set_count(PHA_EN)
    print('added', len(rows), 'authorities')


if __name__ == '__main__':
    main()
