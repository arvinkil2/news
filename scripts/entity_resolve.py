#!/usr/bin/env python3
"""Cross-dataset entity resolution (Step B, first slice).

Pass A: swaps single-name CDS panel rows -> bond registry issuers and
watched issuers. Pass B: CMBS trust pages -> N-PORT marks panel classes.

Output: ~/workspace/news-site/data/entity_index_resolution.json
(build record; consumed by build_entity_index.py; not a site download).

Match discipline: exact (suffix-unified) -> normalized (core key) ->
alias (issuer crosswalk) -> manual (hand-verified map in this file).
Anything hitting two distinct registry families is ambiguous, never
forced. Parent/subsidiary pairs are never merged: a name resolves
only to its own issuer string.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

WS = os.path.expanduser("~/workspace")
NEWS = os.path.join(WS, "news-site")
OUT = os.path.join(NEWS, "data", "entity_index_resolution.json")

# ---------------------------------------------------------------- names
SUFFIX_UNIFY = {
    "CORPORATION": "CORP", "INCORPORATED": "INC", "COMPANY": "CO",
    "LIMITED": "LTD", "INC.": "INC", "CORP.": "CORP", "CO.": "CO",
    "LTD.": "LTD",
}
LEGAL_TOKENS = {
    "INC", "CORP", "CO", "LTD", "LLC", "LP", "LLP", "PLC", "SA", "NV",
    "BV", "AG", "SPA", "KK", "GMBH", "SDN", "BHD", "ASA", "AB", "OYJ",
    "THE",
}


def norm_full(name):
    """Suffix-unified, punctuation-stripped uppercase form."""
    s = str(name).upper().replace("&", " AND ")
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    toks = [SUFFIX_UNIFY.get(t, t) for t in s.split()]
    return " ".join(toks).strip()


def core_key(name):
    """norm_full with trailing legal-form tokens removed."""
    toks = norm_full(name).split()
    while toks and toks[-1] in LEGAL_TOKENS:
        toks.pop()
    if toks and toks[0] == "THE":
        toks = toks[1:]
    return " ".join(toks)


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
    return s or "name"


# Hand-verified matches the mechanical rules cannot make safely.
# key: core_key of swaps display -> registry issuer string exactly as
# printed in bonds.json. Each entry was checked to be the same legal
# entity (not a parent/subsidiary substitution).
MANUAL = {}

SOVEREIGN_RE = re.compile(
    r"^(REPUBLIC|KINGDOM|FEDERATIVE REPUBLIC|FEDERAL REPUBLIC|"
    r"UNITED MEXICAN STATES|ARGENTINE REPUBLIC|DOMINICAN REPUBLIC|"
    r"ARAB REPUBLIC|SULTANATE|EMIRATE|PRINCIPALITY|GRAND DUCHY|"
    r"STATE OF|COMMONWEALTH OF|HASHEMITE KINGDOM|PEOPLES REPUBLIC|"
    r"PEOPLE'S REPUBLIC)")


def unmatched_reason(display, key):
    if re.search(r"\(|TLB|TRS|-DDTL|\d+/\d+\)", display):
        return "loan underlier string in the panel, not a CDS reference entity"
    if SOVEREIGN_RE.match(norm_full(display)) or "REPUBLIC" in key \
            or key.endswith("STATES") or "KINGDOM" in key:
        return "sovereign reference entity; the registry holds corporate and structured issuers"
    return "no registry or watched issuer under this name or a variant"


# ---------------------------------------------------------------- pass A
def pass_a():
    stats = json.load(open(os.path.join(
        WS, "dtcc-swaps/stats/out/cds_names.json")))
    panel = []
    for nm in stats["names"]:
        pt = (nm.get("points") or {}).get("60")
        if pt and pt.get("trades", 0) >= 3 and pt.get("median_bp") is not None:
            panel.append(nm)
    panel.sort(key=lambda n: -(n["points"]["60"]["trades"]))

    curve_slugs = {}
    name_dir = os.path.join(NEWS, "content/swaps/credit/name")
    for fn in os.listdir(name_dir):
        if fn.endswith(".md"):
            txt = open(os.path.join(name_dir, fn)).read(600)
            m = re.search(r'title:\s*"([^"]+)"', txt)
            if m:
                curve_slugs[m.group(1)] = fn[:-3]

    reg = json.load(open(os.path.join(NEWS, "data/macro/bonds.json")))
    bonds = reg["bonds"]
    by_issuer = defaultdict(list)
    for b in bonds:
        by_issuer[b["issuer"]].append(b)
    iss_dir = os.path.join(NEWS, "content/leverage/issuer")
    have_pages = {fn[:-3] for fn in os.listdir(iss_dir) if fn.endswith(".md")}
    title_core_to_slug = {}
    for slug in have_pages:
        txt = open(os.path.join(iss_dir, slug + ".md")).read(400)
        m = re.search(r'title:\s*"([^"]+)"', txt)
        if m:
            title_core_to_slug.setdefault(core_key(m.group(1)), slug)

    def issuer_slug_for(fam, canon_iss):
        for cand in (slugify(fam or ""), slugify(canon_iss or "")):
            if cand in have_pages:
                return cand
        for key in (core_key(fam or ""), core_key(canon_iss or "")):
            if key in title_core_to_slug:
                return title_core_to_slug[key]
        return None

    issuer_page = {}
    for iss, bl in by_issuer.items():
        s = issuer_slug_for(bl[0].get("deal"), iss)
        if s:
            issuer_page[iss] = s

    nport = json.load(open(os.path.join(NEWS, "data/macro/nport_panel.json")))
    nport_bonds = nport.get("bonds", {})

    watched = json.load(open(os.path.join(
        WS, "ai-leverage-monitor/data/watched_issuers.json")))["issuers"]

    cw = json.load(open(os.path.join(
        WS, "ai-leverage-monitor/data/issuer_crosswalk.json")))["records"]
    # crosswalk alias index: normalized name -> record
    cw_alias = {}
    for rec in cw:
        names = list(rec.get("registry_names") or [])
        if rec.get("finra_name_proven"):
            names.append(rec["finra_name_proven"])
        names += list(rec.get("additional_finra_names") or [])
        for n in names:
            cw_alias.setdefault(norm_full(n), rec)
            cw_alias.setdefault(core_key(n), rec)

    # lookup indices over registry issuers and watched names
    reg_by_full, reg_by_core = {}, defaultdict(set)
    for iss in by_issuer:
        reg_by_full.setdefault(norm_full(iss), iss)
        reg_by_core[core_key(iss)].add(iss)
    wat_by_full, wat_by_core = {}, defaultdict(set)
    for w in watched:
        wat_by_full.setdefault(norm_full(w["finra_name"]), w)
        wat_by_core[core_key(w["finra_name"])].add(w["finra_name"])

    entities = {}
    rows = []
    for nm in panel:
        disp = nm["display"]
        full, core = norm_full(disp), core_key(disp)
        status, method, evidence = "unmatched", "none", ""
        reg_hits, wat_hit = [], None

        cand_full = reg_by_full.get(full)
        cand_core = reg_by_core.get(core, set())
        if cand_full:
            reg_hits, method = [cand_full], "exact"
            evidence = "suffix-unified full name equals registry issuer"
        elif len(cand_core) == 1:
            reg_hits, method = list(cand_core), "normalized"
            evidence = "core name (legal suffix removed) equals registry issuer"
        elif len(cand_core) > 1:
            fams = {by_issuer[i][0].get("deal") for i in cand_core}
            if len(fams) == 1:
                reg_hits, method = sorted(cand_core), "normalized"
                evidence = ("core name matches several issuer strings of "
                            "one registry family")
            else:
                status = "ambiguous"
                evidence = ("core name matches issuer strings in %d "
                            "registry families" % len(fams))
        if not reg_hits and status != "ambiguous":
            rec = cw_alias.get(full) or cw_alias.get(core)
            if rec:
                fam = rec.get("family")
                fam_iss = [i for i in by_issuer
                           if by_issuer[i][0].get("deal") == fam]
                named = [i for i in (rec.get("registry_names") or [])
                         if i in by_issuer]
                hits = named or fam_iss
                if hits:
                    reg_hits, method = sorted(hits), "alias"
                    evidence = ("issuer crosswalk family %s links this "
                                "name to the registry" % fam)
        if not reg_hits and status != "ambiguous" and core in MANUAL:
            reg_hits, method = [MANUAL[core]], "manual"
            evidence = "hand-verified legal-entity match"
        # watched side (independent of registry)
        wf = wat_by_full.get(full)
        wc = wat_by_core.get(core, set())
        if wf:
            wat_hit = wf
        elif len(wc) == 1:
            wat_hit = next(w for w in watched if w["finra_name"] in wc)
        if reg_hits:
            status = "matched"
        rows.append({
            "display": disp, "key": nm["key"], "full": full, "core": core,
            "bp": nm["points"]["60"]["median_bp"],
            "trades": nm["points"]["60"]["trades"],
            "status": status, "method": method, "evidence": evidence,
            "registry_issuers": reg_hits,
            "watched": ({"finra_name": wat_hit["finra_name"],
                         "group": wat_hit["group"],
                         "tier": wat_hit["tier"]} if wat_hit else None),
            "curve_slug": curve_slugs.get(disp),
            "reason": ("" if status == "matched" else
                       evidence if status == "ambiguous" else
                       unmatched_reason(disp, core)),
        })

    # group panel rows into entities: matched rows group by their
    # registry family; unmatched rows group by core key (variants).
    for r in rows:
        if r["registry_issuers"]:
            fam = by_issuer[r["registry_issuers"][0]][0].get("deal")
            gid = "reg:" + str(fam)
        else:
            gid = "core:" + r["core"]
        e = entities.setdefault(gid, {
            "gid": gid, "swaps_forms": [], "rows": [],
            "registry_issuers": set(), "watched": None,
            "status": r["status"], "method": r["method"],
            "evidence": r["evidence"], "reason": r["reason"],
            "curve_slug": None})
        e["swaps_forms"].append(r["display"])
        e["rows"].append({"display": r["display"], "bp": r["bp"],
                          "trades": r["trades"], "key": r["key"]})
        e["registry_issuers"].update(r["registry_issuers"])
        if r["watched"] and not e["watched"]:
            e["watched"] = r["watched"]
        if r["curve_slug"]:
            e["curve_slug"] = r["curve_slug"]
        if r["status"] == "matched":
            e["status"] = "matched"
    out_entities = []
    for gid, e in entities.items():
        bl = []
        for iss in sorted(e["registry_issuers"]):
            bl += by_issuer[iss]
        cusips = sorted({b["cusip"] for b in bl})
        priced = [c for c in cusips
                  if c in nport_bonds and nport_bonds[c].get("latest")]
        periods = Counter(
            nport_bonds[c]["latest"]["period_end"] for c in priced
            if nport_bonds[c]["latest"].get("period_end"))
        fam = bl[0].get("deal") if bl else None
        fam_issuers = sorted({b["issuer"] for b in bonds
                              if fam and b.get("deal") == fam})
        fam_cusips = sorted({b["cusip"] for b in bonds
                             if fam and b.get("deal") == fam})
        canon = (sorted(e["registry_issuers"])[0] if e["registry_issuers"]
                 else max(e["rows"], key=lambda x: x["trades"])["display"])
        out_entities.append({
            "gid": gid,
            "canonical": canon,
            "slug": slugify(canon),
            "swaps_forms": e["swaps_forms"],
            "swaps_rows": e["rows"],
            "bp_primary": max(e["rows"], key=lambda x: x["trades"])["bp"],
            "curve_slug": e["curve_slug"],
            "status": e["status"], "method": e["method"],
            "evidence": e["evidence"], "reason": e["reason"],
            "registry_issuers": sorted(e["registry_issuers"]),
            "family": fam,
            "family_issuers": fam_issuers,
            "family_cusip_count": len(fam_cusips),
            "cusips": cusips,
            "issuer_page": next((issuer_page[i] for i in
                                 sorted(e["registry_issuers"])
                                 if i in issuer_page), None),
            "watched": e["watched"],
            "nport": ({"priced": len(priced), "total": len(cusips),
                       "modal_period": (periods.most_common(1)[0][0]
                                        if periods else None)}
                      if cusips else None),
        })
    out_entities.sort(key=lambda e: -(max(r["trades"] for r in e["swaps_rows"])))
    # reverse coverage: registry families and watched issuers w/o panel
    matched_fams = {e["family"] for e in out_entities if e["family"]}
    all_fams = sorted({b.get("deal") for b in bonds if b.get("deal")})
    matched_watched = {e["watched"]["finra_name"] for e in out_entities
                       if e["watched"]}
    return {
        "panel_rows": len(panel),
        "entities": out_entities,
        "registry_families_total": len(all_fams),
        "registry_families_matched": sorted(matched_fams),
        "registry_families_unmatched": [f for f in all_fams
                                        if f not in matched_fams],
        "watched_total": len(watched),
        "watched_matched": sorted(matched_watched),
        "watched_unmatched": [w["finra_name"] for w in watched
                              if w["finra_name"] not in matched_watched],
        "registry_bonds_total": len(bonds),
        "registry_issuers_total": len(by_issuer),
    }


# ---------------------------------------------------------------- pass B
def pass_b():
    import duckdb
    marks = json.load(open(os.path.join(NEWS, "data/macro/cmbs_marks.json")))
    classes = marks["classes"]
    deal_dir = os.path.join(NEWS, "content/cmbs/deal")
    pages = []
    for fn in sorted(os.listdir(deal_dir)):
        if not fn.endswith(".md") or fn == "_index.md":
            continue
        txt = open(os.path.join(deal_dir, fn)).read(2500)
        title = re.search(r'title:\s*"([^"]+)"', txt)
        lede = re.search(r'lede:\s*"([^"]+)"', txt)
        title = title.group(1) if title else fn[:-3]
        name = title
        if lede:
            m = re.search(r"for (.+)\.$", lede.group(1))
            if m:
                name = m.group(1)
        cik = re.search(r"CIK (\d+)", title)
        seg = re.search(r"segment ([A-Z0-9]+)", title)
        pages.append({"slug": fn[:-3], "title": title, "name": name,
                      "cik": int(cik.group(1)) if cik else None,
                      "segment": seg.group(1) if seg else None})

    con = duckdb.connect(os.path.join(WS, "merged-db/merged.duckdb"),
                         read_only=True)
    con.execute("SET memory_limit='2GB'")
    con.execute("SET threads=2")
    deals = con.execute(
        "SELECT cik, deal_segment, trust_name FROM deals").fetchall()
    tr = con.execute(
        "SELECT cik, deal_segment, trust_name, cusip FROM tranches "
        "WHERE cusip IS NOT NULL").fetchall()
    con.close()
    # A trust name can be registered under several (cik, segment) units
    # in the merged DB (filing-segment duplicates of one trust). The
    # class set of the trust is the union over its units; sets were
    # verified identical across units for 127 of 128 multi-unit names.
    unit_sets = defaultdict(set)
    name_units = defaultdict(set)
    for cik, seg, tname, cusip in tr:
        unit_sets[(cik, seg, norm_full(tname))].add(cusip)
        name_units[norm_full(tname)].add((cik, seg))
    tr_by_name = {}
    sets_identical = {}
    for nname, us in name_units.items():
        union = set()
        first = None
        ident = True
        for (cik, seg) in us:
            s = unit_sets[(cik, seg, nname)]
            union |= s
            if first is None:
                first = s
            elif s != first:
                ident = False
        tr_by_name[nname] = sorted(union)
        sets_identical[nname] = ident
    deal_units = Counter()
    for cik, seg, tname in deals:
        deal_units[norm_full(tname)] += 1

    out = []
    for p in pages:
        nname = norm_full(p["name"])
        cusips, method, status = [], "none", "unmatched"
        n_units = len(name_units.get(nname, ()))
        unit_key = (p["cik"], p["segment"], nname)
        if p["cik"] is not None and p["segment"] and unit_key in unit_sets:
            # exact unit: page title carries both CIK and segment
            cusips = sorted(unit_sets[unit_key])
            status, method = "resolved", "cik+segment"
        elif nname in tr_by_name:
            cusips = tr_by_name[nname]
            status = "resolved"
            unit_ciks = {c for (c, s) in name_units[nname]}
            if p["cik"] is not None and p["cik"] in unit_ciks:
                method = "cik+name"
            elif p["cik"] is not None:
                method = "name (page CIK not among DB units)"
            else:
                method = "name"
        covered = [c for c in set(cusips) if c in classes]
        periods = Counter(classes[c]["period_end"] for c in covered
                          if classes[c].get("period_end"))
        out.append({
            "slug": p["slug"], "name": p["name"], "title": p["title"],
            "cik": p["cik"], "segment": p["segment"],
            "db_status": status, "db_method": method,
            "db_units": n_units,
            "db_sets_identical": sets_identical.get(nname),
            "classes_total": len(set(cusips)),
            "classes_with_marks": len(covered),
            "fund_class_reports": sum(classes[c]["n_funds"] for c in covered),
            "mark_period_modal": (periods.most_common(1)[0][0]
                                  if periods else None),
            "mark_period_max": (max(periods) if periods else None),
            "in_panel": len(covered) > 0,
        })
    return {
        "trust_pages": len(pages),
        "marks_classes_total": len(classes),
        "marks_latest_quarter": marks.get("latest_quarter"),
        "trusts": out,
        "db_units_total": len(deals),
        "db_trust_names_total": len(deal_units),
    }


def main():
    a = pass_a()
    b = pass_b()
    doc = {"generated": "2026-10-21", "pass_a": a, "pass_b": b}
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=1)
    ea = a["entities"]
    print("PASS A: panel rows", a["panel_rows"], "-> entities", len(ea))
    print("  matched", sum(1 for e in ea if e["status"] == "matched"),
          "ambiguous", sum(1 for e in ea if e["status"] == "ambiguous"),
          "unmatched", sum(1 for e in ea if e["status"] == "unmatched"))
    print("  methods:", Counter(e["method"] for e in ea
                                if e["status"] == "matched"))
    tb = b["trusts"]
    print("PASS B: trust pages", b["trust_pages"],
          "in panel", sum(1 for t in tb if t["in_panel"]),
          "not in panel", sum(1 for t in tb if not t["in_panel"]))
    print("  db:", Counter(t["db_status"] for t in tb))
    print("wrote", OUT)


if __name__ == "__main__":
    sys.exit(main())
