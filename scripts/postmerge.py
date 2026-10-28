"""After merging an agent's commit(s): sitemap + search index for the pages it added or changed.
Usage (from the repo root):  python scripts/postmerge.py <base_rev> [<date YYYY-MM-DD>]
- new served .html pages  -> sitemap <url> block copied from a sibling in the same directory
                             (same changefreq/priority), inserted after that sibling; search_index add
- modified served pages   -> sitemap lastmod = date; search_index refresh (where SECTIONS covers it)
Writes LF files. Prints what it did; never touches blog/drafts/ or non-sitemap pages."""
import os, re, subprocess, sys, datetime

base = sys.argv[1]
date = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
SITE = 'https://waythroughproject.com/'
SKIP_PREFIX = ('blog/drafts/', 'templates/', '_', '.github/')

def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True, encoding='utf-8').stdout

def url_for(path):
    p = path[:-5]  # strip .html
    if p.endswith('/index'):
        p = p[:-5]
    return p if p != 'index' else ''

changes = [l.split('\t') for l in git('diff', '--name-status', base, 'HEAD').splitlines()]
added, modified = [], []
for st, *paths in changes:
    path = paths[-1]
    if not path.endswith('.html') or path.startswith(SKIP_PREFIX) or path in ('404.html', '_link_checker.html'):
        continue
    (added if st.startswith('A') else modified if st.startswith('M') else []).append(path)

sm_path = 'sitemap.xml'
sm = open(sm_path, 'rb').read().decode('utf-8').replace('\r\n', '\n')
blocks = re.findall(r'  <url>\n.*?</url>\n', sm, re.S)

def loc_of(b):
    return re.search(r'<loc>([^<]*)</loc>', b).group(1)

have = {loc_of(b) for b in blocks}
new_urls, refresh_urls = [], []
for path in added:
    u = url_for(path); loc = SITE + u
    if loc in have:
        continue
    d = os.path.dirname(path) + '/'
    sibs = [b for b in blocks if loc_of(b).startswith(SITE + d) and loc_of(b) != SITE + d]
    if not sibs:
        print('NO SIBLING for', path, '- add it by hand'); continue
    tpl = sibs[-1]
    nb = re.sub(r'<loc>[^<]*</loc>', '<loc>' + loc + '</loc>', tpl)
    nb = re.sub(r'<lastmod>[^<]*</lastmod>', '<lastmod>' + date + '</lastmod>', nb)
    sm = sm.replace(tpl, tpl + nb, 1); blocks = re.findall(r'  <url>\n.*?</url>\n', sm, re.S)
    have.add(loc); new_urls.append('/' + u); print('sitemap +', loc)
for path in modified:
    loc = SITE + url_for(path)
    sm2, n = re.subn(r'(<loc>' + re.escape(loc) + r'</loc>\s*<lastmod>)[^<]*', r'\g<1>' + date, sm)
    if n:
        sm = sm2; refresh_urls.append('/' + url_for(path))
open(sm_path, 'wb').write(sm.encode('utf-8'))
print('sitemap lastmod ->', date, 'on', len(refresh_urls), 'modified pages')

idx = 'js/search-index.json'
b = open(idx, 'rb').read(); open(idx, 'wb').write(b.replace(b'\r\n', b'\n'))
env = dict(os.environ, MSYS_NO_PATHCONV='1')
failures = []
# Every added page gets an index entry, whether or not its sitemap entry was new this run
# (add is idempotent). One URL per call, so one failure can't silently skip the rest.
for u in sorted(set(new_urls) | {'/' + url_for(p) for p in added}):
    r = subprocess.run([sys.executable, 'scripts/search_index.py', 'add', u], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        failures.append(u); print('INDEX ADD FAILED', u, (r.stderr or r.stdout).strip().splitlines()[-1:])
    else:
        print(r.stdout.strip())
covered = []
for u in refresh_urls:
    r = subprocess.run([sys.executable, 'scripts/search_index.py', 'refresh', u, '--dry-run'], capture_output=True, text=True, env=env)
    if r.returncode == 0:
        covered.append(u)
if covered:
    print(subprocess.run([sys.executable, 'scripts/search_index.py', 'refresh', *covered], capture_output=True, text=True, env=env).stdout.strip().splitlines()[-1])
r = subprocess.run([sys.executable, 'scripts/search_index.py', 'missing'], capture_output=True, text=True, env=env)
print('missing exit', r.returncode, r.stdout.strip()[:300])
assert 'Program Files' not in open(idx, encoding='utf-8').read()
if failures or r.returncode != 0:
    sys.exit('POSTMERGE INCOMPLETE: fix the failures above (index add failed: %s; missing exit %d)' % (failures, r.returncode))
