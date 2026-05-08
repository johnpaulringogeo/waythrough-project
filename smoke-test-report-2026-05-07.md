# Waythrough Project — Smoke Test Report
**Date:** May 7, 2026  
**Tester:** Claude (Senior UX Engineer role)  
**Scope:** Full site smoke test across all sections

---

## Summary

Tested all major sections of waythroughproject.com: homepage, navigation, interactive tools, guides (49), state pages (51), letter templates, Spanish pages, landlord section, printable guides, and 404 page.

**Found and fixed 8 bugs** (7 truncated guide files + 1 misplaced script tag). All fixes are local and ready for `git push`.

---

## Bugs Fixed This Session

### 1. Truncated Guide Files (7 files)
These files were cut off mid-content, missing closing tags and/or LD+JSON structured data:

| File | Truncation Point |
|------|-----------------|
| `criminal-records-and-housing.html` | Mid-word in related resources ("File a Discrimination Com") |
| `how-to-appeal-housing-denial.html` | Mid-tag in related resources |
| `waiting-list-strategies.html` | Mid-related resources section |
| `how-to-find-your-pha.html` | Mid-related resources section |
| `emergency-rental-assistance.html` | LD+JSON block cut off after `"@context": "ht` |
| `how-to-file-housing-discrimination-complaint.html` | LD+JSON block cut off after `<script type="appli` |
| `how-to-recover-security-deposit.html` | LD+JSON block cut off after `<sc` |

**Fix:** Completed the related resources sections, added proper LD+JSON structured data, and added closing `</body></html>` tags to all 7 files.

**Impact:** On the live site, these pages render without a footer-area related resources section (or show garbled text like "File a Discrimination Com"). The browser auto-closes tags so the nav/footer still appear, but the content is visibly broken at the bottom.

### 2. printable.html — Script in Wrong Location
The `components.js` script tag was in the `<head>` instead of before `</body>`.

**Fix:** Moved the script to the correct position before `</body>`.

**Note:** This file also has trailing null bytes on the last line. This is cosmetic (doesn't affect rendering) but couldn't be cleaned because the bash sandbox was unavailable. Can be cleaned with: `truncate -s $(grep -c '' resources/printable.html) resources/printable.html` or similar.

---

## Known Issues (Not Fixed — Require Architecture Decisions)

### 1. Rent Estimator Tool — Completely Non-Functional
**Location:** `/resources/tools/rent-estimator`  
**Problem:** The HUD User API (`huduser.gov`) requires a Bearer token in the Authorization header. This triggers a CORS preflight (OPTIONS) request, and the HUD API server doesn't return `Access-Control-Allow-Origin` headers, so the browser blocks the response.

**What works:** State dropdown has a hardcoded fallback array (`populateStatesFallback()`), so states load.  
**What doesn't:** County lookup and ZIP code lookup both fail with `TypeError: Failed to fetch`.

**Recommended fix:** Add a Cloudflare Worker proxy that forwards requests to the HUD API server-side (no CORS issues). This is a 30-line Worker that adds the Authorization header and returns the response. No changes to the existing Cloudflare Pages setup needed — Workers are a separate product that can be added alongside Pages.

### 2. Spanish Section — English Navigation
**Location:** All `/es/` pages  
**Problem:** `components.js` injects the same English nav bar on every page regardless of language. Spanish pages show English navigation, search, and footer.

**Options:**
- A. Detect `lang="es"` on `<html>` in components.js and inject Spanish nav/footer
- B. Add a `data-lang` attribute and maintain a translation map in components.js
- C. Accept this limitation and add a small "Esta página está en español" banner

### 3. Spanish Pages — "IN THIS GUIDE" Not Localized
**Location:** Spanish guide pages (e.g., `/es/recursos/donde-empezar`)  
**Problem:** The table of contents heading is hardcoded as "IN THIS GUIDE" in English. Should be "EN ESTA GUÍA" for Spanish pages.

**Fix:** Update the TOC generation in components.js to check the page language and use the appropriate heading text.

---

## Sections Tested — All Clear

| Section | Pages | Status |
|---------|-------|--------|
| Homepage | 1 | Clean — curated sections, nav, footer all working |
| Navigation | All nav links | All dropdown menus, breadcrumbs working |
| Browse pages | `/series`, `/sermons` | Filters, search, badges working |
| Interactive tools | Budget calculator, benefits calculator, eligibility screener, compare programs | All client-side JS tools working correctly |
| Rent estimator | 1 | Broken (see Known Issues above) |
| Letter templates | 4 (repair request, denial appeal, accommodation request, fair housing) | All rendering correctly with placeholder text |
| Guides | 49 total | 42 clean, 7 truncated (now fixed locally) |
| State pages | 51 (50 states + DC) | All structurally sound |
| State index | 1 | Clean — SOI badge system working |
| Landlord section | 2 pages | Clean |
| Spanish section | 3+ pages | Rendering but with English nav (see Known Issues) |
| Printable guides | 1 index page | Fixed script placement |
| 404 page | 1 | Well-designed — nav, friendly message, Popular Resources, action buttons |
| Blog | Multiple posts | Checked in previous session — duplicate components.js fixed |

---

## UX Recommendations

### High Priority
1. **Fix or remove the rent estimator.** A broken tool hurts credibility. Either add a Cloudflare Worker proxy or replace with a simpler "look up your area's FMR" link to HUD's own tool.

2. **Run a file integrity check after any bulk content creation.** The truncated files suggest a batch process that occasionally produces incomplete output. Consider adding a simple CI check: `grep -rL '</html>' resources/guides/ resources/states/` to catch any file missing its closing tag.

### Medium Priority
3. **Localize the Spanish nav.** Even a partial solution (translating the main nav links) would make the Spanish section feel intentional rather than like an afterthought.

4. **Add print styles review.** The printable guides page promises clean printing, but the actual print CSS hasn't been verified recently. Worth a Ctrl+P test on a few guides.

### Low Priority
5. **Letter templates could be interactive.** Currently they use static `[YOUR NAME]` placeholders. A simple JS enhancement could add input fields that auto-fill the template — would make them significantly more useful for case managers.

6. **Consider adding a "Last updated" date to state pages.** Housing laws change, and users may want to know how current the information is. Several guides already have "Updated May 2026" — state pages could benefit from the same.

---

## Files Modified (Ready for Git)

```
resources/guides/criminal-records-and-housing.html
resources/guides/how-to-appeal-housing-denial.html
resources/guides/waiting-list-strategies.html
resources/guides/how-to-find-your-pha.html
resources/guides/emergency-rental-assistance.html
resources/guides/how-to-file-housing-discrimination-complaint.html
resources/guides/how-to-recover-security-deposit.html
resources/printable.html
```

All changes are local. Run `git add -A && git commit -m "Fix 7 truncated guide files and printable.html script placement" && git push` to deploy.
