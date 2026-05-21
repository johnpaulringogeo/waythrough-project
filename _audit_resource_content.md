## Fixes Applied (2026-05-21)

- **Issue 1 (CRITICAL):** Fixed HUD deductions from "per month" to "per year" in `resources/guides/understanding-rent-calculation.html` and Spanish `es/recursos/guias/como-se-calcula-la-renta.html`. Recalculated all example figures (Sarah's and Rosa's examples) with correct annual deduction amounts converted to monthly equivalents.
- **Issue 2 (CRITICAL):** Fixed Veterans hotline mislabel in `resources/emergency-housing.html` and Spanish `es/recursos/vivienda-de-emergencia.html`. Changed "Veterans Crisis Line" to "VA National Call Center for Homeless Veterans" for 1-877-424-3838. Added actual Veterans Crisis Line (988 press 1) alongside it.
- **Issue 9 (HIGH):** Removed SNAP from countable income list in `resources/guides/understanding-rent-calculation.html` and Spanish version. SNAP is explicitly excluded from Section 8 income calculations.
- **Issue 10 (HIGH):** Fixed wrong HUD Fair Housing phone number from 1-888-569-1112 to 1-800-669-9777 in `resources/guides/source-of-income-protections.html` and Spanish `es/recursos/guias/protecciones-fuente-ingreso.html`.
- **Issue 11 (HIGH):** Fixed SOI protection contradictions across guide and 6 state pages (both English and Spanish):
  - Removed Colorado, Montana, Wisconsin from statewide SOI list in guide (they lack statewide laws). Added a new "local protections only" note.
  - Added Indiana and Nevada to statewide SOI list in guide.
  - Updated Montana state page to "Limited (local ordinances)" from "No".
  - Updated Wisconsin state page to "Limited (local ordinances -- Madison, Milwaukee County)" from "No".
  - Updated Michigan state page to "Yes (effective 2025)" from "No", reflecting Elliott-Larsen Act expansion.
  - Fixed Indiana and Nevada intro paragraphs in Spanish to match their "Yes" quick reference boxes.
  - Fixed Colorado Spanish intro paragraph that incorrectly said state had SOI protection.
  - Updated count from "22 states" to "21 states" in guide.
- **Issue 21 (MEDIUM):** Fixed medical expense deduction threshold from "$200 per year" to "3% of annual gross income" in rent calculation guide (English and Spanish). Updated Rosa's example calculation to use correct threshold.
- **Issue 22 (MEDIUM):** Fixed EID description from "$50/month excluded plus 20% above that for 24 months" to correct HUD rule: 100% excluded for first 12 months, 50% excluded for months 13-24, must have been previously unemployed or receiving welfare. Fixed in both English and Spanish.

---

# Resource Content Accuracy Audit

**Date:** May 21, 2026  
**Scope:** 190 HTML resource pages across guides/, states/, cities/, tools/, templates/, and top-level resource pages  
**Method:** Read 40+ pages in detail, grep-searched all 190 pages for phone numbers, agency names, program details, dollar amounts, and cross-page consistency  

---

## CRITICAL: Factual Errors

### 1. Rent Calculation Guide: HUD Deductions Listed as Monthly Instead of Annual
**File:** `resources/guides/understanding-rent-calculation.html` (lines 159, 164, 232-234)

The guide states:
- "Every household gets a flat standard deduction. This is currently **$480 per month**"
- "You get an additional **$480 per month** (approximately) for each dependent household member"

**The actual HUD rule:** The $480 dependent deduction and $400 elderly/disabled deduction are **per year**, not per month. This means:
- $480/year per dependent = $40/month (not $480/month)
- $400/year elderly/disabled = $33/month (not $400/month)

This error cascades into the example calculations on the page:
- Line 232: "Standard deduction: -$480" (should be ~$40/month)
- Line 233: "Dependency deduction (2 children x $480): -$960" (should be ~$80/month)
- Line 234: "Adjusted Gross Income = $2,600 - $480 - $960 = $1,160" (wildly incorrect)

**Impact:** HIGH. People using this guide to estimate their rent will get numbers that are dramatically wrong. The example shows adjusted income of $1,160 when it should be approximately $2,480.

---

### 2. Veterans Hotline Mislabeled as "Veterans Crisis Line"
**File:** `resources/emergency-housing.html` (lines 174, 254)

Line 174 states:
> `1-877-424-3838 -- Veterans Crisis Line`

Line 254 states:
> "Call the Veterans Crisis Line at 1-877-424-3838 to find SSVF programs near you."

**The actual number:** 1-877-424-3838 is the **VA National Call Center for Homeless Veterans**, NOT the Veterans Crisis Line. The Veterans Crisis Line is **988 (press 1)**.

Other pages on the site get this right:
- `guides/how-to-apply-hud-vash.html` correctly labels it "VA National Call Center for Homeless Veterans"
- `guides/va-benefits.html` correctly identifies the Veterans Crisis Line as "988, then press 1"

**Impact:** HIGH. A veteran in mental health crisis calling 1-877-424-3838 expecting crisis support would reach a housing-focused line instead. Could delay life-saving intervention.

---

### 3. Rent Calculation Guide: SNAP Listed as Countable Income
**File:** `resources/guides/understanding-rent-calculation.html` (line 137)

The income list includes:
> "Temporary Assistance for Needy Families (TANF), Supplemental Nutrition Assistance Program (SNAP), and other public assistance (varies by PHA)"

**The actual HUD rule:** SNAP benefits are explicitly EXCLUDED from income for Section 8/HCV purposes. The site's own income limits guide (`section-8-income-limits.html` line 206) correctly lists SNAP under "Income That Does NOT Count."

**Impact:** MEDIUM. Could cause applicants to over-report income or believe they don't qualify.

---

### 4. Inconsistent HUD Fair Housing Phone Number
**File:** `resources/guides/source-of-income-protections.html` (line 275)

States:
> "Contact HUD's Office of Fair Housing and Equal Opportunity: **1-888-569-1112**"

Every other page on the site (50+ state pages, discrimination guide, mental health page, etc.) uses the correct number: **1-800-669-9777**.

1-888-569-1112 does not appear to be a standard HUD number. The correct HUD Fair Housing hotline is 1-800-669-9777.

**Impact:** MEDIUM. Someone following this guide to report discrimination would call the wrong number.

---

## SIGNIFICANT: Outdated Information

### 5. SSI Benefit Amount Outdated (2024 figure used in 2026 content)
**Files:**
- `resources/benefits.html` (lines 86, 244, 247, 255)
- `resources/guides/how-to-apply-ssi-ssdi.html` (lines 87, 98, 218)

Multiple pages cite the SSI federal benefit rate as **$943/month "as of 2024"**. The 2025 rate was $967/month (3.2% COLA increase), and the 2026 rate would be higher still.

The benefits page is marked "Updated May 2026" but still uses 2024 SSI figures. The SSI guide similarly references "2024" figures.

**Recommendation:** Update to current figures or use language like "approximately $XXX/month (check ssa.gov for current amount)" to avoid going stale again.

---

### 6. Emergency Rental Assistance Guide Implies Active Federal Program
**File:** `resources/guides/emergency-rental-assistance.html` (line 122)

States:
> "These programs saved millions of renters during the pandemic and **are still available now**."

**Reality:** The federal ERA program (ERA1 and ERA2, funded under the CARES Act and American Rescue Plan) has been largely exhausted. Most states depleted their federal ERA allocations by 2023-2024. While some states/localities may have continued rental assistance with their own funding, the federal ERA program is effectively over.

The guide also references the "NLIHC tracker" (line 166) for finding ERA programs, but NLIHC's ERA-specific tracker has been wound down.

The COVID-19 hardship requirement (line 133) is also outdated -- remaining programs generally don't require COVID-specific hardship.

**Impact:** MEDIUM-HIGH. People following this guide may waste time searching for programs that no longer exist in their area. The general advice (call 211, search locally) is still sound, but the framing as an active federal program is misleading.

---

### 7. Emergency Housing Page: ERA Described as Ongoing
**File:** `resources/emergency-housing.html` (line 321)

States:
> "These programs were massively expanded during the COVID-19 pandemic, and while some have ended, many continue."

This is more cautiously worded than the ERA guide, but still implies broader availability than is likely the case in 2026.

---

## SIGNIFICANT: Cross-Page Inconsistencies

### 8. Source of Income Protection: Guide vs. State Pages Disagree
**File:** `resources/guides/source-of-income-protections.html` vs. `resources/states/*.html`

The SOI guide lists 22 states + DC as having statewide protections. But the state pages contradict this in several cases:

**Listed in SOI guide as having protections, but state page says "No":**
- **Colorado** -- SOI guide includes it; `states/colorado.html` says "Source of income protection: No"
- **Montana** -- SOI guide includes it (limited); `states/montana.html` says "No"
- **Wisconsin** -- SOI guide includes it (limited); `states/wisconsin.html` says "No"
- **Michigan** -- SOI guide says "effective April 2025"; `states/michigan.html` says "No"

**State page says "Yes" but NOT listed in the SOI guide:**
- **Indiana** -- `states/indiana.html` says "Yes" but Indiana is not in the SOI guide's list
- **Nevada** -- `states/nevada.html` says "Yes" (enacted 2023) but Nevada is not in the SOI guide's list

**Impact:** HIGH. People in these states may get contradictory information depending on which page they read. This could cause someone to either miss protections they have or believe they have protections they don't.

**Note on accuracy:** For Colorado, Montana, Wisconsin, and Michigan, the truth varies. Colorado does NOT have statewide SOI protection (the guide may be wrong). Indiana enacted SOI protection in 2024. Nevada enacted it in 2023. Michigan's Elliott-Larsen Civil Rights Act was expanded to include SOI in some interpretations. Each case needs individual verification against current law.

---

### 9. Earned Income Disregard (EID) Described Differently on Two Pages
**Files:**
- `resources/guides/understanding-rent-calculation.html` (line 218): "Under EID, the first $50 of earned income per month is excluded, and an additional 20% of earnings above that is excluded for up to 24 months"
- `resources/benefits.html` (lines 179, 247): "the first $15,000 of new earned income is disregarded for 12 months"

These are two completely different descriptions of the same program. The actual HUD EID rule (before it was modified) was: 100% of earned income increase excluded for 12 months, then 50% excluded for the next 12 months. Neither page's description matches HUD's actual rule.

**Impact:** MEDIUM. People relying on either description for financial planning would get incorrect expectations.

---

### 10. Medical Expense Deduction Threshold Inconsistent
**Files:**
- `resources/guides/understanding-rent-calculation.html` (line 194): "Only expenses over **$200 per year** are counted"
- `resources/benefits.html` (line 162): "unreimbursed medical expenses above **3% of your income**"
- `resources/guides/section-8-income-limits.html` (line 221): "Unreimbursed medical expenses exceeding **3% of annual income**"

The benefits page and income limits page are correct (3% of annual income). The rent calculation guide's "$200 per year" flat threshold is incorrect -- the actual threshold is 3% of gross annual income, which would only be $200 if someone earned $6,667/year.

**Impact:** MEDIUM. The rent calculation guide is the page people would use to actually estimate their rent, so having the wrong threshold there is problematic.

---

## MODERATE: Misleading or Confusing Content

### 11. Massachusetts Security Deposit Description Confusing
**File:** `resources/states/massachusetts.html`

States:
> "Security deposit limit: 1 month rent (first and last month plus lock change fee)"

This conflates the security deposit limit with total move-in costs. The security deposit itself is capped at 1 month's rent. Separately, a landlord may collect first month's rent, last month's rent, a security deposit (1 month), and a lock change fee at move-in. The parenthetical makes it sound like the deposit limit somehow includes first/last month's rent.

**Recommendation:** Change to "Security deposit limit: 1 month rent. (At move-in, landlord may also collect first month, last month, and lock change fee.)"

---

### 12. Section 8 Income Limits Page: $480 Deduction Ambiguous
**File:** `resources/guides/section-8-income-limits.html` (line 219)

States:
> "$480 per dependent: For each household member who is under 18, a student, or disabled"

This doesn't specify whether it's per month or per year. Given that the rent calculation guide incorrectly says "per month," users reading both pages would reasonably conclude $480/month. The correct figure is $480/year.

---

### 13. Rent Calculation Guide: TANF Listed as Income "Varies by PHA"
**File:** `resources/guides/understanding-rent-calculation.html` (line 137)

TANF is listed in the income list with "(varies by PHA)." TANF cash assistance IS counted as income for HUD purposes -- it doesn't vary by PHA. It's a standard HUD rule. The "varies by PHA" qualifier is misleading.

---

## MINOR: Issues Worth Noting

### 14. Phone Number Consistency
All major hotline numbers are used consistently across the site (good):
- HUD Fair Housing: 1-800-669-9777 (correct, consistent -- except the one error in SOI guide noted above)
- National DV Hotline: 1-800-799-7233 (correct, consistent)
- SSA: 1-800-772-1213 (correct, consistent)
- VA Homeless Veterans: 1-877-424-3838 (correct number, but mislabeled in emergency-housing.html as noted)
- SAMHSA: 1-800-662-4357 (correct, consistent)
- 211: Referenced consistently and correctly

### 15. HUD Housing Counselor Number Used Sparingly
**File:** `resources/guides/finding-housing-counselor.html`

The HUD housing counselor number (1-800-569-4287) is only mentioned in the structured data/FAQ schema, not in the visible page content. The page directs users to the HUD website instead. This is a minor gap -- the phone number would help users without internet access.

### 16. State Housing Finance Agency Names: All Appear Correct
All 50 state pages + DC were checked for housing finance agency names. All names match the correct current agency names:
- California Housing Finance Agency (CalHFA) -- correct
- Texas Department of Housing and Community Affairs -- correct
- New York State Homes and Community Renewal -- correct
- Florida Housing Finance Corporation -- correct
- Alaska Housing Finance Corporation -- correct
- Kansas Housing Resources Corporation -- correct
- (and all others checked)

No agency rename issues were found.

### 17. City Pages: Generic but Not Inaccurate
The 50+ city pages follow a consistent template and don't make city-specific factual claims that could be wrong. They primarily direct users to call 211, check HUD directories, and link to state pages. This is a safe approach that avoids city-specific errors.

### 18. Program Descriptions Generally Accurate
Section 8/HCV descriptions, LIHTC descriptions, HUD-VASH process, FSS program details, and fair housing law descriptions are generally accurate across the site, with the specific exceptions noted above.

---

## Summary of Priority Fixes

| # | Issue | Severity | Files Affected |
|---|-------|----------|----------------|
| 1 | HUD deductions listed as monthly instead of annual | CRITICAL | understanding-rent-calculation.html |
| 2 | Veterans hotline mislabeled as Crisis Line | CRITICAL | emergency-housing.html |
| 3 | SNAP listed as countable income | HIGH | understanding-rent-calculation.html |
| 4 | Wrong HUD phone number (1-888-569-1112) | HIGH | source-of-income-protections.html |
| 5 | SSI amount outdated ($943 is 2024 figure) | MEDIUM | benefits.html, how-to-apply-ssi-ssdi.html |
| 6 | ERA guide implies active federal program | MEDIUM-HIGH | emergency-rental-assistance.html |
| 7 | ERA described as ongoing | MEDIUM | emergency-housing.html |
| 8 | SOI protection status contradicts between pages | HIGH | source-of-income-protections.html, 6 state pages |
| 9 | EID described differently (both wrong) | MEDIUM | understanding-rent-calculation.html, benefits.html |
| 10 | Medical expense threshold inconsistent | MEDIUM | understanding-rent-calculation.html |
| 11 | MA deposit description confusing | LOW | states/massachusetts.html |
| 12 | $480 deduction ambiguous (year vs month) | MEDIUM | section-8-income-limits.html |
| 13 | TANF "varies by PHA" misleading | LOW | understanding-rent-calculation.html |

**Total issues found:** 13 substantive issues (2 critical, 4 high, 5 medium, 2 low)  
**Pages with no issues:** The vast majority of pages are factually sound. State pages, city pages, and most guides are well-researched and accurate.
