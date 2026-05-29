#!/usr/bin/env python3
"""Audit Spanish (es) HTML pages for missing accents/diacritics.

Usage:
    python3 scripts/check_spanish.py                 # scans es/**/*.html
    python3 scripts/check_spanish.py es/recursos/estados/*.html

Exits non-zero if any page's visible text contains a red-flag un-accented
Spanish word. HTML tags (and therefore href URL slugs) are ignored.
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
    text = re.sub(r"<[^>]+>", " ", html)
    out = {}
    for w in ES_REDFLAGS:
        n = len(re.findall(r"\b" + w + r"\b", text, re.IGNORECASE))
        if n:
            out[w] = n
    return out


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
