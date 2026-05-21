# Content Accuracy Audit - Waythrough Project

**Date:** May 21, 2026  
**Scope:** 22 published blog posts, 19 draft blog posts, 3 stories, 4 for-landlords pages, 4 who-we-help pages, resource pages  
**Auditor:** Claude (automated content review)

---

## CRITICAL - Incorrect or Potentially Harmful Information

### 1. Incorrect EID (Earned Income Disregard/Disallowance) Dollar Figure
**Files:**
- `resources/benefits.html` (line ~179)
- `resources/employment.html` (line ~126)
- `es/recursos/beneficios.html` (line ~181)
- `es/recursos/empleo.html` (line ~128)

**Problem:** States that Section 8's earned income disregard "exclud[es] the first $15,000 of new earned income for 12 months." This $15,000 figure does not match how HUD's Earned Income Disallowance (EID) works. Under 24 CFR 960.255, the EID excludes 100% of increased earned income for the first 12 months, then 50% for the next 12 months. There is no $15,000 cap in the federal regulation. The site appears to have invented or confused this number.

**Impact:** Readers could make financial decisions based on an incorrect cap, potentially underreporting income or misunderstanding their rent calculation.

**Fix:** Replace the $15,000 figure with accurate EID description: 100% exclusion for 12 months, 50% exclusion for months 13-24. Also note EID eligibility requirements (must have been unemployed or on welfare).

---

### 2. Missing "Aid Paid Pending" Protection in Appeals Guidance
**File:** `blog/posts/benefits-cut-what-to-do.html`

**Problem:** The post advises readers about appealing benefit cuts but states "benefits are usually cut immediately" without mentioning the critical "aid paid pending" protection. For SSA, SNAP, Medicaid, and Section 8, if you file an appeal within 10-15 days of receiving a reduction notice (before the effective date), your benefits generally continue at the prior level during the appeal. This is one of the most important protections available and its omission could lead readers to not file timely appeals.

**Impact:** Readers may assume there's no urgency to appeal quickly, missing the window to maintain benefits during the appeal process.

**Fix:** Add a prominent section explaining aid-paid-pending: "If you appeal within 10 days of receiving a benefit reduction notice (before the effective date), your benefits typically continue at the current level until the appeal is decided."

---

### 3. Incorrect SGA (Substantial Gainful Activity) Amount
**Files:**
- `resources/guides/how-benefits-interact.html` (line ~164) - States SGA is "$1,470/month in 2025"
- `es/recursos/guias/como-interactuan-beneficios.html` (line ~168) - Same in Spanish

**Problem:** The 2025 SGA for non-blind individuals is $1,620/month (increased from $1,550 in 2024). The figure of $1,470 was the 2023 amount. This is a significant error because people relying on this number could mistakenly believe they've exceeded SGA when they haven't, or vice versa.

**Fix:** Update to $1,620/month for 2025 (and verify/update to 2026 rate when available).

---

### 4. Outdated 2024 SGA Figures Still Used
**Files:**
- `resources/guides/how-to-apply-ssi-ssdi.html` (lines ~93, ~131) - Uses "$1,550/month" as SGA and work credit amount, labeled "2024"
- `es/recursos/guias/como-solicitar-ssi-ssdi.html` (lines ~96, ~134) - Same in Spanish

**Problem:** While correctly labeled as 2024 figures, the site is being read in 2026. These should be updated to current year values or at minimum flagged as outdated.

**Fix:** Update all SGA references to current 2026 values throughout.

---

## HIGH - Outdated Dollar Amounts and Program Information

### 5. Outdated SSI Federal Benefit Rate ($943/month)
**Files (English + Spanish):**
- `resources/benefits.html` (lines ~86, ~244, ~247, ~255) - "$943/month as of 2024"
- `resources/guides/how-to-apply-ssi-ssdi.html` (lines ~87, ~98, ~218) - "$943 per month"
- `resources/tools/benefits-calculator.html` (line ~908) - "$943/month federally"
- `es/recursos/beneficios.html` (lines ~88, ~246, ~249, ~257)
- `es/recursos/guias/como-solicitar-ssi-ssdi.html` (lines ~90, ~101, ~221)
- `es/recursos/herramientas/calculadora-beneficios.html` (line ~900)

**Problem:** SSI rates increase annually with COLA. The 2024 rate of $943 is outdated for a site being read in 2026. The 2025 SSI rate was $967/month. The 2026 rate would be even higher.

**Fix:** Update to 2026 SSI rate across all files, or use language like "check ssa.gov for current rates" if you want to avoid annual updates.

---

### 6. ACP (Affordable Connectivity Program) Referenced as Active
**File:** `resources/guides/budgeting-when-money-is-tight.html` (line ~463)

**Problem:** Lists "Lifeline/ACP (Phone and Internet)" as an active benefit. The ACP ended on June 1, 2024 when funding ran out. Congress did not reauthorize it. Referencing it as available is misleading.

**Fix:** Remove "ACP" from the reference. Lifeline is still active and can remain. Change to just "Lifeline (Phone)" or add a note that ACP has ended.

---

### 7. Emergency Rental Assistance Draft Implies Active Federal ERA
**File:** `blog/drafts/emergency-rental-assistance-programs.html`

**Problem:** The title says "Emergency Rental Assistance Programs That Still Have Funding" and the content implies many ERA programs are still operational with federal COVID-era funding. Most federal ERA (ERA1 and ERA2) funding has been fully distributed or expired. While some state/local programs may still exist, the framing is misleading.

**Fix:** Before publishing, rewrite to clarify that federal ERA funding is largely exhausted. Focus on state/local emergency assistance that exists independently of the federal ERA program.

---

### 8. Benefits Calculator and Know-Your-Numbers Tools Use 2024 Data
**Files:**
- `resources/tools/benefits-calculator.html` - Uses 2024 FPL and SSI rates
- `resources/tools/know-your-numbers.html` - Uses 2024 federal poverty level figures

**Problem:** Interactive tools that calculate benefits using 2024 poverty levels and benefit rates will produce inaccurate results in 2026. Users relying on these calculators could get wrong eligibility determinations.

**Fix:** Update all hardcoded 2024 values to 2026 rates, or add a prominent disclaimer about data currency.

---

### 9. Source of Income Protection State Count Inconsistency
**Files:**
- `blog/posts/landlord-rejects-voucher.html` - Says "roughly two dozen states"
- `resources/guides/source-of-income-protections.html` - Says "22 states plus Washington D.C. (as of early 2025)"
- `blog/drafts/housing-discrimination-what-to-do.html` - Says "about 20 states"

**Problem:** Three different pages give three different numbers. The actual count as of early 2025 was closer to 21-22 states plus DC, and additional states may have enacted protections since then. The inconsistency undermines credibility.

**Fix:** Standardize the count across all pages and update to the current number. Consider linking to the source-of-income-protections guide as the single source of truth.

---

## MEDIUM - Accuracy Concerns and Missing Nuance

### 10. SNAP Described as Having "Hard Cliffs"
**File:** `blog/posts/benefits-cliff-explained.html`

**Problem:** The post characterizes SNAP as having "hard cliffs" where "you lose everything at once." This is misleading. SNAP benefits actually taper gradually as income rises -- the benefit amount decreases as income goes up, reaching $0 at the eligibility limit. What has a hard cutoff is gross/net income eligibility, but the benefits themselves phase out gradually. This is the opposite of a cliff.

**Fix:** Clarify that SNAP benefits reduce gradually as income increases, but eligibility itself has a hard income cutoff. The "cliff" for SNAP is at the eligibility boundary, not within the benefit structure.

---

### 11. "Earned Income Disallowance" vs "Earned Income Disregard" Naming
**Files:** Used inconsistently across:
- `blog/posts/section-8-explained.html` - "Earned Income Disallowance"
- `blog/posts/section-8-myths.html` - "Earned Income Disallowance"  
- `resources/employment.html` - "Earned Income Disregard"
- `resources/guides/understanding-rent-calculation.html` - "Earned Income Disallowance (EID)"

**Problem:** The program has been renamed. HUD originally called it the "Earned Income Disallowance" (EID). After the 2016 Housing Opportunity Through Modernization Act, HUD began using "Earned Income Disregard." The site uses both terms without explanation, which could confuse readers or make them think these are different programs.

**Fix:** Standardize to the current HUD terminology ("Earned Income Disregard") with a parenthetical noting it was formerly called "Earned Income Disallowance."

---

### 12. VA Hotline "Any Discharge Status" Claim
**File:** `blog/posts/five-programs-you-dont-know.html`

**Problem:** States that the VA hotline serves veterans of "any era, any discharge status." While the Veterans Crisis Line (988, press 1) does serve all veterans regardless of discharge, HUD-VASH eligibility discussed in the same section requires an honorable or other-than-dishonorable discharge. The blanket "any discharge status" claim near HUD-VASH content could be misleading.

**Fix:** Clarify that the crisis line serves all veterans, but HUD-VASH has discharge status requirements.

---

### 13. Section 811 Age Range
**File:** `blog/posts/five-programs-you-dont-know.html`

**Problem:** States Section 811 serves people "ages 18-61 at admission." While Section 811 does primarily target non-elderly disabled adults (18+), there is no hard upper age limit of 61 at admission in the statute. The age 62 distinction relates to elderly definitions in other programs. Section 811 targets non-elderly disabled persons, meaning those under 62, but people can age in place after admission.

**Fix:** Clarify: "Section 811 targets non-elderly adults with disabilities (generally under 62 at admission)" rather than stating a hard cutoff.

---

### 14. FSS Description Inaccuracy in Keisha Story
**File:** `stories/keisha-benefits-cliff.html`

**Problem:** The story describes the FSS coordinator as "an older woman named Jerome" (line ~63). Jerome is traditionally a male name, creating a confusing contradiction. Minor but worth fixing.

**Fix:** Change either the name or the gender reference to be consistent.

---

### 15. Landlord FAQ: SOI Protection Stated as Universal
**File:** `for-landlords/landlord-faq.html` (line ~85)

**Problem:** The FAQ answer to the first question states "you cannot discriminate based on source of income" as if it's universal federal law. But source of income is NOT a federally protected class. Only some states and localities have SOI protections. The same page later correctly notes this distinction (line ~152), but the initial answer is misleading.

**Fix:** Add a qualifier to the first FAQ answer: "In jurisdictions with source of income protections, you cannot..."

---

### 16. DV Survivors Page - Typo in H1
**File:** `who-we-help/dv-survivors.html` (line ~61)

**Problem:** The H1 reads "Housing Resources for Survivors of Domestic Violencece" -- the word "Violence" is misspelled with an extra "ce" at the end.

**Fix:** Change to "Housing Resources for Survivors of Domestic Violence"

---

## LOW - Minor Issues, Style Concerns, and Future-Proofing

### 17. Medicaid FPL Figures Are 2024
**File:** `resources/guides/how-to-apply-for-medicaid.html`

**Problem:** Uses 2024 Federal Poverty Level figures for Medicaid eligibility (138% FPL threshold). While the percentage threshold is correct, the dollar amounts based on 2024 FPL will be slightly outdated.

**Fix:** Update dollar amounts to 2026 FPL or add "check healthcare.gov for current income limits."

---

### 18. VA Compensation Rates Labeled 2025
**File:** `resources/guides/va-benefits.html`

**Problem:** Lists 2025 VA disability compensation rates ($171 for 10%, $3,737 for 100%). These may be slightly outdated by 2026 COLA adjustments.

**Fix:** Verify against 2026 rates when published, or note "rates are adjusted annually."

---

### 19. Multiple Blog Posts Have Duplicate Structured Data
**Files:** Several published posts contain two `application/ld+json` blocks with `BlogPosting` type, sometimes with different dates. Examples:
- `blog/posts/benefits-cliff-explained.html` - Two BlogPosting blocks with different datePublished values
- `blog/posts/section-8-explained.html` - Two Article/BlogPosting blocks

**Problem:** Duplicate structured data can confuse search engines. Google may pick up either date, leading to inconsistent SERP displays.

**Fix:** Remove duplicate structured data blocks, keeping only one per page with the correct date.

---

### 20. Draft Post Dates Set Far in Future
**Problem:** Many draft posts have `datePublished` values set months into the future (July-December 2026). When published, these dates should be updated to the actual publication date to avoid SEO issues.

**Fix:** Update `datePublished` to actual publication date when each draft goes live.

---

### 21. "Why Housing Changes Everything" Loads components.js Twice
**File:** `blog/posts/why-housing-changes-everything.html` (lines ~36 and ~212)

**Problem:** The `components.js` script is loaded twice -- once in `<head>` and once before `</body>`. This could cause duplicate component rendering.

**Fix:** Remove the duplicate `<script>` tag at line ~212.

---

### 22. Missing Footer in Stories Pages
**Files:** All story pages (e.g., `stories/keisha-benefits-cliff.html`, `stories/marcus-veteran-hud-vash.html`, `stories/sarah-dv-survivor.html`)

**Problem:** Stories pages are missing the `<div id="site-footer"></div>` element that other pages use to inject the shared footer.

**Fix:** Add `<div id="site-footer"></div>` before `</body>` on all story pages.

---

## Summary of Findings by Severity

| Severity | Count | Key Theme |
|----------|-------|-----------|
| CRITICAL | 4 | Incorrect dollar figures (EID $15K cap, SGA amounts), missing aid-paid-pending protection |
| HIGH | 5 | Outdated 2024 benefit rates still used (SSI, FPL, SGA), ended program (ACP) referenced, ERA framing |
| MEDIUM | 7 | Misleading characterizations (SNAP cliffs, SOI protections), naming inconsistencies, typo |
| LOW | 6 | Stale dates, duplicate structured data, minor code issues |

## Recommended Priority Actions

1. **Immediately fix** the $15,000 EID figure in `resources/benefits.html` and `resources/employment.html` (plus Spanish versions) -- this is factually wrong and could mislead readers.
2. **Immediately add** aid-paid-pending information to `benefits-cut-what-to-do.html` -- missing this protection is potentially harmful to readers.
3. **Update all 2024 dollar amounts** (SSI, SGA, FPL) to 2026 values across the site, including Spanish translations and interactive tools.
4. **Remove ACP reference** from budgeting guide.
5. **Standardize EID/Earned Income Disregard** terminology across the site.
6. **Fix the SGA error** in `how-benefits-interact.html` ($1,470 should be $1,620 for 2025).
7. **Fix the typo** in `who-we-help/dv-survivors.html` H1.
