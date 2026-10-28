#!/usr/bin/env python3
"""Build the Positioning section of news.kilambi.com from the tidy
positioning datasets (CFTC COT family, Bank Participation, OCC,
ICE CoT, ESMA Article 58, LME COTR, UK and EU short positions,
SGX derivatives, TOCOM, CZCE coverage).

Reads ONLY the processed dataset files under ~/workspace/cftc-data/
and ~/workspace/positioning-harvest/. Computes the derived measures
of the design brief (net, week / 4-week / 13-week change, percent of
open interest, percentile, z-score, COT Index) at build time and
writes data/positioning/*.json plus the pages under
content/positioning/. Modelled on build_markets_pages.py.

Usage:
  build_positioning_pages.py              full build
  build_positioning_pages.py --if-changed build only when the input
                                          fingerprint changed; prints
                                          PUBLISH lines for outputs,
                                          or NOCHANGE.
"""
import collections
import csv
import datetime
import hashlib
import html
import json
import math
import os
import re
import statistics
import sys

csv.field_size_limit(10 ** 8)

SITE = os.path.expanduser("~/workspace/news-site")
CFTC = os.path.expanduser("~/workspace/cftc-data/datasets")
PH = os.path.expanduser("~/workspace/positioning-harvest")
OUT = os.path.join(SITE, "content", "positioning")
OUTD = os.path.join(SITE, "data", "positioning")
STATE = os.path.join(SITE, "scripts", ".positioning_build_state.json")

BLANK = '<span class="blank">-</span>'
PUBLISHED = []  # repo-relative paths written this run


def esc(s):
    return html.escape(str(s), quote=True)


def num(x):
    if x is None or x == "" or x == ".":
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def fi(v, signed=False):
    """Integer with thousands separators."""
    if v is None:
        return BLANK
    v = int(round(v))
    if signed:
        return f"{v:+,}"
    return f"{v:,}"


def fp(v, digits=1):
    if v is None:
        return BLANK
    return f"{v:.{digits}f}"


def fpct(v, digits=1):
    if v is None:
        return BLANK
    return f"{v:.{digits}f}%"


def fdate(iso):
    if not iso:
        return "-"
    d = datetime.date.fromisoformat(str(iso)[:10])
    return d.strftime("%a %-d %b %Y")


def qlabel(period_end):
    """'1998-06-30' -> 'Q2 1998'."""
    y, m = period_end[:4], int(period_end[5:7])
    return f"Q{(m - 1) // 3 + 1} {y}"


def count_rows(path):
    """Data rows in a CSV file (newline count minus the header)."""
    n = 0
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            n += chunk.count(b"\n")
    return max(n - 1, 0)


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", str(s)).strip("-").lower()
    return s or "market"


def friday_after(iso):
    d = datetime.date.fromisoformat(str(iso)[:10])
    delta = (4 - d.weekday()) % 7
    return (d + datetime.timedelta(days=delta)).isoformat()


def spark_svg(values, width=96, height=28):
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1.0
    step = width / (len(vals) - 1)
    pts = []
    for i, v in enumerate(values):
        if v is None:
            continue
        x = i * step
        y = height - 3 - (v - lo) / rng * (height - 6)
        pts.append(f"{x:.1f},{y:.1f}")
    if len(pts) < 2:
        return ""
    color = "#1a7f37" if vals[-1] >= vals[0] else "#b42318"
    return (f'<svg class="spark" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" aria-hidden="true">'
            f'<polyline points="{" ".join(pts)}" fill="none" '
            f'stroke="{color}" stroke-width="1.5"/></svg>')


def gauges(series):
    """series: list of (date, net) ascending. Returns derived measures
    for the latest observation, per the brief's windows and minimums.
    Percentile = share of window observations at or below the current
    net, times 100. Z-score uses the window standard deviation."""
    out = {"n": len(series)}
    if not series:
        return out
    vals = [v for _, v in series]
    cur = vals[-1]
    out["net"] = cur
    out["wow"] = cur - vals[-2] if len(vals) >= 2 else None
    out["chg4"] = cur - vals[-5] if len(vals) >= 5 else None
    out["chg13"] = cur - vals[-14] if len(vals) >= 14 else None
    w52 = vals[-52:]
    out["hi52"] = max(w52)
    out["lo52"] = min(w52)
    if len(w52) >= 40:
        out["pct1y"] = 100.0 * sum(1 for x in w52 if x <= cur) / len(w52)
        sd = statistics.pstdev(w52)
        out["z52"] = (cur - statistics.fmean(w52)) / sd if sd > 0 else None
    w156 = vals[-156:]
    if len(w156) >= 104:
        out["pct3y"] = 100.0 * sum(1 for x in w156 if x <= cur) / len(w156)
        lo, hi = min(w156), max(w156)
        out["cotindex"] = (100.0 * (cur - lo) / (hi - lo)
                           if hi > lo else None)
    return out


def frontmatter(title, lede, data_as_of):
    today = datetime.date.today().isoformat()
    title = title.replace('"', "'")
    lede = lede.replace('"', "'")
    data_as_of = data_as_of.replace('"', "'")
    return (f'---\ntitle: "{title}"\ndate: "{today}"\n'
            f'lede: "{lede}"\ndata_as_of: "{data_as_of}"\n---\n\n')


def write_page(relpath, text):
    path = os.path.join(SITE, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    PUBLISHED.append(relpath)


def write_json(name, obj):
    os.makedirs(OUTD, exist_ok=True)
    rel = f"data/positioning/{name}"
    with open(os.path.join(SITE, rel), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    PUBLISHED.append(rel)


def table(headers, rows, tid=None, cols=None, engine=False):
    """Plain market-table (or bw-grid when cols given)."""
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "\n".join(rows)
    if engine and cols:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from table_engine import bw_open
        return ('<div class="market-table-scroll">'
                + bw_open(tid, cols, engine_sort=True)
                + f"<tbody>\n{body}\n</tbody></table></div>\n")
    return (f'<table class="market-table"><thead><tr>{head}</tr>'
            f"</thead><tbody>\n{body}\n</tbody></table>\n")


def meta_lines(pairs):
    rows = [f'<tr><td>{esc(k)}</td><td>{v}</td></tr>' for k, v in pairs]
    return ('<table class="market-table"><tbody>\n'
            + "\n".join(rows) + "\n</tbody></table>\n")


# ---------------------------------------------------------------- COT

COT_FAMILIES = {
    "disaggregated": {
        "file": "disaggregated.csv", "label": "Disaggregated",
        "cats": [("prod_merc", "Producer/Merchant/Processor/User", None),
                 ("swap", "Swap Dealers", "swap_spread"),
                 ("m_money", "Managed Money", "m_money_spread"),
                 ("other_rept", "Other Reportables", "other_rept_spread"),
                 ("tot_rept", "Total reportable", None),
                 ("nonrept", "Nonreportable", None)],
        "spec": "m_money", "spec_label": "Managed Money",
    },
    "tff": {
        "file": "tff.csv", "label": "Traders in Financial Futures",
        "cats": [("dealer", "Dealer/Intermediary", "dealer_spread"),
                 ("asset_mgr", "Asset Manager/Institutional",
                  "asset_mgr_spread"),
                 ("lev_money", "Leveraged Funds", "lev_money_spread"),
                 ("other_rept", "Other Reportables", "other_rept_spread"),
                 ("tot_rept", "Total reportable", None),
                 ("nonrept", "Nonreportable", None)],
        "spec": "lev_money", "spec_label": "Leveraged Funds",
    },
    "legacy": {
        "file": "legacy.csv", "label": "Legacy",
        "cats": [("noncomm", "Non-commercial", "noncomm_spread"),
                 ("comm", "Commercial", None),
                 ("tot_rept", "Total reportable", None),
                 ("nonrept", "Nonreportable", None)],
        "spec": "noncomm", "spec_label": "Non-commercial",
    },
}


def cot_norm(row, spec):
    cats = {}
    for cat, _label, spread_col in spec["cats"]:
        lo = num(row.get(f"{cat}_long"))
        sh = num(row.get(f"{cat}_short"))
        sp = num(row.get(spread_col)) if spread_col else None
        cats[cat] = {"long": lo, "short": sh, "spread": sp,
                     "net": (lo - sh) if lo is not None
                     and sh is not None else None,
                     "pct_long": num(row.get(f"pctoi_{cat}_long")),
                     "pct_short": num(row.get(f"pctoi_{cat}_short")),
                     "traders_long": num(row.get(f"traders_{cat}_long")),
                     "traders_short": num(row.get(f"traders_{cat}_short"))}
    conc = {k: num(row.get(k)) for k in (
        "conc_gross4_long", "conc_gross4_short", "conc_gross8_long",
        "conc_gross8_short", "conc_net4_long", "conc_net4_short",
        "conc_net8_long", "conc_net8_short")}
    return {"date": row["report_date"],
            "name": row.get("market_and_exchange_names") or "",
            "mkt": row.get("contract_market_name") or "",
            "code": row.get("cftc_contract_market_code") or "",
            "units": row.get("contract_units") or "",
            "oi": num(row.get("open_interest")),
            "change_oi": num(row.get("change_open_interest")),
            "traders_tot": num(row.get("traders_tot")),
            "cats": cats, "conc": conc}


def load_cot():
    """Two passes: pass 1 finds the latest futures-only date per
    (family, code) and the speculative net history; pass 2 collects
    full rows for markets active in the trailing 104 weeks."""
    fams = {}
    ref = {}
    with open(os.path.join(CFTC, "cot", "market_reference.csv"),
              newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ref[r["cftc_contract_market_code"]] = r
    for fam, spec in COT_FAMILIES.items():
        path = os.path.join(CFTC, "cot", spec["file"])
        latest = {}
        hist = collections.defaultdict(list)
        maxdate = ""
        nrows = 0
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("crop_split") != "all":
                    continue
                nrows += 1
                d = row["report_date"]
                if d > maxdate:
                    maxdate = d
                if row.get("basis") != "futures_only":
                    continue
                code = row.get("cftc_contract_market_code") or ""
                sp = spec["spec"]
                lo = num(row.get(f"{sp}_long"))
                sh = num(row.get(f"{sp}_short"))
                net = (lo - sh) if lo is not None and sh is not None \
                    else None
                hist[code].append((d, net, num(row.get("open_interest"))))
                if code not in latest or d > latest[code]:
                    latest[code] = d
        cutoff = (datetime.date.fromisoformat(maxdate)
                  - datetime.timedelta(weeks=104)).isoformat()
        active = {c for c, d in latest.items() if d >= cutoff}
        for c in hist:
            hist[c].sort()
        fams[fam] = {"spec": spec, "latest": latest, "hist": hist,
                     "maxdate": maxdate, "active": active,
                     "nrows": nrows, "full": {}, "combined": {},
                     "splits": {}}
        # pass 2: full rows for active markets
        full = collections.defaultdict(list)
        combined = {}
        splits = {}
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                code = row.get("cftc_contract_market_code") or ""
                if code not in active:
                    continue
                if row.get("crop_split") == "all":
                    if row.get("basis") == "futures_only":
                        full[code].append(cot_norm(row, spec))
                    elif row.get("basis") == "combined":
                        d = row["report_date"]
                        if code not in combined \
                                or d > combined[code]["date"]:
                            combined[code] = cot_norm(row, spec)
                elif row.get("basis") == "futures_only" \
                        and row.get("crop_split") in ("old", "other"):
                    key = (code, row["report_date"])
                    splits.setdefault(key, {})[row["crop_split"]] = \
                        num(row.get("open_interest"))
        for c in full:
            full[c].sort(key=lambda r: r["date"])
        fams[fam]["full"] = dict(full)
        fams[fam]["combined"] = combined
        fams[fam]["splits"] = splits
    # CIT supplement: latest combined row per code
    cit = {}
    cit_path = os.path.join(CFTC, "cot", "cit_supplement.csv")
    cit_latest_date = ""
    with open(cit_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("crop_split") != "all":
                continue
            code = row.get("cftc_contract_market_code") or ""
            d = row["report_date"]
            if d > cit_latest_date:
                cit_latest_date = d
            lo, sh = num(row.get("cit_long")), num(row.get("cit_short"))
            if code not in cit or d > cit[code]["date"]:
                cit[code] = {"date": d,
                             "net": (lo - sh) if lo is not None
                             and sh is not None else None,
                             "long": lo, "short": sh,
                             "oi": num(row.get("open_interest"))}
    return fams, ref, cit, cit_latest_date


def cot_market_summaries(fams, ref, cit):
    """One summary per market (primary family wins: disaggregated,
    then TFF, then legacy), for active markets only."""
    order = ["disaggregated", "tff", "legacy"]
    seen = {}
    for fam in order:
        F = fams[fam]
        for code in sorted(F["active"]):
            if code in seen:
                continue
            hist = [(d, n) for d, n, _oi in F["hist"][code]
                    if n is not None]
            full = F["full"].get(code, [])
            if not full:
                continue
            last = full[-1]
            g = gauges(hist)
            oi_hist = [oi for _d, _n, oi in F["hist"][code]]
            g["oi"] = last["oi"]
            g["oi_wow"] = (last["oi"] - oi_hist[-2]
                           if len(oi_hist) >= 2 and oi_hist[-2]
                           is not None and last["oi"] is not None
                           else None)
            seen[code] = {
                "code": code, "family": fam,
                "family_label": F["spec"]["label"],
                "spec_label": F["spec"]["spec_label"],
                "name": last["mkt"] or last["name"],
                "full_name": last["name"], "units": last["units"],
                "date": last["date"], "gauges": g, "last": last,
                "hist": hist, "oi_hist": oi_hist,
                "in_cit": code in cit,
                "group": (ref.get(code) or {}).get(
                    "commodity_group_name", ""),
                "subgroup": (ref.get(code) or {}).get(
                    "commodity_subgroup_name", ""),
            }
    # slugs, unique within the section
    used = {}
    for code, s in seen.items():
        base = slugify(s["name"])
        slug = base
        if slug in used and used[slug] != code:
            slug = f"{base}-{code}"
        used[slug] = code
        s["slug"] = slug
    return seen


def cat_table(row, spec, basis_label):
    rows = []
    for cat, label, _sp in spec["cats"]:
        c = row["cats"][cat]
        netpct = None
        if c["net"] is not None and row["oi"]:
            netpct = 100.0 * c["net"] / row["oi"]
        rows.append(
            f"<tr><td>{esc(label)}</td>"
            f'<td class="num">{fi(c["long"])}</td>'
            f'<td class="num">{fi(c["short"])}</td>'
            f'<td class="num">{fi(c["spread"])}</td>'
            f'<td class="num">{fi(c["net"], signed=True)}</td>'
            f'<td class="num">{fp(c["pct_long"])}</td>'
            f'<td class="num">{fp(c["pct_short"])}</td>'
            f'<td class="num">{fp(netpct)}</td></tr>')
    headers = ["Category", "Long", "Short", "Spreading", "Net",
               "Long % of OI", "Short % of OI", "Net % of OI"]
    return (f"<h3>{esc(basis_label)}</h3>\n"
            + table(headers, rows))


def cot_market_page(s, fams, cit):
    fam = s["family"]
    F = fams[fam]
    spec = F["spec"]
    last = s["last"]
    g = s["gauges"]
    pub = friday_after(last["date"])
    body = []
    body.append(f'<p class="market-table-updated">Positions as of '
                f'{fdate(last["date"])} - published {fdate(pub)} '
                f"(CFTC, Friday release)</p>\n")
    pairs = [("Report family", esc(spec["label"])),
             ("Basis", "Futures only"),
             ("Market", esc(s["full_name"])),
             ("CFTC contract code", esc(s["code"])),
             ("Contract unit", esc(s["units"].strip("()").title()
                                   if s["units"] else "-")),
             ("Open interest, contracts", fi(last["oi"])),
             ("Change in open interest, contracts",
              fi(g.get("oi_wow"), signed=True))]
    if s["in_cit"]:
        pairs.append(("CIT supplement", "Published for this market"))
    body.append(meta_lines(pairs))
    body.append(cat_table(last, spec, "Latest report, futures only"))
    # extremes block
    erows = []
    erows.append(f'<tr><td>{esc(spec["spec_label"])} net, contracts</td>'
                 f'<td class="num">{fi(g.get("net"), signed=True)}</td></tr>')
    erows.append(f'<tr><td>Week change</td><td class="num">'
                 f'{fi(g.get("wow"), signed=True)}</td></tr>')
    erows.append(f'<tr><td>4-week change</td><td class="num">'
                 f'{fi(g.get("chg4"), signed=True)}</td></tr>')
    erows.append(f'<tr><td>13-week change</td><td class="num">'
                 f'{fi(g.get("chg13"), signed=True)}</td></tr>')
    if g.get("net") is not None and last["oi"]:
        erows.append(f'<tr><td>Net as % of open interest</td>'
                     f'<td class="num">'
                     f'{fp(100.0 * g["net"] / last["oi"])}%</td></tr>')
    erows.append(f'<tr><td>Percentile, 1 year (52 weeks)</td>'
                 f'<td class="num">{fp(g.get("pct1y"), 0)}</td></tr>')
    erows.append(f'<tr><td>Percentile, 3 years (156 weeks)</td>'
                 f'<td class="num">{fp(g.get("pct3y"), 0)}</td></tr>')
    erows.append(f'<tr><td>Z-score, 52 weeks</td><td class="num">'
                 f'{fp(g.get("z52"), 2)}</td></tr>')
    erows.append(f'<tr><td>COT Index, 3 years</td><td class="num">'
                 f'{fp(g.get("cotindex"), 0)}</td></tr>')
    erows.append(f'<tr><td>52-week high of net</td><td class="num">'
                 f'{fi(g.get("hi52"), signed=True)}</td></tr>')
    erows.append(f'<tr><td>52-week low of net</td><td class="num">'
                 f'{fi(g.get("lo52"), signed=True)}</td></tr>')
    body.append(f"<h2>{esc(spec['spec_label'])}: position against "
                f"its own history</h2>\n")
    hist_vals = [n for _d, n in s["hist"][-156:]]
    sp = spark_svg(hist_vals)
    if sp:
        body.append(f"<p>{sp} "
                    f'<span class="gm-sub-inline">Weekly net, last '
                    f"{len(hist_vals)} reports</span></p>\n")
    body.append('<table class="market-table"><tbody>\n'
                + "\n".join(erows) + "\n</tbody></table>\n")
    # traders and concentration
    trows = []
    for cat, label, _sp in spec["cats"]:
        c = last["cats"][cat]
        if c["traders_long"] is None and c["traders_short"] is None:
            continue
        trows.append(f"<tr><td>{esc(label)}</td>"
                     f'<td class="num">{fi(c["traders_long"])}</td>'
                     f'<td class="num">{fi(c["traders_short"])}</td></tr>')
    if trows:
        body.append("<h2>Traders and concentration</h2>\n")
        body.append(table(["Category", "Traders long", "Traders short"],
                          trows))
    conc = last["conc"]
    if conc.get("conc_gross4_long") is not None:
        crows = [
            f'<tr><td>Largest 4 traders, gross long</td>'
            f'<td class="num">{fp(conc["conc_gross4_long"])}%</td></tr>',
            f'<tr><td>Largest 4 traders, gross short</td>'
            f'<td class="num">{fp(conc["conc_gross4_short"])}%</td></tr>',
            f'<tr><td>Largest 8 traders, gross long</td>'
            f'<td class="num">{fp(conc["conc_gross8_long"])}%</td></tr>',
            f'<tr><td>Largest 8 traders, gross short</td>'
            f'<td class="num">{fp(conc["conc_gross8_short"])}%</td></tr>',
            f'<tr><td>Largest 4 traders, net long</td>'
            f'<td class="num">{fp(conc["conc_net4_long"])}%</td></tr>',
            f'<tr><td>Largest 4 traders, net short</td>'
            f'<td class="num">{fp(conc["conc_net4_short"])}%</td></tr>',
            f'<tr><td>Largest 8 traders, net long</td>'
            f'<td class="num">{fp(conc["conc_net8_long"])}%</td></tr>',
            f'<tr><td>Largest 8 traders, net short</td>'
            f'<td class="num">{fp(conc["conc_net8_short"])}%</td></tr>',
        ]
        body.append('<table class="market-table"><tbody>\n'
                    + "\n".join(crows) + "\n</tbody></table>\n")
        body.append('<p class="gm-method">Concentration is the share '
                    "of open interest held by the largest traders, as "
                    "published in the report.</p>\n")
    # combined basis block
    cb = F["combined"].get(s["code"])
    if cb and cb["date"] == last["date"]:
        body.append(cat_table(cb, spec,
                              "Latest report, futures and options "
                              "combined"))
        body.append('<p class="gm-method">The combined basis adds '
                    "options converted to futures equivalents at "
                    "exchange delta factors. The two bases are never "
                    "mixed in one series; the history on this page is "
                    "futures only.</p>\n")
    # CIT block
    if s["code"] in cit:
        c = cit[s["code"]]
        body.append("<h2>Index traders (CIT supplement)</h2>\n")
        body.append(meta_lines([
            ("Index trader net, contracts", fi(c["net"], signed=True)),
            ("Index trader long, contracts", fi(c["long"])),
            ("Index trader short, contracts", fi(c["short"])),
            ("Supplement position date", fdate(c["date"])),
        ]))
        body.append('<p class="gm-method">The CIT supplement reports '
                    "index traders carved out of the legacy categories, "
                    "on the combined basis.</p>\n")
    # maturity split
    sp_key = (s["code"], last["date"])
    sp = F["splits"].get(sp_key)
    if sp:
        body.append("<h2>Open interest by maturity split</h2>\n")
        body.append(meta_lines([
            ("All contract months, contracts", fi(last["oi"])),
            ("Old crop / nearest months, contracts", fi(sp.get("old"))),
            ("Other months, contracts", fi(sp.get("other"))),
        ]))
    # recent history
    full = F["full"][s["code"]][-10:]
    hrows = []
    for r in reversed(full):
        cells = [f"<td>{fdate(r['date'])}</td>",
                 f'<td class="num">{fi(r["oi"])}</td>']
        for cat, _label, _s in spec["cats"]:
            cells.append(f'<td class="num">'
                         f'{fi(r["cats"][cat]["net"], signed=True)}</td>')
        hrows.append("<tr>" + "".join(cells) + "</tr>")
    headers = ["Report date", "Open interest"] + \
        [label for _c, label, _s in spec["cats"]]
    body.append("<h2>Recent reports, net by category</h2>\n")
    body.append(table(headers, hrows))
    body.append('<p class="gm-method">Spreading is calendar-spread '
                "positions. It prints as its own column and is not "
                "part of net. Percentile is the share of weeks in the "
                "window with a net at or below the current net. The "
                "COT Index places the current net within its 3-year "
                "range, 0 at the low and 100 at the high. Gauges print "
                "only when the window holds enough history. History "
                "is the series as currently published by the CFTC, "
                "including its corrections; first-release vintages "
                "are not kept. An extreme reading is a condition of "
                "crowding, not a buy or sell signal: speculative "
                "categories are trend followers and are usually "
                "largest near price extremes.</p>\n")
    body.append('<p class="data-vintage">Source: CFTC Commitments of '
                "Traders, " + esc(spec["label"]) + " report, futures "
                "only unless stated. Positions as of "
                + fdate(last["date"]) + ", published " + fdate(pub)
                + ".</p>\n")
    title = f"{s['name']} COT Report, {spec['label']}"
    lede = (f"{spec['spec_label']} net "
            f"{fi(g.get('net'), signed=True)} contracts in "
            f"{s['name']}, positions as of {fdate(last['date'])}.")
    return frontmatter(title, lede,
                        f"Positions as of {fdate(last['date'])}; "
                        f"published {fdate(pub)}") + "".join(body)


def cot_index_page(summaries, fams, cit):
    body = []
    latest = max(s["date"] for s in summaries.values())
    pub = friday_after(latest)
    body.append(f'<p class="market-table-updated">Positions as of '
                f'{fdate(latest)} - published {fdate(pub)} (CFTC, '
                f"Friday release)</p>\n")
    body.append('<p class="gm-method">One row per market, from the '
                "report family that covers it: disaggregated for "
                "physical commodities, Traders in Financial Futures "
                "for financial markets, legacy where only legacy "
                "carries the market. The speculative category is "
                "managed money, leveraged funds or non-commercial "
                "respectively. Futures only. CIT marks markets with "
                "a CIT supplement.</p>\n")
    for fam in ("disaggregated", "tff", "legacy"):
        rows = [s for s in summaries.values() if s["family"] == fam]
        if not rows:
            continue
        rows.sort(key=lambda s: (-(s["gauges"].get("oi") or 0), s["name"]))
        spec_label = fams[fam]["spec"]["spec_label"]
        body.append(f"<h2>{esc(fams[fam]['spec']['label'])}</h2>\n")
        out = []
        for s in rows:
            g = s["gauges"]
            cit_mark = "Yes" if s["in_cit"] else BLANK
            netpct = None
            if g.get("net") is not None and g.get("oi"):
                netpct = 100.0 * g["net"] / g["oi"]
            out.append(
                f'<tr><td><a href="/positioning/cftc-cot/'
                f'{s["slug"]}/">{esc(s["name"])}</a></td>'
                f'<td class="num">{fi(g.get("net"), signed=True)}</td>'
                f'<td class="num">{fi(g.get("wow"), signed=True)}</td>'
                f'<td class="num">{fp(netpct)}</td>'
                f'<td class="num">{fp(g.get("pct3y"), 0)}</td>'
                f'<td class="num">{fp(g.get("cotindex"), 0)}</td>'
                f'<td class="num">{fi(g.get("oi"))}</td>'
                f"<td>{cit_mark}</td>"
                f"<td>{esc(s['date'])}</td></tr>")
        headers = ["Market", f"{spec_label} net", "Week change",
                   "Net % of OI", "Percentile 3Y", "COT Index",
                   "Open interest", "CIT", "Position date"]
        cols = [("Market", 210, 110), ("Net", 96, 64, 1),
                ("Week change", 96, 64, 1), ("Net % of OI", 84, 60, 1),
                ("Percentile 3Y", 92, 64, 1), ("COT Index", 76, 56, 1),
                ("Open interest", 104, 70, 1), ("CIT", 44, 36),
                ("Position date", 104, 76)]
        tid = f"pos-cot-{fam}"
        body.append(table(headers, out, tid=tid, cols=cols,
                          engine=True))
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from table_engine import reset_btn
        body.insert(len(body) - 1, reset_btn(tid) + "\n")
    body.append('<p class="gm-method">Legacy history runs from 1986 '
                "and disaggregated history from 2006; a market page "
                "never blends families. Percentile and COT Index "
                "print only when the trailing window holds at least "
                "two years of weekly reports.</p>\n")
    body.append('<p class="data-vintage">Source: CFTC Commitments of '
                "Traders weekly reports. Positions as of "
                + fdate(latest) + ", published " + fdate(pub)
                + ".</p>\n")
    from table_engine import TABLE_ENGINE_JS
    body.append(TABLE_ENGINE_JS)
    lede = (f"Commitments of Traders for {len(summaries)} markets: "
            f"speculative net, week change, percentile and COT Index, "
            f"positions as of {fdate(latest)}.")
    return frontmatter("CFTC Commitments of Traders", lede,
                        f"Positions as of {fdate(latest)}; published "
                        f"{fdate(pub)}") + "".join(body)


# ---------------------------------------------------------------- BPR

def load_bpr():
    path = os.path.join(CFTC, "bpr", "bpr_positions.csv")
    markets = collections.defaultdict(dict)  # commodity -> month -> rows
    nrows = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nrows += 1
            if row["report_kind"] != "futures":
                continue
            markets[row["commodity"]][row["month"]] = \
                markets[row["commodity"]].get(row["month"], {})
            markets[row["commodity"]][row["month"]][row["bank_type"]] \
                = row
    return markets, nrows


def bpr_block(rows):
    """rows: {bank_type: csv row} for one market-month."""
    def g(bt, col):
        r = rows.get(bt)
        return num(r.get(col)) if r else None
    return {
        "us_count": g("U.S.", "bank_count"),
        "nonus_count": g("NON U.S.", "bank_count"),
        "tot_count": g("TOTAL", "bank_count"),
        "us_long": g("U.S.", "gross_long"),
        "us_short": g("U.S.", "gross_short"),
        "us_net": g("U.S.", "net"),
        "nonus_long": g("NON U.S.", "gross_long"),
        "nonus_short": g("NON U.S.", "gross_short"),
        "nonus_net": g("NON U.S.", "net"),
        "tot_long": g("TOTAL", "gross_long"),
        "tot_short": g("TOTAL", "gross_short"),
        "tot_net": g("TOTAL", "net"),
        "oi": g("TOTAL", "open_interest"),
        "date": (rows.get("TOTAL") or rows.get("U.S.")
                 or {}).get("report_date", ""),
    }


def count_cell(v):
    if v is None:
        return '<span class="blank">suppressed</span>'
    return fi(v)


def bpr_index_page(markets):
    latest_month = max(m for mm in markets.values() for m in mm)
    rows = []
    meta = {}
    for commodity, months in markets.items():
        if latest_month not in months:
            continue
        b = bpr_block(months[latest_month])
        meta[commodity] = (months, b)
        netpct = None
        if b["tot_net"] is not None and b["oi"]:
            netpct = 100.0 * b["tot_net"] / b["oi"]
        rows.append((commodity, b, netpct))
    rows.sort(key=lambda t: (-(abs(t[1]["tot_net"] or 0)), t[0]))
    body = []
    b0 = rows[0][1] if rows else {}
    body.append(f'<p class="market-table-updated">Positions as of '
                f'{fdate(b0.get("date", ""))} - report month '
                f"{esc(latest_month)}</p>\n")
    body.append('<p class="gm-method">Bank Participation is monthly: '
                "positions at the first Tuesday of the month, "
                "published by the CFTC later the same month. Gross "
                "long and gross short for United States banks and "
                "non-United States banks. Where a group has fewer "
                "than four banks its bank count is suppressed by the "
                "CFTC; the cell prints suppressed, never zero. "
                "Futures only on this page; the report also "
                "publishes gross options positions, not "
                "delta-adjusted.</p>\n")
    out = []
    for commodity, b, netpct in rows:
        slug = slugify(commodity)
        out.append(
            f'<tr><td><a href="/positioning/bank-participation/'
            f'{slug}/">{esc(commodity)}</a></td>'
            f'<td class="num">{fi(b["us_net"], signed=True)}</td>'
            f'<td class="num">{fi(b["nonus_net"], signed=True)}</td>'
            f'<td class="num">{fi(b["tot_net"], signed=True)}</td>'
            f'<td class="num">{fp(netpct)}</td>'
            f'<td class="num">{count_cell(b["us_count"])}</td>'
            f'<td class="num">{count_cell(b["nonus_count"])}</td>'
            f'<td class="num">{fi(b["tot_count"])}</td></tr>')
    headers = ["Market", "US bank net", "Non-US bank net",
               "All bank net", "Net % of OI", "US banks",
               "Non-US banks", "All banks"]
    body.append(table(headers, out))
    silver = meta.get("CMX SILVER")
    if silver:
        months, _b = silver
        body.append("<h2>Silver</h2>\n")
        body.append('<p class="gm-method">Silver is the report\'s '
                    "most complete series: every futures month from "
                    "November 2013 to October 2026, 156 months, no "
                    "gaps. The full bank table is on the "
                    '<a href="/positioning/bank-participation/'
                    'cmx-silver/">silver market page</a>.</p>\n')
    body.append('<p class="data-vintage">Source: CFTC Bank '
                "Participation Report, monthly. Positions as of "
                + fdate(b0.get("date", "")) + ".</p>\n")
    lede = (f"Bank Participation for {len(rows)} markets: United "
            f"States and non-United States bank net positions, "
            f"report month {latest_month}.")
    return frontmatter("Bank Participation Report", lede,
                        f"Positions as of {fdate(b0.get('date', ''))}; "
                        f"report month {latest_month}") \
        + "".join(body), meta, latest_month


def bpr_market_page(commodity, months):
    ms = sorted(months)
    latest = bpr_block(months[ms[-1]])
    slug = slugify(commodity)
    body = []
    body.append(f'<p class="market-table-updated">Positions as of '
                f'{fdate(latest["date"])} - report month '
                f"{esc(ms[-1])}</p>\n")
    suppressed_months = sum(
        1 for m in ms
        if bpr_block(months[m])["us_count"] is None
        or bpr_block(months[m])["nonus_count"] is None)
    body.append(meta_lines([
        ("Market", esc(commodity)),
        ("Months in dataset", fi(len(ms))),
        ("Coverage", f"{esc(ms[0])} to {esc(ms[-1])}"),
        ("Months with a suppressed bank count",
         fi(suppressed_months)),
        ("Latest US bank net, contracts",
         fi(latest["us_net"], signed=True)),
        ("Latest non-US bank net, contracts",
         fi(latest["nonus_net"], signed=True)),
        ("Latest all-bank net, contracts",
         fi(latest["tot_net"], signed=True)),
    ]))
    out = []
    for m in reversed(ms[-24:]):
        b = bpr_block(months[m])
        out.append(
            f"<tr><td>{esc(m)}</td>"
            f'<td class="num">{count_cell(b["us_count"])}</td>'
            f'<td class="num">{fi(b["us_long"])}</td>'
            f'<td class="num">{fi(b["us_short"])}</td>'
            f'<td class="num">{fi(b["us_net"], signed=True)}</td>'
            f'<td class="num">{count_cell(b["nonus_count"])}</td>'
            f'<td class="num">{fi(b["nonus_long"])}</td>'
            f'<td class="num">{fi(b["nonus_short"])}</td>'
            f'<td class="num">{fi(b["nonus_net"], signed=True)}</td>'
            f'<td class="num">{fi(b["tot_count"])}</td>'
            f'<td class="num">{fi(b["tot_net"], signed=True)}</td></tr>')
    headers = ["Month", "US banks", "US long", "US short", "US net",
               "Non-US banks", "Non-US long", "Non-US short",
               "Non-US net", "All banks", "All net"]
    body.append("<h2>Bank positions, last 24 months</h2>\n")
    body.append(table(headers, out))
    body.append('<p class="gm-method">Net is gross long minus gross '
                "short; the report publishes gross positions and the "
                "net is computed here. A suppressed bank count means "
                "the group held fewer than four banks that month; "
                "the split was withheld, not zero. Months where the "
                "split was withheld are part of the record and stay "
                "in the table.</p>\n")
    body.append('<p class="data-vintage">Source: CFTC Bank '
                "Participation Report, monthly, futures. Positions "
                "as of " + fdate(latest["date"]) + ".</p>\n")
    title = f"{commodity} Bank Participation"
    lede = (f"Bank positions in {commodity}: all-bank net "
            f"{fi(latest['tot_net'], signed=True)} contracts, "
            f"positions as of {fdate(latest['date'])}.")
    return slug, frontmatter(title, lede,
                             f"Positions as of {fdate(latest['date'])}; "
                             f"report month {ms[-1]}") + "".join(body)


# ------------------------------------------------------------- Europe

ICE_CATS = [("producer_merchant", "Producer/Merchant"),
            ("swap_dealers", "Swap Dealers"),
            ("managed_money", "Managed Money"),
            ("other_reportables", "Other Reportables"),
            ("total_reportables", "Total Reportables"),
            ("nonreportable", "Nonreportable")]


def load_ice():
    path = os.path.join(PH, "datasets", "ice-cot", "ice_cot_long.csv")
    # (market, basis) -> date -> category -> side -> positions
    data = collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: collections.defaultdict(dict)))
    oi = {}
    units = {}
    nrows = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nrows += 1
            if row["maturity_bucket"] != "All":
                continue
            key = (row["market"], row["basis"])
            data[key][row["report_date"]][row["category"]] \
                [row["side"]] = num(row["positions"])
            if row.get("open_interest"):
                oi[(row["market"], row["basis"],
                    row["report_date"])] = num(row["open_interest"])
            units[row["market"]] = row.get("contract_units", "")
    return data, oi, units, nrows


def ice_market_series(data, oi, market, basis="FutOnly"):
    dates = sorted(data.get((market, basis), {}))
    out = []
    for d in dates:
        cats = data[(market, basis)][d]
        entry = {"date": d, "oi": oi.get((market, basis, d)),
                 "cats": {}}
        for cat, _label in ICE_CATS:
            sides = cats.get(cat, {})
            lo, sh = sides.get("long"), sides.get("short")
            entry["cats"][cat] = {
                "long": lo, "short": sh,
                "net": (lo - sh) if lo is not None and sh is not None
                else None}
        out.append(entry)
    return out


ESMA_CATS = [("investment_firms", "Investment firms or credit "
              "institutions"),
             ("investment_funds", "Investment funds"),
             ("other", "Other financial institutions"),
             ("commercial_undertakings", "Commercial undertakings"),
             ("ets_operators", "Operators with compliance "
              "obligations")]
ESMA_CAT_LABEL = dict(ESMA_CATS)


def load_esma():
    path = os.path.join(PH, "datasets", "esma-art58",
                        "esma_positions.csv")
    # key: (venue_mic, product_code) ; per date: cat -> measures
    pos = collections.defaultdict(
        lambda: collections.defaultdict(dict))
    pct = collections.defaultdict(
        lambda: collections.defaultdict(dict))
    persons = collections.defaultdict(
        lambda: collections.defaultdict(dict))
    meta = {}
    pub = {}
    nrows = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nrows += 1
            key = (row["venue_mic"], row["venue_product_code"],
                   row["report_type"])
            meta[key] = {"venue_name": row["venue_name"],
                         "commodity": row["commodity"],
                         "unit": row["unit"]}
            d = row["ref_date"]
            grp = row["holder_group"]
            # The register files each position three times per
            # group: risk-reducing (RISKR), other (OTHER), and
            # their total (TOTAL). Use the TOTAL rows only;
            # summing all three would double the position.
            # Persons are filed once per group, category ALL.
            if row["measure"] == "Number of positions":
                if row["position_category"] != "TOTAL":
                    continue
                lo = num(row["long"]) or 0.0
                sh = num(row["short"]) or 0.0
                pos[key][d][grp] = {"long": lo, "short": sh,
                                    "net": lo - sh}
            elif row["measure"] == "Percentage of open interest":
                if row["position_category"] != "TOTAL":
                    continue
                pct[key][d][grp] = {
                    "long": num(row["long"]) or 0.0,
                    "short": num(row["short"]) or 0.0}
            elif row["measure"].startswith("Number of persons"):
                v = num(row["long"])
                if v is None:
                    v = num(row["short"])
                if v is not None:
                    persons[key][d][grp] = v
            if d not in pub or row["pub_datetime"] > pub[d][0]:
                pub[d] = (row["pub_datetime"], key)
    return pos, pct, persons, meta, nrows


def esma_choose_keys(pos, meta):
    """Per (venue, product) prefer the futures-only report (FUTR)
    when it exists, else the combined report (COMB)."""
    by_vp = collections.defaultdict(list)
    for key in pos:
        by_vp[(key[0], key[1])].append(key)
    chosen = {}
    for vp, keys in by_vp.items():
        futr = [k for k in keys if k[2] == "FUTR"]
        chosen[vp] = futr[0] if futr else keys[0]
    return chosen


# ---------------------------------------------------------------- LME

LME_CATS = ["Investment Firms or credit institutions",
            "Investment Funds", "Other Financial Institutions",
            "Commercial Undertakings",
            "Operators with compliance obligations under "
            "Directive 2003/87/EC"]
LME_CAT_SHORT = {
    "Investment Firms or credit institutions": "Investment firms",
    "Investment Funds": "Investment funds",
    "Other Financial Institutions": "Other financial institutions",
    "Commercial Undertakings": "Commercial undertakings",
    "Operators with compliance obligations under Directive "
    "2003/87/EC": "ETS operators",
}


def load_lme():
    path = os.path.join(PH, "datasets", "lme-cotr",
                        "lme_cotr_positions.csv")
    data = collections.defaultdict(
        lambda: collections.defaultdict(dict))
    names = {}
    gen = {}
    nrows = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nrows += 1
            if row["position_type"] != "total":
                continue
            code = row["metal_code"]
            names[code] = row["metal_name"]
            d = row["report_date"]
            lo, sh = num(row["long_lots"]), num(row["short_lots"])
            data[code][d][row["category"]] = {
                "long": lo, "short": sh,
                "net": (lo - sh) if lo is not None and sh is not None
                else None,
                "pct_long": num(row["pct_long"]),
                "pct_short": num(row["pct_short"]),
                "holders": num(row["holders"])}
            if row.get("generated_ts"):
                gen[code] = max(gen.get(code, ""), row["generated_ts"])
    return data, names, gen, nrows


def lme_oi(block):
    """COTR open interest as the sum of category long positions.
    The COTR includes delta hedge equivalents and does not equal
    the LME market open interest report; the page says so."""
    vals = [c["long"] for c in block.values() if c["long"] is not None]
    return sum(vals) if vals else None


def lme_index_page(data, names, gen):
    latest = max(d for dd in data.values() for d in dd)
    pub = ""
    for code in data:
        pub = max(pub, gen.get(code, ""))
    body = []
    body.append(f'<p class="market-table-updated">Positions as of '
                f'{fdate(latest)} - published '
                f'{fdate(pub[:10])} (generated T+2)</p>\n')
    body.append('<p class="gm-method">The LME publishes a Commitments '
                "of Traders report per metal: positions at the "
                "Friday close, published the following Tuesday. "
                "Categories are the MiFID II set. Open interest here "
                "is the sum of category long positions in the COTR "
                "itself, which includes delta hedge equivalents and "
                "does not equal the LME market open interest "
                "report.</p>\n")
    out = []
    for code in sorted(data, key=lambda c: names[c]):
        dates = sorted(data[code])
        last = data[code][dates[-1]]
        prev = data[code][dates[-2]] if len(dates) >= 2 else {}
        funds = last.get("Investment Funds", {})
        pf = prev.get("Investment Funds", {})
        wow = None
        if funds.get("net") is not None and pf.get("net") is not None:
            wow = funds["net"] - pf["net"]
        comm = last.get("Commercial Undertakings", {})
        out.append(
            f'<tr><td><a href="/positioning/lme/'
            f'{slugify(names[code])}/">{esc(names[code])}</a></td>'
            f'<td class="num">{fi(funds.get("net"), signed=True)}</td>'
            f'<td class="num">{fi(wow, signed=True)}</td>'
            f'<td class="num">{fi(comm.get("net"), signed=True)}</td>'
            f'<td class="num">{fi(lme_oi(last))}</td>'
            f"<td>{esc(dates[-1])}</td></tr>")
    headers = ["Metal", "Investment funds net", "Week change",
               "Commercial undertakings net", "Open interest, lots",
               "Position date"]
    body.append(table(headers, out))
    body.append('<p class="gm-method">Reports were recalculated and '
                "republished by the LME after a 2023 vendor cyber "
                "incident, and individual reports were corrected in "
                "2025 and 2026. The banked files, and so these "
                "pages, are the current corrected versions.</p>\n")
    body.append('<p class="data-vintage">Source: LME Commitments of '
                "Traders reports, weekly, from 3 Jan 2020. Positions "
                "as of " + fdate(latest) + ".</p>\n")
    lede = (f"LME Commitments of Traders for {len(data)} metals: "
            f"investment funds and commercial undertakings net, "
            f"positions as of {fdate(latest)}.")
    return frontmatter("LME Commitments of Traders", lede,
                        f"Positions as of {fdate(latest)}; published "
                        f"{fdate(pub[:10])}") + "".join(body), latest, pub


def lme_metal_page(code, data, names, gen):
    dates = sorted(data[code])
    last = data[code][dates[-1]]
    prev = data[code][dates[-2]] if len(dates) >= 2 else {}
    body = []
    body.append(f'<p class="market-table-updated">Positions as of '
                f'{fdate(dates[-1])} - published '
                f'{fdate(gen.get(code, "")[:10])} (generated T+2)</p>\n')
    body.append(meta_lines([
        ("Metal", esc(names[code])),
        ("Coverage", f"3 Jan 2020 to {esc(dates[-1])}"),
        ("Reports in dataset", fi(len(dates))),
        ("Open interest, lots (sum of category longs)",
         fi(lme_oi(last))),
    ]))
    out = []
    for cat in LME_CATS:
        c = last.get(cat, {})
        p = prev.get(cat, {})
        wow = None
        if c.get("net") is not None and p.get("net") is not None:
            wow = c["net"] - p["net"]
        holders = c.get("holders")
        hcell = fi(holders) if holders is not None \
            else '<span class="blank">suppressed</span>'
        out.append(
            f"<tr><td>{esc(LME_CAT_SHORT[cat])}</td>"
            f'<td class="num">{fi(c.get("long"))}</td>'
            f'<td class="num">{fi(c.get("short"))}</td>'
            f'<td class="num">{fi(c.get("net"), signed=True)}</td>'
            f'<td class="num">{fi(wow, signed=True)}</td>'
            f'<td class="num">'
            f'{fp(100 * c["pct_long"]) if c.get("pct_long") is not None else BLANK}</td>'
            f'<td class="num">'
            f'{fp(100 * c["pct_short"]) if c.get("pct_short") is not None else BLANK}</td>'
            f'<td class="num">{hcell}</td></tr>')
    headers = ["Category", "Long, lots", "Short, lots", "Net, lots",
               "Week change", "Long % of OI", "Short % of OI",
               "Persons"]
    body.append(table(headers, out))
    funds_hist = [(d, data[code][d].get("Investment Funds", {})
                   .get("net")) for d in dates]
    g = gauges([(d, n) for d, n in funds_hist if n is not None])
    body.append("<h2>Investment funds net against its history</h2>\n")
    body.append(meta_lines([
        ("Net, lots", fi(g.get("net"), signed=True)),
        ("Week change", fi(g.get("wow"), signed=True)),
        ("4-week change", fi(g.get("chg4"), signed=True)),
        ("13-week change", fi(g.get("chg13"), signed=True)),
        ("Percentile, 1 year", fp(g.get("pct1y"), 0)),
        ("Percentile, 3 years", fp(g.get("pct3y"), 0)),
        ("Z-score, 52 weeks", fp(g.get("z52"), 2)),
    ]))
    hrows = []
    for d in reversed(dates[-10:]):
        block = data[code][d]
        cells = [f"<td>{fdate(d)}</td>",
                 f'<td class="num">{fi(lme_oi(block))}</td>']
        for cat in LME_CATS:
            cells.append(f'<td class="num">'
                         f'{fi(block.get(cat, {}).get("net"), signed=True)}</td>')
        hrows.append("<tr>" + "".join(cells) + "</tr>")
    body.append("<h2>Recent reports, net by category</h2>\n")
    body.append(table(["Report date", "Open interest"]
                      + [LME_CAT_SHORT[c] for c in LME_CATS], hrows))
    body.append('<p class="gm-method">Longs and shorts may not sum '
                "exactly: the source notes overnight clearing "
                "suspensions and delta hedge equivalents. A metal "
                "with no open positions produces no report; a "
                "missing week is not a zero.</p>\n")
    body.append('<p class="data-vintage">Source: LME Commitments of '
                "Traders report for " + esc(names[code])
                + ". Positions as of " + fdate(dates[-1])
                + ".</p>\n")
    title = f"{names[code]} LME COTR"
    lede = (f"LME positioning in {names[code]}: investment funds net "
            f"{fi(last.get('Investment Funds', {}).get('net'), signed=True)} "
            f"lots, positions as of {fdate(dates[-1])}.")
    return frontmatter(title, lede,
                        f"Positions as of {fdate(dates[-1])}; "
                        f"published {fdate(gen.get(code, '')[:10])}") \
        + "".join(body)


# -------------------------------------------------------------- Shorts

REGISTERS = [
    ("eu-shorts-afm", "Netherlands (AFM)"),
    ("eu-shorts-amf", "France (AMF)"),
    ("eu-shorts-consob", "Italy (CONSOB)"),
    ("eu-shorts-cnmv", "Spain (CNMV)"),
    ("eu-shorts-no", "Norway (Finanstilsynet)"),
    ("eu-shorts-cbi-ie", "Ireland (Central Bank)"),
    ("eu-shorts-hcmc", "Greece (HCMC)"),
    ("eu-shorts-de-pages", "Germany (BaFin)"),
    ("eu-shorts-hanfa", "Croatia (HANFA)"),
]


def load_register(dirname):
    path = os.path.join(PH, "datasets", dirname, "positions.csv")
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pct = num(row.get("pct_of_capital"))
            if pct is None or not row.get("position_date"):
                continue
            rows.append({"holder": row.get("position_holder", ""),
                         "issuer": row.get("issuer_name", ""),
                         "isin": row.get("isin", ""),
                         "pct": pct, "date": row["position_date"]})
    return rows


def current_positions(rows):
    """Latest disclosure per (holder, ISIN) is the pair's current
    disclosed position."""
    cur = {}
    for r in rows:
        key = (r["holder"], r["isin"])
        if key not in cur or r["date"] > cur[key]["date"]:
            cur[key] = r
    return cur


def pair_history(rows):
    hist = collections.defaultdict(list)
    for r in rows:
        hist[(r["holder"], r["isin"])].append(r)
    for k in hist:
        hist[k].sort(key=lambda r: r["date"])
    return hist


def shorts_page():
    body = []
    all_cur = {}   # (register, holder, isin) -> row
    changes = []
    reg_meta = []
    issuer_agg = collections.defaultdict(
        lambda: {"pct": 0.0, "holders": {}, "issuer": "",
                 "latest": ""})
    holder_agg = collections.defaultdict(
        lambda: {"n": 0, "largest": None, "registers": set()})
    for dirname, label in REGISTERS:
        rows = load_register(dirname)
        if not rows:
            reg_meta.append((label, 0, "", ""))
            continue
        cur = current_positions(rows)
        hist = pair_history(rows)
        maxd = max(r["date"] for r in rows)
        reg_meta.append((label, len(rows),
                         min(r["date"] for r in rows), maxd))
        for (holder, isin), r in cur.items():
            all_cur[(dirname, holder, isin)] = r
            agg = issuer_agg[isin]
            agg["pct"] += r["pct"]
            agg["holders"][holder] = r["pct"]
            agg["issuer"] = r["issuer"] or agg["issuer"]
            agg["latest"] = max(agg["latest"], r["date"])
            ha = holder_agg[holder]
            ha["n"] += 1
            ha["registers"].add(label)
            if ha["largest"] is None or r["pct"] > ha["largest"][1]:
                ha["largest"] = (r["issuer"], r["pct"])
        cutoff = (datetime.date.fromisoformat(maxd)
                  - datetime.timedelta(days=7)).isoformat()
        for key, h in hist.items():
            last = h[-1]
            if last["date"] < cutoff:
                continue
            prior = [r for r in h if r["date"] < cutoff]
            if not prior:
                kind = "New"
                prev = h[-2]["pct"] if len(h) >= 2 else None
            else:
                prev = h[-2]["pct"] if len(h) >= 2 else None
                kind = ("Increase" if prev is not None
                        and last["pct"] > prev
                        else "Decrease" if prev is not None
                        and last["pct"] < prev
                        else "Restated")
            changes.append((last["date"], label, last, kind, prev))
    changes.sort(key=lambda c: (c[0], c[1], c[2]["holder"],
                                c[2]["issuer"]), reverse=True)
    latest_pos = max((m[3] for m in reg_meta if m[3]), default="")
    body.append(f'<p class="market-table-updated">Latest register '
                f'position date {fdate(latest_pos)} - registers '
                f"publish with a lag of about one day</p>\n")
    body.append('<p class="gm-method">Named net short positions as '
                "published by the European national registers: "
                "position holder, issuer, and the net short as a "
                "percent of issued share capital, public at 0.5% and "
                "each 0.1% step. A pair\'s current position is its "
                "latest disclosure. Position date and disclosure "
                "date differ; the tables print the position date "
                "the registers carry.</p>\n")
    # by issuer
    iss = sorted(issuer_agg.items(), key=lambda kv: -kv[1]["pct"])
    out = []
    for isin, agg in iss[:100]:
        top_holder = max(agg["holders"].items(), key=lambda kv: kv[1])
        out.append(
            f"<tr><td>{esc(agg['issuer'])}</td><td>{esc(isin)}</td>"
            f'<td class="num">{agg["pct"]:.2f}%</td>'
            f'<td class="num">{len(agg["holders"])}</td>'
            f"<td>{esc(top_holder[0])}</td>"
            f'<td class="num">{top_holder[1]:.2f}%</td>'
            f"<td>{esc(agg['latest'])}</td></tr>")
    body.append("<h2>Largest disclosed shorts, by issuer</h2>\n")
    body.append(table(["Issuer", "ISIN", "Aggregate disclosed, % of "
                       "capital", "Holders", "Largest holder",
                       "Largest, %", "Latest position date"], out))
    # by holder
    holders = sorted(holder_agg.items(), key=lambda kv: -kv[1]["n"])
    out = []
    for holder, ha in holders[:60]:
        out.append(
            f"<tr><td>{esc(holder)}</td>"
            f'<td class="num">{ha["n"]}</td>'
            f"<td>{esc(ha['largest'][0])}</td>"
            f'<td class="num">{ha["largest"][1]:.2f}%</td>'
            f"<td>{esc(', '.join(sorted(ha['registers'])))}</td></tr>")
    body.append("<h2>Most active holders</h2>\n")
    body.append(table(["Position holder", "Current disclosed "
                       "positions", "Largest position", "Largest, %",
                       "Registers"], out))
    # changes
    out = []
    for d, label, r, kind, prev in changes[:40]:
        out.append(
            f"<tr><td>{esc(d)}</td><td>{esc(label)}</td>"
            f"<td>{esc(kind)}</td><td>{esc(r['holder'])}</td>"
            f"<td>{esc(r['issuer'])}</td>"
            f'<td class="num">{r["pct"]:.2f}%</td>'
            f'<td class="num">'
            f'{("%.2f%%" % prev) if prev is not None else BLANK}</td></tr>')
    body.append("<h2>Latest changes</h2>\n")
    body.append('<p class="gm-method">Disclosures dated within '
                "seven days of each register\'s latest date. A "
                "history per holder and issuer is a step series: "
                "it moves only when a threshold is crossed.</p>\n")
    body.append(table(["Position date", "Register", "Change",
                       "Holder", "Issuer", "Now, % of capital",
                       "Before, %"], out))
    # UK block
    body.append("<h2>United Kingdom</h2>\n")
    ansp_path = os.path.join(PH, "datasets", "fca-shorts",
                             "ansp_positions.csv")
    ansp_cur = []
    ansp_dates = []
    with open(ansp_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ansp_dates.append(row["position_date"])
            if row["record_type"] == "current":
                ansp_cur.append(row)
    ansp_cur.sort(key=lambda r: (-float(r["ansp_pct"]), r["company_name"]))
    body.append('<p class="gm-method">From 13 July 2026 the FCA '
                "publishes an anonymised aggregate net short "
                "position (ANSP) per company instead of named "
                "positions. Holder identity is no longer published "
                "in the United Kingdom. The aggregate is the sum "
                "of notifications at 0.2% and above, as published "
                "in the FCA\'s CSV file.</p>\n")
    out = []
    for r in ansp_cur[:50]:
        out.append(
            f"<tr><td>{esc(r['company_name'])}</td>"
            f"<td>{esc(r['isin'])}</td>"
            f'<td class="num">{float(r["ansp_pct"]):.2f}%</td>'
            f"<td>{esc(r['position_date'])}</td></tr>")
    body.append(table(["Company", "ISIN", "ANSP, % of capital",
                       "Position date"], out))
    named_path = os.path.join(PH, "datasets", "fca-shorts",
                              "named_positions.csv")
    named = []
    with open(named_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            named.append(row)
    ncur = current_positions(
        [{"holder": r["position_holder"], "issuer": r["issuer_name"],
          "isin": r["isin"], "pct": float(r["net_short_pct"]),
          "date": r["position_date"]} for r in named])
    nagg = collections.defaultdict(
        lambda: {"pct": 0.0, "n": 0, "issuer": ""})
    for (holder, isin), r in ncur.items():
        nagg[isin]["pct"] += r["pct"]
        nagg[isin]["n"] += 1
        nagg[isin]["issuer"] = r["issuer"]
    niss = sorted(nagg.items(), key=lambda kv: -kv[1]["pct"])
    body.append("<h3>Named positions, closed archive</h3>\n")
    body.append('<p class="gm-method">The named regime ended on '
                "13 July 2026. The archive below is the final state "
                "of named disclosures: position dates run to "
                "9 July 2026. It is a closed record and is never "
                "joined to the ANSP series.</p>\n")
    out = []
    for isin, agg in niss[:25]:
        out.append(
            f"<tr><td>{esc(agg['issuer'])}</td><td>{esc(isin)}</td>"
            f'<td class="num">{agg["pct"]:.2f}%</td>'
            f'<td class="num">{agg["n"]}</td></tr>')
    body.append(table(["Issuer", "ISIN", "Aggregate named, % of "
                       "capital", "Holders"], out))
    body.append(meta_lines([
        ("Named archive rows", fi(len(named))),
        ("Named archive span", "31 Oct 2012 to 9 Jul 2026"),
        ("ANSP companies, current file", fi(len(ansp_cur))),
        ("Registers in the European tables",
         ", ".join(f"{label} ({n:,} disclosures, {a} to {b})"
                   if n else f"{label} (no disclosures banked)"
                   for label, n, a, b in reg_meta)),
    ]))
    body.append('<p class="data-vintage">Sources: EU national '
                "short-position registers and the UK FCA. Latest "
                "position date " + fdate(latest_pos) + ".</p>\n")
    lede = ("Named short positions across the European registers "
            "and the United Kingdom: largest disclosed shorts by "
            "issuer, most active holders, latest changes.")
    return (frontmatter("Short positions, Europe and the United "
                        "Kingdom", lede,
                        f"Latest register position date "
                        f"{fdate(latest_pos)}")
            + "".join(body)), {
        "top_issuers": [(agg["issuer"], round(agg["pct"], 2))
                        for _i, agg in iss[:10]],
        "latest_pos": latest_pos,
        "n_disclosures": sum(m[1] for m in reg_meta)
        + len(ansp_dates) + len(named),
        "ansp_top": ansp_cur[0]["company_name"] if ansp_cur else None}


# ---------------------------------------------------------------- Asia

def asia_page(czce_status):
    body = []
    # SGX
    files = sorted(
        f for f in os.listdir(os.path.join(PH, "datasets",
                                           "sgx-derivs"))
        if f.startswith("sgx_derivs_oi_") and f.endswith(".csv"))
    snaps = {}
    for fn in files:
        with open(os.path.join(PH, "datasets", "sgx-derivs", fn),
                  newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                snaps.setdefault(row["snapshot_date"], []).append(row)
    dates = sorted(snaps)
    latest = dates[-1] if dates else ""
    body.append(f'<p class="market-table-updated">SGX positions as '
                f'of {fdate(latest)} - daily file</p>\n')
    body.append("<h2>Singapore Exchange derivatives</h2>\n")
    body.append('<p class="gm-method">SGX publishes volume and open '
                "interest by contract, with no trader category "
                "split. This series starts on 27 October 2026, the "
                "first day of collection; earlier history is not "
                "available from this source and is not reconstructed."
                "</p>\n")
    sgx_summary = {}
    if latest:
        agg = collections.defaultdict(
            lambda: {"oi": 0.0, "vol": 0.0, "n": 0, "name": ""})
        for row in snaps[latest]:
            if row["derivative_type"] not in ("futures", "options") \
                    and row["category"] not in ("futures", "options"):
                pass
            key = (row["category"], row["symbol"])
            a = agg[key]
            a["oi"] += num(row["open_interest"]) or 0.0
            a["vol"] += num(row["total_volume"]) or 0.0
            a["n"] += 1
            a["name"] = row["contract_name"]
        prev = dates[-2] if len(dates) >= 2 else None
        prev_agg = {}
        if prev:
            for row in snaps[prev]:
                key = (row["category"], row["symbol"])
                prev_agg[key] = prev_agg.get(key, 0.0) \
                    + (num(row["open_interest"]) or 0.0)
        out = []
        for (cat, sym), a in sorted(agg.items(),
                                    key=lambda kv: -kv[1]["oi"])[:30]:
            chg = None
            if prev and (cat, sym) in prev_agg:
                chg = a["oi"] - prev_agg[(cat, sym)]
            out.append(
                f"<tr><td>{esc(a['name'])}</td><td>{esc(cat)}</td>"
                f'<td class="num">{fi(a["oi"])}</td>'
                f'<td class="num">{fi(a["vol"])}</td>'
                f'<td class="num">{fi(chg, signed=True)}</td>'
                f'<td class="num">{a["n"]}</td></tr>')
            sgx_summary[sym] = a["oi"]
        body.append(table(["Contract group", "Type", "Open interest",
                           "Volume", "OI change vs prior file",
                           "Contract months"], out))
        body.append(meta_lines([
            ("Files in series", fi(len(dates))),
            ("Series span", f"{esc(dates[0])} to {esc(dates[-1])}"),
            ("Contracts in latest file", fi(len(snaps[latest]))),
        ]))
    # TOCOM
    body.append("<h2>Tokyo Commodity Exchange (JPX)</h2>\n")
    tocom_path = os.path.join(PH, "datasets", "tocom",
                              "tocom_daily_quotations.csv")
    tdata = collections.defaultdict(dict)
    with open(tocom_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["market"], row["product"])
            d = row["report_date"]
            tdata[key][d] = tdata[key].get(d, 0.0) \
                + (num(row["open_interest"]) or 0.0)
    body.append('<p class="gm-method">Weekly open interest by '
                "contract from the exchange\'s published reports. "
                "The banked archive is a sample: about 11% of "
                "trading days between July 2022 and January 2026. "
                "Open interest sums are lower bounds, because the "
                "parse of each sampled report is partial. The "
                "standing collector adds each new day\'s report; "
                "the sampled history is labelled and is not "
                "presented as a continuous series.</p>\n")
    out = []
    for (market, product), dd in sorted(tdata.items()):
        ds = sorted(dd)
        out.append(
            f"<tr><td>{esc(product)}</td><td>{esc(market)}</td>"
            f'<td class="num">{fi(dd[ds[-1]])}</td>'
            f"<td>{esc(ds[-1])}</td>"
            f'<td class="num">{len(ds)}</td>'
            f"<td>{esc(ds[0])} to {esc(ds[-1])}</td></tr>")
    body.append(table(["Product", "Market", "Open interest, latest "
                       "sampled day (lower bound)", "Latest sampled "
                       "date", "Sampled days", "Sample span"], out))
    # CZCE
    body.append("<h2>Zhengzhou Commodity Exchange (CZCE)</h2>\n")
    body.append('<p class="gm-method">China\'s exchanges publish a '
                "daily member ranking, not a trader category "
                "report: per contract, the top 20 members by volume "
                "and by long and short open interest. The standard "
                "aggregate is top-20 long lots, top-20 short lots, "
                "top-20 net and the long-short ratio, at daily "
                "cadence. It is a member concentration gauge and is "
                "never presented as category positioning.</p>\n")
    if czce_status:
        body.append(meta_lines([
            ("Raw daily files banked in the vault",
             fi(czce_status.get("files_banked"))),
            ("Banked span", esc(str(czce_status.get("span", "")))),
            ("Backfill state",
             "Running off-VM (GitHub Actions) with hourly vault "
             "receipt; the daily collector is current"),
            ("Tidy dataset state",
             "A parser-proof sample only: member rankings for "
             "3 Jan 2023 and 1 Feb 2023 and daily tables for "
             "6 Jan 2023 and 2 Feb 2023"),
            ("Positioning tables",
             "Not published until the tidy build covers the "
             "banked files; a two-day sample would misstate the "
             "series"),
        ]))
    body.append('<p class="data-vintage">Sources: SGX derivatives '
                "daily files, JPX daily quotations (sampled "
                "archive), CZCE daily files (banked, processing "
                "pending).</p>\n")
    lede = ("Asia positioning: SGX derivatives open interest from "
            "27 October 2026, TOCOM sampled open interest, and the "
            "CZCE member-ranking coverage state.")
    return (frontmatter("Asia positioning", lede,
                        f"SGX as of {fdate(latest)}; TOCOM sampled; "
                        f"CZCE banked, processing pending")
            + "".join(body)), {"sgx_latest": latest,
                               "sgx_dates": len(dates)}


# ----------------------------------------------------------------- OCC

def _is_total_cp(cp):
    """The total-derivatives column; some XML-era quarters carry a
    percent prefix in the column path."""
    return cp == "TOTAL | DERIVATIVES" \
        or cp.endswith("| TOTAL | DERIVATIVES")


def occ_page():
    agg_path = os.path.join(CFTC, "occ", "occ_aggregates.csv")
    total_series = {}
    latest = ""
    with open(agg_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["exhibit_id"] != "E01":
                continue
            if not row["row_label"].startswith("TOTAL"):
                continue
            pe = row["period_end"]
            v = num(row["value"])
            if v is None:
                continue
            if _is_total_cp(row["column_path"]):
                total_series[pe] = v
                latest = max(latest, pe)
    comp = {}
    with open(agg_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["exhibit_id"] == "E01" \
                    and row["row_label"].startswith("TOTAL") \
                    and row["period_end"] == latest:
                comp[row["column_path"]] = num(row["value"])
    obs_path = os.path.join(CFTC, "occ", "occ_observations.csv")
    inst = []
    with open(obs_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["exhibit_id"] == "E01" \
                    and row["row_type"] == "institution" \
                    and row["period_end"] == latest \
                    and _is_total_cp(row["column_path"]):
                v = num(row["value"])
                if v:
                    inst.append((row["row_label"], v))
    inst.sort(key=lambda t: (-t[1], t[0]))
    total = total_series.get(latest)
    body = []
    q = latest[:4] + " Q" + latest[5:7].replace("03", "1") \
        .replace("06", "2").replace("09", "3").replace("12", "4") \
        if latest else ""
    body.append(f'<p class="market-table-updated">Quarter ended '
                f'{fdate(latest)} - published about 10 to 12 weeks '
                f"after quarter end</p>\n")
    body.append('<p class="gm-method">The OCC Quarterly Report on '
                "Bank Trading and Derivatives Activities is a "
                "structural series, not a positioning flow: notional "
                "amounts at bank holding company and bank level, by "
                "product, at quarter end. Levels print in USD "
                "trillions; shares are percent of the total.</p>\n")
    if total:
        span_first = min(total_series)
        span_last = max(total_series)
        body.append(meta_lines([
            ("Total derivatives notional, USD trillions",
             f"{total / 1e6:,.1f}"),
            ("Quarter ended", fdate(latest)),
            ("Dataset span",
             f"{qlabel(span_first)} to {qlabel(span_last)} "
             f"({len(total_series)} quarters)"),
            ("Observations in dataset", "202,465"),
        ]))
    comp_rows = []
    comp_map = [("TOTAL | FUTURES | (EXCH TR)",
                 "Futures, exchange traded"),
                ("TOTAL | OPTIONS | (EXCH TR)",
                 "Options, exchange traded"),
                ("TOTAL | FORWARDS | (OTC)", "Forwards, OTC"),
                ("TOTAL | SWAPS | (OTC)", "Swaps, OTC"),
                ("TOTAL | OPTIONS | (OTC)", "Options, OTC"),
                ("TOTAL | CREDIT | DERIVATIVES | (OTC)",
                 "Credit derivatives, OTC")]
    for cp, label in comp_map:
        v = comp.get(cp)
        share = (100.0 * v / total) if v and total else None
        comp_rows.append(
            f"<tr><td>{esc(label)}</td>"
            f'<td class="num">{(f"{v / 1e6:,.1f}" if v else BLANK)}</td>'
            f'<td class="num">{fp(share)}</td></tr>')
    body.append("<h2>Notional by instrument, latest quarter</h2>\n")
    body.append(table(["Instrument", "Notional, USD trillions",
                       "Share of total, %"], comp_rows))
    out = []
    for name, v in inst[:10]:
        share = 100.0 * v / total if total else None
        out.append(
            f"<tr><td>{esc(name)}</td>"
            f'<td class="num">{v / 1e6:,.1f}</td>'
            f'<td class="num">{fp(share)}</td></tr>')
    body.append("<h2>Largest derivatives books, latest quarter</h2>\n")
    body.append(table(["Institution, as published", "Notional, USD "
                       "trillions", "Share of total, %"], out))
    hist = sorted(total_series.items())
    out = []
    for pe, v in hist[-20:]:
        out.append(f"<tr><td>{esc(pe)}</td>"
                   f'<td class="num">{v / 1e6:,.1f}</td></tr>')
    body.append("<h2>Total notional, last 20 quarters</h2>\n")
    body.append(table(["Quarter ended", "Notional, USD trillions"],
                      out))
    body.append('<p class="data-vintage">Source: OCC Quarterly '
                "Report on Bank Trading and Derivatives Activities, "
                "Exhibit 1 (notional amounts). Quarter ended "
                + fdate(latest) + ".</p>\n")
    lede = (f"OCC bank derivatives: total notional "
            f"{(f'{total / 1e6:,.1f}' if total else '-')} trillion "
            f"USD at {fdate(latest)}, by instrument and institution.")
    return (frontmatter("OCC Bank Derivatives Activities", lede,
                        f"Quarter ended {fdate(latest)}")
            + "".join(body)), {"latest": latest, "total": total,
                               "quarters": len(total_series),
                               "first": min(total_series)
                               if total_series else "",
                               "last": max(total_series)
                               if total_series else ""}


# ------------------------------------------------------- Europe pages

def europe_pages(ice_data, ice_oi, ice_units, esma):
    pos, pct, persons, meta, _n = esma
    chosen = esma_choose_keys(pos, meta)
    body = []
    # ICE summary
    ice_markets = sorted({m for (m, _b) in ice_data})
    ice_latest = ""
    ice_rows = []
    ice_series = {}
    for market in ice_markets:
        series = ice_market_series(ice_data, ice_oi, market)
        if not series:
            continue
        ice_series[market] = series
        last = series[-1]
        ice_latest = max(ice_latest, last["date"])
        prev = series[-2] if len(series) >= 2 else None
        mm = last["cats"].get("managed_money", {})
        pm = prev["cats"].get("managed_money", {}) if prev else {}
        wow = None
        if mm.get("net") is not None and pm.get("net") is not None:
            wow = mm["net"] - pm["net"]
        comm = last["cats"].get("producer_merchant", {})
        ice_rows.append((market, last, mm, wow, comm))
    pub = friday_after(ice_latest) if ice_latest else ""
    body.append(f'<p class="market-table-updated">ICE positions as '
                f'of {fdate(ice_latest)} - published {fdate(pub)}; '
                f"ESMA register below carries its own dates</p>\n")
    body.append("<h2>ICE Commitments of Traders</h2>\n")
    body.append('<p class="gm-method">ICE Futures Europe publishes '
                "a Commitments of Traders report in the CFTC shape: "
                "Tuesday positions, published Friday, futures only "
                "in this table. Categories mirror the disaggregated "
                "set.</p>\n")
    out = []
    for market, last, mm, wow, comm in ice_rows:
        out.append(
            f'<tr><td><a href="/positioning/europe/'
            f'{slugify("ice-" + market)}/">'
            f'{esc(market)}</a></td>'
            f'<td class="num">{fi(mm.get("net"), signed=True)}</td>'
            f'<td class="num">{fi(wow, signed=True)}</td>'
            f'<td class="num">{fi(comm.get("net"), signed=True)}</td>'
            f'<td class="num">{fi(last["oi"])}</td>'
            f"<td>{esc(last['date'])}</td></tr>")
    body.append(table(["Market", "Managed money net", "Week change",
                       "Producer/merchant net", "Open interest",
                       "Position date"], out))
    # ESMA summary
    body.append("<h2>ESMA Article 58 venue reports</h2>\n")
    body.append('<p class="gm-method">Every EU venue files a weekly '
                "position report under MiFID II Article 58: long "
                "and short by holder category, percent of open "
                "interest, and persons per category. Positions are "
                "Friday close, published the following week; the "
                "register carries each report\'s own publication "
                "timestamp. A missing report means the venue was "
                "below the holder and size thresholds that week; "
                "it is not a zero. The register files each "
                "position as risk-reducing, as other, and as a "
                "total of the two; these pages use the total. "
                "Where a venue files both a futures-only "
                "and a combined report, the futures-only report is "
                "used and labelled.</p>\n")
    esma_rows = []
    esma_latest = ""
    for (mic, prod), key in chosen.items():
        dates = sorted(pos[key])
        if not dates:
            continue
        last_d = dates[-1]
        esma_latest = max(esma_latest, last_d)
        block = pos[key][last_d]
        funds = block.get("investment_funds", {})
        comm = block.get("commercial_undertakings", {})
        prev_d = dates[-2] if len(dates) >= 2 else None
        wow = None
        if prev_d:
            pf = pos[key][prev_d].get("investment_funds", {})
            if funds.get("net") is not None \
                    and pf.get("net") is not None:
                wow = funds["net"] - pf["net"]
        esma_rows.append({"mic": mic, "prod": prod, "key": key,
                          "meta": meta[key], "date": last_d,
                          "funds": funds, "comm": comm, "wow": wow,
                          "ndates": len(dates)})
    esma_rows.sort(key=lambda r: (-(abs(r["funds"].get("net") or 0)), r["meta"]["commodity"]))
    if esma_latest:
        recent_cutoff = (datetime.date.fromisoformat(esma_latest)
                         - datetime.timedelta(weeks=13)).isoformat()
    else:
        recent_cutoff = ""
    recent_rows = [r for r in esma_rows if r["date"] >= recent_cutoff]
    out = []
    for r in recent_rows[:100]:
        out.append(
            f'<tr><td><a href="/positioning/europe/'
            f'{slugify(r["mic"] + "-" + r["prod"])}/">'
            f'{esc(r["meta"]["commodity"])}</a></td>'
            f"<td>{esc(r['meta']['venue_name'])}</td>"
            f'<td class="num">'
            f'{fi(r["funds"].get("net"), signed=True)}</td>'
            f'<td class="num">{fi(r["wow"], signed=True)}</td>'
            f'<td class="num">'
            f'{fi(r["comm"].get("net"), signed=True)}</td>'
            f"<td>{esc(r['key'][2])}</td>"
            f"<td>{esc(r['date'])}</td></tr>")
    body.append(table(["Contract", "Venue", "Investment funds net",
                       "Week change", "Commercial net", "Basis",
                       "Position date"], out))
    body.append(f'<p class="gm-method">The table lists contracts '
                f"with a report in the last 13 weeks "
                f"({len(recent_rows)} contracts), largest "
                f"investment funds net first. The register holds "
                f"{len(esma_rows)} contracts in total. UK venues "
                f"left this register when the UK left the EU: ICE "
                f"Futures Europe and LME reports in the register "
                f"end in December 2020, and their current "
                f"positioning prints in the ICE table above and "
                f"the LME section.</p>\n")
    body.append('<p class="data-vintage">Sources: ICE Futures '
                "Europe Commitments of Traders (from 2011) and the "
                "ESMA Article 58 register (from 2018).</p>\n")
    lede = ("European venue positioning: ICE Commitments of Traders "
            "and the ESMA Article 58 register, by category.")
    index = (frontmatter("Europe positioning", lede,
                         f"ICE as of {fdate(ice_latest)}; ESMA as of "
                         f"{fdate(esma_latest)}") + "".join(body))
    pages = {}
    # ICE contract pages
    for market in ice_markets:
        series = ice_series.get(market)
        if not series:
            continue
        last = series[-1]
        prev = series[-2] if len(series) >= 2 else None
        b = []
        pubm = friday_after(last["date"])
        b.append(f'<p class="market-table-updated">Positions as of '
                 f'{fdate(last["date"])} - published {fdate(pubm)} '
                 f"(Friday release)</p>\n")
        b.append(meta_lines([
            ("Market", esc(market)),
            ("Basis", "Futures only"),
            ("Contract unit",
             esc(ice_units.get(market, "").strip("()").title())),
            ("Open interest, contracts", fi(last["oi"])),
            ("Reports in dataset", fi(len(series))),
            ("Coverage", f"{esc(series[0]['date'])} to "
             f"{esc(last['date'])}"),
        ]))
        out = []
        for cat, label in ICE_CATS:
            c = last["cats"].get(cat, {})
            p = prev["cats"].get(cat, {}) if prev else {}
            wow = None
            if c.get("net") is not None and p.get("net") is not None:
                wow = c["net"] - p["net"]
            netpct = None
            if c.get("net") is not None and last["oi"]:
                netpct = 100.0 * c["net"] / last["oi"]
            out.append(
                f"<tr><td>{esc(label)}</td>"
                f'<td class="num">{fi(c.get("long"))}</td>'
                f'<td class="num">{fi(c.get("short"))}</td>'
                f'<td class="num">{fi(c.get("net"), signed=True)}</td>'
                f'<td class="num">{fi(wow, signed=True)}</td>'
                f'<td class="num">{fp(netpct)}</td></tr>')
        b.append(table(["Category", "Long", "Short", "Net",
                        "Week change", "Net % of OI"], out))
        mm_hist = [(e["date"], e["cats"].get("managed_money", {})
                    .get("net")) for e in series]
        g = gauges([(d, n) for d, n in mm_hist if n is not None])
        b.append("<h2>Managed money net against its history</h2>\n")
        b.append(meta_lines([
            ("Net, contracts", fi(g.get("net"), signed=True)),
            ("Week change", fi(g.get("wow"), signed=True)),
            ("4-week change", fi(g.get("chg4"), signed=True)),
            ("13-week change", fi(g.get("chg13"), signed=True)),
            ("Percentile, 1 year", fp(g.get("pct1y"), 0)),
            ("Percentile, 3 years", fp(g.get("pct3y"), 0)),
            ("Z-score, 52 weeks", fp(g.get("z52"), 2)),
            ("COT Index, 3 years", fp(g.get("cotindex"), 0)),
        ]))
        cb_series = ice_market_series(ice_data, ice_oi, market,
                                      basis="Combined")
        if cb_series and cb_series[-1]["date"] == last["date"]:
            cb = cb_series[-1]
            out = []
            for cat, label in ICE_CATS:
                c = cb["cats"].get(cat, {})
                out.append(
                    f"<tr><td>{esc(label)}</td>"
                    f'<td class="num">{fi(c.get("long"))}</td>'
                    f'<td class="num">{fi(c.get("short"))}</td>'
                    f'<td class="num">'
                    f'{fi(c.get("net"), signed=True)}</td></tr>')
            b.append("<h2>Futures and options combined</h2>\n")
            b.append(table(["Category", "Long", "Short", "Net"], out))
            b.append('<p class="gm-method">The combined basis adds '
                     "delta-adjusted options. It is a separate "
                     "basis and is never mixed into the futures-only "
                     "history above.</p>\n")
        b.append('<p class="data-vintage">Source: ICE Futures '
                 "Europe Commitments of Traders. Positions as of "
                 + fdate(last["date"]) + ", published "
                 + fdate(pubm) + ".</p>\n")
        title = f"{market} ICE COT"
        lede = (f"ICE positioning in {market}: managed money net "
                f"{fi(last['cats'].get('managed_money', {}).get('net'), signed=True)} "
                f"contracts, positions as of {fdate(last['date'])}.")
        pages[slugify("ice-" + market)] = frontmatter(
            title, lede, f"Positions as of {fdate(last['date'])}; "
            f"published {fdate(pubm)}") + "".join(b)
    # ESMA contract pages: contracts reported in the last 13 weeks
    if esma_latest:
        cutoff = (datetime.date.fromisoformat(esma_latest)
                  - datetime.timedelta(weeks=13)).isoformat()
    else:
        cutoff = ""
    for r in esma_rows:
        if r["date"] < cutoff:
            continue
        key = r["key"]
        dates = sorted(pos[key])
        last_d = dates[-1]
        block = pos[key][last_d]
        b = []
        b.append(f'<p class="market-table-updated">Positions as of '
                 f'{fdate(last_d)} (Friday close) - published the '
                 f"following week in the ESMA register</p>\n")
        b.append(meta_lines([
            ("Contract", esc(r["meta"]["commodity"])),
            ("Venue", esc(r["meta"]["venue_name"])),
            ("Basis", "Futures only" if key[2] == "FUTR"
             else "Futures and options combined"),
            ("Unit", esc(r["meta"]["unit"])),
            ("Reports in dataset", fi(len(dates))),
            ("Coverage", f"{esc(dates[0])} to {esc(last_d)}"),
        ]))
        out = []
        for grp, label in ESMA_CATS:
            c = block.get(grp, {})
            pc = pct[key][last_d].get(grp, {})
            persons_v = persons[key][last_d].get(grp)
            out.append(
                f"<tr><td>{esc(label)}</td>"
                f'<td class="num">{fi(c.get("long"))}</td>'
                f'<td class="num">{fi(c.get("short"))}</td>'
                f'<td class="num">{fi(c.get("net"), signed=True)}</td>'
                f'<td class="num">{fp(pc.get("long"))}</td>'
                f'<td class="num">{fp(pc.get("short"))}</td>'
                f'<td class="num">{fi(persons_v)}</td></tr>')
        b.append(table(["Category", "Long", "Short", "Net",
                        "Long % of OI", "Short % of OI",
                        "Persons, as filed"], out))
        funds_hist = [(d, pos[key][d].get("investment_funds", {})
                       .get("net")) for d in dates]
        fh = [(d, n) for d, n in funds_hist if n is not None]
        if len(fh) >= 2:
            b.append("<h2>Investment funds net, recent change</h2>\n")
            b.append(meta_lines([
                ("Net", fi(fh[-1][1], signed=True)),
                ("Week change",
                 fi(fh[-1][1] - fh[-2][1], signed=True)),
                ("4-week change",
                 fi(fh[-1][1] - fh[-5][1], signed=True)
                 if len(fh) >= 5 else BLANK),
                ("13-week change",
                 fi(fh[-1][1] - fh[-14][1], signed=True)
                 if len(fh) >= 14 else BLANK),
            ]))
            b.append('<p class="gm-method">Percentile gauges are '
                     "not printed for Article 58 contracts: reports "
                     "exist only in weeks when the venue clears the "
                     "holder and size thresholds, so the history has "
                     "gaps that are threshold events, not zeros.</p>\n")
        b.append('<p class="data-vintage">Source: ESMA Article 58 '
                 "position register, " + esc(r["meta"]["venue_name"])
                 + ". Positions as of " + fdate(last_d) + ".</p>\n")
        title = f"{r['meta']['commodity']} Article 58"
        lede = (f"Article 58 positioning in "
                f"{r['meta']['commodity']} at "
                f"{r['meta']['venue_name']}: investment funds net "
                f"{fi(r['funds'].get('net'), signed=True)}, positions "
                f"as of {fdate(last_d)}.")
        pages[slugify(r["mic"] + "-" + r["prod"])] = frontmatter(
            title, lede, f"Positions as of {fdate(last_d)}") \
            + "".join(b)
    summary = {"ice_latest": ice_latest, "ice_markets": len(ice_rows),
               "esma_latest": esma_latest,
               "esma_contracts": len(esma_rows),
               "movers": []}
    for market, _last, mm, wow, _c in ice_rows:
        if wow is not None:
            summary["movers"].append(
                {"market": market, "family": "ICE", "wow": wow,
                 "unit": "contracts"})
    for r in esma_rows:
        if r["wow"] is not None:
            summary["movers"].append(
                {"market": r["meta"]["commodity"], "family": "ESMA",
                 "wow": r["wow"], "unit": "lots"})
    return index, pages, summary


# -------------------------------------------------------------- Landing

def landing_page(ctx):
    body = []
    body.append('<p class="gm-method">Positioning is what '
                "regulators publish about who holds what: weekly "
                "commitments of traders in the United States and "
                "Europe, monthly bank participation, daily short "
                "position disclosures, and exchange open interest "
                "in Asia. Every family carries its own dates. "
                "Position dates and publication dates both print; "
                "the families update on different days and are "
                "never given one combined stamp.</p>\n")
    # per-family datelines
    dl = []
    for fam in ctx["families"]:
        dl.append(
            f"<tr><td>{esc(fam['name'])}</td>"
            f"<td>{esc(fam['position'])}</td>"
            f"<td>{esc(fam['publication'])}</td>"
            f"<td>{esc(fam['coverage'])}</td></tr>")
    body.append("<h2>Datelines by family</h2>\n")
    body.append(table(["Family", "Latest position date",
                       "Latest publication date", "Coverage"], dl))
    # extremes
    ex = [s for s in ctx["summaries"].values()
          if s["gauges"].get("z52") is not None]
    ex.sort(key=lambda s: (-abs(s["gauges"]["z52"]), s["name"]))
    out = []
    for s in ex[:25]:
        g = s["gauges"]
        netpct = None
        if g.get("net") is not None and g.get("oi"):
            netpct = 100.0 * g["net"] / g["oi"]
        flag = "extreme" if abs(g["z52"]) >= 2.5 else \
            "stretched" if abs(g["z52"]) >= 1.8 else ""
        out.append(
            f'<tr><td><a href="/positioning/cftc-cot/'
            f'{s["slug"]}/">{esc(s["name"])}</a></td>'
            f"<td>{esc(s['family_label'])}</td>"
            f'<td class="num">{fi(g.get("net"), signed=True)}</td>'
            f'<td class="num">{fi(g.get("wow"), signed=True)}</td>'
            f'<td class="num">{fp(netpct)}</td>'
            f'<td class="num">{fp(g.get("pct1y"), 0)}</td>'
            f'<td class="num">{fp(g.get("pct3y"), 0)}</td>'
            f'<td class="num">{fp(g.get("z52"), 2)}</td>'
            f"<td>{esc(flag)}</td></tr>")
    body.append("<h2>Extremes, CFTC speculative positioning</h2>\n")
    body.append('<p class="gm-method">Ranked by the absolute '
                "z-score of the speculative net over 52 weeks. A "
                "z-score at or above 1.8 in absolute value is "
                "marked stretched, at or above 2.5 extreme. The "
                "full table is on the "
                '<a href="/positioning/cftc-cot/">CFTC page</a>.'
                "</p>\n")
    body.append(table(["Market", "Family", "Speculative net",
                       "Week change", "Net % of OI", "Percentile 1Y",
                       "Percentile 3Y", "Z-score 52W", "Reading"],
                      out))
    # biggest movers
    movers = []
    for s in ctx["summaries"].values():
        g = s["gauges"]
        if g.get("wow") is not None:
            pct_oi = None
            if g.get("oi"):
                pct_oi = 100.0 * g["wow"] / g["oi"]
            movers.append({"market": s["name"], "family": "CFTC",
                           "wow": g["wow"], "unit": "contracts",
                           "pct": pct_oi,
                           "url": f"/positioning/cftc-cot/"
                           f"{s['slug']}/"})
    for m in ctx["europe_movers"]:
        movers.append({"market": m["market"], "family": m["family"],
                       "wow": m["wow"], "unit": m["unit"],
                       "pct": None, "url": "/positioning/europe/"})
    movers.sort(key=lambda m: (-abs(m["wow"]), m["market"]))
    out = []
    for m in movers[:15]:
        out.append(
            f'<tr><td><a href="{m["url"]}">{esc(m["market"])}</a></td>'
            f"<td>{esc(m['family'])}</td>"
            f'<td class="num">{fi(m["wow"], signed=True)}</td>'
            f"<td>{esc(m['unit'])}</td>"
            f'<td class="num">{fp(m["pct"])}</td></tr>')
    body.append("<h2>Biggest week changes in speculative net</h2>\n")
    body.append(table(["Market", "Family", "Change, contracts or "
                       "lots", "Unit", "Change as % of OI (CFTC)"],
                      out))
    # shorts summary
    if ctx.get("shorts_top"):
        out = []
        for issuer, pct in ctx["shorts_top"]:
            out.append(f"<tr><td>{esc(issuer)}</td>"
                       f'<td class="num">{pct:.2f}%</td></tr>')
        body.append("<h2>Largest disclosed shorts, Europe</h2>\n")
        body.append('<p class="gm-method">Aggregate named net '
                    "short positions as a percent of issued share "
                    "capital, summed across holders per issuer. "
                    'The full tables are on the '
                    '<a href="/positioning/shorts/">shorts page</a>.'
                    "</p>\n")
        body.append(table(["Issuer", "Aggregate disclosed, % of "
                           "capital"], out))
    # asia summary
    body.append("<h2>Asia</h2>\n")
    body.append('<p class="gm-method">Asia publishes open interest '
                "and member rankings, not trader categories. SGX "
                "open interest prints from 27 October 2026, the "
                "start of the collected series. CZCE member "
                "rankings are banked in the vault back to 2016 and "
                "in backfill; the tidy build is a sample, so no "
                "CZCE table prints yet. Detail is on the "
                '<a href="/positioning/asia/">Asia page</a>.</p>\n')
    # family index blocks
    body.append("<h2>Families</h2>\n")
    for fam in ctx["families"]:
        body.append(f"<h3>{esc(fam['name'])}</h3>\n")
        body.append(meta_lines([
            ("Coverage", esc(fam["coverage"])),
            ("Dataset size", esc(fam["size"])),
            ("Collector cadence", esc(fam["cadence"])),
            ("Latest position date", esc(fam["position"])),
            ("Latest publication date", esc(fam["publication"])),
            ("Pages", f'<a href="{fam["url"]}">'
             f'{esc(fam["name"])}</a>'),
        ]))
    body.append('<p class="gm-method">Method, in brief: net is long '
                "minus short, spreading excluded. Percentile is "
                "the share of weeks in the window at or below the "
                "current net. The COT Index places the current net "
                "in its 3-year range. Gauges print only when the "
                "window holds the history they need. Suppressed and "
                "below-threshold cells print as suppressed or as "
                "no report, never as zero. Positioning extremes "
                "are conditions of crowding, not buy or sell "
                "signals.</p>\n")
    body.append('<p class="data-vintage">Sources: CFTC, OCC, ICE, '
                "ESMA, LME, FCA, EU national registers, SGX, JPX, "
                "CZCE, as labelled per family.</p>\n")
    lede = ("Who holds what, from the regulators and exchanges "
            "that publish it: CFTC commitments of traders, bank "
            "participation, European venue reports, LME, short "
            "positions and Asia open interest.")
    return frontmatter("Positioning", lede,
                        "Datelines per family below; no single "
                        "combined stamp") + "".join(body)


# ----------------------------------------------------------------- Main

def fingerprint():
    h = hashlib.sha256()
    roots = [os.path.join(CFTC, "cot"), os.path.join(CFTC, "bpr"),
             os.path.join(CFTC, "occ"),
             os.path.join(PH, "datasets"),
             os.path.join(PH, "status", "asia-commod-china.json")]
    for root in roots:
        if os.path.isfile(root):
            files = [root]
        else:
            files = []
            for dp, _dn, fn in os.walk(root):
                for name in sorted(fn):
                    if name.endswith((".csv", ".json")):
                        files.append(os.path.join(dp, name))
        for p in sorted(files):
            st = os.stat(p)
            h.update(f"{p}|{st.st_size}|{st.st_mtime_ns}\n".encode())
    with open(os.path.abspath(__file__), "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def build_all():
    fams, ref, cit, cit_date = load_cot()
    summaries = cot_market_summaries(fams, ref, cit)
    write_page("content/positioning/cftc-cot/_index.md",
               cot_index_page(summaries, fams, cit))
    for s in summaries.values():
        write_page(f"content/positioning/cftc-cot/{s['slug']}.md",
                   cot_market_page(s, fams, cit))
    bpr_markets, bpr_nrows = load_bpr()
    bpr_index, bpr_meta, bpr_latest_month = bpr_index_page(bpr_markets)
    write_page("content/positioning/bank-participation/_index.md",
               bpr_index)
    for commodity, months in bpr_markets.items():
        if bpr_latest_month not in months and len(months) < 24:
            continue
        slug, page = bpr_market_page(commodity, months)
        write_page(f"content/positioning/bank-participation/"
                   f"{slug}.md", page)
    ice_data, ice_oi, ice_units, ice_nrows = load_ice()
    esma = load_esma()
    eu_index, eu_pages, eu_summary = europe_pages(
        ice_data, ice_oi, ice_units, esma)
    write_page("content/positioning/europe/_index.md", eu_index)
    for slug, page in eu_pages.items():
        write_page(f"content/positioning/europe/{slug}.md", page)
    lme_data, lme_names, lme_gen, lme_nrows = load_lme()
    lme_index, lme_latest, lme_pub = lme_index_page(
        lme_data, lme_names, lme_gen)
    write_page("content/positioning/lme/_index.md", lme_index)
    for code in lme_data:
        write_page(f"content/positioning/lme/"
                   f"{slugify(lme_names[code])}.md",
                   lme_metal_page(code, lme_data, lme_names, lme_gen))
    shorts, shorts_summary = shorts_page()
    write_page("content/positioning/shorts.md", shorts)
    czce_status = None
    spath = os.path.join(PH, "status", "asia-commod-china.json")
    if os.path.exists(spath):
        with open(spath, encoding="utf-8") as f:
            czce_status = json.load(f)
    asia, asia_summary = asia_page(czce_status)
    write_page("content/positioning/asia.md", asia)
    occ, occ_summary = occ_page()
    write_page("content/positioning/occ.md", occ)
    # landing
    cot_latest = max(s["date"] for s in summaries.values())
    cot_total_rows = sum(
        count_rows(os.path.join(CFTC, "cot", spec["file"]))
        for spec in COT_FAMILIES.values()) + count_rows(
            os.path.join(CFTC, "cot", "cit_supplement.csv"))
    bpr_latest_date = ""
    for months in bpr_markets.values():
        if bpr_latest_month in months:
            bpr_latest_date = max(
                bpr_latest_date,
                bpr_block(months[bpr_latest_month])["date"])
    families = [
        {"name": "CFTC Commitments of Traders",
         "url": "/positioning/cftc-cot/",
         "position": fdate(cot_latest),
         "publication": fdate(friday_after(cot_latest)),
         "coverage": f"{len(summaries)} markets, three report "
                     f"families, history from 1986 (legacy), 2006 "
                     f"(disaggregated)",
         "size": f"{cot_total_rows:,} tidy rows",
         "cadence": "Weekly, Friday after the CFTC release"},
        {"name": "Bank Participation",
         "url": "/positioning/bank-participation/",
         "position": fdate(bpr_latest_date),
         "publication": f"Report month {bpr_latest_month}, "
                        f"published later the same month",
         "coverage": f"{len(bpr_markets)} markets, monthly, "
                     f"November 2013 to October 2026",
         "size": f"{bpr_nrows:,} tidy rows",
         "cadence": "Monthly"},
        {"name": "Europe: ICE and ESMA Article 58",
         "url": "/positioning/europe/",
         "position": fdate(eu_summary["esma_latest"]),
         "publication": "Register timestamps per report; ICE "
                        "Friday release",
         "coverage": f"ICE from 2011; {eu_summary['esma_contracts']} "
                     f"ESMA contracts",
         "size": "1,138,950 ESMA rows; 356,031 ICE rows",
         "cadence": "Weekly, Wednesday"},
        {"name": "LME Commitments of Traders",
         "url": "/positioning/lme/",
         "position": fdate(lme_latest),
         "publication": fdate(lme_pub[:10]),
         "coverage": f"{len(lme_data)} metals, from 3 Jan 2020",
         "size": f"{lme_nrows:,} tidy rows",
         "cadence": "Weekly, Tuesday publication"},
        {"name": "Short positions",
         "url": "/positioning/shorts/",
         "position": fdate(shorts_summary["latest_pos"]),
         "publication": "Registers publish about one day after "
                        "the position date",
         "coverage": "Eight EU registers, UK ANSP from "
                     "13 Jul 2026, UK named archive to 9 Jul 2026",
         "size": f"{shorts_summary['n_disclosures']:,} disclosures",
         "cadence": "Daily, weekdays"},
        {"name": "Asia",
         "url": "/positioning/asia/",
         "position": f"SGX {fdate(asia_summary['sgx_latest'])}",
         "publication": "Daily files",
         "coverage": "SGX from 27 Oct 2026; TOCOM sampled "
                     "2022 to 2026; CZCE banked 2016 to 2026, "
                     "processing pending",
         "size": "SGX daily files; TOCOM 13,589 rows; CZCE "
                 "3,325 raw files banked",
         "cadence": "Daily"},
        {"name": "OCC Bank Derivatives",
         "url": "/positioning/occ/",
         "position": f"Quarter ended {fdate(occ_summary['latest'])}",
         "publication": "About 10 to 12 weeks after quarter end",
         "coverage": f"{occ_summary['quarters']} quarters, "
                     f"{qlabel(occ_summary['first'])} to "
                     f"{qlabel(occ_summary['last'])}",
         "size": "202,465 observations",
         "cadence": "Quarterly"},
    ]
    ctx = {"summaries": summaries, "families": families,
           "europe_movers": eu_summary["movers"],
           "shorts_top": shorts_summary["top_issuers"]}
    write_page("content/positioning/_index.md", landing_page(ctx))
    summary_json = {
        "built_for": "positioning section",
        "cot_markets": len(summaries),
        "cot_latest": cot_latest,
        "bpr_latest_month": bpr_latest_month,
        "europe": eu_summary,
        "lme_latest": lme_latest,
        "shorts_latest": shorts_summary["latest_pos"],
        "asia": asia_summary,
        "occ_latest": occ_summary["latest"],
    }
    write_json("landing.json", summary_json)
    # remove stale generated pages under content/positioning
    keep = {os.path.join(SITE, p) for p in PUBLISHED
            if p.startswith("content/positioning/")}
    for dp, _dn, fn in os.walk(OUT):
        for name in fn:
            p = os.path.join(dp, name)
            if name.endswith(".md") and p not in keep:
                os.remove(p)
    return summary_json


def main():
    if "--if-changed" in sys.argv:
        fp = fingerprint()
        old = None
        if os.path.exists(STATE):
            try:
                old = json.load(open(STATE)).get("fingerprint")
            except Exception:
                old = None
        if old == fp and os.path.exists(
                os.path.join(OUT, "_index.md")):
            print("NOCHANGE")
            return
        summary = build_all()
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump({"fingerprint": fp, "summary": summary}, f)
        for p in PUBLISHED:
            print(f"PUBLISH {p}")
        return
    summary = build_all()
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump({"fingerprint": fingerprint(), "summary": summary},
                  f)
    print("built positioning section:", json.dumps(summary))


if __name__ == "__main__":
    main()
