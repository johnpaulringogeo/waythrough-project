# GSC Content Strengthening Plan

**Drafted:** 2026-05-28
**Goal:** Move all "Crawled — currently not indexed" URLs to indexed, and proactively reinforce weak pages before they get flagged.

---

## Diagnosis

The GSC snapshot from 2026-05-26 flagged 20 URLs. Two important signals:

1. **Only one city (`colorado-springs`) was flagged**, but every other state page is structurally identical to Kansas (10–13 KB, same template). Kansas is the canary — the rest will follow.
2. **Kansas was already enriched to ~24 KB and is still not indexed.** That means raw word count isn't the lever. Google sees the page as indistinguishable from neighboring state pages because the *structure*, *headings*, and *generic framing* repeat across the set. The fix is **substantive, locally-grounded content per page** — the same playbook that just worked on 46 city pairs.

The proven city pattern was: real named PHA + waitlist status with a date + named local rental-assistance programs with phone numbers + state tenant-law citations + named shelters. That's what we'll port to states, guides, and the rest.

---

## Phase 1 — Close out cities (Batch 11)

**Scope:** colorado-springs, fresno, long-beach, tulsa (4 pairs, 8 HTML files)

Notes:
- `colorado-springs` EN is already Edit-tool enriched (19 KB) but its ES is still a 12 KB stub. Doing it through the generator gives parity and lets us retire the Edit-tool variant.
- The other three are 10 KB stubs on both sides.

**Estimated effort:** 1 session, same pattern as batches 1–10.

**Done criteria:** All 50 cities are JSON-generator-driven; smoke tests green.

---

## Phase 2 — State pages (largest workstream)

**Scope:** 50 states + DC = 51 pages. None are currently JSON-generator-driven.

**Why this is bigger than cities:** state pages need a different content shape than city pages. The city pattern was "what to do *tonight in this city*." The state pattern should be "the legal and program framework that applies *anywhere in this state*, plus where to find your city's PHA." Different content, but the same depth bar.

### State page schema (proposed)

Each `data/states/<slug>.json` should produce a page with:

1. **Quick numbers** — statewide 211, state Attorney General consumer line, state legal aid hotline, state DHS or housing finance agency line, state tenant rights hotline if one exists.
2. **Statewide PHAs** — the state-level voucher program (TDHCA in TX, HCR in NY, IHDA in IL, etc.) plus a directory link to local PHAs.
3. **State tenant law (the substantive section)** — named statutes by chapter/section, with the distinctive features that differ from the average state. This is what makes the page un-templated.
   - Source-of-income protection (status + statute)
   - Rent control / preemption posture
   - Notice periods for nonpayment, lease violations, no-fault
   - Security deposit cap, interest, return deadline
   - Habitability framework
   - Self-help eviction penalties
   - Retaliation window
   - Court venue (which court hears evictions in this state)
   - Recent statutory changes (the SB/HB/AB numbers that matter)
4. **Eviction process timeline** — concrete days from notice to lockout in this state.
5. **State-level emergency assistance** — state ERAP successor programs, state-funded Homelessness Prevention dollars, state CAA network, state LIHEAP administration.
6. **Major cities cross-reference** — link to every city page within the state that we have content for.
7. **FAQs** — 5 state-specific questions that don't repeat what's on the city page.

### State page batching

States are not equal. Prioritize by:
1. **Already flagged** — Kansas (do first, then "Validate Fix" in GSC)
2. **States with completed city pages** — these get the most internal link juice and are most likely to be crawled. The 31 states + DC already covered by city work.
3. **High-population states without city pages yet** — they'll get crawled too.
4. **The long tail** — small states last.

**Suggested batch order (4 states per batch, ~12 batches):**
- Batch S1: Kansas + 3 city-rich states with weak HTML (California, Texas, New York — even though they have content, they're 11–12 KB stubs)
- Batch S2: Florida, Illinois, Arizona, North Carolina
- Batch S3: Ohio, Pennsylvania, Massachusetts, Michigan
- Batch S4: Washington, Oregon, Colorado, Tennessee
- Batch S5: Virginia, Maryland, Indiana, Wisconsin
- Batch S6: Missouri, Minnesota, Georgia, Kentucky
- Batch S7: Nevada, New Mexico, DC, Oklahoma
- Batch S8: Alabama, Louisiana, South Carolina, Iowa
- Batch S9: Connecticut, Mississippi, Arkansas, Utah
- Batch S10: Nebraska, West Virginia, New Jersey, New Hampshire
- Batch S11: Maine, Rhode Island, Delaware, Hawaii, Idaho
- Batch S12: Vermont, Montana, North Dakota, South Dakota, Wyoming, Alaska

**Per batch:** 4 states researched + JSON + generator run + commit. Same pacing as cities.

---

## Phase 3 — GSC-flagged non-city, non-state URLs

These are the rest of the original 20 from the 2026-05-26 report.

### Guides (8 pages, all flagged)
1. `resources/guides/how-to-file-housing-discrimination-complaint`
2. `resources/guides/criminal-records-and-housing`
3. `resources/guides/rebuilding-credit-for-housing`
4. `resources/guides/how-to-request-reasonable-accommodation`
5. `resources/guides/how-to-handle-recertification`
6. `resources/guides/how-to-talk-to-your-pha`
7. `resources/guides/what-to-expect-at-inspection`
8. `resources/guides/understanding-rent-calculation`

**Treatment per guide:** named federal and state-level program references, step-by-step (HUD-VASH-style) procedures, real document examples, FAQPage JSON-LD, internal links to the cities/states pages that mention the topic. Add HowTo structured data where applicable.

**Batching:** 2 guides per session is realistic if we keep the depth bar high.

### Audience pages (2 flagged)
- `who-we-help/seniors.html`
- `who-we-help/disabilities`

**Treatment:** named programs (HCBS waivers, ADRC network, Mainstream vouchers for non-elderly disabled, Section 202/811, LIHEAP cooling assistance for vulnerable adults), real eligibility numbers, and lots of internal links into the city/state network we just built.

### `/for-landlords/` (1 flagged)
**Treatment:** convert from generic "what is Section 8" to a substantive PHA-payment-process guide with named payment standards (we have these from the city research), inspection details, voucher tenant rights from the landlord side, and the SOI-protection map.

### Tools (3 flagged)
- `resources/tools/letter-generator`
- `resources/tools/compare-programs`
- `es/recursos/herramientas/calculadora-presupuesto`

**Treatment:** these are interactive — likely flagged because the static HTML shell is thin without JS. Server-render the introduction copy, FAQ section, and example outputs. Add structured data describing what the tool does.

### Spanish blog posts (2 flagged)
- `es/blog/posts/consejos-busqueda-vivienda-voucher`
- `es/blog/posts/propietario-rechaza-voucher`

**Treatment:** review for English-mirror parity, add Spanish-language source citations (national newspaper coverage, Spanish-language legal aid orgs), expand examples.

### No-action
- `blog/feed.xml` — RSS feed, correctly not indexable.

---

## Phase 4 — Proactive content audit

After Phases 1–3, run a programmatic sweep of the site looking for pages that share the same risk profile as the flagged ones.

### Audit script (to write)

`scripts/audit_thin_content.py` should produce a CSV with one row per HTML page, columns:

- URL path
- File size (bytes)
- Word count (text content only, strip nav/footer)
- Unique-substring score vs. cohort (how many 6-grams in the body appear in 3+ other pages in the same folder)
- Outbound internal link count
- Inbound internal link count (requires building a site graph)
- Has FAQPage / HowTo / BreadcrumbList JSON-LD?
- Last-modified date
- Crawled-not-indexed flag (yes if it appears in the latest GSC export)

### Audit thresholds (initial proposal)

Flag a page as **at-risk** if it meets ≥2 of:
- Word count < 600
- Unique-substring score < 0.4 (i.e., >60% of its body text n-grams also appear in cohort)
- Inbound internal link count < 3
- No structured data
- Last-modified > 90 days

### Then

For each at-risk page, decide:
- **Strengthen** (add named programs, citations, FAQ schema)
- **Consolidate** (merge into a nearby canonical page if duplicative)
- **Noindex** (if the page is genuinely a thin landing or utility)

### Refresh cadence

- Re-export GSC's Crawled-not-indexed report monthly.
- Re-run the audit script monthly.
- Track trend: count of at-risk pages over time should fall.

---

## Sequencing recommendation

If we're pacing this realistically:

1. **Now (this session):** Batch 11 cities → commit → smoke test. Sites is then 50/50 cities. (~1 session)
2. **Next:** State batch S1 (Kansas + CA + TX + NY). Kansas is highest priority because it's the named flag. (~1 session)
3. **Then:** Roll through state batches S2–S12 over ~11 more sessions. Smoke-test the heaviest 4 (CA, TX, NY, FL) end-to-end. (~11 sessions)
4. **Then:** Phase 3 — guides, audience, landlords, tools, Spanish blog posts. (~4–6 sessions)
5. **Then:** Phase 4 — write `audit_thin_content.py`, run it, triage the results, fix the top 10 at-risk pages. (~2–3 sessions)

**Total rough estimate:** 18–22 sessions of work to close the GSC gap and establish ongoing audit hygiene.

---

## Decisions I need from you

1. **State page depth:** do you want every state to hit the same ~25 KB / 4,000-word bar as the city pages, or a lighter ~12–15 KB bar with a more aggressive cross-reference network? (My recommendation: same bar — that's what works.)
2. **Bilingual states:** the existing state pages don't have ES counterparts. Do you want me to build the JSON with EN + ES from the start (50 EN + 50 ES = 100 pages), or EN only and Spanish in a later phase?
3. **GSC export refresh:** want me to ask you to re-pull the GSC Crawled-not-indexed report before Phase 4 so the audit uses fresh data?
4. **Audit script output:** OK to drop the CSV in `_audit/thin_content_<date>.csv` (gitignored) so it doesn't pollute the repo?

Answer those four and I'll start Batch 11 immediately.
