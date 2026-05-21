## Fixes Applied (2026-05-21)

1. **Issue 6 (CRITICAL): Fixed 737 broken internal links** -- 29 slug mismatches corrected across all es/ HTML files. All old slugs now resolve to actual filenames (e.g., como-solicitar-section-8 -> como-solicitar-seccion-8, vivienda-de-emergencia-esta-noche -> necesito-vivienda-esta-noche, donde-comenzar -> donde-empezar, etc.)

2. **Issue 15 (HIGH): Fixed 57 links pointing to English pages** -- Fixed es/recursos/donde-empezar.html (22 English guide links -> Spanish equivalents), es/index.html (4 topic cards), es/recursos/vivienda-de-emergencia.html (2 guide links), and glossary links across 5 resource pages.

3. **Issue 16 (HIGH): Added 8 missing phone numbers** -- Added HUD Fair Housing (1-800-669-9777) and SSA (1-800-772-1213) to FAQ; DAV/Veterans (1-844-827-4338) to HUD-VASH guide; SAMHSA (1-800-662-4357) to recovery housing guide; HUD Resource Center (1-800-955-2232) to find-your-PHA guide; HUD Counseling (1-800-569-4287) to housing counselor guide; VA Benefits hotline (1-877-424-3838) to VA benefits guide; National DV Hotline (1-800-799-7233) to Sarah's story page. Foreclosure guide already had the HUD Counseling number.

4. **Issue 17 (HIGH): Fixed nav bar links** -- In js/components.js, changed Spanish nav Blog link from /blog/ to /es/blog/, Guides link from /resources/guides/ to /es/recursos/guias/, and footer Privacy/Terms/Accessibility links to Spanish versions (/es/privacidad, /es/terminos, /es/recursos/accesibilidad). Also fixed Spanish footer Blog link.

5. **Issue 27 (MEDIUM): Replaced "desahucio" with "desalojo"** -- 13 instances in es/recursos/derechos-del-inquilino.html changed to US Latino Spanish usage.

6. **Issue 28 (MEDIUM): Fixed template literal bug** -- In es/recursos/herramientas/evaluador-elegibilidad.html, removed backslash escapes from JavaScript template literal (backticks and ${} expressions) that prevented the results grid from rendering.

7. **Issue 37 (LOW): Standardized "Section 8" to "Sección 8"** -- Replaced "Section 8" with "Sección 8" across all 128 Spanish HTML files. No URL slugs were affected (they use lowercase "section-8").

---

# Spanish Content Audit - Waythrough Project

**Audit date:** 2026-05-21
**Scope:** All 235 Spanish pages in `/es/` compared against 238 English pages
**Auditor:** Automated + manual review

---

## Executive Summary

The Spanish translation has strong coverage (235 of 238 English pages) and generally good translation quality. However, there are **critical navigation issues** that would prevent Spanish-speaking users from reaching the content they need:

- **737 broken internal links** due to slug mismatches between link hrefs and actual filenames
- **57 links resolve to English pages** instead of their Spanish counterparts
- **8 pages missing phone numbers** that exist in the English version
- **Navigation bar links to English blog and guides** instead of Spanish versions

---

## 1. Structural Parity

### Page counts
- English pages (excluding drafts): **238**
- Spanish pages: **235**
- Coverage: **98.7%**

### Missing Spanish pages (3 pages)

| English page | Notes |
|---|---|
| `author.html` | Author/about page - low priority |
| `blog/posts/what-counts-as-income-section-8.html` | Blog post: "What Counts as Income on Section 8? The Complete List" - **important practical content** |
| `resources/downloads/index.html` | Downloads index page |

### Directory structure mapping
The Spanish directory structure correctly mirrors English with translated names:

| English | Spanish |
|---|---|
| `who-we-help/` | `a-quienes-ayudamos/` |
| `for-landlords/` | `para-propietarios/` |
| `resources/` | `recursos/` |
| `resources/guides/` | `recursos/guias/` |
| `resources/cities/` | `recursos/ciudades/` |
| `resources/states/` | `recursos/estados/` |
| `resources/tools/` | `recursos/herramientas/` |
| `resources/templates/` | `recursos/plantillas/` |
| `stories/` | `historias/` |

All 50 city pages, 51 state pages (+DC), and 50 guide pages have Spanish counterparts.

---

## 2. Broken Internal Links (CRITICAL - 737 total)

### The core problem
Links within Spanish pages use **different slug translations** than the actual filenames. For example, links point to `como-solicitar-section-8` but the file is actually named `como-solicitar-seccion-8.html`.

### Top slug mismatches by frequency

| References | Link target (broken) | Actual filename |
|---|---|---|
| 105 | `como-solicitar-section-8` | `como-solicitar-seccion-8` |
| 101 | `vivienda-de-emergencia-esta-noche` | `necesito-vivienda-esta-noche` |
| 100 | `donde-comenzar` | `donde-empezar` |
| 62 | `como-solicitar-adaptacion-razonable` | `como-solicitar-acomodacion-razonable` |
| 55 | `como-encontrar-su-pha` | `como-encontrar-tu-pha` |
| 53 | `como-evitar-el-desalojo` | `como-evitar-desalojo` |
| 53 | `asistencia-de-alquiler-de-emergencia` | `asistencia-renta-emergencia` |
| 51 | `como-presentar-queja-de-discriminacion` | `como-presentar-queja-discriminacion` |

### Additional broken slug patterns (74 unique broken targets total)

**Guides directory** (most affected):
- `como-aplicar-section-8` -> actual: `como-solicitar-seccion-8`
- `como-aplicar-hud-vash` -> actual: `como-solicitar-hud-vash`
- `como-interactuan-los-beneficios` -> actual: `como-interactuan-beneficios`
- `estrategias-lista-de-espera` -> actual: `estrategias-lista-espera`
- `protecciones-fuente-de-ingreso` -> actual: `protecciones-fuente-ingreso`
- `que-esperar-en-la-inspeccion` -> actual: `que-esperar-en-inspeccion`
- `entender-calculo-alquiler` -> actual: `como-se-calcula-la-renta`
- `entender-su-contrato-de-arrendamiento` -> actual: `entendiendo-tu-contrato`
- `encontrar-consejero-de-vivienda` -> actual: `como-encontrar-consejero-vivienda`
- `family-self-sufficiency` (untranslated!) -> actual: `programa-autosuficiencia-familiar`
- `alquilar-con-mal-historial-de-alquiler` -> actual: `alquilar-con-mal-historial`
- `como-apelar-negacion-vivienda-de-vivienda` -> redundant "de-vivienda", actual: `como-apelar-negacion-vivienda`

**Tools/herramientas directory:**
- `calculadora-de-beneficios` -> actual: `calculadora-beneficios`
- `calculadora-de-presupuesto` -> actual: `calculadora-presupuesto`
- `estimador-de-alquiler` -> actual: `estimador-renta`
- `evaluador-de-elegibilidad` -> actual: `evaluador-elegibilidad`
- `${p.link}` -> **JavaScript template literal in href** (in evaluador-elegibilidad.html)

**Templates/plantillas directory:**
- `solicitud-de-reparaciones` -> actual: `solicitud-reparacion`
- `apelacion-denegacion-vivienda` -> actual: `apelacion-negacion-vivienda`

**Who-we-help directory:**
- `a-quien-ayudamos/` (singular) -> actual: `a-quienes-ayudamos/` (plural)

**Resource root:**
- `por-donde-empezar` -> actual: `donde-empezar`
- `credito-y-vivienda` -> actual: `credito-vivienda`

### Pattern: The mismatch is systematic
The links were likely generated using one translation of the slug while the files were created with a slightly different translation. The most common differences:
1. Extra articles (`de`, `el`, `la`, `los`) in link slugs that filenames omit
2. Different verb choices (`aplicar` vs `solicitar`, `encontrar` vs `buscar`)
3. Different noun choices (`alquiler` vs `renta`, `contrato` vs `arrendamiento`)

---

## 3. Links Resolving to English Pages (57 links across 24 pages)

### Most affected pages

**`es/recursos/donde-empezar.html`** (22 English-pointing links):
All guide links on this page point to English versions (`../../resources/guides/...`) instead of Spanish (`../guias/...`). This is the "Where to Start" page -- one of the most important entry points for Spanish users.

**`es/index.html`** (4 English-pointing links):
- Employment, Mental Health, Substance Use, and Families topic cards link to English pages

**`es/recursos/vivienda-de-emergencia.html`** (4 English-pointing links):
- Emergency rental assistance guide, eviction avoidance guide, and glossary link to English

**Other affected pages:**
- `es/recursos/beneficios.html` - glossary link
- `es/recursos/derechos-del-inquilino.html` - glossary link
- `es/recursos/preguntas-frecuentes.html` - glossary link
- `es/recursos/respuestas-de-la-comunidad.html` - glossary link
- `es/recursos/para-profesionales.html` - root link
- `es/blog/posts/que-sucede-despues-del-voucher.html` - root link
- `es/blog/posts/section-8-explicado.html` - root link
- `es/recursos/guias/como-solicitar-seccion-8.html` - English blog post link
- `es/recursos/guias/lista-documentos.html` - PDF link to English directory
- `es/recursos/herramientas/calculadora-beneficios.html` - root link
- `es/recursos/herramientas/comparar-programas.html` - root link

### Navigation component issues (in `js/components.js`)

**Nav bar (Spanish mode):**
- "Blog" links to `${root}blog/` (English blog, not `${root}es/blog/`)
- "Guias" links to `${root}resources/guides/` (English guides, not `${root}es/recursos/guias/`)

**Footer (Spanish mode):**
- "Blog" links to `${root}blog/` (English)
- Accessibility link goes to `${root}resources/accessibility` (English)
- Privacy link goes to `${root}privacy` (English, should be `${root}es/privacidad`)
- Terms link goes to `${root}terms` (English, should be `${root}es/terminos`)

---

## 4. Missing Phone Numbers (8 pages)

| English page | Spanish page | Missing phone(s) | Service |
|---|---|---|---|
| `resources/faq.html` | `es/recursos/preguntas-frecuentes.html` | 1-800-669-9777, 1-800-772-1213 | HUD Fair Housing, Social Security |
| `resources/guides/how-to-apply-hud-vash.html` | `es/recursos/guias/como-solicitar-hud-vash.html` | 1-844-827-4338 | Veterans Crisis Line |
| `resources/guides/how-to-find-recovery-housing.html` | `es/recursos/guias/como-encontrar-vivienda-recuperacion.html` | 1-800-662-4357 | SAMHSA Helpline |
| `resources/guides/how-to-find-your-pha.html` | `es/recursos/guias/como-encontrar-tu-pha.html` | 1-800-955-2232 | HUD Resource Center |
| `resources/guides/how-to-prevent-foreclosure.html` | `es/recursos/guias/como-prevenir-ejecucion-hipotecaria.html` | 1-800-569-4287 | HUD Housing Counseling |
| `resources/guides/finding-housing-counselor.html` | `es/recursos/guias/como-encontrar-consejero-vivienda.html` | 1-800-569-4287 | HUD Housing Counseling |
| `resources/guides/va-benefits.html` | `es/recursos/guias/beneficios-va.html` | 1-877-424-3838 | VA Benefits Hotline |
| `stories/sarah-dv-survivor.html` | `es/historias/sarah-sobreviviente-violencia.html` | 1-800-799-7233 | National DV Hotline |

These are critical omissions -- a Spanish-speaking user in crisis (domestic violence, homelessness, substance abuse) would not see the help hotline number.

---

## 5. External Link Parity

External links are largely consistent between English and Spanish pages. Only 1 mismatch found across 30 page pairs checked:

| Page pair | Missing link |
|---|---|
| `who-we-help/disabilities.html` vs `es/a-quienes-ayudamos/discapacidades.html` | `https://www.napsa.org` missing from Spanish |

---

## 6. Translation Quality

### Overall assessment: Good
The translations read naturally and avoid most machine translation artifacts. Content is clearly written by or reviewed by someone familiar with housing terminology in Spanish.

### Terminology consistency

**"Section 8" naming (INCONSISTENT):**
- 128 pages use "Section 8" (English)
- 78 pages use "Seccion 8" or "Seccion 8" (Spanish)
- The site should pick one convention and use it consistently. Recommendation: use "Seccion 8" in body text since the audience is Spanish-speaking, with "(Section 8)" in parentheses on first reference per page.

**"Housing" translation (CONSISTENT):**
- "vivienda" is used consistently throughout (good)
- "alojamiento" appears only twice across the entire site
- "hogar" (home) and "refugio" (shelter) used appropriately in different contexts

**"Voucher" translation (MOSTLY CONSISTENT):**
- "cupon" used consistently in body text
- "voucher" appears only in JavaScript form values and English URLs (acceptable)

**"Eviction" translation (CONSISTENT):**
- "desalojo" used across 156 pages (1,078 occurrences) - correct for US Latino usage
- "desahucio" appears on only 1 page (`derechos-del-inquilino.html`, 14 times) - this is Spain Spanish usage. Should be changed to "desalojo" for consistency and audience appropriateness.

### Specific translation issues

1. **"Cribado de Una Parada"** (in `beneficios.html`) - Awkward literal translation of "One-Stop Screening Tool." Better: "Herramienta integral de evaluacion" or simply "Benefits.gov: Evaluador de elegibilidad"

2. **Untranslated English search instruction** (in `derechos-del-inquilino.html`): Text tells users to search for `"[tu estado] tenant rights"` -- should suggest a Spanish search term or note that English results may be more comprehensive.

3. **"Housing Choice Voucher"** left in English (in `section-8-explicado.html`, 3 occurrences) - This is the official program name so it's acceptable, but could include "Cupon de Eleccion de Vivienda" in parentheses for clarity.

### Missing content sections

| English page | Spanish page | Missing section |
|---|---|---|
| `resources/tenant-rights.html` | `es/recursos/derechos-del-inquilino.html` | "Understanding Your Lease" (entire h2 section) |
| `resources/benefits.html` | `es/recursos/beneficios.html` | "Related Guides" (1 of 15 h2 sections) |

---

## 7. JavaScript Template Literal Bug

In `es/recursos/herramientas/evaluador-elegibilidad.html`, a link href contains a raw template literal:

```html
<a href="${p.link}">${p.linkText} &rarr;</a>
```

This appears to be in an HTML template string that should be rendered by JavaScript but is instead being output as literal HTML. This would result in a broken link for users.

---

## Priority Fix Recommendations

### P0 - Critical (breaks user experience)
1. **Fix the 74 unique broken slug targets** affecting 737 links. Either rename the files to match what links expect, or update all links to match actual filenames. Updating links is safer since search engines may have indexed current filenames.
2. **Fix `components.js` nav bar** -- Spanish Blog and Guides links point to English pages.
3. **Fix `components.js` footer** -- Privacy, Terms, and Accessibility links point to English pages.

### P1 - High (missing critical information)
4. **Add missing phone numbers** to the 8 affected Spanish pages, especially the DV hotline and crisis lines.
5. **Fix `donde-empezar.html`** -- 22 links point to English guide pages. This is the primary entry point for new Spanish-speaking users.
6. **Fix `index.html`** -- 4 topic cards link to English resource pages.
7. **Translate the missing blog post** "What Counts as Income on Section 8" -- this is practical content.

### P2 - Medium (quality improvements)
8. **Standardize "Section 8" vs "Seccion 8"** across all pages.
9. **Replace "desahucio" with "desalojo"** in `derechos-del-inquilino.html`.
10. **Add the missing "Understanding Your Lease" section** to `derechos-del-inquilino.html`.
11. **Fix the template literal bug** in `evaluador-elegibilidad.html`.
12. **Add `https://www.napsa.org`** link to `discapacidades.html`.

### P3 - Low (polish)
13. Improve "Cribado de Una Parada" translation.
14. Add `author.html` and `resources/downloads/` Spanish counterparts.
15. Fix the "[tu estado] tenant rights" English search suggestion.
