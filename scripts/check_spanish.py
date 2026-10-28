#!/usr/bin/env python3
"""Audit Spanish (es) HTML pages for missing accents/diacritics.

Usage:
    python3 scripts/check_spanish.py                 # scans es/**/*.html
    python3 scripts/check_spanish.py es/recursos/estados/*.html

Exits non-zero if any page's visible text contains a red-flag un-accented
Spanish word. HTML tags (and therefore href URL slugs) plus <script>/<style>
blocks (JS string literals, slugs) are ignored.

Known false positives to eyeball manually (these are correct as-is):
  - "Division" inside an English proper noun, e.g. "Salvation Army Cascade
    Division" or a place like "Division Circle" - correct English, not Spanish.
  - "limites"/"limite" as the VERB ("no te limites a una sola PHA", "que
    limite ...") - correctly un-accented, unlike the noun "limite/limites".
"""
import sys
import re
import glob
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ES_REDFLAGS = [
    "informacion", "deposito", "depositos", "seccion", "proteccion",
    "pagina", "paginas", "telefono", "numero", "numeros", "credito", "creditos",
    "energia", "mayoria", "garantia", "dias", "ano", "anos", "dueno", "duenos",
    "duena", "danos", "nino", "ninos", "despues", "segun", "tambien", "ademas",
    "aqui", "alli", "asi", "comision", "division", "articulo", "economica",
    "economico", "energetica", "energetico", "restitucion", "citacion",
    "devolucion", "discriminacion", "reubicacion", "inspeccion", "renovacion",
    "aplicacion", "terminacion", "estabilizacion", "anulacion", "calefaccion",
    "jurisdiccion", "organizacion", "declaracion", "condicion", "situacion",
    "duracion", "comunicacion", "preempcion", "practicamente", "pequeno",
    "pequenos", "pequena", "interes", "cupon", "razon", "habia", "habian",
    "tenia", "limite", "limites", "maximo", "maxima", "minimo",
]


def violations(html):
    # Drop <script>/<style> blocks first so JS string literals and URL slugs
    # (correctly plain-ASCII) aren't mistaken for un-accented visible prose.
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    out = {}
    for w in ES_REDFLAGS:
        n = len(re.findall(r"\b" + w + r"\b", text, re.IGNORECASE))
        n -= len(_exempt(w, text))
        if n:
            out[w] = n
    return out


# The two documented false positives, recognised instead of eyeballed:
#  - "Division" as part of an English proper noun: a capitalised word right before or after it
#    ("Salvation Army Midland Division", "Division Circle"). Lowercase "division" in prose still fails.
#  - "limite"/"limites" as the subjunctive VERB right after te/se/que/no
#    ("no te limites", "que limite"). The noun ("el limite", "los limites") still fails.
def _exempt(word, text):
    if word == "division":
        return re.findall(r"\b[A-Z][A-Za-z.]*\s+Division\b|\bDivision\s+(?=[A-Z])", text)
    if word in ("limite", "limites"):
        return re.findall(r"\b(?:te|se|que|no)\s+" + word + r"\b", text, re.IGNORECASE)
    return []


def main():
    args = sys.argv[1:]
    files = []
    if args:
        for a in args:
            files.extend(glob.glob(a))
    else:
        files = glob.glob(str(REPO_ROOT / "es" / "**" / "*.html"), recursive=True)
    files = sorted(set(files))
    bad = 0
    for f in files:
        v = violations(Path(f).read_text(encoding="utf-8"))
        if v:
            bad += 1
            print(f"FAIL  {f}: {v}")
    if bad:
        print(f"\n{bad} of {len(files)} Spanish file(s) have un-accented words.")
        sys.exit(1)
    print(f"OK: all {len(files)} Spanish file(s) clean.")


if __name__ == "__main__":
    main()
