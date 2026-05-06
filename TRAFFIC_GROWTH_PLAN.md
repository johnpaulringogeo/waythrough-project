# Waythrough Project — Traffic Growth & Retention Plan

**Based on:** Google Search Console data (3 months, as of May 6, 2026)
**Cloudflare:** Dashboard was unresponsive during review — revisit for visitor-level analytics

---

## Current State

| Metric | Value | What It Means |
|--------|-------|---------------|
| Total impressions (3 mo) | 1,030 | Google is showing you in results — that's good for a new site |
| Total clicks (3 mo) | 12 | Very few people are clicking through |
| Average CTR | 1.2% | Below the ~3-5% typical for informational content |
| Average position | 23.5 | Most results on page 2-3 of Google (page 1 = positions 1-10) |
| Pages indexed | 64 of 183 | Only 35% of your site is in Google's index |
| Pages discovered, not indexed | 136 | Google knows about them but hasn't crawled them yet |
| Pages with redirect issues | 20 | www vs non-www or .html redirects eating crawl budget |
| Alternate canonical pages | 15 | Spanish pages or duplicate URL variants |
| Queries appearing for | 130 | Decent query diversity for a new site |

### Top Performing Pages (by clicks)

| Page | Clicks | Impressions |
|------|--------|-------------|
| How to Appeal Housing Denial (guide) | 3 | 160 |
| Housing Denial Appeal (template) | 3 | 64 |
| Homepage | 2 | 50 |
| Louisiana state page | 2 | 7 |
| Utility Allowances Explained (blog) | 1 | 31 |
| Indiana state page | 1 | 2 |

### High-Impression, Zero-Click Pages (biggest opportunities)

| Page | Impressions | What to do |
|------|-------------|------------|
| Idaho state page | 67 | Optimize title/description for click-through |
| How to File Housing Discrimination Complaint | 64 | Optimize title/description for click-through |
| New Hampshire state page | 39 | Optimize title/description for click-through |
| Where to Start | 38 | Optimize title/description for click-through |

### Top Search Queries

| Query | Impressions | Clicks |
|-------|-------------|--------|
| way through | 30 | 0 |
| hud eviction rules | 20 | 0 |
| waythrough | 7 | 0 |
| hud fair housing complaint | 5 | 0 |
| north dakota eviction process | 5 | 0 |
| tenant rights van nuys | 5 | 0 |
| renters rights in idaho | 4 | 0 |
| hud complaint online | 3 | 0 |
| idaho eviction laws | 3 | 0 |

---

## The Core Problem

The site has great content (183 pages) but Google has only indexed 35% of it. Of the indexed pages, most rank on page 2-3 (position 23.5 average), and the titles/descriptions aren't compelling enough to earn clicks even when they do appear (1.2% CTR).

This is a **crawl budget + content authority** problem, typical for new sites. The good news: Google already found 130 different queries to show you for — that's real demand. The path to traffic is getting indexed, getting to page 1, and getting clicked.

---

## Phase 1: Get Indexed (Weeks 1-2)

**Goal:** Move from 64 to 120+ indexed pages

### 1.1 Fix the redirect issues (20 pages)

Those 20 "page with redirect" entries are wasting crawl budget. Most likely causes:
- `www.waythroughproject.com` vs `waythroughproject.com` (I saw the Indiana page showing up with the www prefix in GSC)
- URLs with and without `.html` extensions
- URLs with and without trailing slashes

**Action:** Check Cloudflare redirect rules — ensure a single canonical redirect from www to non-www (or vice versa). Audit the 20 redirect URLs in GSC to identify the pattern.

### 1.2 Manual indexing requests for high-value pages

Use GSC's URL Inspection tool to request indexing for the top 10-15 pages that aren't indexed yet. Prioritize:
- State pages for high-population states (California, Texas, Florida, New York)
- Guide pages with the most search potential (eviction, Section 8, benefits)
- Tool pages (eligibility screener, budget calculator)

Google allows ~10 indexing requests per day.

### 1.3 Improve internal linking

Google is more likely to crawl and index pages that are well-linked internally. Right now the 50 state pages are likely only linked from the states index. Add contextual internal links:
- From guides to relevant state pages ("See specific rules for your state")
- From blog posts to related guides
- From the homepage to more deep pages
- Add a "Related Resources" section at the bottom of every guide page linking to 3-5 other relevant pages

### 1.4 Add lastmod dates to sitemap

The sitemap currently has 182 URLs. Adding `<lastmod>` dates tells Google which pages to prioritize re-crawling. This is a quick win.

---

## Phase 2: Improve Rankings (Weeks 2-4)

**Goal:** Move average position from 23.5 to under 15

### 2.1 Optimize titles and meta descriptions for top opportunity pages

The pages with high impressions but 0 clicks need better titles. Current titles are likely too generic or too long (the audit noted 92 titles over 60 chars).

**Priority pages to optimize:**
1. Idaho state page (67 impressions, 0 clicks)
2. How to File Housing Discrimination Complaint (64 impressions, 0 clicks)
3. New Hampshire state page (39 impressions, 0 clicks)
4. Where to Start (38 impressions, 0 clicks)
5. Utility Allowances Explained (31 impressions, 1 click)

**Title formula for state pages:** `[State] Tenant Rights & Housing Help — Waythrough Project`
**Title formula for guides:** `How to [Action] — Free Step-by-Step Guide`

### 2.2 Target the queries Google is already showing you for

The GSC data reveals what people actually search. Write or enhance content that directly targets these:

| Query cluster | Content action |
|---------------|---------------|
| "hud eviction rules" (20 imp) | Create a dedicated guide or expand existing eviction content with HUD-specific rules |
| "hud fair housing complaint" + "hud complaint online" (8 imp combined) | Your discrimination complaint guide is ranking — expand it, add step-by-step screenshots |
| "[state] eviction laws/process" | Enhance state pages with state-specific eviction timelines and laws |
| "[state] tenant rights" | Enhance state pages with tenant rights summaries |
| "renters rights in [state]" | These are direct matches for state pages — ensure titles include "Renters Rights" |

### 2.3 Add FAQ schema to high-value pages

You already have FAQPage JSON-LD on some pages. Add it to the top guide pages and state pages. FAQ rich results can dramatically increase CTR by showing expandable answers directly in search results.

---

## Phase 3: Increase Click-Through Rate (Weeks 3-6)

**Goal:** Move CTR from 1.2% to 3%+

### 3.1 Write compelling meta descriptions

Every high-impression page needs a meta description that:
- Starts with a benefit or answer ("Learn exactly how to...")
- Includes a credibility signal ("Based on real caseworker experience")
- Has a soft call to action ("Free guide with step-by-step instructions")
- Stays within 120-155 characters

### 3.2 Add structured data for rich results

Beyond FAQ schema, add:
- **HowTo schema** on step-by-step guides (appeals, applications, complaints)
- **BreadcrumbList** (already present — verify it's rendering in search results)
- **Article schema** on blog posts with datePublished/dateModified

### 3.3 Improve the homepage title tag

"Waythrough Project — Affordable Housing Help & Guides" is fine but doesn't target any search query. Consider:
"Free Affordable Housing Help — Section 8, HUD-VASH & More | Waythrough Project"

---

## Phase 4: Drive Non-Search Traffic (Weeks 4-8)

**Goal:** Build traffic sources beyond Google

### 4.1 Social media launch

This has been on the roadmap. The site has social icon placeholders in the footer. Prioritize:
- **TikTok/Instagram Reels:** Short-form videos explaining housing concepts (you have video scripts ready)
- **Facebook groups:** Affordable housing and tenant rights groups are highly active — share guides as helpful answers
- **Reddit:** r/povertyfinance, r/personalfinance, r/legaladvice, r/homeless — genuinely helpful answers with links to relevant guides

### 4.2 Community and forum outreach

Find where your audience asks questions:
- HUD.gov community forums
- Local PHA Facebook groups
- Veterans' forums (for HUD-VASH content)
- Social worker/caseworker professional networks

### 4.3 Backlink building through utility

Your interactive tools (eligibility screener, budget calculator, letter generator) are genuinely useful and linkable. Reach out to:
- Legal aid organizations
- Housing counseling agencies (HUD.gov lists them)
- University social work departments
- Nonprofit resource directories

One quality backlink from a .gov or .edu site is worth more than 100 from random blogs.

---

## Phase 5: Retain Visitors (Ongoing)

**Goal:** Reduce bounce, increase pages per session

### 5.1 Strengthen internal navigation

Add "Next Steps" sections to every page suggesting the logical next action:
- Read a guide about Section 8 → link to eligibility screener, state page, application guide
- Read a state page → link to relevant guides, tools, templates
- Use a tool → link to related guides and templates

### 5.2 Add breadcrumb navigation

Visual breadcrumbs (not just schema) help visitors orient themselves and explore more:
`Home > Resources > Guides > How to Appeal a Housing Denial`

### 5.3 "Related Resources" sidebar or bottom section

On every content page, show 3-5 related pages. Group by topic rather than type:
- If reading about eviction → show eviction prevention guide, tenant rights, letter templates, know-your-rights
- If reading about benefits → show calculator, SNAP guide, SSI guide, benefits cliff explainer

### 5.4 Consider a "Reading Path" feature

For someone brand new: Where to Start → Eligibility Screener → Relevant Program Guide → Application Steps → Document Checklist → State-Specific Info. Make this journey explicit with "Next step" buttons.

---

## Quick Wins (Can Do This Week)

1. **Request indexing** for top 10 un-indexed pages via GSC URL Inspection
2. **Fix redirect pattern** (www vs non-www) — check the 20 redirect URLs
3. **Rewrite titles** on the 5 highest-impression zero-click pages
4. **Add lastmod to sitemap.xml**
5. **Improve homepage title** to target a real search query
6. **Add internal links** from homepage and blog posts to deep guide/state pages

---

## Metrics to Track Monthly

| Metric | Current | 30-Day Target | 90-Day Target |
|--------|---------|---------------|---------------|
| Pages indexed | 64 | 120 | 170+ |
| Impressions/month | ~350 | 1,000 | 3,000 |
| Clicks/month | ~4 | 30 | 150 |
| Average CTR | 1.2% | 3% | 5% |
| Average position | 23.5 | 18 | 12 |
| Queries appearing for | 130 | 200 | 400 |
