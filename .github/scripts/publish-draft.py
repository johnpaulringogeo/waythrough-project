#!/usr/bin/env python3
"""
Auto-publish the next blog draft.

Picks the draft with the earliest datePublished from blog/drafts/,
moves it to blog/posts/, and updates:
  - blog/index.html  (adds card after the Welcome pinned card)
  - blog/posts.json  (prepends entry)
  - blog/feed.xml    (adds <item>, updates lastBuildDate)
  - sitemap.xml      (adds <url> entry)

Run from the repo root:
    python .github/scripts/publish-draft.py

WARNING: Never re-add a draft that has already been published (i.e. one that
was moved out of blog/drafts/ into blog/posts/). Re-adding a published draft
here causes DUPLICATE PUBLICATION -- this script will move it to blog/posts/
again and add a second blog/index.html card, blog/posts.json entry,
blog/feed.xml <item>, and sitemap.xml <url>. Ghost drafts of already-published
posts must be deleted, never restored to blog/drafts/.
"""

import os, re, json, sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DRAFTS = os.path.join(REPO, "blog", "drafts")
POSTS  = os.path.join(REPO, "blog", "posts")
INDEX  = os.path.join(REPO, "blog", "index.html")
PJSON  = os.path.join(REPO, "blog", "posts.json")
FEED   = os.path.join(REPO, "blog", "feed.xml")
SMAP   = os.path.join(REPO, "sitemap.xml")

# ── helpers ──────────────────────────────────────────────────────────

def extract_meta(html):
    """Pull title, description, date, readTime, tag, slug from draft HTML."""
    m = {}
    t = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    m["title"] = t.group(1) if t else "Untitled"
    d = re.search(r'<meta name="description" content="([^"]+)"', html)
    m["description"] = d.group(1) if d else ""
    dp = re.search(r'"datePublished":\s*"([^"]+)"', html)
    m["date"] = dp.group(1) if dp else "2026-01-01"
    rt = re.search(r'(\d+ min read)', html)
    m["readTime"] = rt.group(1) if rt else ""
    # tag from <span class="blog-tag ...">Tag</span>
    tag_match = re.search(r'class="blog-tag[^"]*">([^<]+)<', html)
    m["tag"] = tag_match.group(1).strip() if tag_match else "Guide"
    return m

def date_human(iso):
    """2026-05-13 → May 13, 2026"""
    dt = datetime.strptime(iso, "%Y-%m-%d")
    return dt.strftime("%B %-d, %Y").replace(" 0", " ")

def rfc822(iso):
    """2026-05-13 → Tue, 13 May 2026 00:00:00 GMT"""
    dt = datetime.strptime(iso, "%Y-%m-%d")
    return dt.strftime("%a, %d %b %Y 00:00:00 GMT")

def tag_class(tag):
    t = tag.lower().replace(" ", "-")
    mapping = {
        "guide": "tag-guide", "explainer": "tag-explainer",
        "practical": "tag-practical", "your-rights": "tag-rights",
        "personal": "tag-personal", "tips": "tag-guide",
        "benefits": "tag-guide", "myths": "tag-guide",
        "urgent": "tag-urgent",
    }
    return mapping.get(t, "tag-guide")

def asset_versions(index_html):
    """Current ?v= cache-buster for each shared asset, read from blog/index.html."""
    versions = {}
    for asset in ("components.js", "style.css"):
        m = re.search(re.escape(asset) + r"\?v=(\d+)", index_html)
        if m:
            versions[asset] = m.group(1)
    return versions


def normalize_asset_versions(html, versions):
    """Re-stamp components.js / style.css ?v= to the versions the site uses now.

    js/ and css/ are served immutable for a year, so a post carrying a stale
    ?v= pins its visitors to a year-old cached script. Drafts sit in
    blog/drafts/ for weeks or months and are published verbatim, so their
    ?v= is routinely behind by the time this script runs -- which is how a
    stale draft reference silently becomes a stale live post. Re-stamping at
    publish time keeps every post on the same assets as the rest of the site.
    """
    for asset, ver in versions.items():
        html = re.sub(re.escape(asset) + r"\?v=\d+", asset + "?v=" + ver, html)
    return html


# ── main ─────────────────────────────────────────────────────────────

def main():
    if not os.path.isdir(DRAFTS):
        print("No drafts directory found. Nothing to publish.")
        return 1

    drafts = [f for f in os.listdir(DRAFTS) if f.endswith(".html")]
    if not drafts:
        print("No drafts to publish.")
        return 1

    # Read all drafts, pick the one with the earliest date
    candidates = []
    for fname in drafts:
        path = os.path.join(DRAFTS, fname)
        with open(path) as f:
            html = f.read()
        meta = extract_meta(html)
        meta["filename"] = fname
        meta["slug"] = fname.replace(".html", "")
        candidates.append(meta)

    candidates.sort(key=lambda x: x["date"])
    pick = candidates[0]
    slug = pick["slug"]
    src = os.path.join(DRAFTS, pick["filename"])
    dst = os.path.join(POSTS, pick["filename"])

    print(f"Publishing: {pick['title']} ({pick['date']})")

    # 1. Copy draft to posts/, re-stamping the shared-asset cache-busters to
    #    whatever blog/index.html uses right now (we delete the draft at the
    #    very end, so a crash mid-run leaves the draft intact for retry)
    with open(INDEX) as f:
        versions = asset_versions(f.read())
    with open(src, newline="") as f:
        draft_html = f.read()
    with open(dst, "w", newline="") as f:
        f.write(normalize_asset_versions(draft_html, versions))

    # 2. Update blog/index.html — insert card after Welcome card
    with open(INDEX) as f:
        idx = f.read()

    card = f'''            <a href="posts/{slug}" class="blog-list-card">
                <div class="blog-list-card-body">
                    <span class="blog-tag {tag_class(pick['tag'])}">{pick['tag']}</span>
                    <h2>{pick['title']}</h2>
                    <p>{pick['description']}</p>
                    <div class="blog-list-card-meta">{date_human(pick['date'])} · {pick['readTime']}</div>
                </div>
                <span class="blog-list-card-arrow" aria-hidden="true">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                </span>
            </a>

'''

    # Insert after the opening blog-list-cards div, before the first card
    marker = '<div class="blog-list-cards fade-in">\n'
    if marker in idx:
        pos = idx.index(marker) + len(marker)
        idx = idx[:pos] + card + idx[pos:]
    with open(INDEX, "w") as f:
        f.write(idx)

    # 3. Update posts.json — prepend
    with open(PJSON) as f:
        posts_data = json.load(f)
    # posts.json may be {"posts": [...]} or a bare [...]
    if isinstance(posts_data, dict) and "posts" in posts_data:
        posts_list = posts_data["posts"]
    else:
        posts_list = posts_data
    posts_list.insert(0, {
        "title": pick["title"],
        "description": pick["description"],
        "url": f"blog/posts/{pick['filename']}",
        "date": pick["date"],
        "readTime": pick["readTime"],
        "tag": pick["tag"]
    })
    with open(PJSON, "w") as f:
        json.dump(posts_data, f, indent=2)

    # 4. Update feed.xml — add item after <image> block, update lastBuildDate
    with open(FEED) as f:
        feed = f.read()

    item = f'''    <item>
      <title>{pick['title']}</title>
      <link>https://waythroughproject.com/blog/posts/{slug}</link>
      <guid isPermaLink="true">https://waythroughproject.com/blog/posts/{slug}</guid>
      <pubDate>{rfc822(pick['date'])}</pubDate>
      <description>{pick['description']}</description>
      <author>matt@waythroughproject.com (Matt)</author>
    </item>

'''
    # Insert after </image> block
    img_end = "</image>"
    if img_end in feed:
        pos = feed.index(img_end) + len(img_end)
        feed = feed[:pos] + "\n\n" + item + feed[pos:]

    # Update lastBuildDate
    today = datetime.now(timezone.utc).strftime("%a, %d %b %Y 00:00:00 GMT")
    feed = re.sub(r'<lastBuildDate>[^<]+</lastBuildDate>',
                  f'<lastBuildDate>{today}</lastBuildDate>', feed)

    with open(FEED, "w") as f:
        f.write(feed)

    # 5. Update sitemap.xml — add URL
    with open(SMAP) as f:
        sm = f.read()
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_url = f'  <url><loc>https://waythroughproject.com/blog/posts/{slug}</loc><lastmod>{today_iso}</lastmod><changefreq>weekly</changefreq><priority>0.6</priority></url>\n'
    # Insert before </urlset>
    sm = sm.replace("</urlset>", new_url + "</urlset>")
    with open(SMAP, "w") as f:
        f.write(sm)

    # 6. All updates succeeded — now remove the draft
    os.remove(src)

    print(f"Done! Published {slug} and updated index, posts.json, feed.xml, sitemap.xml")
    return 0

if __name__ == "__main__":
    sys.exit(main())
