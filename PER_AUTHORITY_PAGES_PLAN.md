# Per-Housing-Authority Pages — Build Plan

**Date:** July 6, 2026
**Status:** Plan + scaffold, ready to execute (not yet built)
**Owner:** Matt

---

## Why

Google Search Console shows the single biggest wasted opportunity on the site: the **Section 8 Tracker tool page pulls ~4,690 impressions (about 15% of all site impressions) at average position 4.3 but earns essentially 0 clicks.** It ranks for a large cluster of *branded, navigational* searches for specific housing authorities — confirmed examples, all with 0 clicks:

| Query | Impressions | Position |
|---|---|---|
| "riverton housing authority" | 906 | 6.5 |
| "rivertonhousing.org" | 459 | 1.5 |
| "riverton housing authority" housing choice voucher | 195 | 3.4 |
| "riverton housing authority" wyoming | 161 | 2.5 |
| "riverton housing authority" official | 133 | 6.6 |
| "www.rivertonhousing.org" | 108 | 1.6 |

People searching "riverton housing authority" want *that authority's* information. A generic tool page doesn't match the intent, so nobody clicks. But the site **already ranks page 1** for these names — which means a page that actually answers the query ("here's the Riverton Housing Authority's contact info, waitlist status, and how to apply") could convert a meaningful slice of thousands of currently-wasted impressions into real visits. And this pattern repeats for **every** housing authority in the country.

This is a content-and-product opportunity, not a quick fix. This document is the plan to capture it safely.

---

## The core risk to design around

The site already has **~127 pages that Google "crawled/discovered but chose not to index."** That is a thin-content signal. If we mass-generate hundreds of near-identical authority stubs, Google will treat them the same way and we'll have spent effort for nothing — or hurt the site's overall quality signal.

**Therefore the guiding rule: each authority page must contain genuinely useful, specific information that a searcher (or an AI assistant) would find valuable.** Quality per page beats quantity of pages. We start small, prove indexing + engagement, then scale.

---

## What a good authority page contains

Each page answers the questions behind the branded search:

1. **Identity & contact** — official authority name, address, phone, email, official website (linked, `rel="nofollow"` optional), office hours.
2. **Jurisdiction** — which city/county/ZIP codes it serves.
3. **Programs offered** — Housing Choice Voucher (Section 8), Public Housing, Project-Based Vouchers, any specialty programs.
4. **Waiting-list status** — open/closed per program, with a "last checked" date. This is the highest-value, most-searched fact.
5. **How to apply** — steps specific to this authority, linking to the general [how-to-apply-section-8 guide](/resources/guides/how-to-apply-section-8).
6. **Payment standards / FMR context** — link to the existing rent tools where relevant.
7. **Source links** — official pages the data came from (builds trust + helps E-E-A-T).
8. **Clear disclaimer** — "Waythrough is an independent resource, not the [Authority]. For official applications, use the links above." This is important: it sets intent expectations and avoids impersonation.

A page with all of the above is *not* thin — it's often more useful and better-organized than the authority's own site.

---

## URL structure

Recommended: `/housing-authorities/<slug>` (new top-level section), with an index hub at `/housing-authorities/`.

- Example: `/housing-authorities/riverton-wy`
- Slug pattern: `<authority-locale>-<state>` to disambiguate (many "Housing Authority of the City of X").
- Spanish mirror: `/es/autoridades-de-vivienda/<slug>` (bilingual parity, matching the rest of the site).

Rationale for a dedicated section (vs. nesting under `/resources/cities/`): authorities don't map 1:1 to the 50 city pages — there are thousands, often several per metro. A dedicated namespace keeps the taxonomy clean and lets the hub grow independently.

---

## Data model (per-authority JSON)

Reuse the existing `data/` + Jinja + `scripts/generate_page.py` pipeline. Add `data/authorities/<slug>.json`:

```json
{
  "slug": "riverton-wy",
  "kind": "authority",
  "en": {
    "name": "Riverton Housing Authority",
    "city": "Riverton",
    "state": "WY",
    "serves": "Riverton and Fremont County, Wyoming",
    "address": "2020 Meadow Lark Ln, Riverton, WY 82501",
    "phone": "307-856-XXXX",
    "email": "",
    "official_url": "https://www.rivertonhousing.org",
    "hours": "Mon–Fri, 8am–4:30pm",
    "programs": ["Housing Choice Voucher (Section 8)", "Public Housing"],
    "waitlists": [
      { "program": "Housing Choice Voucher", "status": "closed", "checked": "2026-07-01", "notes": "Opens periodically; check the official site." },
      { "program": "Public Housing", "status": "open", "checked": "2026-07-01", "notes": "" }
    ],
    "how_to_apply_html": "<p>Applications are submitted ... </p>",
    "sources": [
      { "label": "Riverton Housing Authority — official site", "url": "https://www.rivertonhousing.org" },
      { "label": "HUD PHA contact record", "url": "https://www.hud.gov/..." }
    ],
    "updated": "July 2026"
  },
  "es": { "...": "mirror of the above, professionally translated with full diacritics" }
}
```

**Data sourcing:** HUD publishes a public PHA dataset (name, address, phone, programs, jurisdiction) that can seed the identity fields for every authority at once. Waitlist status is the volatile part — seed it from the official site and stamp a "checked" date; do not fabricate. Fields left blank simply don't render.

---

## Template & schema

Add `templates/authority.html.j2`, modeled on the existing `city.html.j2` (same `<head>`, nav/footer via `components.js`, breadcrumb + FAQ JSON-LD blocks). Add one authority-specific structured-data block, `GovernmentOffice` or `Organization`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "GovernmentOffice",
  "name": "{{ data.name }}",
  "address": { "@type": "PostalAddress", "streetAddress": "{{ ... }}", "addressLocality": "{{ data.city }}", "addressRegion": "{{ data.state }}" },
  "telephone": "{{ data.phone }}",
  "url": "{{ data.official_url }}",
  "areaServed": "{{ data.serves }}"
}
</script>
```

The title/meta strategy is what captures the branded search:

- **Title:** `{{ name }} — Section 8 Waitlist Status, Contact & How to Apply | Waythrough`
- **Meta:** `{{ name }} in {{ city }}, {{ state }}: current Section 8 / Housing Choice Voucher waitlist status, phone and address, programs offered, and step-by-step how to apply.`

This directly promises what the searcher wants (status, contact, how to apply) — the reason to click even when it's not the official `.gov`.

---

## Generator

`scripts/generate_page.py` already renders EN + ES from JSON and accepts file globs. Extend it to recognize `"kind": "authority"` and use `authority.html.j2`, writing to `/housing-authorities/<slug>.html` and `/es/autoridades-de-vivienda/<slug>.html`. Command stays the same shape:

```
python scripts/generate_page.py data/authorities/riverton-wy.json
```

Then add generated URLs to `sitemap.xml` (extend whatever step already emits the city/state entries), and add the hub link to the footer in `js/components.js` (as we just did for City Guides).

---

## Internal linking

- The new `/housing-authorities/` hub links to every authority; link the hub from the footer and the resources page.
- Each **city page** links to the authorities serving that city (e.g., Milwaukee → HACM).
- Each **state page** links to its authorities.
- The **Section 8 Tracker tool** links each result to its authority page — turning the tool from a dead-end into a gateway.

---

## Rollout (phased — this is the safe part)

**Phase 0 — Pilot (10 authorities).** Build the ones already proven to have search demand from GSC: Riverton (WY), plus the authorities behind your other branded-search clusters and your top city pages (HACM Milwaukee, HACLA Los Angeles, NYCHA, etc.). Full, hand-checked data. Ship, submit to GSC, and **wait 2–3 weeks.**

**Phase 1 — Measure.** In GSC, confirm the pilot pages get **indexed** (not "crawled – not indexed") and start taking clicks on the branded queries. In GA, confirm engagement time and outbound-to-official clicks (now tracked). If the pilot indexes and converts, the model works.

**Phase 2 — Scale in batches.** Seed identity data from the HUD PHA dataset, generate in batches of ~50, and spot-check. Prioritize authorities that already appear in your GSC query data with impressions. Never ship a batch whose pages would be thin — if you don't have real per-authority data, don't publish the page yet.

**Phase 3 — Maintain.** Waitlist status goes stale. Add a "last checked" date to every page (already in the schema) and a lightweight process (or scheduled task) to re-verify the highest-traffic authorities monthly.

---

## Success criteria

- Pilot pages **indexed** within 3 weeks (vs. the current ~127 not-indexed).
- Branded authority queries move from **0 clicks** to a measurable CTR.
- `outbound_click` events with `is_authority: true` (from the new tracking) rise — proof users are reaching official resources through us.
- No increase in the site-wide "crawled – not indexed" count (the thin-content guardrail).

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Thin/duplicate pages → not indexed, quality drag | Real per-authority data; start with a pilot; never ship thin batches |
| Stale waitlist info misleads users | "Last checked" date on every page; link to official source; monthly re-check of top pages |
| Looking like we impersonate the authority | Prominent "independent resource, not the Authority" disclaimer; link official site clearly |
| Scale/maintenance burden (thousands of PHAs) | Only build pages with real demand (GSC) and real data; automate identity from HUD dataset |
| Vercel/Cloudflare build size | Static pages on Cloudflare Pages scale fine; no serverless functions added |

---

## First concrete step

Create `data/authorities/riverton-wy.json` with verified data, add `templates/authority.html.j2`, extend the generator, build that one page, and manually submit it in GSC's URL Inspection → Request Indexing. That single page is the experiment that de-risks the entire initiative.
