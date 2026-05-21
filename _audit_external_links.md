# External Link Audit - The Waythrough Project

## Fixes Applied (2026-05-21)

All 28 link issues identified in this audit have been fixed across the entire site (English and Spanish). Summary:

**Dead Links (7 fixed):**
1. `www.adfa.arkansas.gov` -> `adfa.arkansas.gov` (removed www) - 2 files
2. HUD rental history FAQ -> `hud.gov/topics/rental_assistance` - 2 files
3. `fcc.gov/broadbandbenefits` -> `lifelinesupport.org` - 2 files
4. `archives.gov/.../dd-form-214` -> `archives.gov/veterans/military-service-records` - 2 files
5. `experian.com/consumer/experian-boost/` -> `experian.com/boost` - 4 files
6. `consumerfinance.gov/consumer-tools/credit-reports/` -> `.../credit-reports-and-scores/` - 2 files
7. `habitat.org/find-your-local-habitat` -> `habitat.org/local` - 2 files

**Suspicious Links (2 fixed):**
8. `smartmove.us` -> `mysmartmove.com` - 2 files
9. `napsa.org` (NAPSA) -> `ndrn.org` (NDRN) with updated anchor text - 1 file

**High-Traffic Redirects (3 fixed - hundreds of pages each):**
10. `apps.hud.gov/offices/hsg/sfh/hcc/hcs.cfm` -> `answers.hud.gov/housingcounseling/s/` - 101 files
11. `hud.gov/.../public_indian_housing/pha/contacts` -> `hud.gov/contactus/public-housing-contacts` - 213 files
12. `hud.gov/.../fair_housing_equal_opp/online-complaint` -> `hud.gov/reporthousingdiscrimination` - 118 files

**Other Redirects (16 fixed):**
13. `hud.gov/fairhousing` -> `hud.gov/program_offices/fair_housing_equal_opp` - 6 files
14. `hud.gov/findhelp` -> `hud.gov/counseling` - 3 files
15. `hud.gov/.../housing_counseling/find_houspic` -> `answers.hud.gov/housingcounseling/s/` - 3 files
16. `hud.gov/.../contact_fheo` -> `hud.gov/contactus/fairhousing` - 3 files
17. `iowafinance.com` -> `opportunityiowa.gov/about/iowa-finance-authority` - 2 files
18. `ssa.gov/benefits/ssi` -> `ssa.gov/ssi` - 2 files
19. `va.gov/vso/` -> `va.gov/get-help-from-accredited-representative/` - 2 files
20. `legalassist.org` -> `lsnd.org/` - 2 files
21. `lgbtmap.org/` -> `mapresearch.org/` - 2 files
22. `energy.gov/scep/wap/...` -> `energy.gov/cmei/scep/wap/...` - 2 files
23. `acf.hhs.gov/ocs/liheap` -> `acf.gov/ocs/programs/liheap` - 2 files
24. `experian.com/disputes/main.html` -> `experian.com/help/dispute-credit/` - 2 files
25. `lsc.gov/.../get-legal-help` -> `lsc.gov/.../i-need-legal-help` - 2 files
26. `rd.usda.gov/contact-us/state-offices` -> `rd.usda.gov/about-rd/offices/state-offices` - 2 files
27. `ndhfa.org` -> `ndhousing.nd.gov/` - 2 files
28. `housing.mt.gov` -> `commerce.mt.gov/Housing/` - 4 files

Display text in anchor tags was also updated where it showed old URLs. The `_link_checker.html` URLs were updated to match.

---

**Audit Date:** 2026-05-21
**Total External Links Found:** 210 unique URLs across 505 HTML files
**Method:** Bulk reachability scan (no-cors fetch from browser) + individual navigation verification for all 210 URLs

---

## Summary

| Category | Count |
|----------|-------|
| OK (working, correct content) | 189 |
| Dead (404 / DNS failure) | 7 |
| Suspicious (wrong content) | 2 |
| Redirected (content matches but URL changed) | 12 |
| **Total** | **210** |

---

## Dead Links (7)

These links return 404 errors or fail to resolve. They need to be fixed or replaced.

### 1. `https://www.adfa.arkansas.gov`
- **Status:** DNS_PROBE_FINISHED_NXDOMAIN (www subdomain does not exist)
- **Fix:** Change to `https://adfa.arkansas.gov` (without www - this works)
- **Anchor text:** "Arkansas Development Finance Authority"
- **Found in:**
  - `resources/states/arkansas.html`
  - `es/recursos/estados/arkansas.html`

### 2. `https://www.hud.gov/program_offices/public_indian_housing/programs/phd/phr/about/faq`
- **Status:** 404 - Page Not Found on HUD.gov
- **Fix:** Remove or replace with `https://www.hud.gov/topics/rental_assistance` or another current HUD rental assistance page
- **Anchor text:** "HUD's Housing Counseling Program" / "Programa de Consejeria de Vivienda de HUD"
- **Found in:**
  - `resources/guides/renting-with-poor-rental-history.html`
  - `es/recursos/guias/alquilar-con-mal-historial.html`

### 3. `https://www.fcc.gov/broadbandbenefits`
- **Status:** Redirects to fcc.gov/page-not-found (404)
- **Note:** The Affordable Connectivity Program (ACP) ended in June 2024. This page no longer exists.
- **Fix:** Remove the link or replace with `https://www.fcc.gov/acp` (which also has program-ended info) or `https://www.lifelinesupport.org` (the Lifeline program is still active)
- **Anchor text:** "fcc.gov/broadbandbenefits"
- **Found in:**
  - `resources/guides/budgeting-when-money-is-tight.html`
  - `es/recursos/guias/presupuesto-con-poco-dinero.html`

### 4. `https://www.archives.gov/veterans/military-service-records/dd-form-214`
- **Status:** 404 - Page Not Found on National Archives
- **Fix:** Change to `https://www.archives.gov/veterans/military-service-records` (parent page works and includes DD-214 info)
- **Anchor text:** "archives.gov"
- **Found in:**
  - `resources/guides/how-to-apply-hud-vash.html`
  - `es/recursos/guias/como-solicitar-hud-vash.html`

### 5. `https://www.experian.com/consumer/experian-boost/`
- **Status:** "Experian - Page Not Found"
- **Fix:** Change to `https://www.experian.com/boost` or `https://www.experian.com/consumer/experian-boost.html`
- **Anchor text:** "Experian Boost"
- **Found in:**
  - `resources/credit-housing.html`
  - `resources/guides/rebuilding-credit-for-housing.html`
  - `es/recursos/credito-vivienda.html`
  - `es/recursos/guias/reconstruir-credito-para-vivienda.html`

### 6. `https://www.consumerfinance.gov/consumer-tools/credit-reports/`
- **Status:** "404 error: not found" on CFPB
- **Fix:** Change to `https://www.consumerfinance.gov/consumer-tools/credit-reports-and-scores/` or `https://www.consumerfinance.gov/ask-cfpb/category-credit-reporting/`
- **Anchor text:** "CFPB Credit Guidance" / "Guia de Credito del CFPB"
- **Found in:**
  - `resources/guides/rebuilding-credit-for-housing.html`
  - `es/recursos/guias/reconstruir-credito-para-vivienda.html`

### 7. `https://www.habitat.org/find-your-local-habitat`
- **Status:** "404: page not found" on Habitat for Humanity
- **Fix:** Change to `https://www.habitat.org/local` or `https://www.habitat.org/us-map`
- **Anchor text:** "habitat.org"
- **Found in:**
  - `resources/guides/home-repair-assistance.html`
  - `es/recursos/guias/programas-reparacion-vivienda.html`

---

## Suspicious Links (2)

These URLs load but the content does not match what the site says they should be.

### 1. `https://www.smartmove.us`
- **Problem:** Linked as "TransUnion SmartMove" (a tenant screening service), but the domain now serves "SmartMove - Get Internet, Cable TV & Phone Service Offers" - a completely unrelated telecom comparison site
- **Fix:** The actual TransUnion SmartMove tenant screening tool is at `https://www.mysmartmove.com`
- **Anchor text:** "TransUnion SmartMove"
- **Found in:**
  - `resources/guides/renting-with-poor-rental-history.html`
  - `es/recursos/guias/alquilar-con-mal-historial.html`

### 2. `https://www.napsa.org`
- **Problem:** Linked as "National Association of Protection and Advocacy Systems (NAPSA)" but the actual site is "NAPSA Annual Conference | National Association Of Pretrial Services Agencies" - a completely different organization
- **Fix:** The correct organization is now the National Disability Rights Network (NDRN). Change to `https://www.ndrn.org` (which is already linked elsewhere on the site)
- **Anchor text:** "National Association of Protection and Advocacy Systems (NAPSA)"
- **Found in:**
  - `who-we-help/disabilities.html`

---

## Redirected Links (12)

These links work but redirect to a different URL. The content is generally correct but the URLs should be updated for better user experience and to avoid relying on redirects that may break in the future.

### High Priority (significant URL change or content shift)

#### 1. `https://hud.gov/fairhousing` and `https://www.hud.gov/fairhousing`
- **Redirects to:** `https://www.hud.gov/hud-partners#FairHousing`
- **Note:** Now points to a "HUD Partners" page with a Fair Housing anchor, rather than a dedicated fair housing page. Content is related but not ideal.
- **Anchor text:** "HUD's Fair Housing website" / "hud.gov/fairhousing"
- **Found in:** `hud.gov/fairhousing` appears in 2 files; `www.hud.gov/fairhousing` appears in 4 files (total 6 files across English and Spanish)
- **Suggested fix:** Consider `https://www.hud.gov/program_offices/fair_housing_equal_opp` or `https://www.hud.gov/reporthousingdiscrimination`

#### 2. `https://www.hud.gov/findhelp`
- **Redirects to:** `https://www.hud.gov/` (homepage)
- **Note:** The specific "find help" page no longer exists; redirects to generic homepage
- **Anchor text:** "hud.gov/findhelp"
- **Found in:**
  - `resources/guides/budgeting-when-money-is-tight.html`
  - `es/recursos/guias/presupuesto-con-poco-dinero.html`
- **Suggested fix:** `https://www.hud.gov/counseling` or `https://resources.hud.gov/`

#### 3. `https://www.hud.gov/program_offices/housing_counseling/find_houspic`
- **Redirects to:** `https://www.hud.gov/` (homepage)
- **Note:** HUD Housing Counselor Locator page is gone; redirects to homepage
- **Anchor text:** "HUD Housing Counselor Locator" / "HUD's Housing Counselor Locator"
- **Found in:**
  - `resources/guides/finding-housing-counselor.html`
  - `es/recursos/guias/como-encontrar-consejero-vivienda.html`
- **Suggested fix:** `https://answers.hud.gov/housingcounseling/s/` (the new counseling locator)

#### 4. `https://www.iowafinance.com`
- **Redirects to:** `https://opportunityiowa.gov/about/iowa-finance-authority`
- **Note:** Iowa Finance Authority was absorbed into Opportunity Iowa
- **Anchor text:** "Iowa Finance Authority"
- **Found in:**
  - `resources/states/iowa.html`
  - `es/recursos/estados/iowa.html`
- **Suggested fix:** Update to `https://opportunityiowa.gov/about/iowa-finance-authority`

### Medium Priority (redirects to correct content)

#### 5. `https://apps.hud.gov/offices/hsg/sfh/hcc/hcs.cfm`
- **Redirects to:** `https://answers.hud.gov/housingcounseling/s/?language=en_US`
- **Note:** Old counselor search redirects to new platform. Content matches.
- **Anchor text:** "HUD's counselor locator"
- **Found in:** 100 city pages (50 English + 50 Spanish)
- **Suggested fix:** Update to `https://answers.hud.gov/housingcounseling/s/`

#### 6. `https://www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint`
- **Redirects to:** `https://www.hud.gov/reporthousingdiscrimination`
- **Note:** Correct content (file a complaint), just a cleaner URL now
- **Anchor text:** "HUD FHEO Complaint Portal" / "HUD's Online Complaint Portal"
- **Found in:** 115+ files (all 50 state pages in both languages, plus guides and blog posts)
- **Suggested fix:** Update to `https://www.hud.gov/reporthousingdiscrimination`

#### 7. `https://www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo`
- **Redirects to:** `https://www.hud.gov/contactus/fairhousing`
- **Note:** Correct content, cleaner URL
- **Found in:**
  - `resources/guides/how-to-file-housing-discrimination-complaint.html`
  - `es/recursos/guias/como-presentar-queja-discriminacion.html`

#### 8. `https://www.hud.gov/program_offices/public_indian_housing/pha/contacts`
- **Redirects to:** `https://www.hud.gov/contactus/public-housing-contacts`
- **Note:** Correct content, cleaner URL
- **Found in:** 160+ files (all city and state pages in both languages, plus guides and blog posts)
- **Suggested fix:** Update to `https://www.hud.gov/contactus/public-housing-contacts`

#### 9. `https://www.ssa.gov/benefits/ssi`
- **Redirects to:** `https://www.ssa.gov/ssi`
- **Note:** Correct content, shorter URL
- **Found in:**
  - `resources/guides/how-to-apply-ssi-ssdi.html`
  - `es/recursos/guias/como-solicitar-ssi-ssdi.html`

#### 10. `https://www.va.gov/vso/`
- **Redirects to:** `https://www.va.gov/resources/va-accredited-representative-faqs/`
- **Note:** VSO page now redirects to accredited rep FAQs. Related but not quite the same as finding a VSO.
- **Found in:**
  - `resources/guides/va-benefits.html`
  - `es/recursos/guias/beneficios-va.html`
- **Suggested fix:** Consider `https://www.va.gov/get-help-from-accredited-representative/`

### Low Priority (domain change, content identical)

#### 11. `https://www.legalassist.org`
- **Redirects to:** `https://lsnd.org/`
- **Note:** Rebranded from Legal Assistance of North Dakota to Legal Services of North Dakota. Same org.
- **Found in:**
  - `resources/states/north-dakota.html`
  - `es/recursos/estados/north-dakota.html`

#### 12. `https://www.lgbtmap.org/`
- **Redirects to:** `https://mapresearch.org/`
- **Note:** Movement Advancement Project rebranded domain. Same organization.
- **Found in:**
  - `resources/lgbtq-housing.html`
  - `es/recursos/vivienda-lgbtq.html`

---

## Additional Redirects Noted (content-preserving, lower priority)

These URLs redirect but land on the correct content. They still work fine but could be updated for cleanliness:

- `https://www.hud.gov/counseling` -> `https://answers.hud.gov/housingcounseling/s/` (3 files)
- `https://www.energy.gov/scep/wap/weatherization-assistance-program` -> `https://www.energy.gov/cmei/scep/wap/weatherization-assistance-program` (2 files)
- `https://www.acf.hhs.gov/ocs/liheap` -> `https://acf.gov/ocs/programs/liheap` (4 files)
- `https://www.experian.com/disputes/main.html` -> `https://www.experian.com/help/dispute-credit/` (2 files)
- `https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help` -> `https://www.lsc.gov/about-lsc/what-legal-aid/i-need-legal-help` (4 files)
- `https://www.rd.usda.gov/contact-us/state-offices` -> `https://www.rd.usda.gov/about-rd/offices/state-offices` (2 files)
- `https://www.ndhfa.org` -> `https://www.ndhousing.nd.gov/` (2 files)
- `https://housing.mt.gov` -> `https://commerce.mt.gov/Housing/` (content-preserving redirect)

---

## Impact Assessment

### Highest Impact Fixes (affect the most pages)

1. **`apps.hud.gov/offices/hsg/sfh/hcc/hcs.cfm`** - 100 city pages. Update to `answers.hud.gov/housingcounseling/s/`
2. **`www.hud.gov/program_offices/public_indian_housing/pha/contacts`** - 160+ pages. Update to `www.hud.gov/contactus/public-housing-contacts`
3. **`www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint`** - 115+ pages. Update to `www.hud.gov/reporthousingdiscrimination`

### Most Urgent Fixes (broken or misleading)

1. **`www.smartmove.us`** - Points to wrong site entirely (telecom instead of tenant screening)
2. **`www.napsa.org`** - Points to wrong organization entirely
3. **`www.adfa.arkansas.gov`** - DNS failure, easy fix (remove www)
4. **`www.fcc.gov/broadbandbenefits`** - Program no longer exists
5. **`www.experian.com/consumer/experian-boost/`** - 404 on Experian
6. **`www.consumerfinance.gov/consumer-tools/credit-reports/`** - 404 on CFPB
7. **`www.habitat.org/find-your-local-habitat`** - 404 on Habitat
8. **`www.archives.gov/veterans/military-service-records/dd-form-214`** - 404 on National Archives
9. **`www.hud.gov/program_offices/public_indian_housing/programs/phd/phr/about/faq`** - 404 on HUD

---

## OK Links (189)

All remaining 189 links were verified as working and pointing to the expected content. These include:
- 50 state housing finance agency websites
- 50 state legal aid websites
- Various federal government resources (VA, SSA, HUD, USDA, etc.)
- Nonprofit organizations (Feeding America, Habitat for Humanity main site, NAMI, AA, NA, etc.)
- Credit reporting and tenant screening services
- LGBTQ+ advocacy organizations
- Immigration legal services
- Privacy policy pages (Google, Cloudflare)
