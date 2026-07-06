# Waythrough Project — Search & Analytics Deep Dive

**Date:** July 6, 2026
**Data windows:** Google Search Console = last 3 months · Google Analytics 4 = last 90 days (Apr 7 – Jul 5, 2026)

---

## The headline

Traffic is growing fast and accelerating — clicks and impressions have climbed steadily since mid-May, and GA shows the same curve. The core problem isn't traffic, it's **conversion of impressions into clicks**: the site earns 31,200 impressions but only 295 clicks (0.9% CTR). The good news is the reasons are now specific and fixable, and roughly a third of that gap comes from one page returning almost nothing.

---

## Where you stand

| Metric | Value | Read |
|---|---|---|
| GSC clicks (3mo) | 295 | Small but climbing steeply since mid-May |
| GSC impressions (3mo) | 31,200 | Strong visibility |
| GSC average CTR | 0.9% | Low — dragged down by unconvertible branded impressions (see #1) |
| GSC average position | 16.3 | Page 2 territory; several key pages just off page 1 |
| GA active users (90d) | 469 | Matches the GSC growth curve |
| GA engagement rate | 43.8% | Healthy for an informational resource |
| GA avg engagement/user | 1m 35s | Solid |
| Device mix | **65% mobile**, 34% desktop | Mobile-first audience — prioritize accordingly |
| Key events (conversions) | **0** | Nothing is being measured as a success action |

**Channel mix (GA, sessions):** Organic Search 55% · Direct 29% · **AI Assistants 7.7%** · Unassigned 6% · Referral 2% · **Organic Social ~0% (1 session)**

---

## Prioritized opportunities

### 1. The Section 8 Tracker eats ~15% of your impressions and returns ~0 clicks *(confirmed)*

`/resources/tools/section-8-tracker` pulled **4,690 impressions at position 4.3 with 1 click (0% CTR)** — about 15% of all site impressions.

I confirmed *why*: this one page ranks for the entire "Riverton Housing Authority" branded cluster —

| Query | Impressions | Clicks | Position |
|---|---|---|---|
| "riverton housing authority" | 906 | 0 | 6.5 |
| "rivertonhousing.org" | 459 | 0 | 1.5 |
| "riverton housing authority" housing choice voucher | 195 | 0 | 3.4 |
| "riverton housing authority" wyoming | 161 | 0 | 2.5 |
| "riverton housing authority" official | 133 | 0 | 6.6 |
| "www.rivertonhousing.org" | 108 | 0 | 1.6 |

These are **navigational searches** — people want that specific Wyoming authority's own website, so they don't click a generic tool. This inflates impressions, tanks your site-wide CTR, and spends crawl budget for nothing.

**What to do (pick your appetite):**
- **Highest upside:** build real, useful per-authority pages (e.g. `/housing-authority/riverton-wy`) with contact info, waitlist status, voucher details, and a "how to apply" walkthrough. You *already rank page 1* for these names with a bare tool — a page that actually answers the query could convert a chunk of ~5,000 wasted impressions into visits, and this pattern repeats for every housing authority.
- **Quick fix:** rewrite the tracker's `<title>`/meta so the snippet earns clicks for authority-name searches.
- **At minimum:** know that your "real" CTR on informational content is much healthier than 0.9% once this noise is set aside — don't over-react to the headline number.

### 2. Rewrite titles & meta descriptions on page-1 pages with abnormally low CTR *(fastest wins — minutes each)*

These already rank on page 1 but get far fewer clicks than their position should earn. The snippet is the lever:

| Page | Position | CTR | Impressions |
|---|---|---|---|
| `/resources/cities/san-francisco` | 8.2 | 0.2% | 563 |
| `/resources/guides/how-to-appeal-housing-denial` | 8.5 | 1.4% | 2,329 |
| `/resources/guides/how-long-does-section-8-take` | 8.2 | 1.0% | 489 |

A position-8 result should typically see ~2–3% CTR. Front-load the keyword, add the year, use a concrete number or benefit, and match the searcher's intent. On the appeal-denial page alone, going from 1.4% to 3% roughly doubles its clicks.

### 3. Push three high-demand pages from page 2 onto page 1

Lots of impressions, stuck just out of reach:

| Page | Position | Impressions | Clicks | Note |
|---|---|---|---|---|
| `/resources/guides/how-to-apply-section-8` | **25.0** | 1,454 | 11 | Core, high-intent query stuck on page 3 — biggest ceiling |
| `/resources/cities/milwaukee` | 17.5 | 2,009 | 35 | Already your #1 clicker *from page 2* — page 1 would multiply it |
| `/resources/states/florida` | 14.0 | 914 | 2 | |
| `/resources/states/georgia` | 17.4 | 610 | 0 | |
| `/resources/guides/document-checklist` | 18.6 | 479 | 3 | |

Levers: deepen the content, add internal links from related guides, tighten on-page SEO (H1/headers, FAQ schema). Milwaukee clearly resonates (top clicks *and* good on-site engagement) — it's the best bet for a fast page-1 breakthrough.

### 4. Turn on conversion tracking — you currently have 0 key events

GA is recording `page_view`, `scroll`, `click`, and `form_start` (fired 5×), but **none are marked as key events**, so you can't measure what actually helps users. Define 2–3 key events — e.g. outbound "apply / contact your housing authority" clicks, template downloads, and `form_submit`. Without this, you can't tell whether the fixes above are working.

### 5. Indexing hygiene

380 pages indexed, 551 not. Most "not indexed" is normal (214 canonical alternates, 149 redirects). Two buckets are worth action:
- **56 "Not found (404)"** — real broken URLs Google tried to crawl. Find and fix or redirect them (likely stale internal links).
- **127 "Crawled / Discovered – currently not indexed"** — Google chose not to index these, which usually signals thin or too-templated content (relevant for the state/city page template). Strengthen the weakest with unique local detail, or consolidate. *(This is improving — "Discovered" dropped from ~154 to 73.)*

### 6. Lean into what's already working

- **Spanish content punches above its weight.** `/es/recursos/estados/oklahoma` gets 13.6% CTR (pos 6.7); "refugio para personas sin hogar" 20% CTR. Less competition, high intent, underserved audience — worth expanding. (Counter-example: "proteccion al inquilino" ranks 37.6 — a content gap to fill.)
- **AI Assistants are 7.7% of sessions and rising.** ChatGPT / Perplexity / Gemini are citing the site — a free, growing channel. Clean, factual, well-structured content with clear steps and definitions is exactly what gets cited; keep leaning that way.
- **Organic Social is ~0.** If social is meant to be a channel, either it isn't linking back or isn't tagged (UTMs). Low priority while SEO is working, but it's a real gap.
- **65% mobile** — test every title, layout, and speed change on a phone first.

---

## If you only touch three things this week

1. **Rewrite titles/meta** on the low-CTR page-1 pages in #2 (San Francisco, appeal-denial, how-long-does). Minutes of work, immediate impact.
2. **Beef up `how-to-apply-section-8` and Milwaukee** to crack page 1 (#3) — the two highest-ceiling pages.
3. **Add key-event tracking** (#4) so you can actually measure whether 1 and 2 worked.

---

*Note on the 0.9% CTR: it looks alarming but is heavily distorted by the ~5,000 unconvertible branded impressions on the tracker page. Your informational pages already see 2–33% CTR when intent matches. The real work is ranking better (positions 14–25 → page 1) and writing snippets that earn the click.*
