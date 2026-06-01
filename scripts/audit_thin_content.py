#!/usr/bin/env python3
"""Site-wide thin-content auditor (GSC Phase 4).

Sweeps every content HTML page and scores it on the same risk profile as the
URLs Google flagged "Crawled - currently not indexed", so weak pages can be
caught proactively.

Per page it records: byte size, body word count (nav/footer/script stripped),
a cohort 6-gram uniqueness score (how non-duplicative the body is vs. other
pages in the same folder), outbound + inbound internal link counts, which
JSON-LD types are present, last-modified date, and an optional GSC flag.

A page is AT-RISK if it meets >=2 of:
  - word count < 600
  - uniqueness score < 0.40  (>60% of its 6-grams also appear in 3+ folder peers)
  - inbound internal links < 3
  - no structured data (no JSON-LD at all)
  - last-modified > 90 days ago

Writes _audit/thin_content_<date>.csv (the _audit/ dir is gitignored) and prints
a summary. Drop a GSC export at _audit/gsc_not_indexed.txt (one URL or path per
line) to populate the gsc_not_indexed column.

Usage:  python3 scripts/audit_thin_content.py
"""
import os, re, sys, json, csv, datetime
import html as htmllib
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.date.today().isoformat()
NOW = datetime.datetime.now().timestamp()
EXCLUDE_DIRS = {".git", "_audit", "node_modules", "scripts", "templates", "data", ".github"}

def discover():
    out = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        out.append(p)
    return sorted(out)

def canon(s):
    s = str(s).replace("\\", "/").split("#")[0].split("?")[0]
    s = re.sub(r"/+$", "", s)
    s = re.sub(r"\.html$", "", s)
    s = re.sub(r"/index$", "", s)
    return "" if s == "index" else s

def resolve(href, page_dir):
    href = href.strip()
    if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:")):
        return None
    if href.startswith("/"):
        base = href[1:]
    else:
        base = os.path.normpath(os.path.join(page_dir, href)).replace("\\", "/")
    return canon(base)

def body_text(raw):
    t = re.sub(r"<(script|style|nav|footer|header)\b[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmllib.unescape(t)
    return re.sub(r"\s+", " ", t).strip()

def ld_types(raw):
    types = set()
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        try:
            d = json.loads(b)
        except Exception:
            continue
        nodes = d.get("@graph", [d]) if isinstance(d, dict) else (d if isinstance(d, list) else [d])
        for n in nodes:
            t = n.get("@type") if isinstance(n, dict) else None
            if isinstance(t, list):
                types.update(t)
            elif t:
                types.add(t)
    return types

def grams(words, n=6):
    return {tuple(words[i:i+n]) for i in range(len(words) - n + 1)} if len(words) >= n else set()

# ---- gather ----
files = discover()
pages = {}
for p in files:
    raw = p.read_text(encoding="utf-8", errors="replace")
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    key = canon(rel)
    txt = body_text(raw)
    pages[key] = {
        "path": rel, "dir": os.path.dirname(rel),
        "size": len(raw.encode("utf-8")), "words": len(txt.split()),
        "ld": ld_types(raw), "text": txt,
        "age_days": int((NOW - p.stat().st_mtime) / 86400),
        "raw": raw,
    }
keyset = set(pages)

# ---- link graph ----
for key, info in pages.items():
    outs = {resolve(m.group(1), info["dir"]) for m in re.finditer(r'href="([^"]+)"', info["raw"])}
    info["out_internal"] = {o for o in outs if o in keyset and o != key}
inbound = defaultdict(set)
for key, info in pages.items():
    for tgt in info["out_internal"]:
        inbound[tgt].add(key)

# ---- cohort uniqueness (per folder) ----
folders = defaultdict(list)
for key, info in pages.items():
    folders[info["dir"]].append(key)
gset = {k: grams(pages[k]["text"].lower().split()) for k in pages}
for folder, keys in folders.items():
    df = defaultdict(int)
    for k in keys:
        for g in gset[k]:
            df[g] += 1
    for k in keys:
        gs = gset[k]
        if not gs:
            pages[k]["uniq"] = 1.0
            continue
        shared = sum(1 for g in gs if df[g] - 1 >= 3)  # appears in 3+ OTHER folder pages
        pages[k]["uniq"] = round(1 - shared / len(gs), 3)

# ---- optional GSC export ----
gsc = set()
for cand in ("_audit/gsc_not_indexed.txt", "_audit/gsc_not_indexed.csv"):
    fp = ROOT / cand
    if fp.exists():
        for line in fp.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip().strip('",')
            if not line or line.lower().startswith(("url", "page")):
                continue
            m = re.search(r"waythroughproject\.com(/\S*)", line)
            gsc.add(canon(m.group(1) if m else line))

# ---- score + write ----
rows = []
for key, info in sorted(pages.items()):
    inb = len(inbound.get(key, ()))
    has_ld = bool(info["ld"])
    reasons = []
    if info["words"] < 600: reasons.append("thin(<600w)")
    if info["uniq"] < 0.40: reasons.append("duplicative(<0.40)")
    if inb < 3: reasons.append("few-inbound(<3)")
    if not has_ld: reasons.append("no-structured-data")
    if info["age_days"] > 90: reasons.append("stale(>90d)")
    at_risk = len(reasons) >= 2
    action = ""
    if at_risk:
        action = "Consolidate/noindex" if info["words"] < 300 else "Strengthen"
    rows.append({
        "url_path": "/" + key if key else "/",
        "size_bytes": info["size"], "word_count": info["words"],
        "uniq_score": info["uniq"], "outbound_internal": len(info["out_internal"]),
        "inbound_internal": inb,
        "FAQPage": "Y" if "FAQPage" in info["ld"] else "",
        "HowTo": "Y" if "HowTo" in info["ld"] else "",
        "BreadcrumbList": "Y" if "BreadcrumbList" in info["ld"] else "",
        "any_structured_data": "Y" if has_ld else "",
        "age_days": info["age_days"],
        "gsc_not_indexed": "Y" if key in gsc else "",
        "risk_count": len(reasons), "at_risk": "Y" if at_risk else "",
        "risk_reasons": "; ".join(reasons), "suggested_action": action,
    })

(ROOT / "_audit").mkdir(exist_ok=True)
out_csv = ROOT / "_audit" / f"thin_content_{TODAY}.csv"
cols = list(rows[0].keys())
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

at_risk = [r for r in rows if r["at_risk"]]
stale_all = all(r["age_days"] == rows[0]["age_days"] for r in rows)
print(f"Pages scanned : {len(rows)}")
print(f"At-risk pages : {len(at_risk)}  ({100*len(at_risk)//max(1,len(rows))}%)")
print(f"CSV written   : _audit/thin_content_{TODAY}.csv")
if stale_all:
    print("NOTE: every file shares the same mtime (filesystem copy) -> 'stale(>90d)' is not a")
    print("      reliable signal here; weigh the other four metrics. Use git log for true age.")
print("\nTop at-risk (by risk_count desc, then word_count asc):")
for r in sorted(at_risk, key=lambda r: (-r["risk_count"], r["word_count"]))[:25]:
    print(f"  [{r['risk_count']}] {r['url_path']:<48} {r['word_count']:>4}w uniq={r['uniq_score']} "
          f"in={r['inbound_internal']} ld={r['any_structured_data'] or '-'}  {r['risk_reasons']}")
