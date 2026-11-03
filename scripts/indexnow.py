#!/usr/bin/env python3
"""Tell IndexNow (Bing, Yandex, Seznam, Naver...) which pages changed, so they recrawl in minutes.

Usage (repo root):
    python scripts/indexnow.py <base_rev> <head_rev> [--dry-run]
    python scripts/indexnow.py --all [--dry-run]        # every URL in sitemap.xml

Changed = served .html pages added, modified or deleted between the two revs (blog/drafts/,
templates/ and _* files are not served). Deleted pages are submitted too: IndexNow uses that to
drop them. The key file lives at the site root (<KEY>.txt) and must be deployed before submitting,
so the script first waits for it to answer 200.
"""
import json, re, subprocess, sys, time, urllib.request, urllib.error

HOST = 'waythroughproject.com'
KEY = '70e41e1c629ce22f9cd8e5d933920b2c'
KEY_URL = 'https://%s/%s.txt' % (HOST, KEY)
ENDPOINT = 'https://api.indexnow.org/indexnow'
SKIP = ('blog/drafts/', 'templates/', '_', '.github/', 'node_modules/')


def url_for(path):
    p = path[:-5]
    if p.endswith('/index'):
        p = p[:-5]
    elif p == 'index':
        p = ''
    return 'https://%s/%s' % (HOST, p)


def changed(base, head):
    out = subprocess.run(['git', 'diff', '--name-status', '--no-renames', base, head],
                         capture_output=True, text=True, check=True).stdout
    urls = []
    for line in out.splitlines():
        status, path = line.split('\t')[0], line.split('\t')[-1]
        if path.endswith('.html') and not path.startswith(SKIP) and path not in ('404.html', '_link_checker.html'):
            urls.append(url_for(path))
    return sorted(set(urls))


def sitemap_urls():
    s = open('sitemap.xml', encoding='utf-8').read()
    return re.findall(r'<loc>([^<]+)</loc>', s)


def wait_for_key(timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(KEY_URL, timeout=20) as r:
                if r.status == 200 and r.read().decode().strip() == KEY:
                    return True
        except Exception:
            pass
        time.sleep(15)
    return False


def submit(urls):
    for i in range(0, len(urls), 10000):
        body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': KEY_URL,
                           'urlList': urls[i:i + 10000]}).encode()
        req = urllib.request.Request(ENDPOINT, data=body, method='POST',
                                     headers={'Content-Type': 'application/json; charset=utf-8'})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                print('IndexNow HTTP', r.status, 'for', len(urls[i:i + 10000]), 'URLs')
        except urllib.error.HTTPError as e:
            # 200/202 = accepted; 422 = URLs don't match host/key; 429 = too many requests
            print('IndexNow HTTP', e.code, e.read().decode(errors='replace')[:300])
            if e.code not in (200, 202):
                sys.exit(1)


def main():
    args = [a for a in sys.argv[1:] if a != '--dry-run']
    dry = '--dry-run' in sys.argv
    urls = sitemap_urls() if args == ['--all'] else changed(args[0], args[1])
    print(len(urls), 'URLs')
    for u in urls[:20]:
        print(' ', u)
    if dry or not urls:
        return
    if not wait_for_key():
        sys.exit('key file %s not reachable; not submitting' % KEY_URL)
    submit(urls)


if __name__ == '__main__':
    main()
