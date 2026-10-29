#!/usr/bin/env python3
"""Build the three Macro pages from data/macro/*.json.
Writes content/macro/{spreads,central-banks,economies}.md with HTML tables.
Charts live in static/macro/.
"""
import json, os, datetime, re

SITE = os.path.expanduser("~/workspace/news-site")
DATA = os.path.join(SITE, "data", "macro")
OUT = os.path.join(SITE, "content", "macro")

REGION_LABEL = {
    "north-america": "North America", "latin-america": "Latin America",
    "europe": "Europe", "middle-east": "Middle East", "africa": "Africa",
    "asia-pacific": "Asia-Pacific",
}

def frontmatter(title, lede, vintage, aliases=None, url=None):
    alias_block = ""
    if aliases:
        items = "\n".join(f"  - \"{a}\"" for a in aliases)
        alias_block = f"aliases:\n{items}\n"
    url_block = f"url: \"{url}\"\n" if url else ""
    import datetime as _dt
    _today = _dt.date.today().isoformat()
    return f"""---
title: "{title}"
date: "{_today}"
lede: "{lede}"
data_as_of: "{vintage}"
{alias_block}{url_block}---

"""

_ENTITY_CACHE = None


def _entity_links():
    """Entity Index reciprocal links (Stage 4 completion,
    2026-10-21): issuer page slug -> (hub slug, canonical name) and
    CUSIP -> (hub slug, canonical name), for the companies resolved
    against the registry in data/entity_index_resolution.json."""
    global _ENTITY_CACHE
    if _ENTITY_CACHE is not None:
        return _ENTITY_CACHE
    by_issuer, by_cusip = {}, {}
    try:
        res = json.load(open(os.path.join(
            SITE, "data", "entity_index_resolution.json")))
        for e in res["pass_a"]["entities"]:
            if e["status"] != "matched":
                continue
            if e.get("issuer_page"):
                by_issuer[e["issuer_page"]] = (e["slug"],
                                               e["canonical"])
            for c in e.get("cusips") or []:
                by_cusip[c] = (e["slug"], e["canonical"])
    except Exception:
        pass
    _ENTITY_CACHE = (by_issuer, by_cusip)
    return _ENTITY_CACHE


def spreads_page():
    d = json.load(open(os.path.join(DATA, "spreads.json")))
    charts = json.load(open(os.path.join(DATA, "spread_charts.json")))
    countries = d["countries"]
    non_bench = [c for c in countries if c["spread_bp"] != 0]
    widest = max(non_bench, key=lambda c: c["spread_bp"])
    tightest = min(non_bench, key=lambda c: c["spread_bp"])
    big_up = max(countries, key=lambda c: c["change_12m_bp"])
    big_dn = min(countries, key=lambda c: c["change_12m_bp"])
    stats = (
        "<div class=\"stat-row\">\n"
        f"<div class=\"stat\"><span class=\"stat-label\">Widest spread</span><span class=\"stat-value\">{widest['name']} {widest['spread_bp']:+.0f} bp</span></div>\n"
        f"<div class=\"stat\"><span class=\"stat-label\">Tightest spread</span><span class=\"stat-value\">{tightest['name']} {tightest['spread_bp']:+.0f} bp</span></div>\n"
        f"<div class=\"stat\"><span class=\"stat-label\">Biggest 12m widening</span><span class=\"stat-value\">{big_up['name']} {big_up['change_12m_bp']:+.0f} bp</span></div>\n"
        f"<div class=\"stat\"><span class=\"stat-label\">Biggest 12m tightening</span><span class=\"stat-value\">{big_dn['name']} {big_dn['change_12m_bp']:+.0f} bp</span></div>\n"
        "</div>\n"
    )
    rows = []
    for c in countries:
        chg1 = c["change_1m_bp"]; chg12 = c["change_12m_bp"]
        rows.append(
            f"<tr><td>{c['name']}</td>"
            f"<td class=\"num\">{c['yield_10y']:.2f}%</td>"
            f"<td class=\"num\">{c['spread_bp']:+.0f} bp</td>"
            f"<td class=\"muted\">{c['benchmark']}</td>"
            f"<td class=\"num {'up' if chg1 >= 0 else 'down'}\">{chg1:+.0f}</td>"
            f"<td class=\"num {'up' if chg12 >= 0 else 'down'}\">{chg12:+.0f}</td></tr>"
        )
    body = frontmatter(
        "Sovereign Spreads",
        "Ten-year government bond yields and spreads for 17 economies.",
        f"{d['data_through']} (monthly)",
    )
    body += (
        stats
        + "<h2>All countries</h2>\n"
        "<p class=\"data-vintage\">Yields in percent; spreads in basis points vs the regional benchmark. "
        "Changes are in basis points.</p>\n"
        "<div class=\"market-table-scroll\"><table class=\"market-table\">\n"
        "<thead><tr><th>Country</th><th>10Y yield</th><th>Spread</th><th>Benchmark</th>"
        "<th>1m chg (bp)</th><th>12m chg (bp)</th></tr></thead>\n<tbody>\n"
        + "\n".join(rows) +
        "\n</tbody></table></div>\n"
        "<h2>Europe vs Bunds, 2006 to now</h2>\n" + charts["europe"] + "\n"
        "<h2>Benchmark yields, 2006 to now</h2>\n" + charts["benchmarks"] + "\n"
        "<h2>12-month spread moves</h2>\n" + charts["movers12m"] + "\n"
        f"<p class=\"data-vintage\">Source: {d['source']}. {d.get('refresh_note', '')}</p>\n"
    )
    return body

def central_banks_page():
    d = json.load(open(os.path.join(DATA, "central_banks.json")))
    rows = []
    for b in d["rates"]:
        lc = b["last_change"]
        action = f"{lc['action']} {lc['bp']}bp on {lc['date']}" if lc.get("bp") else f"{lc['action']} on {lc['date']}"
        nm = b.get("next_meeting", "TBD")
        rows.append(
            f"<tr><td>{b['bank_short']}</td><td>{b['country']}</td>"
            f"<td class=\"num\">{b['current_rate']:.2f}%</td>"
            f"<td>{action}</td><td>{nm}</td></tr>"
        )
    body = frontmatter(
        "Central Banks",
        "Policy rates, last moves, and next meetings for 11 major central banks.",
        d.get("data_through", d.get("updated", "")),
    )
    body += (
        "<div class=\"market-table-scroll\"><table class=\"market-table\">\n"
        "<thead><tr><th>Bank</th><th>Country</th><th>Policy rate</th><th>Last change</th>"
        "<th>Next meeting</th></tr></thead>\n<tbody>\n"
        + "\n".join(rows) +
        "\n</tbody></table></div>\n"
        f"<p class=\"data-vintage\">{d.get('method', '')}</p>\n"
    )
    return body

def economies_page():
    d = json.load(open(os.path.join(DATA, "snapshot.json")))
    rows = []
    for e in d["economies"]:
        g, i, u = e["gdp"], e["inflation"], e["unemployment"]
        q = e.get("quarterly_gdp_yoy")
        qstr = f"{q['value']:.1f}% ({q['quarter']})" if q else "n/a"
        rows.append(
            f"<tr><td>{e['country']}</td>"
            f"<td class=\"num\">{g['actual_2025']:.1f}%</td>"
            f"<td class=\"num\">{g['estimate_2026']:.1f}%</td>"
            f"<td class=\"num\">{i['actual_2025']:.1f}%</td>"
            f"<td class=\"num\">{i['estimate_2026']:.1f}%</td>"
            f"<td class=\"num\">{u['actual_2025']:.1f}%</td>"
            f"<td class=\"num\">{qstr}</td></tr>"
        )
    vintage = d.get("updated", "")
    body = frontmatter(
        "Economies",
        "GDP growth, inflation, and unemployment for 20 economies.",
        vintage,
    )
    body += (
        "<p class=\"data-vintage\">Annual figures: 2025 actual, 2026 estimate. "
        "Quarterly GDP is year-on-year where available.</p>\n"
        "<div class=\"market-table-scroll\"><table class=\"market-table\">\n"
        "<thead><tr><th>Economy</th><th>GDP 2025</th><th>GDP 2026e</th>"
        "<th>Inflation 2025</th><th>Inflation 2026e</th><th>Unemp. 2025</th>"
        "<th>GDP y/y (latest qtr)</th></tr></thead>\n<tbody>\n"
        + "\n".join(rows) +
        "\n</tbody></table></div>\n"
        f"<p class=\"data-vintage\">{d.get('method', '')}</p>\n"
    )
    return body

def _bond_label(r):
    name = (r.get("issuer") or r.get("deal") or r["cusip"]).title()
    bits = [name]
    if r.get("coupon_pct"):
        bits.append(f"{r['coupon_pct']:.3f}".rstrip("0").rstrip(".") + "%")
    if r.get("maturity"):
        bits.append("due " + r["maturity"][:4])
    return " ".join(bits)

def _marks_cell(r):
    hist = r["history"][-4:]
    return " &rarr; ".join(f"{p:.2f}" for _, p in hist)

def _bond_row(r, thin=False):
    chg = r["change_pts"]
    chg_cls = "down" if (chg is not None and chg < 0) else "up"
    chg_str = f"{chg:+.2f}" if chg is not None else "n/a"
    price = r["latest_price"]
    chg_v = f"{chg:.2f}" if chg is not None else "-999"
    prin = r.get("principal_usd")
    prin_cell = (f"<td class=\"num\" data-v=\"{prin}\">"
                 f"{prin / 1e6:,.1f}</td>" if prin is not None
                 else "<td class=\"muted\" data-v=\"-999\">n/a</td>")
    return (
        f"<tr><td data-v=\"{_bond_label(r)}\"><a class=\"bond-link\" "
        f"href=\"/leverage/bond/{r['cusip'].lower()}/\">{_bond_label(r)}</a></td>"
        f"{_issued_cell(r['cusip'])}"
        f"<td class=\"num\" data-v=\"{price:.2f}\">{price:.2f}</td>"
        f"<td class=\"num {chg_cls}\" data-v=\"{chg_v}\">{chg_str}</td>"
        f"<td class=\"muted\">{_fmt_date(r['latest_period'])}</td>"
        f"<td class=\"muted\">{_marks_cell(r)}</td>"
        f"<td class=\"num\">{r['positions']}</td>"
        f"{prin_cell}"
        f"<td class=\"muted\">{r['cusip']}</td></tr>"
    )

def _minus_6m(d):
    import calendar as _cal
    y, m = d.year, d.month - 6
    if m <= 0:
        y, m = y - 1, m + 12
    return d.replace(year=y, month=m,
                     day=min(d.day, _cal.monthrange(y, m)[1]))


def _d360(d1, d2):
    dd1 = min(d1.day, 30)
    dd2 = min(d2.day, 30) if dd1 < 30 else d2.day
    return (d2.year - d1.year) * 360 + (d2.month - d1.month) * 30 + (dd2 - dd1)


def _ytm(price, coupon_pct, maturity, settle, redemption=100.0):
    """Yield to maturity in percent: semiannual compounding, 30/360,
    settlement at the trade date. Same convention as price_watch.py;
    validated against the reported 15.06% on the CoreWeave 2032 notes at
    79.50 on 2026-10-14 (this formula gives 15.07%)."""
    from datetime import date as _date
    if price is None or not coupon_pct or not maturity or not settle:
        return None
    if isinstance(maturity, str):
        maturity = _date.fromisoformat(maturity)
    if isinstance(settle, str):
        settle = _date.fromisoformat(settle)
    c = coupon_pct / 2.0
    fut = []
    d = maturity
    while d > settle:
        fut.append(d)
        d = _minus_6m(d)
    if not fut:
        return None
    fut.reverse()
    prev = _minus_6m(fut[0])
    da, dp = _d360(prev, settle), _d360(prev, fut[0])
    if dp <= 0:
        return None
    w = 1.0 - da / dp
    dirty = price + c * (da / dp)
    n = len(fut)

    def pv(y):
        v = 1.0 / (1.0 + y / 2.0)
        return sum((c if i < n - 1 else c + redemption) * v ** (w + i)
                   for i in range(n))

    lo, hi = -0.5, 3.0
    if pv(lo) < dirty:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if pv(mid) > dirty:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0 * 100.0


def _mod_duration(price, coupon_pct, maturity, settle, y_pct):
    """Modified duration from the same street-convention schedule."""
    from datetime import date as _date
    if y_pct is None or not coupon_pct or not maturity:
        return None
    if isinstance(maturity, str):
        maturity = _date.fromisoformat(maturity)
    if isinstance(settle, str):
        settle = _date.fromisoformat(settle)
    c = coupon_pct / 2.0
    fut = []
    d = maturity
    while d > settle:
        fut.append(d)
        d = _minus_6m(d)
    if not fut:
        return None
    fut.reverse()
    prev = _minus_6m(fut[0])
    da, dp = _d360(prev, settle), _d360(prev, fut[0])
    if dp <= 0:
        return None
    w = 1.0 - da / dp
    y = y_pct / 100.0
    v = 1.0 / (1.0 + y / 2.0)
    n = len(fut)
    pvsum, wsum = 0.0, 0.0
    for i in range(n):
        cf = c if i < n - 1 else c + 100.0
        t = (w + i) / 2.0  # years
        pvsum += cf * v ** (w + i)
        wsum += t * cf * v ** (w + i)
    if pvsum <= 0:
        return None
    macaulay = wsum / pvsum
    return macaulay / (1.0 + y / 2.0)


def _treasury_curve():
    """US Treasury yields (percent) at 5/10/30 years from the market
    tables the site refreshes hourly. Returns [(5, y), (10, y), (30, y)]
    or None if unavailable."""
    path = os.path.join(SITE, "data", "market_tables.json")
    if not os.path.exists(path):
        return None
    try:
        mt = json.load(open(path))
        pts = []
        for tenor, name in ((5, "US 5Y"), (10, "US 10Y"), (30, "US 30Y")):
            row = [r for r in mt.get("rates", []) if r.get("name") == name]
            if not row:
                return None
            pts.append((tenor, float(row[0]["value"])))
        return pts
    except Exception:
        return None


_TSY_HIST = None


def _tsy_hist():
    global _TSY_HIST
    if _TSY_HIST is None:
        path = os.path.join(SITE, "data", "macro", "treasury_history.json")
        try:
            _TSY_HIST = json.load(open(path))
        except Exception:
            _TSY_HIST = {}
    return _TSY_HIST


def _tsy_on(date_str, years):
    """Treasury yield on a past date at a maturity in years, from the
    FRED DGS history (last observation on or before the date, tenor
    interpolation across 2/5/10/30)."""
    hist = _tsy_hist()
    pts = []
    for tenor, sid in ((2, "DGS2"), (5, "DGS5"), (10, "DGS10"), (30, "DGS30")):
        series = hist.get(sid, {})
        dates = [d for d in series if d <= date_str]
        if not dates:
            return None
        pts.append((tenor, series[max(dates)]))
    if years <= pts[0][0]:
        return pts[0][1]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if years <= x2:
            return y1 + (y2 - y1) * (years - x1) / (x2 - x1)
    return pts[-1][1]


def _tsy(pts, years):
    """Interpolated Treasury yield at a maturity in years (linear between
    the 5/10/30 points, flat outside)."""
    if years <= pts[0][0]:
        return pts[0][1]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if years <= x2:
            return y1 + (y2 - y1) * (years - x1) / (x2 - x1)
    return pts[-1][1]


_DETAIL = None


def _load_bond_detail():
    """Per-bond detail (marks, funds, trades). Split into shards on
    2026-10-21: the monolith bond_detail.json reached 47 MB, past the
    GitHub blob API ceiling, so bond_detail_prep.py now writes
    data/macro/bond_detail/{index.json,shard-NN.json}. Merge the
    shards listed in the index back into the identical dict. Falls
    back to the legacy monolith if the shard directory is absent."""
    sdir = os.path.join(DATA, "bond_detail")
    idxp = os.path.join(sdir, "index.json")
    if os.path.exists(idxp):
        idx = json.load(open(idxp))
        out = {}
        for name in idx["shards"]:
            out.update(json.load(open(os.path.join(sdir, name))))
        return out
    p = os.path.join(DATA, "bond_detail.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def _detail_data():
    global _DETAIL
    if _DETAIL is None:
        _DETAIL = _load_bond_detail()
    return _DETAIL


_NPORT = None


def _nport_panel():
    """The N-PORT full-universe join panel (data/macro/nport_panel
    .json, built by ~/workspace/nport/build_site_panel.py): per-bond
    quarterly medians with each quarter's modal report period (the
    as-of date of the holdings, N-PORT Item A.3.b REPORT_DATE),
    holder aggregates and top holders. The single source for every
    N-PORT figure the builders render (Stage 2, 2026-10-20)."""
    global _NPORT
    if _NPORT is None:
        p = os.path.join(DATA, "nport_panel.json")
        _NPORT = json.load(open(p)) if os.path.exists(p) else {}
    return _NPORT


def _fmt_date(iso):
    if not iso:
        return ""
    import datetime as _dt
    try:
        return _dt.date.fromisoformat(iso).strftime("%d %b %Y")
    except ValueError:
        return iso


def _sparkline2(cusip):
    """Trend on a true time axis, last 12 months: fund marks as
    hollow squares, trades as dots, line segments only across gaps
    of 45 days or less. Fewer than four points in the window: a
    trade count instead of a line (research R4, 2026-10-14)."""
    import datetime as _dt
    det = _detail_data().get(cusip) or {}
    pts = [(m[0], m[1], "m") for m in det.get("marks", [])]
    pts += [(t[0], t[2], "t") for t in det.get("trades", [])]
    if not pts:
        return ""
    pts.sort()
    end_d = _dt.date.fromisoformat(pts[-1][0])
    start_d = end_d - _dt.timedelta(days=365)
    win = [p for p in pts if _dt.date.fromisoformat(p[0]) >= start_d]
    if len(win) < 4:
        n_tr = sum(1 for p in win if p[2] == "t")
        return f"<span class=\"muted\">{n_tr} trades</span>"
    vals = [v for _, v, _ in win]
    lo, hi = min(vals), max(vals)
    # Draw at most one trade point per 3-day bucket (the spark is
    # 112 px wide over 365 days; denser points carry no visible
    # information and, after the 3-year backfill, bloated the watch
    # page past the 25 MiB Pages file limit). Scale stays computed
    # from the full window; marks are never reduced.
    _by_bucket = {}
    for p in win:
        if p[2] == "t":
            _by_bucket[(_dt.date.fromisoformat(p[0]) - start_d).days
                       // 3] = p
    win = sorted([p for p in win if p[2] == "m"]
                 + list(_by_bucket.values()))
    pad = max((hi - lo) * 0.12, 0.4)
    lo, hi = lo - pad, hi + pad
    W, H = 112, 24

    def X(d):
        return 2 + (_dt.date.fromisoformat(d) - start_d).days / 365.0 * (W - 4)

    def Y(v):
        return H - 3 - (v - lo) / (hi - lo) * (H - 6)

    segs, cur = [], [win[0]]
    for p in win[1:]:
        gap = (_dt.date.fromisoformat(p[0])
               - _dt.date.fromisoformat(cur[-1][0])).days
        if gap > 45:
            segs.append(cur)
            cur = [p]
        else:
            cur.append(p)
    segs.append(cur)
    parts = []
    for s in segs:
        if len(s) > 1:
            coords = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, v, _ in s)
            parts.append(f"<polyline points=\"{coords}\" fill=\"none\" "
                         f"stroke=\"#8a8378\" stroke-width=\"1\"/>")
    for d, v, k in win:
        if k == "t":
            parts.append(f"<circle cx=\"{X(d):.1f}\" cy=\"{Y(v):.1f}\" "
                         f"r=\"1.7\" fill=\"#1a1a1a\"/>")
        else:
            parts.append(f"<rect x=\"{X(d) - 1.6:.1f}\" y=\"{Y(v) - 1.6:.1f}\" "
                         f"width=\"3.2\" height=\"3.2\" fill=\"#fff\" "
                         f"stroke=\"#8a8378\" stroke-width=\"0.8\"/>")
    last = win[-1]
    dot = "#b42318" if last[1] < win[0][1] else "#1a7f37"
    parts.append(f"<circle cx=\"{X(last[0]):.1f}\" cy=\"{Y(last[1]):.1f}\" "
                 f"r=\"2.2\" fill=\"{dot}\"/>")
    return (f"<svg class=\"trace-spark\" width=\"{W}\" height=\"{H}\" "
            f"viewBox=\"0 0 {W} {H}\" aria-hidden=\"true\">"
            + "".join(parts) + "</svg>")


# Column specifications: (header, default px, minimum px, fixed).
# One interaction system for every grid on the page (research R1/R5).
TRACE_COLS = [("Bond", 300, 180, False), ("Issued ($M)", 104, 72, False),
              ("Last print (% of par)", 124, 76, False),
              ("Yield at last print (%)", 118, 76, False), ("Spread (bp)", 88, 76, False),
              ("Gap (pts)", 84, 76, False), ("Fund mark (% of par)", 128, 76, False),
              ("Duration (yrs)", 96, 76, False), ("Traded", 176, 92, False),
              ("Coupon (%)", 84, 72, False), ("Matures", 110, 92, False),
              ("Rating", 96, 64, False),
              ("CUSIP", 108, 96, False), ("Trend - 12 mo", 112, 112, True)]
BENCH_COLS = [("Bond", 300, 180, False), ("Issued ($M)", 104, 72, False),
              ("Last print (% of par)", 124, 76, False),
              ("Yield at last print (%)", 118, 76, False), ("Spread (bp)", 88, 76, False),
              ("Duration (yrs)", 96, 76, False), ("Traded", 176, 92, False),
              ("Coupon (%)", 84, 72, False), ("Matures", 110, 92, False),
              ("Rating", 96, 64, False),
              ("CUSIP", 108, 96, False), ("Trend - 12 mo", 112, 112, True)]
MARKS_COLS = [("Bond", 300, 180, False), ("Issued ($M)", 104, 72, False),
              ("Fund mark (% of par)", 124, 76, False),
              ("Change (pts)", 104, 76, False),
              ("Period ended", 110, 92, False), ("Recent marks", 230, 120, False),
              ("Funds", 76, 76, False), ("Principal held ($M)", 130, 92, False),
              ("CUSIP", 108, 96, False)]
BREADTH_COLS = [("Date", 110, 92, False), ("Corporate adv", 124, 76, False),
                ("Corporate dec", 124, 76, False), ("144A adv", 100, 76, False),
                ("144A dec", 100, 76, False),
                ("High-yield adv", 124, 76, False),
                ("High-yield dec", 124, 76, False)]
FLAGS_COLS = [("Bond", 300, 180, False), ("CUSIP", 108, 96, False),
              ("Issued ($M)", 104, 72, False),
              ("Rule", 176, 100, False), ("Detail", 430, 160, False)]


def _grid(tid, cols, rows_html, sortable=True, cls=""):
    if isinstance(rows_html, (list, tuple)):
        rows_html = "\n".join(rows_html)
    defs = [c[1] for c in cols]
    mins = [c[2] for c in cols]
    fixed = [i for i, c in enumerate(cols) if c[3]]
    cg = "".join(f"<col style=\"width:{c[1]}px\">" for c in cols)
    ths = "".join(f"<th>{c[0]}</th>" for c in cols)
    sort_attr = " data-sort=\"1\"" if sortable else ""
    return (f"<div class=\"market-table-scroll\"><table class=\"market-table "
            f"bw-grid {cls}\" data-tid=\"{tid}\" data-def=\"{defs}\" "
            f"data-min=\"{mins}\" data-fixed=\"{fixed}\"{sort_attr}>\n"
            f"<colgroup>{cg}</colgroup>\n<thead><tr>{ths}</tr></thead>\n"
            f"<tbody>\n{rows_html}\n</tbody></table></div>\n")


def _reset_btn(tid):
    return (f" <button type=\"button\" class=\"bw-reset\" "
            f"data-reset-for=\"{tid}\">Reset layout</button>")


TABLE_ENGINE_JS = """<script>
document.querySelectorAll('table.bw-grid').forEach(function(t){
  var tid = t.getAttribute('data-tid'); if (!tid) return;
  var ths = Array.prototype.slice.call(t.querySelectorAll(':scope > thead > tr > th'));
  var n = ths.length;
  var defs = JSON.parse(t.getAttribute('data-def') || '[]');
  var mins = JSON.parse(t.getAttribute('data-min') || '[]');
  var fixed = JSON.parse(t.getAttribute('data-fixed') || '[]');
  if (defs.length !== n) return;
  var cg = t.querySelector(':scope > colgroup'); if (!cg) return;
  var widths = defs.slice(), sort = null, lastDrag = 0;
  try {
    var raw = localStorage.getItem('bondwatch:v1:' + tid);
    if (raw) { var st = JSON.parse(raw);
      if (st && st.w && st.w.length === n) widths = st.w.map(function(w, i){ var v = parseFloat(w); return isNaN(v) ? defs[i] : Math.max(mins[i] || 40, v); });
      if (st && st.s) sort = st.s; }
  } catch (e) {}
  function apply(){ var sum = 0; for (var i = 0; i < n; i++){ cg.children[i].style.width = widths[i] + 'px'; sum += widths[i]; } t.style.width = sum + 'px'; }
  function save(){ try { localStorage.setItem('bondwatch:v1:' + tid, JSON.stringify({w: widths, s: sort})); } catch (e) {} }
  apply();
  var head = t.querySelector(':scope > thead');
  function boundary(ev){
    var best = -1, bestD = 9;
    for (var i = 0; i < n; i++){
      if (fixed.indexOf(i) >= 0) continue;
      var d = Math.abs(ev.clientX - ths[i].getBoundingClientRect().right);
      if (d < bestD) { bestD = d; best = i; }
    }
    return best;
  }
  function startDrag(i, ev, shift){
    var startX = ev.clientX, startW = widths[i], startN = (i + 1 < n) ? widths[i + 1] : 0;
    shift = shift && i + 1 < n;
    function move(e){
      var dx = e.clientX - startX;
      if (shift) { var w = Math.max(mins[i], Math.min(startW + startN - mins[i + 1], startW + dx)); widths[i] = w; widths[i + 1] = startW + startN - w; }
      else widths[i] = Math.max(mins[i], startW + dx);
      apply(); lastDrag = Date.now();
    }
    function up(){ document.removeEventListener('pointermove', move); document.removeEventListener('pointerup', up); document.removeEventListener('pointercancel', up); save(); }
    document.addEventListener('pointermove', move);
    document.addEventListener('pointerup', up);
    document.addEventListener('pointercancel', up);
  }
  function autoFit(i){
    var clone = t.cloneNode(true);
    clone.style.cssText = 'position:absolute;visibility:hidden;left:-9999px;top:0;width:auto;table-layout:auto;';
    var ccg = clone.querySelector('colgroup'); if (ccg) ccg.remove();
    document.body.appendChild(clone);
    var cths = clone.querySelectorAll(':scope > thead > tr > th');
    var w = cths[i] ? cths[i].offsetWidth : 0;
    clone.remove();
    if (w > 0) { widths[i] = Math.max(mins[i], w); apply(); save(); }
  }
  head.addEventListener('pointerdown', function(ev){
    var i = boundary(ev); if (i < 0) return;
    ev.preventDefault(); ev.stopPropagation();
    startDrag(i, ev, ev.shiftKey);
  });
  head.addEventListener('dblclick', function(ev){
    var i = boundary(ev); if (i < 0) return;
    ev.preventDefault();
    autoFit(i);
  });
  ths.forEach(function(th, i){
    if (fixed.indexOf(i) >= 0) return;
    var grip = document.createElement('span');
    grip.className = 'bw-grip';
    grip.setAttribute('aria-hidden', 'true');
    th.appendChild(grip);
    var lastTap = 0, downX = 0;
    grip.addEventListener('pointerdown', function(ev){
      ev.preventDefault(); ev.stopPropagation();
      downX = ev.clientX;
      startDrag(i, ev, false);
    });
    grip.addEventListener('pointerup', function(ev){
      if (Math.abs(ev.clientX - downX) > 6) { lastTap = 0; return; }
      var now = Date.now();
      if (now - lastTap < 300) { lastTap = 0; autoFit(i); }
      else lastTap = now;
    });
    grip.addEventListener('click', function(ev){ ev.stopPropagation(); });
  });
  function sortRows(i, asc){
    var rows = Array.prototype.slice.call(t.querySelectorAll(':scope > tbody > tr'));
    rows.sort(function(a, b){
      var x = a.children[i], y = b.children[i];
      var xv = x && x.hasAttribute('data-v') ? x.getAttribute('data-v') : (x ? x.textContent.trim() : '');
      var yv = y && y.hasAttribute('data-v') ? y.getAttribute('data-v') : (y ? y.textContent.trim() : '');
      var xn = parseFloat(xv), yn = parseFloat(yv);
      var c = (!isNaN(xn) && !isNaN(yn)) ? xn - yn : String(xv).localeCompare(String(yv));
      return asc ? c : -c;
    });
    var tb = t.querySelector(':scope > tbody');
    rows.forEach(function(r){ tb.appendChild(r); });
    ths.forEach(function(h){ h.classList.remove('sasc', 'sdesc'); });
    ths[i].classList.add(asc ? 'sasc' : 'sdesc');
  }
  if (t.hasAttribute('data-sort')) {
    ths.forEach(function(th, i){
      th.addEventListener('click', function(){
        if (Date.now() - lastDrag < 250) return;
        var asc = !th.classList.contains('sasc');
        sort = {i: i, asc: asc};
        sortRows(i, asc); save();
      });
    });
    if (sort && sort.i < n) sortRows(sort.i, sort.asc);
  }
  ths.forEach(function(th, i){
    if (fixed.indexOf(i) >= 0) return;
    th.setAttribute('tabindex', '0');
    th.addEventListener('keydown', function(ev){
      if (!ev.altKey) return;
      if (ev.key === 'ArrowRight') { widths[i] += 8; apply(); save(); ev.preventDefault(); }
      if (ev.key === 'ArrowLeft') { widths[i] = Math.max(mins[i], widths[i] - 8); apply(); save(); ev.preventDefault(); }
    });
  });
  var rb = document.querySelector('[data-reset-for="' + tid + '"]');
  if (rb) rb.addEventListener('click', function(){
    try { localStorage.removeItem('bondwatch:v1:' + tid); } catch (e) {}
    widths = defs.slice(); sort = null; apply();
    ths.forEach(function(h){ h.classList.remove('sasc', 'sdesc'); });
  });
});
</script>
"""


def _sparkline(hist, width=150, height=26):
    pts = [(h["date"], float(h["price"])) for h in hist]
    if len(pts) < 2:
        return ""
    vals = [v for _, v in pts]
    lo, hi = min(vals), max(vals)
    pad = max((hi - lo) * 0.15, 0.5)
    lo, hi = lo - pad, hi + pad
    step = width / (len(pts) - 1)
    coords = " ".join(
        f"{i * step:.1f},{height - 3 - (v - lo) / (hi - lo) * (height - 6):.1f}"
        for i, (_, v) in enumerate(pts))
    color = "#b42318" if vals[-1] < vals[0] else "#1a7f37"
    return (f"<svg class=\"trace-spark\" width=\"{width}\" height=\"{height}\" "
            f"viewBox=\"0 0 {width} {height}\" aria-hidden=\"true\">"
            f"<polyline points=\"{coords}\" fill=\"none\" stroke=\"{color}\" "
            f"stroke-width=\"1.5\"/></svg>")


def _trace_section():
    tp = _trace_prints()
    if not tp.get("prints"):
        return "", ""
    tape_latest = _tape_latest(tp)

    def sort_key(p):
        if p.get("last_trade_price") is None:
            return 999.0
        y = _ytm(p["last_trade_price"], p.get("coupon_pct"),
                 p.get("maturity"), p["last_trade_date"])
        return -(y if y is not None else -999.0)

    _all_prints = sorted(tp["prints"], key=sort_key)
    prints = [p for p in _all_prints if p.get("watch") != "benchmark"]
    bench_prints = [p for p in _all_prints
                    if p.get("watch") == "benchmark"]
    curve = _treasury_curve()
    _reg_by_cusip = {}
    _reg_path = os.path.join(DATA, "bonds.json")
    if os.path.exists(_reg_path):
        _reg_by_cusip = {b["cusip"]: b
                         for b in json.load(open(_reg_path))["bonds"]}
    rows = []
    for p in prints:
        trade = p["last_trade_price"]
        mark = p.get("latest_fund_mark")
        if trade is None:
            _c0 = p.get("coupon_pct")
            _cs0 = (f"{_c0:.3f}".rstrip("0").rstrip(".") + "%"
                    if _c0 else "n/a")
            _m0 = _fmt_date(p.get("maturity")) or "n/a"
            _mk0 = (f"<td class=\"num\" data-v=\"{mark:.2f}\">"
                    f"{mark:.2f}"
                    + (f"<span class=\"cell-sub\">Period ended "
                       f"{_fmt_date(p['mark_period'])}</span>"
                       if p.get("mark_period") else "")
                    + "</td>" if mark is not None
                    else "<td class=\"muted\">n/a</td>")
            rows.append(
                "<tr>"
                f"<td data-v=\"{p['issuer']} {p['security']}\">"
                f"<a class=\"bond-link\" "
                f"href=\"/leverage/bond/{p['cusip'].lower()}/\">"
                f"<span class=\"bond-name\">{p['issuer']}</span>"
                f"<span class=\"bond-sub\">{p['security']}</span></a></td>"
                f"{_issued_cell(p['cusip'])}"
                "<td class=\"muted\">n/a</td>"
                "<td class=\"muted\">n/a</td>"
                "<td class=\"muted\">n/a</td>"
                "<td class=\"muted\">n/a</td>"
                f"{_mk0}"
                "<td class=\"muted\">n/a</td>"
                "<td class=\"muted\" data-v=\"9999-99-99\">"
                "no trades in the stored record</td>"
                f"<td class=\"num\" data-v=\"{_c0 or -999}\">{_cs0}</td>"
                f"<td class=\"muted\" data-v=\"{p.get('maturity') or ''}\">"
                f"{_m0}</td>"
                f"{_rating_cell(p['cusip'], _reg_by_cusip)}"
                f"<td class=\"muted\">{p['cusip']}</td>"
                f"<td>{_sparkline2(p['cusip'])}</td>"
                "</tr>")
            continue
        y = _ytm(trade, p.get("coupon_pct"), p.get("maturity"),
                 p["last_trade_date"])
        _rb = _reg_by_cusip.get(p["cusip"], {})
        _sched = _rb.get("call_schedule") or []
        if y is not None and _sched and "Convertible" not in (_rb.get("call_notes") or ""):
            for _cs in _sched:
                if _cs["date"] > p["last_trade_date"]:
                    _yc = _ytm(trade, p.get("coupon_pct"), _cs["date"],
                               p["last_trade_date"],
                               redemption=_cs["price_pct"])
                    if _yc is not None:
                        y = min(y, _yc)
        coup = p.get("coupon_pct")
        coup_s = f"{coup:.3f}".rstrip("0").rstrip(".") + "%" if coup else "n/a"
        mat = p.get("maturity") or ""
        if mark is not None:
            gap = trade - mark
            gcls = "down" if gap < 0 else "up"
            mark_s = f"{mark:.2f}"
            if p.get("mark_period"):
                mark_s += (f"<span class=\"cell-sub\">Period ended "
                           f"{_fmt_date(p['mark_period'])}</span>")
            gap_cell = (f"<td class=\"num\" data-v=\"{gap:.2f}\">"
                        f"<span class=\"{gcls}\">{gap:+.2f}</span></td>")
            mark_v = f"{mark:.2f}"
        else:
            mark_s, gap_cell, mark_v = "n/a", "<td class=\"muted\">n/a</td>", "-999"
        y_s = f"{y:.2f}%" if y is not None else "n/a"
        y_v = f"{y:.2f}" if y is not None else "-999"
        # Spread to Treasury (bp) and modified duration replace the
        # yield-less-coupon column (removed 2026-10-14 after the audit
        # against bank/BIS practice: not a recognised metric).
        from datetime import date as _date
        td_d = _date.fromisoformat(p["last_trade_date"])
        stale = (_date.fromisoformat(tape_latest) - td_d).days > 30
        if y is not None and mat and curve:
            yrs = (_date.fromisoformat(mat) - td_d).days / 365.25
            spd = round((y - _tsy(curve, yrs)) * 100)
            spd_cell = (f"<td class=\"num\" data-v=\"{spd}\">"
                        f"{spd:+,} bp</td>")
        else:
            spd_cell = "<td class=\"muted\" data-v=\"-999\">n/a</td>"
        dur = _mod_duration(trade, coup, p.get("maturity"),
                            p["last_trade_date"], y)
        if dur is not None:
            dur_cell = (f"<td class=\"num\" data-v=\"{dur:.2f}\">"
                        f"{dur:.2f}</td>")
        else:
            dur_cell = "<td class=\"muted\" data-v=\"-999\">n/a</td>"
        stale_tag = ' <span class="stale-tag">stale</span>' if stale else ""
        price_cls = ("num trace-price-cell" + (" low" if trade < 90 else "")
                     + (" stale" if stale else ""))
        spark = _sparkline2(p["cusip"])
        _age_d = (_date.fromisoformat(tape_latest) - td_d).days
        _age = ("today" if _age_d == 0 else
                "1d ago" if _age_d == 1 else f"{_age_d}d ago")
        _twin = _reg_by_cusip.get(p["cusip"], {}).get("twin_of")
        _twin_s = " (144A line)" if _twin else ""
        _label = f"{p['issuer']} {p['security']}"
        _row_html = (
            "<tr>"
            f"<td data-v=\"{_label}\"><a class=\"bond-link\" "
            f"href=\"/leverage/bond/{p['cusip'].lower()}/\">"
            f"<span class=\"bond-name\">{p['issuer']}</span>"
            f"<span class=\"bond-sub\">{p['security']}{_twin_s}</span></a></td>"
            f"{_issued_cell(p['cusip'])}"
            f"<td class=\"{price_cls}\" data-v=\"{trade:.2f}\">{trade:.2f}</td>"
            f"<td class=\"num\" data-v=\"{y_v}\">{y_s}</td>"
            f"{spd_cell}"
            f"{gap_cell}"
            f"<td class=\"num\" data-v=\"{mark_v}\">{mark_s}</td>"
            f"{dur_cell}"
            f"<td class=\"muted\" data-v=\"{p['last_trade_date']}\">{_fmt_date(p['last_trade_date'])}<span class=\"cell-sub\">{_age}{stale_tag}</span>{('<span class=\"cell-sub\">' + str(p['trades_seen']) + ' trades</span>') if p.get('trades_seen') else ''}</td>"
            f"<td class=\"num\" data-v=\"{coup if coup else -999}\">{coup_s}</td>"
            f"<td class=\"muted\" data-v=\"{mat}\">{_fmt_date(mat) if mat else 'n/a'}</td>"
            f"{_rating_cell(p['cusip'], _reg_by_cusip)}"
            f"<td class=\"muted\">{p['cusip']}</td>"
            f"<td>{spark}</td>"
            "</tr>")
        rows.append(_row_html)
    trace_html = (
        "<h2 id=\"trace\">Latest TRACE prints</h2>\n"
        f"<p class=\"data-vintage\">{len(rows)} bonds. Actual secondary-market "
        "trades reported to FINRA TRACE, collected through FINRA's public "
        "bond lookup every 15 minutes in market hours. A bond updates only "
        "when it trades; an untraded bond keeps its last print. Prices "
        "are percent of par: 100 is face value, repaid at maturity. Gap: "
        "last print less the latest fund mark, in points of par. Issued: "
        "the note's original amount issued, in millions of dollars, "
        "from the issuer's pricing filing where one is on record; "
        "blank where no held source states it. Yield: "
        "yield to worst where a call schedule is on record, else yield to "
        "maturity. Spread: that yield less the interpolated Treasury yield "
        "at the same maturity, in basis points. Duration: modified "
        "duration in years. Ratings name their agency: S&amp;P as "
        "recorded by FINRA, with Moody's shown beneath it where both "
        "exist. Stale: no trade in over 30 days before the tape's "
        "latest date. Trend: fund marks "
        "(squares) and trades (dots), true time axis, 12 months, each row "
        "scaled to its own range. Select a bond name for its full history. "
        "Drag a heading boundary to resize; Shift-drag trades width with "
        "the neighbour; double-click fits the column."
        + _reset_btn("trace") + "</p>\n"
        + _grid("trace", TRACE_COLS, "\n".join(rows), cls="trace-table"))
    bench_html = ""
    if bench_prints:
        brows = []
        for p in bench_prints:
            trade = p["last_trade_price"]
            _c = p.get("coupon_pct")
            _cs = (f"{_c:.3f}".rstrip("0").rstrip(".") + "%"
                   if _c else "n/a")
            _mt = p.get("maturity") or ""
            _lab = f"{p['issuer']} {p['security']}"
            _bond_cell = (
                f"<td data-v=\"{_lab}\"><a class=\"bond-link\" "
                f"href=\"/leverage/bond/{p['cusip'].lower()}/\">"
                f"<span class=\"bond-name\">{p['issuer']}</span>"
                f"<span class=\"bond-sub\">{p['security']}</span></a></td>")
            if trade is None:
                brows.append(
                    "<tr>" + _bond_cell
                    + _issued_cell(p['cusip'])
                    + "<td class=\"muted\">n/a</td>" * 4
                    + "<td class=\"muted\" data-v=\"9999-99-99\">"
                      "no trades in the stored record</td>"
                    + f"<td class=\"num\" data-v=\"{_c or -999}\">{_cs}</td>"
                    + f"<td class=\"muted\" data-v=\"{_mt}\">"
                      f"{_fmt_date(_mt) if _mt else 'n/a'}</td>"
                    + _rating_cell(p['cusip'], _reg_by_cusip)
                    + f"<td class=\"muted\">{p['cusip']}</td>"
                    + f"<td>{_sparkline2(p['cusip'])}</td></tr>")
                continue
            y = _ytm(trade, _c, p.get("maturity"), p["last_trade_date"])
            y_s = f"{y:.2f}%" if y is not None else "n/a"
            y_v = f"{y:.2f}" if y is not None else "-999"
            from datetime import date as _d2
            td2 = _d2.fromisoformat(p["last_trade_date"])
            stale2 = (_d2.fromisoformat(tape_latest) - td2).days > 30
            if y is not None and _mt and curve:
                yrs2 = (_d2.fromisoformat(_mt) - td2).days / 365.25
                spd2 = round((y - _tsy(curve, yrs2)) * 100)
                spd_cell2 = (f"<td class=\"num\" data-v=\"{spd2}\">"
                             f"{spd2:+,} bp</td>")
            else:
                spd_cell2 = "<td class=\"muted\" data-v=\"-999\">n/a</td>"
            dur2 = _mod_duration(trade, _c, p.get("maturity"),
                                 p["last_trade_date"], y)
            dur_cell2 = (f"<td class=\"num\" data-v=\"{dur2:.2f}\">"
                         f"{dur2:.2f}</td>" if dur2 is not None
                         else "<td class=\"muted\" data-v=\"-999\">n/a</td>")
            _age2 = (_d2.fromisoformat(tape_latest) - td2).days
            _age_s2 = ("today" if _age2 == 0 else
                       "1d ago" if _age2 == 1 else f"{_age2}d ago")
            _stale2 = (' <span class="stale-tag">stale</span>'
                       if stale2 else "")
            _pcls2 = ("num trace-price-cell"
                      + (" low" if trade < 90 else "")
                      + (" stale" if stale2 else ""))
            brows.append(
                "<tr>" + _bond_cell
                + _issued_cell(p['cusip'])
                + f"<td class=\"{_pcls2}\" data-v=\"{trade:.2f}\">"
                  f"{trade:.2f}</td>"
                + f"<td class=\"num\" data-v=\"{y_v}\">{y_s}</td>"
                + spd_cell2 + dur_cell2
                + f"<td class=\"muted\" data-v=\"{p['last_trade_date']}\">"
                  f"{_fmt_date(p['last_trade_date'])}"
                  f"<span class=\"cell-sub\">{_age_s2}{_stale2}</span>"
                + (f"<span class=\"cell-sub\">{p['trades_seen']} trades"
                   f"</span>"
                   if p.get("trades_seen") else "")
                + "</td>"
                + f"<td class=\"num\" data-v=\"{_c or -999}\">{_cs}</td>"
                + f"<td class=\"muted\" data-v=\"{_mt}\">"
                  f"{_fmt_date(_mt) if _mt else 'n/a'}</td>"
                + _rating_cell(p['cusip'], _reg_by_cusip)
                + f"<td class=\"muted\">{p['cusip']}</td>"
                + f"<td>{_sparkline2(p['cusip'])}</td></tr>")
        _ntraded = sum(1 for p in bench_prints
                       if p.get("last_trade_price") is not None)
        _bench_names = ", ".join(
            i.get("group") or _issuer_display(i.get("finra_name"))
            for i in _watched_issuers()
            if i.get("tier") == "benchmark")
        bench_html = (
            "<h2 id=\"benchmark\">Benchmark TRACE prints</h2>\n"
            f"<p class=\"data-vintage\">{len(brows)} bonds: the "
            f"benchmark universe ({_bench_names}), "
            "collected hourly in market hours through the same FINRA "
            f"lookup. {_ntraded} have trades in the stored record; "
            "the rest have not traded since collection began and show "
            "no price. These bonds are outside the fund-holdings "
            "sample, so no fund mark or gap is shown. Select a bond "
            "name for its page."
            + _reset_btn("bench") + "</p>\n"
            + _grid("bench", BENCH_COLS, "\n".join(brows),
                    cls="trace-table"))
    trace_html = trace_html + bench_html
    breadth_html = ""

    fa_path = os.path.join(DATA, "finra_aggregates.json")
    if os.path.exists(fa_path):
        fa = json.load(open(fa_path))
        ds = fa["datasets"]

        def series(name, cat):
            out = {}
            for r in ds.get(name, []):
                if str(r.get("productCategory")) == cat:
                    out[r["tradeReportDate"]] = r
            return out

        corp = series("corporateMarketBreadth", "all securities")
        a144 = series("corporate144AMarketBreadth", "all securities")
        hy = series("corporateMarketBreadth", "high yield")
        conv = series("corporateMarketBreadth", "convertibles")
        dates = sorted(set(corp) | set(a144), reverse=True)
        if dates:
            d0 = dates[0]

            def card(label, r):
                if not r:
                    return ""
                adv, dec = r["advances"], r["declines"]
                tot = adv + dec
                share = f"{adv / tot * 100:.0f}% advancing" if tot else ""
                return (f"<div class=\"bw-sum-item\"><dt>{label}</dt>"
                        f"<dd>{adv:,} / {dec:,} <span class=\"muted\">{share}</span></dd></div>\n")

            breadth_html += (
                "<h2 id=\"breadth\">Market breadth</h2>\n"
                "<p class=\"data-vintage\">Advances against declines across the "
                "whole US corporate bond market, from FINRA's aggregate datasets "
                "(the API layer; it names no individual bond). Data is T+1."
                + _reset_btn("breadth") + "</p>\n"
                "<dl class=\"bw-summary\">\n"
                + card(f"Corporate, {d0}", corp.get(d0))
                + card(f"Rule 144A, {d0}", a144.get(d0))
                + card(f"High yield, {d0}", hy.get(d0))
                + card(f"Convertibles, {d0}", conv.get(d0))
                + "</dl>\n")
            trows = []
            for dt in dates[:5]:
                c, a = corp.get(dt), a144.get(dt)
                h = hy.get(dt)
                trows.append(
                    "<tr>"
                    f"<td class=\"muted\">{dt}</td>"
                    f"<td class=\"num\">{c['advances']:,}</td><td class=\"num\">{c['declines']:,}</td>"
                    f"<td class=\"num\">{a['advances']:,}</td><td class=\"num\">{a['declines']:,}</td>"
                    f"<td class=\"num\">{h['advances']:,}</td><td class=\"num\">{h['declines']:,}</td>"
                    "</tr>")
            breadth_html += _grid("breadth", BREADTH_COLS,
                                  "\n".join(trows), sortable=False)
    trace_html += (f"<p class=\"data-vintage\">Prints as of "
                   f"{_fmt_date(tape_latest)}. "
                   f"Source: {tp['source']}.</p>\n")
    return trace_html, breadth_html


def _fmt_vol(v):
    if v is None:
        return "\u2014"
    if v >= 1e9:
        return f"${v / 1e9:.2f}B"
    if v >= 1e6:
        return f"${v / 1e6:.1f}M"
    if v >= 1e3:
        return f"${v / 1e3:.0f}K"
    return f"${v:,.0f}"


_FLOW = None


def _flow_data():
    global _FLOW
    if _FLOW is None:
        p = os.path.join(DATA, "bond_flow.json")
        _FLOW = json.load(open(p)) if os.path.exists(p) else {}
    return _FLOW


def _flow_range(a, b):
    import datetime as _dt
    if not a:
        return ""
    if a == b:
        return _fmt_date(a)
    da = _dt.date.fromisoformat(a)
    db = _dt.date.fromisoformat(b)
    if da.year == db.year and da.month == db.month:
        return f"{da.day}\u2013{db.day} {db.strftime('%b %Y')}"
    if da.year == db.year:
        return (f"{da.day} {da.strftime('%b')} \u2013 "
                f"{db.day} {db.strftime('%b %Y')}")
    return f"{_fmt_date(a)} \u2013 {_fmt_date(b)}"


FLOW_JS = """<script>
document.querySelectorAll('.flow-panel').forEach(function(p){
  var btns = p.querySelectorAll('.flow-toggle button');
  btns.forEach(function(btn){
    btn.addEventListener('click', function(){
      btns.forEach(function(x){ x.setAttribute('aria-pressed', 'false'); });
      btn.setAttribute('aria-pressed', 'true');
      p.querySelectorAll('.flow-win').forEach(function(w){
        w.hidden = w.getAttribute('data-w') !== btn.getAttribute('data-w');
      });
    });
  });
});
</script>
"""


def _flow_day_table(w):
    rows = []
    tot = [0, 0, 0, 0, 0]
    for d, n, b, s, bv, sv in w["days"]:
        rows.append(
            f"<tr><td>{_fmt_date(d)}</td>"
            f"<td class=\"num\">{n:,}</td><td class=\"num\">{b:,}</td>"
            f"<td class=\"num\">{s:,}</td>"
            f"<td class=\"num\">{_fmt_vol(bv)}</td>"
            f"<td class=\"num\">{_fmt_vol(sv)}</td></tr>")
        tot[0] += n
        tot[1] += b
        tot[2] += s
        tot[3] += bv
        tot[4] += sv
    rows.append(
        f"<tr class=\"flow-total\"><td>Total</td>"
        f"<td class=\"num\">{tot[0]:,}</td>"
        f"<td class=\"num\">{tot[1]:,}</td>"
        f"<td class=\"num\">{tot[2]:,}</td>"
        f"<td class=\"num\">{_fmt_vol(tot[3])}</td>"
        f"<td class=\"num\">{_fmt_vol(tot[4])}</td></tr>")
    head = "Week of" if w.get("weekly") else "Date"
    return ('<div class="market-table-scroll">'
            '<table class="market-table"><thead><tr>'
            f"<th>{head}</th><th class=\"num\">Trades</th>"
            "<th class=\"num\">Dealer bought</th>"
            "<th class=\"num\">Dealer sold</th>"
            "<th class=\"num\">Min. buy volume</th>"
            "<th class=\"num\">Min. sell volume</th></tr></thead>"
            "<tbody>" + "".join(rows) + "</tbody></table></div>")


def _flow_window(wname, w, fam=False):
    label = {
        "1d": "Latest trade date",
        "5d": ("Last ten trade dates for this "
               + ("issuer" if fam else "bond") if w.get("ext")
               else "Last five trade dates"),
        "1w": "Last seven days",
        "1m": "Last 30 days",
        "1y": "Last 365 days",
    }[wname]
    rng = w.get("range") or [None, None]
    out = [f'<p class="flow-win-label">{label} - '
           f'{_flow_range(rng[0], rng[1])}</p>']
    if w.get("none"):
        d, pr = w["last"]
        out.append(f'<p class="flow-line">No reported trades since '
                   f'{_fmt_date(d)} (last print {pr:.2f}).</p>')
        return "".join(out)
    n, b, s = w["n"], w["b"], w["s"]
    if n <= 4:
        ld, lt, lp, lv, ls = w["last"]
        vol = None
        if lv:
            if "MM" in str(lv):
                vol = str(lv)
            else:
                try:
                    vol = _fmt_vol(float(lv))
                except (TypeError, ValueError):
                    vol = str(lv)
        side = {"B": "dealer bought", "S": "dealer sold"}.get(ls)
        det = f"Most recent: {_fmt_date(ld)}"
        if lt:
            det += f", {lt} ET"
        if vol:
            det += f", {vol}"
        det += f" at {lp:.2f}"
        if side:
            det += f" ({side})"
        out.append(f'<p class="flow-line">{n} reported '
                   f'trade{"s" if n != 1 else ""} in this window. '
                   f'{det}.</p>')
        if w["days"]:
            out.append(_flow_day_table(w))
        return "".join(out)
    denom = b + s

    def share(x):
        return f"{100.0 * x / denom:.0f}%" if denom else "\u2014"

    items = [("Reported trades", f"{n:,}", None)]
    if n >= 20:
        items.append(("Dealer bought", f"{b:,}",
                      f"Share {share(b)}"))
        items.append(("Dealer sold", f"{s:,}",
                      f"Share {share(s)}"))
    else:
        items.append(("Dealer bought", f"{b:,}", None))
        items.append(("Dealer sold", f"{s:,}", None))
    out.append('<dl class="bw-summary">' + "".join(
        f'<div class="bw-sum-item"><dt>{k}</dt><dd>{v}</dd>'
        + (f'<dd class="bw-sum-sub">{sub}</dd>' if sub else "")
        + "</div>"
        for k, v, sub in items) + "</dl>")
    if 10 <= n < 20:
        out.append('<p class="flow-note">Shares not shown \u2014 fewer '
                   'than 20 reported trades.</p>')
    if w["ns"]:
        out.append(f'<p class="flow-note">{w["ns"]} reported '
                   f'trade{"s" if w["ns"] != 1 else ""} in this window '
                   f'carry no reported side.</p>')
    if n >= 10 and denom:
        bp = 100.0 * b / denom
        out.append(
            '<div class="flow-bar">'
            f'<div class="flow-seg b" style="width:{bp:.1f}%"></div>'
            f'<div class="flow-seg s" style="width:{100 - bp:.1f}%">'
            '</div></div>'
            '<div class="flow-bar-labels">'
            f'<span>Dealer bought {b:,}</span>'
            f'<span>Dealer sold {s:,}</span></div>')
    out.append(
        f'<p class="flow-vol">Minimum reported volume \u2014 dealer '
        f'bought {_fmt_vol(w["bv"])}; dealer sold '
        f'{_fmt_vol(w["sv"])}</p>')
    out.append(_flow_day_table(w))
    if n >= 10:
        bands = w["bands"]
        sized = sum(bands)
        if sized:
            labels = ["Under $100k (retail-sized)", "$100k\u2013$1MM",
                      "$1MM and over (institutional-sized)"]
            if w["capped"]:
                cap = w["cap"] or "1MM+"
                labels[2] += (
                    f' \u2014 includes {w["capped"]:,} print'
                    f'{"s" if w["capped"] != 1 else ""} at the '
                    f'${cap[:-1]} cap (reported as {cap})')
            srows = "".join(
                f'<tr><td>{lab}</td><td class="num">{c:,}</td>'
                f'<td class="num">{100.0 * c / sized:.0f}%</td></tr>'
                for lab, c in zip(labels, bands))
            out.append('<div class="market-table-scroll">'
                       '<table class="market-table flow-size">'
                       '<thead><tr><th>Reported size</th>'
                       '<th class="num">Prints</th>'
                       '<th class="num">Share</th></tr></thead>'
                       '<tbody>' + srows + '</tbody></table></div>')
            if w["med"] is not None:
                med = _fmt_vol(w["med"])
                if w["cap"] and w["med"] >= (
                        5000000 if w["cap"] == "5MM+" else 1000000):
                    med += " (at the cap)"
                out.append(f'<p class="flow-vol">Median reported '
                           f'print: {med}</p>')
        sp = w.get("split")
        if sp:
            def sshare(x):
                return (f'<span class="flow-share">Share '
                        f'{100.0 * x / sp["base"]:.0f}%</span>'
                        if sp["base"] >= 20 else '')

            segs = [
                f'Customers bought {sp["cb"]:,}{sshare(sp["cb"])}',
                f'Customers sold {sp["cs"]:,}{sshare(sp["cs"])}',
                f'Inter-dealer {sp["id"]:,}{sshare(sp["id"])}',
            ]
            if sp["oc"]:
                segs.append(f'Affiliate and ATS {sp["oc"]:,}')
            out.append('<p class="flow-split">'
                       '<span class="flow-split-h">Customer split '
                       '(corporate prints)</span><br>'
                       + '<br>'.join(segs) + '</p>')
    return "".join(out)


_FLOW_WINS = [("1d", "1 day"), ("5d", "5 days"), ("1w", "1 week"),
              ("1m", "1 month"), ("1y", "1 year")]


def _flow_panel(ent, fam=False, all_abs=False):
    if not ent:
        return ""
    wins = ent.get("windows") or {}
    if not wins:
        return ""
    cap = ent.get("cap")
    if cap == "5MM+":
        cap_txt = ("TRACE caps reported size at $5MM+ for "
                   "investment-grade bonds; capped trades are counted "
                   "at the cap, so all volumes are minimums.")
    elif cap == "1MM+":
        cap_txt = ("TRACE caps reported size at $1MM+ for "
                   "non-investment-grade bonds; capped trades are "
                   "counted at the cap, so all volumes are minimums.")
    else:
        cap_txt = ("TRACE caps reported size at $1MM+ "
                   "(non-investment-grade) or $5MM+ (investment-grade); "
                   "capped trades are counted at the cap, so all "
                   "volumes are minimums.")
    out = ['<div class="flow-panel">',
           '<h2>Reported trading activity</h2>']
    if fam:
        out.append(f'<p class="flow-scope">Across '
                   f'{ent.get("n_bonds")} bonds</p>')
    default_w = "5d" if "5d" in wins else next(iter(wins))
    btns, divs = [], []
    for wname, wlab in _FLOW_WINS:
        w = wins.get(wname)
        if w is None:
            continue
        act = (' aria-pressed="true"' if wname == default_w
               else ' aria-pressed="false"')
        btns.append(f'<button type="button" data-w="{wname}"{act}>'
                    f'{wlab}</button>')
        hid = '' if wname == default_w else ' hidden'
        divs.append(f'<div class="flow-win" data-w="{wname}"{hid}>'
                    + _flow_window(wname, w, fam) + '</div>')
    out.append('<p class="chart-toggle flow-toggle">'
               + " ".join(btns) + '</p>')
    out += divs
    note = ('Sides are the reporting dealer&rsquo;s, as FINRA '
            'disseminates them: &ldquo;dealer bought&rdquo; means the '
            'dealer reporting the trade bought; for a trade with a '
            'customer, a dealer sale is a customer purchase. FINRA '
            'disseminates inter-dealer trades on the sell side only, '
            'so the split is not a measure of investor buying versus '
            'selling. ' + cap_txt + ' Counts reflect the tape&rsquo;s '
            'current state: cancelled trades are excluded, and '
            'corrected trades are counted once, at their corrected '
            'values.')
    if fam and ent.get("abs_mixed"):
        note += (' The customer split covers corporate bonds only; '
                 'asset-backed prints count in the totals, as FINRA '
                 'does not disseminate contra-party type for them.')
    if all_abs or (fam and ent.get("all_abs")):
        note += (' No customer split is shown: FINRA does not '
                 'disseminate contra-party type for asset-backed '
                 'securities.')
    out.append(f'<p class="flow-note">{note}</p>')
    out.append('</div>')
    return "\n".join(out) + "\n" + FLOW_JS


def bond_watch_page():
    d = json.load(open(os.path.join(DATA, "bond_watch.json")))
    rows = d["rows"]
    full = [r for r in rows if r["quality"] == "full"]
    thin = [r for r in rows if r["quality"] == "thin"]
    movers = sorted([r for r in full if r["change_pts"] is not None],
                    key=lambda r: r["change_pts"])
    worst = movers[0] if movers else None
    below90 = [r for r in full if r["latest_price"] < 90]
    _reg_n = len(rows)
    _reg_path2 = os.path.join(DATA, "bonds.json")
    if os.path.exists(_reg_path2):
        _reg_n = len(json.load(open(_reg_path2))["bonds"])
    _sum_items = [("Bonds tracked", f"{_reg_n}", ["in the registry"])]
    _tp = _trace_prints()
    if _tp.get("prints"):
        _pr = _tp["prints"]
        _below = sum(1 for p in _pr
                     if p.get("last_trade_price") is not None
                     and p["last_trade_price"] < 90)
        _withmark = [p for p in _pr
                     if p.get("latest_fund_mark") is not None
                     and p.get("last_trade_price") is not None]
        _gaps = sorted(p["last_trade_price"] - p["latest_fund_mark"]
                       for p in _withmark)
        _med = _gaps[len(_gaps) // 2] if _gaps else 0.0
        _traded7 = sum(1 for p in _pr if (p.get("trades_seen") or 0) > 0)
        _npriced = sum(1 for p in _pr
                       if p.get("last_trade_price") is not None)
        _sum_items += [("Traded in the last 7 days",
                        f"{_traded7} of {len(_pr)}",
                        ["with stored prints"]),
                       ("Median gap to fund mark", f"{_med:+.1f} pts",
                        [f"across {len(_withmark)} bonds with a print "
                         f"and a mark"]),
                       ("Trading below 90", f"{_below} of {_npriced}",
                        ["priced in the window"])]
    _sum_items.append(("Fund marks to", _fmt_date(d['marks_as_of']), []))
    stats = ('<dl class="bw-summary">\n' + "".join(
        f"<div class=\"bw-sum-item\"><dt>{k}</dt><dd>{v}</dd>"
        + "".join(f"<dd class=\"bw-sum-sub\">{s}</dd>" for s in subs)
        + "</div>\n"
        for k, v, subs in _sum_items) + "</dl>\n")
    trace_stats_html = ""
    flag_rows = [f for f in d["flags"] if f.startswith(("MOVE", "LOW"))]
    flags_html = ""
    if flag_rows:
        import re as _re
        _pat = _re.compile(r"^(MOVE|LOW) (\S+) \((.+?)\): (.*)$")
        _trs = []
        for f in flag_rows:
            m = _pat.match(f)
            if m:
                rule, cusip, issuer, detail = m.groups()
                label = ("Mark moved 5 pts or more between reported "
                         "periods" if rule == "MOVE"
                         else "Latest mark below 90")
                _trs.append(
                    f"<tr><td>{issuer.title()}</td><td class=\"muted\">{cusip}</td>"
                    f"{_issued_cell(cusip)}"
                    f"<td>{label}</td><td class=\"muted\">{detail}</td></tr>")
            else:
                _trs.append(f"<tr><td colspan=\"5\">{f}</td></tr>")
        flags_html = ("<h2 id=\"flags\">Flags on fund marks</h2>\n"
                      "<p class=\"data-vintage\">A flag is a mechanical rule, not a judgement: "
                      "a mark that moved 5 points or more between the two most recent reported "
                      "periods, or a latest mark below 90. Flags describe the marks "
                      "series, not trades; they are not trade signals."
                      + _reset_btn("flags") + "</p>\n"
                      + _grid("flags", FLAGS_COLS, "\n".join(_trs),
                              sortable=False))
    full_sorted = sorted(full, key=lambda r: ((r.get("issuer") or ""), r["cusip"]))
    thin_sorted = sorted(thin, key=lambda r: ((r.get("issuer") or ""), r["cusip"]))
    _trace_html, _breadth_html = _trace_section()
    body = frontmatter(
        "Bond Price Watch",
        "Fund-reported prices for the bonds that finance the AI infrastructure buildout.",
        f"Fund marks to {_fmt_date(d['marks_as_of'])}",
        aliases=["/macro/bond-watch/"],
    )
    _anchor = ("<nav class=\"bw-anchor\">"
               "<a href=\"#breadth\">Market breadth</a> / "
               "<a href=\"#trace\">TRACE prints</a> / "
               "<a href=\"#benchmark\">Benchmark</a> / "
               "<a href=\"#flags\">Flags</a> / "
               "<a href=\"#marks\">Fund marks</a> / "
               "<a href=\"#method\">Method</a></nav>\n")
    body += (
        stats + _anchor + _breadth_html + _trace_html + flags_html
        + "<h2 id=\"marks\">Latest marks</h2>\n"
        f"<p class=\"data-vintage\">{len(full_sorted)} bonds with full-quality "
        f"marks, of {_reg_n} bonds in the registry; "
        f"{len(full_sorted) + len(thin_sorted)} bonds have any fund mark, and "
        "the rest have no fund mark to list. Prices are per 100 of principal. Change is against the prior "
        "reported period. Recent marks run oldest to newest, up to four "
        "periods. Funds is the number of fund positions in the latest period. "
        "Select a bond name for its full history."
        + _reset_btn("marks-full") + "</p>\n"
        + _grid("marks-full", MARKS_COLS,
                "\n".join(_bond_row(r) for r in full_sorted))
    )
    if thin_sorted:
        body += (
            "<h2>Thin marks</h2>\n"
            "<p class=\"data-vintage\">Fewer than three fund positions, or under $5 million of "
            "reported principal. One holder's number; shown for completeness, never flagged."
            + _reset_btn("marks-thin") + "</p>\n"
            + _grid("marks-thin", MARKS_COLS,
                    "\n".join(_bond_row(r, thin=True) for r in thin_sorted))
        )
    body += (
        f"<p class=\"data-vintage\" id=\"method\">Source: {d['source']}. {d['method']} "
        f"{d.get('ytm_method', '')} "
        "Securities whose reported units make the implied price unreliable are excluded. "
        "Marks are compiled by Kilambi Research from the SEC bulk data; the watch covers the "
        "bond inventory assembled for working paper KR-WP-2026-27.</p>\n"
    )
    body += TABLE_ENGINE_JS
    return body

def _ytw(price, coup, mat, settle, reg):
    """Yield to worst: yield to maturity, or to a scheduled call
    when the call gives the lower yield. Conditional convertible
    redemption is not treated as a certain call."""
    y = _ytm(price, coup, mat, settle)
    if y is None:
        return None
    sched = (reg or {}).get("call_schedule") or []
    notes = (reg or {}).get("call_notes") or ""
    if sched and "Convertible" not in notes:
        for cs in sched:
            if cs["date"] > settle:
                yc = _ytm(price, coup, cs["date"], settle,
                          redemption=cs["price_pct"])
                if yc is not None:
                    y = min(y, yc)
    return y


def _vol_floor(raw):
    """Numeric floor of a TRACE reported volume string ('5MM+' ->
    5000000), or None. Mirrors the collector's store logic."""
    if raw in (None, ""):
        return None
    s = str(raw).replace(",", "").strip()
    if s.endswith("+"):
        s = s[:-1]
    mult = 1.0
    if s.upper().endswith("MM"):
        mult, s = 1e6, s[:-2]
    elif s.upper().endswith("M"):
        mult, s = 1e6, s[:-1]
    elif s.upper().endswith("K"):
        mult, s = 1e3, s[:-1]
    try:
        return int(float(s) * mult)
    except Exception:
        return None


def _chart_embed(marks, trades):
    """Compact chart data for the ECharts bond chart: trades as
    [epoch_ms, price, yield, volume_floor] ascending, marks as
    [epoch_ms, price]. Timestamps anchor at 12:00 UTC so the rendered
    date matches the trade date in every timezone."""
    import calendar as _cal
    import datetime as _dtt

    def ts(dstr, tstr="00:00:00"):
        t = _dtt.datetime.strptime(f"{dstr} {tstr}",
                                   "%Y-%m-%d %H:%M:%S")
        return _cal.timegm(t.timetuple()) * 1000 + 12 * 3600 * 1000

    t_out = []
    for t in sorted(trades, key=lambda r: (r[0], r[1] or "")):
        t_out.append([ts(t[0], t[1] or "00:00:00"), t[2], t[3],
                      _vol_floor(t[4] if len(t) > 4 else None)])
    m_out = [[ts(m[0]), m[1]] for m in sorted(marks)]
    return json.dumps({"t": t_out, "m": m_out},
                      separators=(",", ":"))


def _chart_svg(marks, trades, mode):
    """One chart, true date axis. marks: [(date, value)];
    trades: [(date, value)]. Value is price (% of par) or yield (%)
    per mode. Trade segments break across gaps over 30 days."""
    import datetime as _dt
    pts_m = [(d, v) for d, v in marks if v is not None]
    pts_t = [(d, v) for d, v in trades if v is not None]
    if not pts_m and not pts_t:
        return "<p class=\"muted\">No price history on record.</p>"
    all_d = [d for d, _ in pts_m + pts_t]
    d0, d1 = min(all_d), max(all_d)
    t0 = _dt.date.fromisoformat(d0)
    t1 = _dt.date.fromisoformat(d1)
    if t0 == t1:
        t0 -= _dt.timedelta(days=10)
        t1 += _dt.timedelta(days=10)
    vals = [v for _, v in pts_m + pts_t]
    lo, hi = min(vals), max(vals)
    pad = max((hi - lo) * 0.1, 0.5 if mode == "price" else 0.2)
    lo, hi = lo - pad, hi + pad
    W, H, ML, MR, MT, MB = 720, 260, 46, 12, 10, 24
    iw, ih = W - ML - MR, H - MT - MB
    span = (t1 - t0).days or 1

    def X(d):
        return ML + (_dt.date.fromisoformat(d) - t0).days / span * iw

    def Y(v):
        return MT + (hi - v) / (hi - lo) * ih

    out = [f"<svg class=\"bond-chart\" viewBox=\"0 0 {W} {H}\" "
           f"width=\"100%\" role=\"img\">"]
    for i in range(5):
        v = lo + (hi - lo) * i / 4
        y = Y(v)
        lab = f"{v:.1f}" if mode == "price" else f"{v:.1f}%"
        out.append(f"<line x1=\"{ML}\" y1=\"{y:.0f}\" x2=\"{W - MR}\" "
                   f"y2=\"{y:.0f}\" stroke=\"#e5ddc8\" stroke-width=\"1\"/>")
        out.append(f"<text x=\"{ML - 6}\" y=\"{y + 3:.0f}\" "
                   f"text-anchor=\"end\" class=\"chart-lab\">{lab}</text>")
    for i in range(7):
        d = t0 + _dt.timedelta(days=span * i // 6)
        x = ML + iw * i / 6
        out.append(f"<text x=\"{x:.0f}\" y=\"{H - 6}\" text-anchor=\"middle\" "
                   f"class=\"chart-lab\">{d.strftime('%b %y')}</text>")
    if len(pts_m) > 1:
        coords = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, v in pts_m)
        out.append(f"<polyline points=\"{coords}\" fill=\"none\" "
                   f"stroke=\"#8a8378\" stroke-width=\"1.2\" "
                   f"stroke-dasharray=\"5 3\"/>")
    for d, v in pts_m:
        out.append(f"<rect x=\"{X(d) - 3:.1f}\" y=\"{Y(v) - 3:.1f}\" "
                   f"width=\"6\" height=\"6\" fill=\"#fff\" "
                   f"stroke=\"#5c564a\" stroke-width=\"1.2\"/>")
    pts_t.sort()
    segs, cur = [], pts_t[:1]
    for p in pts_t[1:]:
        gap = (_dt.date.fromisoformat(p[0])
               - _dt.date.fromisoformat(cur[-1][0])).days
        if gap > 30:
            segs.append(cur)
            cur = [p]
        else:
            cur.append(p)
    segs.append(cur)
    for s in segs:
        if len(s) > 1:
            coords = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, v in s)
            out.append(f"<polyline points=\"{coords}\" fill=\"none\" "
                       f"stroke=\"#1a1a1a\" stroke-width=\"1.4\"/>")
    for d, v in pts_t:
        out.append(f"<circle cx=\"{X(d):.1f}\" cy=\"{Y(v):.1f}\" r=\"2.4\" "
                   f"fill=\"#1a1a1a\"/>")
    out.append("</svg>")
    return "".join(out)


DETAIL_JS = """<script>
(function(){
  var cbs = document.querySelectorAll('.tape-filter input[type=checkbox]');
  cbs.forEach(function(cb){ cb.addEventListener('change', function(){
    var showT = document.getElementById('f-trades').checked;
    var showM = document.getElementById('f-marks').checked;
    document.querySelectorAll('table.tape tbody tr').forEach(function(r){
      var s = r.getAttribute('data-src');
      r.style.display = (s === 't' && showT) || (s === 'm' && showM) ? '' : 'none';
    });
  }); });
})();
</script>
"""


def esc(s):
    return (str(s if s is not None else "")
            .replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


_ANALYTICS = None


def _analytics_data():
    global _ANALYTICS
    if _ANALYTICS is None:
        p = os.path.join(DATA, "bond_analytics.json")
        _ANALYTICS = json.load(open(p)) if os.path.exists(p) else {}
    return _ANALYTICS


_REGISTRY = None


def _registry():
    global _REGISTRY
    if _REGISTRY is None:
        p = os.path.join(DATA, "bonds.json")
        _REGISTRY = {b["cusip"]: b for b in json.load(open(p))["bonds"]}
    return _REGISTRY


def _rating_of(cusip, reg=None):
    """(shown, title) for the FINRA-sourced ratings in the registry:
    the S&P grade if present, else Moody's. The title carries both
    agencies with their rating dates when both exist. (None, None)
    when FINRA records no rating for the bond."""
    b = (reg if reg is not None else _registry()).get(cusip) or {}
    sp, spd = b.get("sp_rating"), b.get("sp_rating_date")
    md, mdd = b.get("moodys_rating"), b.get("moodys_rating_date")
    if not sp and not md:
        return None, None
    parts = []
    if sp:
        parts.append("S&amp;P " + esc(sp)
                     + (f", rated {_fmt_date(spd)}" if spd else ""))
    if md:
        parts.append("Moody's " + esc(md)
                     + (f", rated {_fmt_date(mdd)}" if mdd else ""))
    return (sp or md), "; ".join(parts)


def _rating_cell(cusip, reg=None):
    """Rating cell with the agency named in the cell (spec 3.1):
    the S&P grade where FINRA records one, with Moody's as a
    sub-line where both exist; Moody's alone where it is the only
    grade. The title carries both agencies with rating dates."""
    shown, title = _rating_of(cusip, reg)
    if shown is None:
        return '<td class="muted" data-v="">—</td>'
    b = (reg if reg is not None else _registry()).get(cusip) or {}
    sp, md = b.get("sp_rating"), b.get("moodys_rating")
    if sp and md:
        inner = (f"S&amp;P {esc(sp)}"
                 f"<span class=\"cell-sub\">Moody's {esc(md)}</span>")
        dv = f"S&P {sp}"
    elif sp:
        inner, dv = f"S&amp;P {esc(sp)}", f"S&P {sp}"
    else:
        inner, dv = f"Moody's {esc(md)}", f"Moody's {md}"
    return (f'<td data-v="{esc(dv)}" title="{title}">'
            f'{inner}</td>')


_TP = None


def _trace_prints():
    """One read of trace_prints.json per build (spec step 0: the
    strip and the tape derive from one tape snapshot)."""
    global _TP
    if _TP is None:
        p = os.path.join(DATA, "trace_prints.json")
        _TP = (json.load(open(p)) if os.path.exists(p)
               else {"prints": [], "as_of": ""})
    return _TP


def _tape_latest(tp):
    """The tape's own latest trade date, computed from the prints
    themselves - never the file's as_of metadata (audit P8)."""
    ds = [x.get("last_trade_date") for x in tp.get("prints", [])
          if x.get("last_trade_date")]
    return max(ds) if ds else (tp.get("as_of") or "")


def _fmt_tape_vol(v):
    """Tape volume: FINRA cap labels ('1MM+', '5MM+') render as
    reported; numeric amounts render as full dollars with
    separators and no decimals - never a raw float (spec 2.4)."""
    if v in (None, ""):
        return "—"
    s = str(v).strip()
    if s.endswith("+") or "MM" in s.upper():
        return s
    try:
        return f"{float(s.replace(',', '')):,.0f}"
    except ValueError:
        return s


def _watched_issuers():
    """The issuer sweep configuration (watched_issuers.json): the one
    deliberate config list in the pipeline. Bond-level data is never
    listed anywhere; new bonds of these issuers append themselves."""
    p = os.path.expanduser(
        "~/workspace/ai-leverage-monitor/data/watched_issuers.json")
    if not os.path.exists(p):
        return []
    try:
        return json.load(open(p)).get("issuers", [])
    except Exception:
        return []


_CROSSWALK = None


def _crosswalk():
    """Issuer crosswalk (shared identity layer): registry issuer
    string -> (display family, family page key, vehicle name).
    First record in file order wins a name claimed by two records."""
    global _CROSSWALK
    if _CROSSWALK is None:
        _CROSSWALK = {}
        p = os.path.expanduser(
            "~/workspace/ai-leverage-monitor/data/issuer_crosswalk.json")
        try:
            recs = json.load(open(p)).get("records", [])
        except Exception:
            recs = []
        for r in recs:
            fam = r.get("family")
            if not fam:
                continue
            key = re.sub(r"[^a-z0-9]+", "-",
                         fam.lower()).strip("-")[:40]
            names = list(r.get("registry_names") or [])
            if r.get("finra_name_proven"):
                names.append(r["finra_name_proven"])
            names += list(r.get("additional_finra_names") or [])
            for n in names:
                _CROSSWALK.setdefault(
                    n, (fam, key, r.get("vehicle_name")))
    return _CROSSWALK


def _family_of(issuer_str):
    return _crosswalk().get(issuer_str or "")


def _issuer_display(finra_name):
    stop = {"INC", "CORP", "COM", "CO", "LTD", "LLC", "LP"}
    toks = [t for t in (finra_name or "").replace(".", " ").split()
            if t.upper() not in stop]
    return " ".join(t.title() if t.upper() != "NVIDIA" else "NVIDIA"
                    for t in toks)


def _issued_cell(cusip):
    """The note's amount issued, in $M, from the registry's sourced
    issue_amount_usd (an issuer pricing filing where one is held).
    Blank - an empty cell, never a zero and never fund-held
    principal - where no held source states an amount. Added
    2026-10-26 at Arvin's direction: the amount belongs in the
    table, next to the note. Extended 2026-10-27: where no original
    issue amount is sourced but the issuer's latest 10-K states the
    series' principal outstanding, render that figure followed by
    " (o/s)" - a different quantity, labelled as such, never
    conflated with the original issue amount."""
    b = _registry().get(cusip) or {}
    amt = b.get("issue_amount_usd")
    suffix = ""
    if amt is None:
        amt = b.get("amount_outstanding_usd")
        suffix = " (o/s)"
    if amt is None:
        return '<td class="muted" data-v="-999"></td>'
    m = amt / 1e6
    s = f"{m:,.0f}" if m == int(m) else f"{m:,.1f}"
    return f'<td class="num" data-v="{amt}">{s}{suffix}</td>'


def _ana_bond(cusip):
    d = _detail_data().get(cusip) or {}
    b = _registry().get(cusip) or {}
    issuer = d.get("issuer") or b.get("issuer") or ""
    sec = d.get("security") or b.get("security") or ""
    label = f"{issuer} — {sec}".strip(" —")
    return (f'<td data-v="{esc(label)}"><a class="bond-link" '
            f'href="/leverage/bond/{cusip.lower()}/">'
            f'<span class="bond-name">{esc(issuer)}</span>'
            f'<span class="bond-sub">{esc(sec)}</span></a></td>'
            + _issued_cell(cusip))


def _ana_note(sec):
    out = ""
    if sec.get("method"):
        out += f'<p class="src">Method: {esc(sec["method"])}</p>'
    if sec.get("limits"):
        out += f'<p class="src">Limits: {esc(sec["limits"])}</p>'
    return out


def _hist_svg(buckets, aria):
    """Vertical bar histogram. buckets: list of (label, n)."""
    W, H, L, R, T, B = 560, 168, 8, 8, 18, 24
    mx = max([n for _, n in buckets] + [1])
    bw = (W - L - R) / len(buckets)
    el = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
          f'aria-label="{esc(aria)}">']
    base = H - B
    for i, (lab, n) in enumerate(buckets):
        x = L + i * bw
        h = (base - T) * n / mx
        el.append(
            f'<rect x="{x + 3:.0f}" y="{base - h:.0f}" '
            f'width="{bw - 6:.0f}" height="{h:.0f}" fill="#3f4750"/>')
        el.append(
            f'<text x="{x + bw / 2:.0f}" y="{base - h - 4:.0f}" '
            f'font-size="11" text-anchor="middle" fill="#3f4750">'
            f'{n}</text>')
        el.append(
            f'<text x="{x + bw / 2:.0f}" y="{base + 15:.0f}" '
            f'font-size="10" text-anchor="middle" fill="#6b7280">'
            f'{esc(lab)}</text>')
    el.append(f'<line x1="{L}" y1="{base}" x2="{W - R}" y2="{base}" '
              f'stroke="#c9c4b8" stroke-width="1"/>')
    el.append("</svg>")
    return "".join(el)


def _heat_table(heatmap, mx=None):
    weeks = heatmap.get("weeks") or []
    rows = heatmap.get("rows") or []
    if not weeks or not rows:
        return ""
    if mx is None:
        mx = max([c for r in rows for c in r["counts"]] + [1])
    th = "".join(f"<th>{_fmt_date(w)[:6]}</th>" for w in weeks)
    trs = []
    for r in rows:
        tds = []
        for c in r["counts"]:
            a = 0.05 + 0.5 * (c / mx) if c else 0.0
            tds.append(
                f'<td class="num" style="background:'
                f'rgba(63,71,80,{a:.2f})">'
                f'<span style="color:{"#fff" if a > 0.32 else "inherit"}">'
                f'{c if c else "—"}</span></td>')
        trs.append(
            f'<tr><td>{esc(r["issuer"].title())}</td>'
            + "".join(tds)
            + f'<td class="num">{r["total"]:,}</td></tr>')
    return ('<div class="market-table-scroll"><table class="market-table">'
            f"<thead><tr><th>Issuer</th>{th}<th>Total</th></tr></thead>"
            f"<tbody>{''.join(trs)}</tbody></table></div>")


def _curve_svg(curve):
    pts = [p for p in curve["points"] if p.get("spread_bp") is not None]
    if len(pts) < 2:
        return ""
    W, H, L, R, T, B = 720, 230, 52, 14, 12, 26
    xs = [p["years"] for p in pts]
    ys = [p["spread_bp"] for p in pts]
    x0, x1 = min(xs) - 0.4, max(xs) + 0.4
    y0, y1 = min(ys) - 60, max(ys) + 60
    X = lambda v: L + (v - x0) / (x1 - x0) * (W - L - R)
    Y = lambda v: T + (y1 - v) / (y1 - y0) * (H - T - B)
    el = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
          f'aria-label="Spread curve">']
    for i in range(5):
        v = y0 + (y1 - y0) * i / 4
        el.append(f'<line x1="{L}" y1="{Y(v):.0f}" x2="{W - R}" '
                  f'y2="{Y(v):.0f}" stroke="#e5e2d8"/>')
        el.append(f'<text x="{L - 6}" y="{Y(v) + 3:.0f}" font-size="9.5" '
                  f'text-anchor="end" fill="#6b675c">{v:.0f}</text>')
    el.append(f'<text x="{L - 38}" y="{T + 8}" font-size="9.5" '
              f'fill="#6b675c">bp</text>')
    for v in range(int(x0) + 1, int(x1) + 1):
        el.append(f'<text x="{X(v):.0f}" y="{H - 8}" font-size="9.5" '
                  f'text-anchor="middle" fill="#6b675c">{v}y</text>')
    line = " ".join(f"{X(p['years']):.1f},{Y(p['spread_bp']):.1f}"
                    for p in pts)
    el.append(f'<polyline points="{line}" fill="none" stroke="#8a8578" '
              f'stroke-width="1.2"/>')
    for p in pts:
        cx, cy = X(p["years"]), Y(p["spread_bp"])
        if p["basis"] == "trade":
            el.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.2" '
                      f'fill="#1a1a1a"/>')
        else:
            el.append(f'<rect x="{cx - 3:.1f}" y="{cy - 3:.1f}" width="6" '
                      f'height="6" fill="none" stroke="#1a1a1a" '
                      f'stroke-width="1.3"/>')
    el.append("</svg>")
    return "".join(el)


def _issuer_curve_svg(curves):
    """Yield curves at up to three dates on one axis. curves: label ->
    [[years, yield_pct, cusip], ...], label order Latest, Jul 2026,
    Dec 2025. Latest is a filled-dot line; earlier dates are hollow
    markers (squares, triangles) with no line."""
    series = [(lab, curves[lab]) for lab in
              ("Latest", "Jul 2026", "Dec 2025") if curves.get(lab)]
    pts = [p for _, ps in series for p in ps]
    if len(pts) < 3:
        return ""
    W, H, L, R, T, B = 720, 230, 52, 14, 12, 26
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = min(xs) - 0.4, max(xs) + 0.4
    y0, y1 = min(ys) - 0.6, max(ys) + 0.6
    X = lambda v: L + (v - x0) / (x1 - x0) * (W - L - R)
    Y = lambda v: T + (y1 - v) / (y1 - y0) * (H - T - B)
    el = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
          f'aria-label="Yield curve at three dates">']
    for i in range(5):
        v = y0 + (y1 - y0) * i / 4
        el.append(f'<line x1="{L}" y1="{Y(v):.0f}" x2="{W - R}" '
                  f'y2="{Y(v):.0f}" stroke="#e5e2d8"/>')
        el.append(f'<text x="{L - 6}" y="{Y(v) + 3:.0f}" font-size="9.5" '
                  f'text-anchor="end" fill="#6b675c">{v:.1f}</text>')
    el.append(f'<text x="{L - 40}" y="{T + 8}" font-size="9.5" '
              f'fill="#6b675c">Yield %</text>')
    for v in range(int(x0) + 1, int(x1) + 1):
        el.append(f'<text x="{X(v):.0f}" y="{H - 8}" font-size="9.5" '
                  f'text-anchor="middle" fill="#6b675c">{v}y</text>')
    for lab, ps in series:
        ps = sorted(ps)
        if lab == "Latest":
            line = " ".join(f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in ps)
            el.append(f'<polyline points="{line}" fill="none" '
                      f'stroke="#8a8578" stroke-width="1.2"/>')
            for p in ps:
                el.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" '
                          f'r="3.2" fill="#1a1a1a"/>')
        elif lab == "Jul 2026":
            for p in ps:
                el.append(f'<rect x="{X(p[0]) - 3:.1f}" '
                          f'y="{Y(p[1]) - 3:.1f}" width="6" height="6" '
                          f'fill="none" stroke="#b3541e" '
                          f'stroke-width="1.3"/>')
        else:
            for p in ps:
                cx, cy = X(p[0]), Y(p[1])
                el.append(f'<path d="M {cx:.1f} {cy - 3.6:.1f} '
                          f'L {cx - 3.4:.1f} {cy + 2.6:.1f} '
                          f'L {cx + 3.4:.1f} {cy + 2.6:.1f} Z" '
                          f'fill="none" stroke="#6b675c" '
                          f'stroke-width="1.2"/>')
    el.append("</svg>")
    return "".join(el)


def _median_path_svg(monthly, name):
    """No-JS fallback inside the issuer chart container: month-end
    median last print as a line. Monthly points are equally spaced in
    time by construction; months with no priced bond break the line."""
    pts = [(i, m["median"]) for i, m in enumerate(monthly)
           if m.get("median") is not None]
    if len(pts) < 2:
        return ""
    W, H, L, R, T, B = 720, 300, 52, 14, 14, 26
    n = len(monthly)
    ys = [v for _, v in pts]
    y0, y1 = min(ys) - 2, max(ys) + 2
    X = lambda i: L + i / max(n - 1, 1) * (W - L - R)
    Y = lambda v: T + (y1 - v) / (y1 - y0) * (H - T - B)
    el = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
          f'aria-label="Median last print by month, {esc(name)}">']
    for i in range(5):
        v = y0 + (y1 - y0) * i / 4
        el.append(f'<line x1="{L}" y1="{Y(v):.0f}" x2="{W - R}" '
                  f'y2="{Y(v):.0f}" stroke="#e5e2d8"/>')
        el.append(f'<text x="{L - 6}" y="{Y(v) + 3:.0f}" font-size="9.5" '
                  f'text-anchor="end" fill="#6b675c">{v:.0f}</text>')
    segs, cur = [], []
    prev = None
    for i, v in pts:
        if prev is not None and i - prev > 1 and cur:
            segs.append(cur)
            cur = []
        cur.append(f"{X(i):.1f},{Y(v):.1f}")
        prev = i
    if cur:
        segs.append(cur)
    for s in segs:
        if len(s) > 1:
            el.append(f'<polyline points="{" ".join(s)}" fill="none" '
                      f'stroke="#3f4750" stroke-width="1.4"/>')
    for i, v in pts:
        el.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="2.4" '
                  f'fill="#1a1a1a"/>')
    el.append(f'<text x="{L}" y="{H - 8}" font-size="9.5" '
              f'fill="#6b675c">{esc(monthly[0]["month"])}</text>')
    el.append(f'<text x="{W - R}" y="{H - 8}" font-size="9.5" '
              f'text-anchor="end" fill="#6b675c">'
              f'{esc(monthly[-1]["month"])}</text>')
    el.append("</svg>")
    return "".join(el)


ISSUER_BOND_COLS = [("Bond", 300, 180, False),
                    ("Issued ($M)", 104, 72, False),
                    ("Last print (% of par)", 124, 76, False),
                    ("Traded", 110, 92, False), ("Coupon (%)", 84, 72, False),
                    ("Matures", 110, 92, False), ("Rating", 96, 64, False),
                    ("CUSIP", 108, 96, False)]
ISSUER_BOND_COLS_M = [("Bond", 300, 180, False),
                      ("Issued ($M)", 104, 72, False),
                      ("Last print (% of par)", 124, 76, False),
                      ("Traded", 110, 92, False),
                      ("Gap (pts)", 92, 76, False),
                      ("Fund mark (% of par)", 128, 76, False),
                      ("Coupon (%)", 84, 72, False),
                      ("Matures", 110, 92, False),
                      ("Rating", 96, 64, False),
                      ("CUSIP", 108, 96, False)]
ISSUER_MO_COLS = [("Month", 100, 92, False), ("Trades", 84, 76, False),
                  ("Median last print", 140, 92, False),
                  ("Priced bonds", 110, 76, False),
                  ("Below 90", 92, 76, False)]
ISSUER_FUND_COLS = [("Fund complex", 320, 180, False),
                    ("Principal ($M)", 130, 92, False),
                    ("Positions", 96, 76, False),
                    ("Bonds held", 100, 76, False)]
ISSUER_FILING_COLS = [("Filed", 104, 84, False),
                      ("Filing", 168, 120, False),
                      ("What it shows", 660, 240, False)]


def _issuer_filings():
    """Material SEC filings per issuer group key, maintained by the
    daily filings pull in data/macro/issuer_filings.json and rendered
    as the Filings and developments section on issuer pages. Only
    filings with financing, lease, commitment or capital-structure
    content are entered."""
    p = os.path.join(DATA, "issuer_filings.json")
    if not os.path.exists(p):
        return {}
    try:
        return json.load(open(p)).get("issuers", {})
    except Exception:
        return {}


ANA_DISP_COLS = [("Bond", 300, 180), ("Issued ($M)", 104, 72),
                 ("Period", 100, 92), ("Funds", 76, 76),
                 ("Aggregate", 96, 76), ("Median", 84, 76), ("Min", 76, 76),
                 ("Max", 76, 76), ("Range (pts)", 100, 76),
                 ("Most deviant fund", 280, 140), ("Deviation (pts)", 110, 76),
                 ("CUSIP", 108, 96)]
ANA_GAP_COLS = [("Bond", 300, 180), ("Issued ($M)", 104, 72),
                ("Last print (% of par)", 124, 76),
                ("Traded", 110, 92), ("Fund mark (% of par)", 124, 76),
                ("Period", 100, 92), ("Gap (pts)", 92, 76),
                ("CUSIP", 108, 96)]
ANA_CURVEPT_COLS = [("Issuer", 240, 140), ("Bond", 280, 160),
                    ("Issued ($M)", 104, 72),
                    ("CUSIP", 108, 96), ("Years", 76, 76), ("Price (% of par)", 112, 76),
                    ("Basis (pts)", 84, 76), ("Basis date", 110, 92),
                    ("Yield (%)", 84, 76), ("Spread (bp)", 104, 76)]
ANA_TWIN_COLS = [("Bond", 300, 180), ("Issued ($M)", 104, 72),
                 ("Registered CUSIP", 130, 108),
                 ("Reg. print (% of par)", 124, 76), ("Reg. date", 110, 92),
                 ("144A CUSIP", 120, 108), ("144A print (% of par)", 124, 76),
                 ("144A date", 110, 92), ("Basis (pts)", 96, 76)]
ANA_LIQ_COLS = [("Bond", 300, 180), ("Issued ($M)", 104, 72),
                ("Trades in window", 130, 76),
                ("Trades, last 7d", 120, 76), ("Last trade date", 110, 92),
                ("Days since", 100, 76), ("CUSIP", 108, 96)]
ANA_EVT_COLS = [("Issuer", 240, 140), ("Form", 80, 76), ("Filed", 100, 92),
                ("Bond", 280, 160), ("Issued ($M)", 104, 72),
                ("Print before (% of par)", 132, 76),
                ("Before date", 110, 92), ("Print after (% of par)", 132, 76),
                ("After date", 110, 92), ("Change (pts)", 104, 76),
                ("Accession", 180, 120)]
ANA_BACK_COLS = [("Bond", 300, 180), ("Issued ($M)", 104, 72),
                 ("Marks fire (period)", 140, 92),
                 ("Knowable from", 120, 92),
                 ("Days before news (marks)", 170, 92),
                 ("First tape print < 90", 150, 92),
                 ("Days before news (tape)", 170, 92), ("CUSIP", 108, 96)]
# N-PORT panel tables (Stage 2, 2026-10-20): disagreement between the
# tape and the full-universe fund median, coverage/concentration, the
# zero-holder list, and the per-bond top-holder table.
NP_GAP_COLS = [("Bond", 300, 180), ("Issued ($M)", 104, 72),
               ("Last print (% of par)", 124, 76),
               ("Traded", 110, 92), ("Fund median (% of par)", 132, 76),
               ("Period ended", 110, 92), ("Gap (pts)", 92, 76),
               ("Funds", 76, 76), ("CUSIP", 108, 96)]
NP_CONC_COLS = [("Bond", 300, 180), ("Issued ($M)", 104, 72),
                ("Reported balance ($)", 150, 92),
                ("Largest holder (%)", 120, 84), ("Top five (%)", 104, 76),
                ("Funds", 76, 76), ("CUSIP", 108, 96)]
NP_DISP_COLS = [("Bond", 300, 180), ("Issued ($M)", 104, 72),
                ("Median (% of par)", 124, 76),
                ("P10 (% of par)", 110, 76), ("P90 (% of par)", 110, 76),
                ("Range p10-p90 (pts)", 140, 84), ("Funds", 76, 76),
                ("CUSIP", 108, 96)]
NP_ZERO_COLS = [("Bond", 340, 200), ("Issued ($M)", 104, 72),
                ("Deal", 220, 120),
                ("CUSIP", 108, 96)]
HOLDER_COLS = [("Fund", 340, 180), ("Reported balance ($)", 160, 96),
               ("Share of reported balance (%)", 170, 110)]

for _n in [k for k in list(globals())
           if (k.startswith("ANA_") or k.startswith("NP_")
               or k == "HOLDER_COLS") and k.endswith("_COLS")]:
    globals()[_n] = [(c[0], c[1], c[2], c[3] if len(c) > 3 else False)
                     for c in globals()[_n]]



ACT_MOST_COLS = [("Bond", 340, 200, False), ("Issued ($M)", 104, 72, False),
                 ("Trades", 84, 64, False),
                 ("Volume ($)", 110, 84, False), ("Last (% of par)", 104, 64, False),
                 ("Last trade time (ET)", 120, 84, False), ("CUSIP", 108, 96, False)]
ACT_MOVE_COLS = [("Bond", 340, 200, False), ("Issued ($M)", 104, 72, False),
                 ("Move (pts)", 96, 76, False),
                 ("Last (% of par)", 104, 64, False), ("Prev (% of par)", 104, 64, False),
                 ("Prev date", 110, 92, False), ("CUSIP", 108, 96, False)]
ACT_LATE_COLS = [("Time", 84, 64, False), ("Bond", 340, 200, False),
                 ("Issued ($M)", 104, 72, False),
                 ("Price (% of par)", 104, 64, False), ("Volume ($)", 110, 84, False),
                 ("CUSIP", 108, 96, False)]
ACT_WEEK_COLS = [("Date", 120, 100, False), ("Trades", 96, 76, False),
                 ("Volume", 120, 92, False),
                 ("Bonds traded", 120, 92, False),
                 ("Last prints below 90", 170, 120, False)]
ACT_ALL_COLS = [("Bond", 340, 200, False), ("Issued ($M)", 104, 72, False),
                ("Trades (5d)", 92, 68, False),
                ("Volume ($)", 110, 84, False),
                ("Last (% of par)", 104, 64, False),
                ("Move (5d, pts)", 108, 76, False),
                ("High (5d, % of par)", 118, 84, False),
                ("Low (5d, % of par)", 118, 84, False),
                ("Last trade", 110, 92, False), ("CUSIP", 108, 96, False)]


def activity_page():
    act = (_analytics_data().get("analyses") or {}).get("activity") or {}
    if not act.get("tape_end"):
        return (frontmatter(
            "Bond Activity",
            "Day and week trading activity across the watched bonds.",
            "No tape data yet") + \
            "<p>No activity data has been computed yet.</p>\n"), {}
    s = act.get("summary") or {}
    upd = ""
    try:
        from datetime import datetime as _dt
        u = _dt.fromisoformat(act.get("updated") or "")
        day = "Today" if u.date() == _dt.now(u.tzinfo).date() \
            else _fmt_date(u.date().isoformat())
        upd = f"{day}, {u:%H:%M} ET"
    except Exception:
        upd = ""

    def bond(c, label):
        return f"<a href=\"/leverage/bond/{c.lower()}/\">{label}</a>"

    def cell(r):
        sec = r.get("security") or ""
        sp = (f"<span class=\"muted activity-sec\">{sec}</span>"
              if sec else "")
        return (f"<td>{bond(r['cusip'], r['issuer'])}{sp}</td>")

    strip_items = [("Updated", upd or "\u2014"),
                   ("Tape through", _fmt_date(act["tape_end"])),
                   ("Bonds traded", f"{s.get('bonds_traded', 0)}"),
                   ("Trades", f"{s.get('trades', 0):,}"),
                   ("Last prints below 90", f"{s.get('below90', 0)}")]
    strip = ('<dl class="bw-summary">\n' + "".join(
        f"<div class=\"bw-sum-item\"><dt>{k}</dt><dd>{v}</dd></div>\n"
        for k, v in strip_items) + "</dl>\n")
    mt = "".join(
        f"<tr>{cell(r)}{_issued_cell(r['cusip'])}<td>{r['trades']}</td>"
        f"<td>{_fmt_vol(r['volume'])}</td><td>{r['last_price']:.2f}</td>"
        f"<td>{(r.get('last_time') or '')[:5]}</td>"
        f"<td class=\"muted\">{r['cusip']}</td></tr>"
        for r in act.get("most_traded") or [])
    mv = "".join(
        f"<tr>{cell(r)}{_issued_cell(r['cusip'])}<td>{r['move']:+.2f}</td>"
        f"<td>{r['last_price']:.2f}</td><td>{r['prev_price']:.2f}</td>"
        f"<td>{_fmt_date(r['prev_date'])}</td>"
        f"<td class=\"muted\">{r['cusip']}</td></tr>"
        for r in act.get("biggest_moves") or [])
    lp = "".join(
        f"<tr><td>{(r['time'] or '')[:5]}</td>{cell(r)}{_issued_cell(r['cusip'])}"
        f"<td>{r['price']:.2f}</td><td>{_fmt_vol(r.get('volume'))}</td>"
        f"<td class=\"muted\">{r['cusip']}</td></tr>"
        for r in act.get("latest_prints") or [])
    wk = "".join(
        f"<tr><td>{_fmt_date(r['date'])}</td><td>{r['trades']:,}</td>"
        f"<td>{_fmt_vol(r['volume'])}</td><td>{r['bonds']}</td>"
        f"<td>{r['below90']} of {r['bonds']}</td></tr>"
        for r in act.get("week") or [])

    def arow(r):
        def num(v, signed=False):
            if v is None:
                return "<td class=\"muted\">\u2014</td>"
            txt = f"{v:+.2f}" if signed else f"{v:.2f}"
            return f"<td data-v=\"{v}\">{txt}</td>"
        lp = (f"<td data-v=\"{r['last_price']}\">"
              f"{r['last_price']:.2f}</td>"
              if r.get("last_price") is not None
              else "<td class=\"muted\">\u2014</td>")
        ld = (f"<td data-v=\"{r['last_date']}\">"
              f"{_fmt_date(r['last_date'])}</td>"
              if r.get("last_date") else "<td class=\"muted\">\u2014</td>")
        return (f"<tr>{cell(r)}{_issued_cell(r['cusip'])}"
                f"<td data-v=\"{r['trades']}\">{r['trades']:,}</td>"
                f"<td data-v=\"{r['volume']}\">"
                f"{_fmt_vol(r['volume'])}</td>"
                + lp + num(r.get("week_move"), signed=True)
                + num(r.get("high")) + num(r.get("low")) + ld
                + f"<td class=\"muted\">{r['cusip']}</td></tr>")

    ab_rows = [arow(r) for r in act.get("week_bonds") or []]
    all_head = "<h2 id=\"all\">All watched bonds: last five trade days</h2>\n"
    if act.get("week_start"):
        all_head = (f"<h2 id=\"all\">All watched bonds, "
                    f"{_fmt_date(act['week_start'])} to "
                    f"{_fmt_date(act['tape_end'])}</h2>\n")
    # The all-bonds table runs to several hundred rows; rendered whole
    # it made the page lag. It is paginated at 100 rows per page
    # (2026-10-26, Arvin): page 1 stays at /leverage/activity/ with
    # the day's summary tables, continuations live at
    # /leverage/activity/<n>/ via activity-p<n>.md files.
    page_size = 100
    page_count = max(1, -(-len(ab_rows) // page_size))

    def act_url(n):
        return "/leverage/activity/" if n == 1 \
            else f"/leverage/activity/{n}/"

    def pager(n):
        if page_count <= 1:
            return ""
        links = " / ".join(
            f"<strong>{i}</strong>" if i == n
            else f"<a href=\"{act_url(i)}\">{i}</a>"
            for i in range(1, page_count + 1))
        ends = ""
        if n > 1:
            ends += f"<a href=\"{act_url(n - 1)}\">Previous</a> "
        if n < page_count:
            ends += f"<a href=\"{act_url(n + 1)}\">Next</a>"
        return (f"<nav class=\"bw-pager\" aria-label=\"All watched "
                f"bonds pages\">"
                f"<span class=\"bw-pager-pos\">Page {n} of "
                f"{page_count}</span>"
                f"<span class=\"bw-pager-links\">{links}</span>"
                f"<span class=\"bw-pager-ends\">{ends.strip()}</span>"
                f"</nav>\n")
    body = frontmatter(
        "Bond Activity",
        "Week trading activity for every watched bond, with the day's "
        "most traded, biggest moves and latest prints.",
        f"Tape through {_fmt_date(act['tape_end'])}")
    body += strip
    body += (
        "<p class=\"data-vintage\">Registry bonds only, from the FINRA "
        "TRACE tape as collected. The latest trade date is the tape's "
        "most recent date; on a non-trading day it is the last trading "
        "day. A move is the latest print against the previous print on "
        "an earlier date. In the full table, the 5-day move is the last "
        "print inside the window against the last print before it. "
        "Issued ($M) is the note's original amount issued, from the "
        "issuer's pricing filing where one is on record; blank where "
        "no held source states it.</p>\n"
        + all_head
        + _grid("act-all", ACT_ALL_COLS, "".join(ab_rows[:page_size]))
        + pager(1)
        + "<h2 id=\"most\">Most traded</h2>\n"
        + _grid("act-most", ACT_MOST_COLS, mt)
        + "<h2 id=\"moves\">Biggest moves</h2>\n"
        + _grid("act-moves", ACT_MOVE_COLS, mv)
        + "<h2 id=\"latest\">Latest prints</h2>\n"
        + _grid("act-latest", ACT_LATE_COLS, lp)
        + "<h2 id=\"week\">Last five trade days</h2>\n"
        + _grid("act-week", ACT_WEEK_COLS, wk, sortable=False)
        + "<p class=\"data-vintage\">Volumes are amounts reported to "
          "TRACE. FINRA caps the reported amount on large trades, so "
          "volume understates true size on capped prints.</p>\n")
    body += TABLE_ENGINE_JS
    extras = {}
    for n in range(2, page_count + 1):
        rows = "".join(ab_rows[(n - 1) * page_size:n * page_size])
        eb = frontmatter(
            "Bond Activity",
            "Week trading activity for every watched bond, with the "
            "day's most traded, biggest moves and latest prints.",
            f"Tape through {_fmt_date(act['tape_end'])}",
            url=act_url(n))
        eb += strip
        if act.get("week_start"):
            eb += (f"<h2 id=\"all\">All watched bonds, "
                   f"{_fmt_date(act['week_start'])} to "
                   f"{_fmt_date(act['tape_end'])} - page {n} of "
                   f"{page_count}</h2>\n")
        else:
            eb += (f"<h2 id=\"all\">All watched bonds: last five "
                   f"trade days - page {n} of {page_count}</h2>\n")
        eb += _grid("act-all", ACT_ALL_COLS, rows)
        eb += pager(n)
        eb += TABLE_ENGINE_JS
        extras[n] = eb
    return body, extras


def _pager_html(n, count, url_for, label):
    if count <= 1:
        return ""
    links = " / ".join(
        f"<strong>{i}</strong>" if i == n
        else f"<a href=\"{url_for(i)}\">{i}</a>"
        for i in range(1, count + 1))
    ends = ""
    if n > 1:
        ends += f"<a href=\"{url_for(n - 1)}\">Previous</a> "
    if n < count:
        ends += f"<a href=\"{url_for(n + 1)}\">Next</a>"
    return (f"<nav class=\"bw-pager\" aria-label=\"{label} pages\">"
            f"<span class=\"bw-pager-pos\">Page {n} of {count}</span>"
            f"<span class=\"bw-pager-links\">{links}</span>"
            f"<span class=\"bw-pager-ends\">{ends.strip()}</span>"
            f"</nav>\n")


def bond_analytics_page():
    A = _analytics_data().get("analyses", {})
    if not A:
        return "", {}
    _bwp = os.path.join(DATA, "bond_watch.json")
    bw = json.load(open(_bwp)) if os.path.exists(_bwp) else {}
    as_of = _analytics_data().get("as_of", "")
    liq_s = A["liquidity"]["summary"]
    iss = A.get("issuers") or {}
    groups = iss.get("groups") or []
    strip = [
        ("Issuers", f"{len(groups)}"),
        ("Bonds tracked", f"{len(_registry())}"),
        ("Tape window", "Oct 2023 – Oct 2026"),
        ("Fund marks to", _fmt_date(bw.get("marks_as_of")) if bw else "n/a"),
    ]
    strip_html = ('<dl class="bw-summary">'
                  + "".join(f"<div class=\"bw-sum-item\"><dt>{esc(k)}</dt>"
                            f"<dd>{esc(v)}</dd></div>"
                            for k, v in strip) + "</dl>")
    nav = ('<p class="bw-anchor">'
           '<a href="#issuers">Issuers</a> / '
           '<a href="#twins">Twin basis</a> / '
           '<a href="#liquidity">Liquidity</a> / '
           '<a href="#events">Filings and prints</a> / '
           '<a href="#backtest">Alert backtest</a> / '
           '<a href="#marksgap">Marks vs tape</a> / '
           '<a href="#coverage">Coverage</a> / '
           '<a href="#sources">Sources</a></p>')
    out = [frontmatter(
        "Bond Analytics",
        "Bond prices, trends, curves and holders by issuer, from "
        "the FINRA tape and SEC fund filings.",
        as_of)]
    out.append(strip_html)
    out.append(nav)
    # Pagination (2026-10-26, Arvin): the liquidity heatmap and the
    # fund-marks table made this page lag (1.3 MB rendered whole).
    # Both are paginated: page 1 keeps the first slice of each plus
    # every other section; continuations live at
    # /leverage/bond-analytics/liquidity/<n>/ and .../marks/<n>/.
    def _liq_url(n):
        return "/leverage/bond-analytics/" if n == 1 \
            else f"/leverage/bond-analytics/liquidity/{n}/"

    def _marks_url(n):
        return "/leverage/bond-analytics/" if n == 1 \
            else f"/leverage/bond-analytics/marks/{n}/"

    _gap_trs = []
    _gap_pages = 1
    _heat = {}
    _hrows = []
    _hmx = 1
    _hsize = 10
    _hpages = 1
    # 1 issuers
    if groups:
        from datetime import datetime as _dtm, timezone as _tz
        out.append('<h2 id="issuers">Issuers</h2>')
        fam_labels = [("core", "Core watch"),
                      ("benchmark", "Benchmark"),
                      ("project", "Project issuers")]
        dir_html = ['<div class="issuer-dir">']
        for fam, lab in fam_labels:
            members = [g for g in groups if g["family"] == fam]
            if not members:
                continue
            ul_cls = ' class="cols2"' if len(members) > 8 else ""
            dir_html.append(f'<div class="issuer-dir-group">'
                            f'<h4>{lab}</h4><ul{ul_cls}>')
            for g in members:
                dir_html.append(
                    f'<li><a href="/leverage/issuer/{g["key"]}/">'
                    f'{esc(g["name"])}</a> '
                    f'<span class="src">{g["n_bonds"]} bonds, '
                    f'{g["trades_stored"]:,} trades</span></li>')
            dir_html.append('</ul></div>')
        dir_html.append('</div>')
        out.append("".join(dir_html))
    # Legacy mark exhibits retired 2026-10-20 (Stage 2): the
    # dispersion and trade-mark gap sections below were computed
    # from the retired narrow marks pipeline. The N-PORT panel
    # sections (marks vs tape; coverage and concentration) are
    # their replacements; the code is kept for reference.
    if False:
        # 2 dispersion
        sec = A["fund_dispersion"]
        s = sec["summary"]
        rows = []
        for r in sec["rows"]:
            rows.append("<tr>" + _ana_bond(r["cusip"])
                        + f'<td data-v="{r["period"]}">{_fmt_date(r["period"])}</td>'
                        + f'<td data-v="{r["funds"]}">{r["funds"]}</td>'
                        + f'<td data-v="{r["aggregate"]}">{r["aggregate"]:.2f}</td>'
                        + f'<td data-v="{r["median"]}">{r["median"]:.2f}</td>'
                        + f'<td data-v="{r["min"]}">{r["min"]:.2f}</td>'
                        + f'<td data-v="{r["max"]}">{r["max"]:.2f}</td>'
                        + f'<td data-v="{r["range_pts"]}">{r["range_pts"]:.2f}</td>'
                        + f'<td data-v="{esc(r["deviant_fund"])}">'
                          f'{esc(r["deviant_fund"])}</td>'
                        + f'<td data-v="{r["deviation_pts"]}">'
                          f'{r["deviation_pts"]:+.2f}</td>'
                        + f'<td data-v="{r["cusip"]}">{r["cusip"]}</td></tr>')
        out.append('<h2 id="dispersion">Fund mark dispersion</h2>')
        out.append(f'<p class="data-vintage">Range of per-fund implied '
                   f'marks, points, latest report period per bond, '
                   f'n = {s["cusips_with_5plus_funds"]} bonds with five '
                   f'or more funds</p>')
        _db = [(("0–0.5" if d["hi"] == 0.5 else
                 "0.5–1" if d["hi"] == 1 else
                 "1–2" if d["hi"] == 2 else
                 "2–3" if d["hi"] == 3 else "3+"), d["n"])
               for d in sec.get("distribution", [])]
        if _db:
            out.append(_hist_svg(_db, "Dispersion range histogram"))
        out.append(_grid("ana-disp", ANA_DISP_COLS, rows[:10]))
        out.append(f'<p class="src">Widest 10 of {len(rows)}. Range = '
                   'highest minus lowest fund mark at the period end.</p>')
        # 3 gap
        sec = A["gap_convergence"]
        s = sec["summary"]
        rows = []
        for r in sec["rows"]:
            gcls = ' class="neg"' if r["gap"] <= -5 else (
                ' class="pos"' if r["gap"] >= 5 else "")
            rows.append("<tr>" + _ana_bond(r["cusip"])
                        + f'<td data-v="{r["last_trade"]}">{r["last_trade"]:.2f}</td>'
                        + f'<td data-v="{r["trade_date"]}">'
                          f'{_fmt_date(r["trade_date"])}</td>'
                        + f'<td data-v="{r["mark"]}">{r["mark"]:.2f}</td>'
                        + f'<td data-v="{r["period"]}">{_fmt_date(r["period"])}</td>'
                        + f'<td{gcls} data-v="{r["gap"]}">{r["gap"]:+.2f}</td>'
                        + f'<td data-v="{r["cusip"]}">{r["cusip"]}</td></tr>')
        out.append('<h2 id="gap">Trade-mark gap</h2>')
        q = sec.get("quartiles") or {}
        out.append(f'<p class="data-vintage">Points, last trade minus '
                   f'latest fund mark, n = {s["bonds_with_both"]} bonds '
                   f'with both</p>')
        _gb = [(d["label"], d["n"]) for d in sec.get("distribution", [])]
        if _gb:
            out.append(_hist_svg(_gb, "Gap distribution"))
        out.append(f'<p class="data-vintage">Median {s["median_gap"]:+.2f}; '
                   f'Q1 {q.get("q1", 0):+.2f}; Q3 {q.get("q3", 0):+.2f}; '
                   f'below −15: {s["gap_below_minus15"]}; above +5: '
                   f'{s["gap_above_plus5"]}</p>')
        out.append('<p class="src">Per-bond gap values are on '
                   '<a href="/leverage/bond-watch/">Bond Price Watch</a>.'
                   '</p>')
    # 4 twins
    sec = A["twin_basis"]
    s = sec["summary"]
    rows = []
    for r in sec["rows"]:
        rows.append("<tr>" + _ana_bond(r["registered_cusip"])
                    + f'<td data-v="{r["registered_cusip"]}">'
                      f'{r["registered_cusip"]}</td>'
                    + f'<td data-v="{r["registered_price"]}">'
                      f'{r["registered_price"]:.2f}</td>'
                    + f'<td data-v="{r["registered_date"]}">'
                      f'{_fmt_date(r["registered_date"])}</td>'
                    + f'<td data-v="{r["twin_cusip"]}">{r["twin_cusip"]}</td>'
                    + f'<td data-v="{r["twin_price"]}">{r["twin_price"]:.2f}</td>'
                    + f'<td data-v="{r["twin_date"]}">{_fmt_date(r["twin_date"])}</td>'
                    + f'<td data-v="{r["basis_pts"]}">{r["basis_pts"]:+.2f}</td>'
                    + "</tr>")
    out.append('<h2 id="twins">Twin-line basis</h2>')
    out.append(f'<p class="data-vintage">Points, last print of the '
               f'Rule 144A line minus last print of the registered '
               f'line, {s["pairs"]} pairs, mean absolute basis '
               f'{s["mean_abs_basis"]:.2f}</p>')
    out.append(_grid("ana-twin", ANA_TWIN_COLS, rows, sortable=False))
    # 5 liquidity (heatmap; per-bond counts live on Bond Price Watch)
    sec = A["liquidity"]
    s = sec["summary"]
    out.append('<h2 id="liquidity">Liquidity</h2>')
    out.append(f'<p class="data-vintage">Stored trades per week, '
               f'core watch, {_fmt_date(s["window_start"])} – '
               f'{_fmt_date(s["tape_end"])}</p>')
    _heat = sec.get("heatmap") or {}
    _hrows = _heat.get("rows") or []
    _hmx = max([c for r in _hrows for c in r["counts"]] + [1])
    _hpages = max(1, -(-len(_hrows) // _hsize))
    out.append(_heat_table({"weeks": _heat.get("weeks") or [],
                            "rows": _hrows[:_hsize]}, mx=_hmx))
    out.append(_pager_html(1, _hpages, _liq_url, "Liquidity"))
    out.append(f'<p class="data-vintage">Traded in the last 7 days '
               f'of the window: {s["traded_last_7d"]} of '
               f'{len(sec["rows"])} core bonds; silent: '
               f'{s["silent_last_7d"]}</p>')
    out.append('<p class="src">Per-bond trade counts are on '
               '<a href="/leverage/bond-watch/">Bond Price Watch</a>.'
               '</p>')
    # 6 events
    sec = A["event_study"]
    s = sec["summary"]
    out.append(f'<h2 id="events">Filings and prints</h2>')
    covered = ", ".join(s["issuers_covered"]) or "none"
    if sec["rows"]:
        rows = []
        for r in sorted(sec["rows"], key=lambda r: r["filing_date"],
                        reverse=True)[:15]:
            rows.append(
                f'<tr><td data-v="{esc(r["issuer"])}">{esc(r["issuer"].title())}</td>'
                + f'<td data-v="{r["form"]}">{r["form"]}</td>'
                + f'<td data-v="{r["filing_date"]}">{_fmt_date(r["filing_date"])}</td>'
                + _ana_bond(r["cusip"])
                + f'<td data-v="{r["print_before"]}">{r["print_before"]:.2f}</td>'
                + f'<td data-v="{r["before_date"]}">{_fmt_date(r["before_date"])}</td>'
                + f'<td data-v="{r["print_after"]}">{r["print_after"]:.2f}</td>'
                + f'<td data-v="{r["after_date"]}">{_fmt_date(r["after_date"])}</td>'
                + f'<td data-v="{r["change_pts"]}">{r["change_pts"]:+.2f}</td>'
                + f'<td data-v="{r["accession"]}">{r["accession"]}</td></tr>')
        out.append(f'<p class="data-vintage">Prints either side of '
                   f'material filings; issuers covered: '
                   f'{esc(covered)}</p>')
        out.append(_grid("ana-evt", ANA_EVT_COLS, rows, sortable=False))
        out.append(f'<p class="src">{len(sec["rows"])} filings carry '
                   'prints on both sides; the 15 most recent are '
                   'shown.</p>')
    else:
        out.append(f'<p class="data-vintage">Issuers covered: '
                   f'{esc(covered)}</p>')
        out.append('<p>No filing by a covered issuer in the window '
                   'carries prints on both sides of its filing '
                   'date.</p>')
    # 7 backtest
    sec = A["alert_backtest"]
    s = sec["summary"]
    rows = []
    for r in sorted(sec["rows"],
                    key=lambda r: r["marks_knowledge_date"] or "9999"
                    )[:12]:
        rows.append("<tr>" + _ana_bond(r["cusip"])
                    + f'<td data-v="{r["marks_fire_period"] or ""}">'
                      f'{_fmt_date(r["marks_fire_period"]) if r["marks_fire_period"] else "—"}</td>'
                    + f'<td data-v="{r["marks_knowledge_date"] or ""}">'
                      f'{_fmt_date(r["marks_knowledge_date"]) if r["marks_knowledge_date"] else "—"}</td>'
                    + f'<td data-v="{r["days_marks_before_news"] if r["days_marks_before_news"] is not None else -999}">'
                      f'{r["days_marks_before_news"] if r["days_marks_before_news"] is not None else "—"}</td>'
                    + f'<td data-v="{r["tape_fire_date"] or ""}">'
                      f'{_fmt_date(r["tape_fire_date"]) if r["tape_fire_date"] else "—"}</td>'
                    + f'<td data-v="{r["days_tape_before_news"] if r["days_tape_before_news"] is not None else -999}">'
                      f'{r["days_tape_before_news"] if r["days_tape_before_news"] is not None else "—"}</td>'
                    + f'<td data-v="{r["cusip"]}">{r["cusip"]}</td></tr>')
    out.append('<h2 id="backtest">Alert backtest</h2>')
    out.append(f'<p class="data-vintage">Standing flag rules on '
               f'history; marks knowledge date = period end + 60 '
               f'days; reference date 14 Oct 2026; fired on marks '
               f'before that date: '
               f'{s["fired_on_marks_before_the_news"]} of '
               f'{s["bonds_fired_by_either_leg"]}; earliest '
               f'{_fmt_date(s["earliest_knowledge_date"])} '
               f'({s["earliest_cusip"]})</p>')
    out.append(_grid("ana-back", ANA_BACK_COLS, rows))
    out.append(f'<p class="src">{len(sec["rows"])} bonds fired by '
               'either leg; the 12 earliest by marks knowledge date '
               'are shown.</p>')
    # 8 marks vs tape (Stage 2, 2026-10-20): disagreement between the
    # latest stored print and the full-universe fund median, from the
    # N-PORT panel. One table, both directions, engine-sortable.
    _np = _nport_panel()
    _det = _detail_data()
    _grow = []
    for _c, _pb in (_np.get("bonds") or {}).items():
        _L = _pb["latest"]
        _tr = (_det.get(_c) or {}).get("trades") or []
        if not _tr or _L.get("median") is None:
            continue
        _lp, _ld = _tr[0][2], _tr[0][0]
        _grow.append({"cusip": _c, "print": _lp, "date": _ld,
                      "median": _L["median"],
                      "period_end": _L["period_end"],
                      "gap": _lp - _L["median"],
                      "funds": _L["n_funds"]})
    _grow.sort(key=lambda r: r["gap"])
    out.append('<h2 id="marksgap">Fund marks vs the tape</h2>')
    if _grow:
        _gaps = sorted(r["gap"] for r in _grow)
        _gmed = _gaps[len(_gaps) // 2]
        _nbelow = sum(1 for r in _grow if r["gap"] < -15)
        _nabove = sum(1 for r in _grow if r["gap"] > 5)
        out.append(
            f'<p class="data-vintage">Latest stored print minus the '
            f'fund median, points, n = {len(_grow)} bonds with both '
            f'a print and a mark. Median gap {_gmed:+.2f}; '
            f'{_nbelow} bonds print more than 15 points below the '
            f'median; {_nabove} print more than 5 points above. The '
            f'mark is the median of fund-reported prices across the '
            f'full fund universe (SEC N-PORT), each dated at its own '
            f'modal report period; a gap mixes market '
            f'repricing with the fund reporting lag.</p>')
        _trs = []
        for r in _grow:
            _gcls = (' class="neg"' if r["gap"] <= -5 else
                     (' class="pos"' if r["gap"] >= 5 else ""))
            _trs.append(
                "<tr>" + _ana_bond(r["cusip"])
                + f'<td data-v="{r["print"]}">{r["print"]:.2f}</td>'
                + f'<td data-v="{r["date"]}">'
                  f'{_fmt_date(r["date"])}</td>'
                + f'<td data-v="{r["median"]}">{r["median"]:.2f}</td>'
                + f'<td data-v="{r["period_end"] or ""}">'
                  f'{_fmt_date(r["period_end"])}</td>'
                + f'<td{_gcls} data-v="{r["gap"]}">'
                  f'{r["gap"]:+.2f}</td>'
                + f'<td data-v="{r["funds"]}">{r["funds"]}</td>'
                + f'<td data-v="{r["cusip"]}">{r["cusip"]}</td></tr>')
        _gap_trs = _trs
        _gap_pages = max(1, -(-len(_trs) // 100))
        out.append(_grid("ana-npgap", NP_GAP_COLS, _trs[:100]))
        out.append(_pager_html(1, _gap_pages, _marks_url, "Fund marks"))
        out.append('<p class="src">Sorted by gap, lowest first; '
                   'select a column heading to re-sort.</p>')
    else:
        out.append('<p>No bond carries both a stored print and a '
                   'fund median in the current panel.</p>')
    # 9 coverage and concentration (Stage 2, 2026-10-20)
    _cov = _np.get("coverage") or {}
    _lq = _np.get("latest_quarter", "")
    _lat = [(_c, _pb["latest"]) for _c, _pb in
            (_np.get("bonds") or {}).items()
            if _pb["latest"].get("quarter") == _lq]
    out.append('<h2 id="coverage">Fund coverage and concentration</h2>')
    out.append(
        f'<p class="data-vintage">In the latest N-PORT archive '
        f'({_lq}), funds report a priced position in '
        f'{_cov.get("priced_latest", 0)} of '
        f'{_cov.get("registry", 0)} registry bonds '
        f'({_cov.get("priced_latest", 0) / max(_cov.get("registry", 1), 1) * 100:.0f}%), '
        f'and a position of any kind in '
        f'{_cov.get("held_latest", 0)}. '
        f'{_cov.get("zero_holder", 0)} registry rows have no holder '
        f'in the quarter; the bonds among them are listed on the '
        f'<a href="/leverage/zero-holders/">zero-holder page</a>.</p>')
    _conc = sorted(
        ((_c, _L) for _c, _L in _lat
         if _L.get("balance") and _L["balance"] >= 25_000_000
         and _L.get("top1") is not None),
        key=lambda x: -x[1]["top1"])[:12]
    if _conc:
        out.append('<h3>Most concentrated holdings</h3>')
        out.append('<p class="data-vintage">Largest single-fund '
                   'share of the reported balance; bonds with at '
                   'least $25 million reported.</p>')
        _trs = []
        for _c, _L in _conc:
            _trs.append(
                "<tr>" + _ana_bond(_c)
                + f'<td data-v="{_L["balance"]}">'
                  f'${_L["balance"]:,.0f}</td>'
                + f'<td data-v="{_L["top1"]}">'
                  f'{_L["top1"] * 100:.1f}</td>'
                + f'<td data-v="{_L["top5"]}">'
                  f'{_L["top5"] * 100:.1f}</td>'
                + f'<td data-v="{_L["n_funds"]}">{_L["n_funds"]}</td>'
                + f'<td data-v="{_c}">{_c}</td></tr>')
        out.append(_grid("ana-conc", NP_CONC_COLS, _trs))
    _disp = sorted(
        ((_c, _L) for _c, _L in _lat
         if _L.get("n_funds", 0) >= 10 and _L.get("p10") is not None
         and _L.get("p90") is not None),
        key=lambda x: -(x[1]["p90"] - x[1]["p10"]))[:12]
    if _disp:
        out.append('<h3>Widest mark dispersion</h3>')
        out.append('<p class="data-vintage">Widest p10 to p90 range '
                   'of fund marks; bonds with at least ten funds '
                   'reporting a priced position.</p>')
        _trs = []
        for _c, _L in _disp:
            _trs.append(
                "<tr>" + _ana_bond(_c)
                + f'<td data-v="{_L["median"]}">{_L["median"]:.2f}</td>'
                + f'<td data-v="{_L["p10"]}">{_L["p10"]:.2f}</td>'
                + f'<td data-v="{_L["p90"]}">{_L["p90"]:.2f}</td>'
                + f'<td data-v="{_L["p90"] - _L["p10"]}">'
                  f'{_L["p90"] - _L["p10"]:.2f}</td>'
                + f'<td data-v="{_L["n_funds"]}">{_L["n_funds"]}</td>'
                + f'<td data-v="{_c}">{_c}</td></tr>')
        out.append(_grid("ana-disp2", NP_DISP_COLS, _trs))
    out.append('<h2 id="sources">Sources and coverage</h2>')
    out.append(
        f'<p>Trades: FINRA TRACE via the public lookup, collected '
        f'every 15 minutes for the core watch and hourly for the '
        f'benchmark tier; the stored tape runs '
        f'{_fmt_date(liq_s["window_start"])} to '
        f'{_fmt_date(liq_s["tape_end"])}. '
        f'The dataset holds '
        f'{liq_s.get("total_trades_all", liq_s["total_trades"]):,} '
        f'stored trades in total. '
        'Marks: SEC N-PORT bulk filings. A fund mark is a period-end '
        'valuation, not a trade price, and filings lag the period '
        'end by about 60 days. Yields are yield-to-worst, '
        'semiannual 30/360; spreads are against the interpolated '
        'US Treasury curve. Benchmark bonds carry no fund marks. '
        'Quantities the window cannot support are stated as '
        'absent, not estimated. Issued ($M) is the note\'s '
        'original amount issued, from the issuer\'s pricing '
        'filing where one is on record; the column is blank '
        'where no held source states an amount.</p>')
    out.append(TABLE_ENGINE_JS)
    _lede = ("Bond prices, trends, curves and holders by issuer, "
             "from the FINRA tape and SEC fund filings.")
    extras = {}
    for n in range(2, _hpages + 1):
        eb = [frontmatter("Bond Analytics", _lede, as_of,
                          url=_liq_url(n))]
        eb.append(strip_html)
        eb.append(f'<h2 id="liquidity">Liquidity - page {n} of '
                  f'{_hpages}</h2>')
        eb.append(f'<p class="data-vintage">Stored trades per week, '
                  f'core watch, {_fmt_date(liq_s["window_start"])} – '
                  f'{_fmt_date(liq_s["tape_end"])}</p>')
        eb.append(_heat_table(
            {"weeks": _heat.get("weeks") or [],
             "rows": _hrows[(n - 1) * _hsize:n * _hsize]}, mx=_hmx))
        eb.append(_pager_html(n, _hpages, _liq_url, "Liquidity"))
        extras[f"liquidity-p{n}"] = "\n".join(eb)
    for n in range(2, _gap_pages + 1):
        eb = [frontmatter("Bond Analytics", _lede, as_of,
                          url=_marks_url(n))]
        eb.append(strip_html)
        eb.append(f'<h2 id="marksgap">Fund marks vs the tape - page '
                  f'{n} of {_gap_pages}</h2>')
        eb.append(_grid("ana-npgap", NP_GAP_COLS,
                        _gap_trs[(n - 1) * 100:n * 100]))
        eb.append(_pager_html(n, _gap_pages, _marks_url, "Fund marks"))
        eb.append(TABLE_ENGINE_JS)
        extras[f"marks-p{n}"] = "\n".join(eb)
    return "\n".join(out), extras

def _projects():
    """Standing project pages, gated list in data/projects.json. A
    project earns a page only when it is a named deal in the leverage
    program registry with material scale and a running record of
    dated developments, or when Arvin names it. The list is the gate:
    nothing renders a project page unless it is entered here."""
    p = os.path.join(DATA, "projects.json")
    if not os.path.exists(p):
        return []
    try:
        return json.load(open(p)).get("projects", [])
    except Exception:
        return []


PROJECT_DEV_COLS = [("Date", 104, 84, False),
                    ("Development", 660, 240, False),
                    ("Source", 190, 110, False)]


def _fmt_dev_date(d):
    """Development dates may carry month precision (YYYY-MM) when
    the record fixes only the month; render those as Mon YYYY."""
    if d and len(d) == 7:
        from datetime import datetime as _dm
        return _dm.strptime(d, "%Y-%m").strftime("%b %Y")
    return _fmt_date(d)
PROJECT_PARTY_COLS = [("Party", 320, 160, False),
                      ("Role", 560, 220, False)]
PROJECT_INST_COLS = [("Instrument", 300, 160, False),
                     ("Terms on record", 620, 240, False)]


def project_pages():
    """One standing page per gated project at /projects/<slug>/:
    summary, key facts, parties, and the dated development record,
    newest first. Pages regenerate from data/projects.json on every
    build, so an appended development updates the page."""
    pages = {}
    for pr in _projects():
        devs = sorted(pr.get("developments", []),
                      key=lambda d: d["date"], reverse=True)
        latest = devs[0]["date"] if devs else ""
        lede = pr.get("lede", "")
        out = [frontmatter(pr["name"], lede, latest)]
        out.append('<p class="src"><a href="/projects/">'
                   '&larr; Projects</a></p>')
        if pr.get("sponsor_key"):
            out.append(
                f'<p class="src">Sponsor: <a href="/leverage/issuer/'
                f'{pr["sponsor_key"]}/">{esc(pr.get("sponsor", ""))}'
                f'</a>. Bond record for the sponsor sits on its '
                f'issuer page.</p>')
        for para in pr.get("summary", []):
            out.append(f"<p>{para}</p>")
        facts = pr.get("facts") or []
        if facts:
            out.append('<dl class="bw-summary">'
                       + "".join(
                           f'<div class="bw-sum-item"><dt>{esc(k)}'
                           f'</dt><dd>{esc(v)}</dd></div>'
                           for k, v in facts) + "</dl>")
        parties = pr.get("parties") or []
        if parties:
            out.append("<h2>Parties</h2>")
            prows = [f'<tr><td data-v="{esc(x["name"])}">'
                     f'{esc(x["name"])}</td>'
                     f'<td data-v="">{esc(x["role"])}</td></tr>'
                     for x in parties]
            out.append(_grid(f'proj-p-{pr["slug"]}',
                             PROJECT_PARTY_COLS, prows,
                             sortable=False))
        insts = pr.get("instruments") or []
        if insts:
            out.append("<h2>Financing on record</h2>")
            if pr.get("instruments_note"):
                out.append(f'<p class="src">'
                           f'{pr["instruments_note"]}</p>')
            irows = []
            for x in insts:
                nm = esc(x["name"])
                if x.get("url"):
                    nm = (f'<a href="{esc(x["url"])}">{nm}</a>')
                irows.append(
                    f'<tr><td data-v="{esc(x["name"])}">{nm}</td>'
                    f'<td data-v="">{esc(x["detail"])}</td></tr>')
            out.append(_grid(f'proj-i-{pr["slug"]}',
                             PROJECT_INST_COLS, irows,
                             sortable=False))
        if devs:
            out.append("<h2>Developments</h2>")
            out.append('<p class="src">The running record, newest '
                       'first. Each entry is dated by the event, '
                       'not by when it was collected.</p>')
            drows = []
            for d in devs:
                src = esc(d.get("source_label", ""))
                if d.get("source_url"):
                    src = (f'<a href="{esc(d["source_url"])}">'
                           f'{src}</a>')
                if d.get("grade"):
                    src += (f'<span class="cell-sub">Grade '
                            f'{esc(d["grade"])}</span>')
                drows.append(
                    f'<tr><td data-v="{d["date"]}">'
                    f'{_fmt_dev_date(d["date"])}</td>'
                    f'<td data-v=""><span class="bond-name">'
                    f'{esc(d["title"])}</span>'
                    f'<span class="bond-sub">{esc(d["detail"])}'
                    f'</span></td>'
                    f'<td data-v="">{src}</td></tr>')
            out.append(_grid(f'proj-d-{pr["slug"]}',
                             PROJECT_DEV_COLS, drows, sortable=False))
        stories = pr.get("stories") or []
        if stories:
            out.append("<h2>Coverage on this site</h2>")
            items = "".join(
                f'<li><a href="/stories/{s["slug"]}/">'
                f'{esc(s["title"])}</a></li>' for s in stories)
            out.append(f"<ul>{items}</ul>")
        out.append('<p class="src">Record maintained by the AI '
                   'infrastructure leverage monitor: SEC filings, '
                   'county and municipal records, and the news '
                   'operation&rsquo;s own coverage, each entry '
                   'graded at collection.</p>')
        out.append(TABLE_ENGINE_JS)
        pages[pr["slug"]] = "\n".join(out)
    return pages


def projects_index():
    """Section index at /projects/: the gated project list with the
    latest development on each."""
    projs = _projects()
    rows = []
    for pr in projs:
        devs = sorted(pr.get("developments", []),
                      key=lambda d: d["date"], reverse=True)
        latest = devs[0] if devs else {}
        rows.append(
            f'<tr><td data-v="{esc(pr["name"])}">'
            f'<a class="bond-link" href="/projects/{pr["slug"]}/">'
            f'<span class="bond-name">{esc(pr["name"])}</span>'
            f'<span class="bond-sub">{esc(pr.get("location", ""))}'
            f'</span></td>'
            f'<td data-v="{esc(pr.get("sponsor", ""))}">'
            f'{esc(pr.get("sponsor", ""))}</td>'
            f'<td data-v="{latest.get("date", "")}">'
            f'{_fmt_dev_date(latest["date"]) if latest else "—"}</td>'
            f'<td data-v="">{esc(latest.get("title", ""))}</td></tr>')
    cols = [("Project", 300, 180, False), ("Sponsor", 150, 100, False),
            ("Latest development", 130, 92, False),
            ("What happened", 420, 200, False)]
    body = [frontmatter(
        "Projects",
        "Standing pages for the largest tracked data center "
        "projects: the financing, the parties, and the dated record "
        "of developments, updated as events land.",
        "")]
    body.append('<p>The leverage program follows named projects '
                'through filings, county records and permitting. A '
                'project earns a standing page when its scale and '
                'record warrant one; the list is deliberately short. '
                'Each page carries the development record in date '
                'order and updates when a new filing, vote or '
                'decision lands.</p>')
    body.append(_grid("proj-index", cols, rows, sortable=False))
    body.append(TABLE_ENGINE_JS)
    return "\n".join(body)


def issuer_pages():
    """One page per issuer group at /leverage/issuer/<key>/:
    summary strip, bonds grid, monthly trend (ECharts + table),
    three-date yield curve, fund holders. Moved off the analytics
    page 2026-10-15 so one exhibit has one owner."""
    from datetime import datetime as _dtm, timezone as _tz
    A = _analytics_data().get("analyses", {})
    if not A:
        return {}
    iss = A.get("issuers") or {}
    groups = iss.get("groups") or []
    as_of = _analytics_data().get("as_of", "")
    fam_labels = {"core": "Core watch", "benchmark": "Benchmark",
                  "project": "Project"}
    pages = {}
    for g in groups:
        fam = fam_labels.get(g["family"], "Benchmark")
        has_marks = any(b["mark"] is not None for b in g["bonds"])
        lede = (f"{fam} issuer, {g['n_bonds']} bonds: prices, "
                f"trend, yield curve and fund holders from the "
                f"FINRA tape and SEC fund filings.")
        out = [frontmatter(g["name"], lede, as_of)]
        out.append('<p class="src"><a href="/leverage/bond-analytics/">'
                   '&larr; Bond Analytics</a></p>')
        _ent = _entity_links()[0].get(g["key"])
        if _ent:
            out.append(
                f'<p class="src">Cross-dataset record: '
                f'<a href="/entities/{_ent[0]}/">Entity Index</a>. '
                f'Name forms, swaps panel row and fund-mark coverage '
                f'for this issuer.</p>')
        for _pr in _projects():
            if _pr.get("sponsor_key") == g["key"]:
                out.append(
                    f'<p class="src">Tracked project: '
                    f'<a href="/projects/{_pr["slug"]}/">'
                    f'{esc(_pr["name"])}</a>. Standing page with '
                    f'the project record and its dated '
                    f'developments.</p>')
        med = (f'{g["median_last"]:.2f}'
               if g["median_last"] is not None else "n/a")
        strip = [("Bonds", f"{g['n_bonds']}"),
                 ("Median last print", med),
                 ("Below 90", f"{g['below90']} of {g['n_priced']} priced"),
                 ("Latest trade",
                  _fmt_date(g["latest_trade"])
                  if g["latest_trade"] else "—")]
        if has_marks and g.get("fund_period"):
            strip.append(("Fund marks to", _fmt_date(g["fund_period"])))
        out.append('<dl class="bw-summary">'
                   + "".join(f'<div class="bw-sum-item"><dt>{esc(k)}'
                             f'</dt><dd>{esc(v)}</dd></div>'
                             for k, v in strip) + "</dl>")
        _fil = _issuer_filings().get(g["key"]) or []
        if _fil:
            out.append("<h2>Filings and developments</h2>")
            out.append('<p class="src">Material SEC filings recorded '
                       'by the daily filings pull. Figures are as '
                       'stated in the filing itself.</p>')
            frows = []
            for e in _fil:
                frows.append(
                    f'<tr><td data-v="{e["date"]}">'
                    f'{_fmt_date(e["date"])}</td>'
                    f'<td data-v="{esc(e["form"])}">'
                    f'<a href="{esc(e["url"])}">{esc(e["form"])}</a>'
                    f'<span class="cell-sub">Accession '
                    f'{esc(e["accession"])}</span></td>'
                    f'<td data-v=""><span class="bond-name">'
                    f'{esc(e["title"])}</span>'
                    f'<span class="bond-sub">{esc(e["detail"])}'
                    f'</span></td></tr>')
            out.append(_grid(f'iss-fil-{g["key"]}',
                             ISSUER_FILING_COLS, frows,
                             sortable=False))
        out.append("<h2>Bonds</h2>")

        def brow(b, sec_marks):
            gap = (b["last_price"] - b["mark"]) if (
                b["last_price"] is not None
                and b["mark"] is not None) else None
            pcls = ' class="neg"' if (
                b["last_price"] is not None
                and b["last_price"] < 90) else ""
            cells = [_ana_bond(b["cusip"])]
            if b["last_price"] is not None:
                cells.append(f'<td{pcls} data-v="{b["last_price"]}">'
                             f'{b["last_price"]:.2f}</td>')
                cells.append(f'<td data-v="{b["last_date"]}">'
                             f'{_fmt_date(b["last_date"])}</td>')
            else:
                cells.append('<td data-v="-999">n/a</td>')
                cells.append('<td data-v="">no trades in the '
                             'stored record</td>')
            if sec_marks:
                if gap is not None:
                    gcls = ' class="neg"' if gap <= -5 else (
                        ' class="pos"' if gap >= 5 else "")
                    cells.append(f'<td{gcls} data-v="{gap}">'
                                 f'{gap:+.2f}</td>')
                    _mk = f'{b["mark"]:.2f}'
                    if b.get("mark_period"):
                        _mk += (f'<span class="cell-sub">Period ended '
                                f'{_fmt_date(b["mark_period"])}</span>')
                    cells.append(f'<td data-v="{b["mark"]}">{_mk}</td>')
                else:
                    cells.append('<td data-v="-999">n/a</td>')
                    cells.append('<td data-v="-999">n/a</td>')
            cells.append(f'<td data-v="{b["coupon"] or -1}">'
                         f'{("%.3f" % b["coupon"]).rstrip("0").rstrip(".") if b["coupon"] is not None else "—"}'
                         f'</td>')
            cells.append(f'<td data-v="{b["maturity"] or ""}">'
                         f'{_fmt_date(b["maturity"]) if b["maturity"] else "—"}</td>')
            cells.append(_rating_cell(b["cusip"]))
            cells.append(f'<td data-v="{b["cusip"]}">{b["cusip"]}</td>')
            return "<tr>" + "".join(cells) + "</tr>"

        # A family with more than one issuing vehicle splits into
        # sub-sections headed by the vehicle; the legal issuer of
        # record stays on each bond row. Single-vehicle families and
        # non-crosswalk groups render as one grid, as before.
        sections = [(None, g["bonds"])]
        if g.get("family_name"):
            by_veh, veh_order = {}, []
            for b in g["bonds"]:
                lab = b.get("vehicle") or b.get("issuer") or ""
                if lab not in by_veh:
                    by_veh[lab] = []
                    veh_order.append(lab)
                by_veh[lab].append(b)
            if len(veh_order) > 1:
                sections = [(lab, by_veh[lab]) for lab in veh_order]
        for si, (lab, sbonds) in enumerate(sections):
            if lab is not None:
                out.append(f"<h3>{esc(lab)}</h3>")
            # One table shape per page (spec 3.3): the gap and
            # mark columns appear in every section or in none,
            # decided by the whole page's marks coverage.
            sec_marks = has_marks
            tid = f'iss-b-{g["key"]}' + (
                f"-{si}" if lab is not None else "")
            out.append(_grid(tid,
                             ISSUER_BOND_COLS_M if sec_marks
                             else ISSUER_BOND_COLS,
                             [brow(b, sec_marks) for b in sbonds]))
        _fent = _flow_data().get("families", {}).get(g["key"])
        if _fent:
            out.append(_flow_panel(_fent, fam=True))
        if len(g["monthly"]) >= 2:
            out.append("<h2>Month-end trend</h2>")
            price, vol = [], []
            for m in g["monthly"]:
                y, mo = int(m["month"][:4]), int(m["month"][5:7])
                ms = int(_dtm(y, mo, 15, 12, tzinfo=_tz.utc)
                         .timestamp() * 1000)
                if m["median"] is not None:
                    price.append([ms, m["median"]])
                vol.append([ms, m["trades"]])
            chart_data = {g["key"]: {"name": g["name"],
                                      "price": price, "vol": vol}}
            out.append('<p class="bond-chart-cap">Month-end median '
                       'last print and trades per month. A month '
                       'point exists only when at least one of the '
                       'issuer&rsquo;s bonds traded that month.</p>')
            out.append(f'<div id="issuer-chart-e" '
                       f'class="issuer-chart-e" role="img" '
                       f'aria-label="Issuer trend chart: '
                       f'{esc(g["name"])}">'
                       f'{_median_path_svg(g["monthly"], g["name"])}'
                       f'</div>')
            out.append('<script type="application/json" '
                       'id="issuer-chart-data">'
                       + json.dumps(chart_data, separators=(",", ":"))
                       + "</script>")
            mrows = []
            for m in reversed(g["monthly"][-13:]):
                lab = _dtm.strptime(m["month"], "%Y-%m") \
                    .strftime("%b %Y")
                share = (f'{100.0 * m["below90"] / m["priced"]:.0f}%'
                         if m["priced"] else "—")
                mmed = (f'{m["median"]:.2f}'
                        if m["median"] is not None else "—")
                medv = m["median"] if m["median"] is not None \
                    else -999
                mrows.append(
                    f'<tr><td data-v="{m["month"]}">{lab}</td>'
                    f'<td data-v="{m["trades"]}">{m["trades"]:,}</td>'
                    f'<td data-v="{medv}">{mmed}</td>'
                    f'<td data-v="{m["priced"]}">{m["priced"]}</td>'
                    f'<td data-v="{m["below90"]}">{share}</td></tr>')
            out.append(_grid(f'iss-m-{g["key"]}', ISSUER_MO_COLS,
                             mrows, sortable=False))
        if g["curves"]:
            out.append("<h2>Yield curve - last trade on or before "
                       "each date</h2>")
            out.append(_issuer_curve_svg(g["curves"]))
            out.append('<p class="src">Filled dots: latest, '
                       'hollow squares: Jul 2026, triangles: '
                       'Dec 2025. One point per bond, yield at '
                       'its last trade on or before the date.</p>')
        if g["funds"]:
            out.append("<h2>Fund holders on record</h2>")
            out.append(f'<p class="data-vintage">Principal '
                       f'across the issuer&rsquo;s bonds, '
                       f'N-PORT report period '
                       f'{_fmt_date(g["fund_period"]) if g["fund_period"] else "—"}</p>')
            frows = []
            for f in g["funds"]:
                frows.append(
                    f'<tr><td data-v="{esc(f["complex"])}">'
                    f'{esc(f["complex"])}</td>'
                    f'<td data-v="{f["principal"]}">'
                    f'{f["principal"] / 1e6:,.0f}</td>'
                    f'<td data-v="{f["positions"]}">'
                    f'{f["positions"]}</td>'
                    f'<td data-v="{f["bonds"]}">{f["bonds"]}</td>'
                    f'</tr>')
            out.append(_grid(f'iss-f-{g["key"]}', ISSUER_FUND_COLS,
                             frows, sortable=False))
        prov = ('Sources: FINRA TRACE via the public lookup '
                '(trades) and SEC N-PORT bulk filings (fund marks '
                'and holders). '
                f'Coverage: {g["trades_stored"]:,} trades are '
                f'stored in the dataset for this issuer\'s bonds. '
                'Issued ($M) is the note\'s original amount issued, '
                'from the issuer\'s pricing filing where one is on '
                'record; blank where no held source states it.')
        if has_marks:
            prov += (' A fund mark is a period-end valuation, not '
                     'a trade price; holder data is positions at '
                     'the report period, not trading activity. '
                     'TRACE names no buyer or seller.')
        out.append(f'<p class="src">{prov}</p>')
        out.append('<script defer src="/js/echarts.min.js"></script>')
        out.append('<script defer '
                   'src="/js/issuer_chart.js"></script>')
        out.append(TABLE_ENGINE_JS)
        pages[g["key"]] = "\n".join(out)
    return pages


def leverage_monitor_page():
    """Program overview page: mandate, coverage, status, indicators,
    latest changes, cadence and archive. Aggregates only; per-bond
    values live on Bond Price Watch, distributions on Bond Analytics."""
    _reg_raw = _registry()
    reg = (list(_reg_raw.values()) if isinstance(_reg_raw, dict)
           else _reg_raw)
    tiers = {}
    for b in reg:
        tiers[b.get("watch")] = tiers.get(b.get("watch"), 0) + 1
    tp_path = os.path.join(DATA, "trace_prints.json")
    tp = json.load(open(tp_path)) if os.path.exists(tp_path) else {}
    pr = tp.get("prints", [])
    priced = [p for p in pr if p.get("last_trade_price") is not None]
    below90 = sum(1 for p in priced if p["last_trade_price"] < 90)
    traded7 = sum(1 for p in pr if (p.get("trades_seen") or 0) > 0)
    gaps = sorted(p["last_trade_price"] - p["latest_fund_mark"]
                  for p in priced
                  if p.get("latest_fund_mark") is not None)
    med_gap = gaps[len(gaps) // 2] if gaps else 0.0
    bw_path = os.path.join(DATA, "bond_watch.json")
    bw = json.load(open(bw_path)) if os.path.exists(bw_path) else {}
    ana = _analytics_data().get("analyses", {})
    liq = (ana.get("liquidity") or {}).get("summary", {})
    disp = (ana.get("fund_dispersion") or {})
    sig_path = os.path.join(DATA, "bond_signals.json")
    sig = json.load(open(sig_path)) if os.path.exists(sig_path) else {}
    n_sig = len(sig.get("signals", []))
    tape_end = liq.get("tape_end") or _tape_latest(tp)
    alm = os.path.expanduser("~/workspace/ai-leverage-monitor/data")
    sweep = {}
    sw_path = os.path.join(alm, "issuer_sweep.json")
    if os.path.exists(sw_path):
        try:
            sweep = json.load(open(sw_path))
        except Exception:
            sweep = {}
    strip = [
        ("Bonds in registry", f"{len(reg)}"),
        ("Core watch", f"{tiers.get('daily', 0)}"),
        ("Benchmark", f"{tiers.get('benchmark', 0)}"),
        ("Trades in the dataset", f"{liq.get('total_trades_all', 0):,}"),
        ("Fund marks to", _fmt_date(bw.get("marks_as_of"))
         if bw.get("marks_as_of") else "n/a"),
    ]
    strip_html = ('<dl class="bw-summary">'
                  + "".join(f"<div class=\"bw-sum-item\"><dt>{esc(k)}</dt>"
                            f"<dd>{esc(v)}</dd></div>"
                            for k, v in strip) + "</dl>")
    tiles = [
        ("Median gap to fund mark", f"{med_gap:+.1f} pts"),
        ("Trading below 90", f"{below90} of {len(priced)} priced"),
        ("Traded in the last 7 days", f"{traded7} of {len(pr)}"),
        ("Signals, last 48 h", f"{n_sig}"),
        ("Median fund-mark range",
         f"{disp.get('median_range_pts', 0):.2f} pts"),
    ]
    tiles_html = ('<dl class="bw-summary">'
                  + "".join(f"<div class=\"bw-sum-item\"><dt>{esc(k)}</dt>"
                            f"<dd>{esc(v)}</dd></div>"
                            for k, v in tiles) + "</dl>")
    cov = [
        ("TRACE prints, core", "FINRA public lookup",
         f"{tiers.get('daily', 0)} bonds",
         "Every 15 min, market hours", _fmt_date(tape_end)),
        ("TRACE prints, benchmark", "FINRA public lookup",
         f"{tiers.get('benchmark', 0)} bonds",
         "Hourly, market hours", _fmt_date(tape_end)),
        ("Fund marks", "SEC N-PORT bulk data",
         f"{bw.get('cusips_tracked', 0)} bonds",
         "On filing; ~60-day lag",
         _fmt_date(bw.get("marks_as_of")) if bw.get("marks_as_of")
         else "—"),
        ("Market aggregates", "FINRA Query API", "US corporate market",
         "Daily, T+1", "—"),
        ("Treasury curve", "FRED archive; market tables",
         "2, 5, 10, 30 year", "Daily", "—"),
        ("Issuer discovery", "FINRA issuer search",
         f"{len(_watched_issuers())} issuers",
         "Daily", _fmt_date(sweep.get("date")) if sweep.get("date")
         else "—"),
        ("Collateral and ratings", "Public sources",
         "Issuer families", "Monthly", "—"),
    ]
    cov_rows = "".join(
        f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td>"
        f"<td>{esc(d)}</td><td>{esc(e)}</td></tr>"
        for a, b, c, d, e in cov)
    cov_html = ('<div class="market-table-scroll">'
                '<table class="market-table"><thead><tr><th>Layer</th>'
                "<th>Source</th><th>Universe</th><th>Cadence</th>"
                f"<th>Latest</th></tr></thead><tbody>{cov_rows}"
                "</tbody></table></div>")
    changes = []
    log_path = os.path.join(alm, "signals_log.jsonl")
    if os.path.exists(log_path):
        try:
            lines = [ln for ln in open(log_path).read().splitlines()
                     if ln.strip()]
            for ln in lines[-6:][::-1]:
                srec = json.loads(ln)
                changes.append(
                    (srec.get("trade_date", ""),
                     f"{srec.get('level', '').upper()} - "
                     f"{srec.get('issuer', '')} - {srec.get('rule', '')}"
                     f" - print {srec.get('price', '')}"))
        except Exception:
            changes = []
    if sweep.get("new_entries"):
        changes.append(
            (sweep.get("date", ""),
             f"Issuer sweep: {len(sweep['new_entries'])} new bonds "
             f"added to the registry"))
    if not changes:
        changes = [("", "No signal or registry changes in the "
                    "current log window.")]
    ch_rows = "".join(
        f"<tr><td>{_fmt_date(d) if d else '—'}</td><td>{esc(t)}</td>"
        "</tr>" for d, t in changes[:6])
    ch_html = ('<div class="market-table-scroll">'
               '<table class="market-table"><thead><tr><th>Date</th>'
               f"<th>Change</th></tr></thead><tbody>{ch_rows}"
               "</tbody></table></div>")
    body = frontmatter(
        "AI Infrastructure Leverage Monitor",
        "The debt behind the AI infrastructure buildout, priced "
        "against FINRA TRACE and SEC filings.",
        f"Data to {_fmt_date(tape_end)}" if tape_end else "")
    body += (
        "<p>Issuers: those in working paper KR-WP-2026-27. "
        "Sources: FINRA TRACE and SEC filings, as they arrive.</p>\n"
        + strip_html
        + '<nav class="bw-anchor"><a href="#indicators">Indicators</a>'
          ' / <a href="#coverage">Coverage</a> / '
          '<a href="#changes">Latest changes</a> / '
          '<a href="#archive">Cadence and archive</a></nav>\n'
        + '<h2 id="indicators">Indicators</h2>\n'
        + tiles_html
        + '<p class="data-vintage">Per-bond values: '
          '<a href="/leverage/bond-watch/">Bond Price Watch</a>. '
          'Distributions and curves: '
          '<a href="/leverage/bond-analytics/">Bond Analytics</a>.'
          '</p>\n'
        + '<h2 id="coverage">Coverage</h2>\n'
        + cov_html
        + '<h2 id="changes">Latest changes</h2>\n'
        + ch_html
        + '<h2 id="archive">Cadence and archive</h2>\n'
        '<p class="data-vintage">Weekly issue: Mondays, to this '
        'section. Daily filings pull: 06:23 ET. Signal evaluation: '
        'every collection cycle; Tier-1 signals are reported the '
        'hour they fire.</p>\n'
        '<p>Working paper: <a href="https://research.kilambi.com/'
        'paper-27.html">KR-WP-2026-27, Visible Money, Invisible '
        'Counterparties</a>. Weekly issues (PDF): '
        '<a href="/files/ai-leverage-monitor-2026-10-18.pdf">'
        '18 October 2026</a> / '
        '<a href="/files/ai-leverage-monitor-2026-10-11.pdf">'
        '11 October 2026</a> / '
        '<a href="/files/ai-leverage-monitor-2026-10-04.pdf">'
        '4 October 2026</a> / '
        '<a href="/files/ai-leverage-monitor-2026-09-29.pdf">'
        '29 September 2026</a> / '
        '<a href="/files/ai-leverage-monitor-2026-09-28.pdf">'
        '28 September 2026</a> / '
        '<a href="/files/ai-leverage-monitor-2026-09-27.pdf">'
        '27 September 2026</a>.</p>\n')
    return body


def bond_pages():
    import datetime as _dt
    reg_path = os.path.join(DATA, "bonds.json")
    if not os.path.exists(reg_path):
        return 0
    reg = json.load(open(reg_path))["bonds"]
    det_all = _detail_data()
    bw_path = os.path.join(DATA, "bond_watch.json")
    bw_rows = {}
    if os.path.exists(bw_path):
        bw_rows = {r["cusip"]: r
                   for r in json.load(open(bw_path))["rows"]}
    _tp = _trace_prints()
    prints = {p["cusip"]: p for p in _tp["prints"]}
    tape_stamp = _tape_latest(_tp)
    curve = _treasury_curve()
    outdir = os.path.join(SITE, "content", "leverage", "bond")
    os.makedirs(outdir, exist_ok=True)
    import re as _re
    reg = [b for b in reg if _re.fullmatch(r"[A-Z0-9]{9}", b["cusip"])
           and b["cusip"] not in ("000000000", "999999999")]
    ordered = sorted(reg, key=lambda b: ((b.get("issuer") or "").lower(),
                                         b.get("maturity") or "",
                                         b["cusip"]))
    n = 0
    for idx, b in enumerate(ordered):
        cusip = b["cusip"]
        det = det_all.get(cusip) or {"marks": [], "funds": [],
                                     "fund_period": None, "trades": []}
        marks = det["marks"]          # [period, price, positions, principal]
        trades = det["trades"]        # [date, time, price, yield, vol, side]
        p = prints.get(cusip)
        bw = bw_rows.get(cusip)
        coup = b.get("coupon_pct")
        mat = b.get("maturity")
        # snapshot basis: last trade if any, else latest mark
        last_trade = None
        if trades:
            t0 = trades[0]
            last_trade = (t0[2], t0[0], t0[1])
        latest_mark = None
        if marks:
            latest_mark = (marks[-1][1], marks[-1][0], marks[-1][2])
        basis_price = basis_date = basis_kind = None
        if last_trade:
            basis_price, basis_date, basis_kind = last_trade[0], last_trade[1], "trade"
        elif latest_mark:
            basis_price, basis_date, basis_kind = latest_mark[0], latest_mark[1], "mark"
        y = spread = dur = None
        if basis_price is not None and coup and mat:
            y = _ytw(basis_price, coup, mat, basis_date, b)
            if y is not None:
                yrs = (_dt.date.fromisoformat(mat)
                       - _dt.date.fromisoformat(basis_date)).days / 365.25
                # One reference basis per label (spec 2.2): the
                # Treasury yield interpolated at the basis date,
                # for the trade and mark bases alike.
                tsy = _tsy_on(basis_date, yrs)
                if tsy is not None:
                    spread = round((y - tsy) * 100)
            dur = _mod_duration(basis_price, coup, mat, basis_date, y)
        items = []
        if last_trade:
            items.append(("Last TRACE trade",
                          f"{last_trade[0]:.2f}",
                          [f"{_fmt_date(last_trade[1])}, "
                           f"{last_trade[2][:5]} ET"]))
        if latest_mark:
            items.append(("Fund mark (median)",
                          f"{latest_mark[0]:.2f}",
                          [f"Period ended "
                           f"{_fmt_date(latest_mark[1])}",
                           f"Median of {latest_mark[2]} fund marks"]))
        if last_trade and latest_mark:
            items.append(("Gap to fund mark",
                          f"{last_trade[0] - latest_mark[0]:+.2f} pts",
                          []))
        if y is not None:
            _y_label = ("Yield to worst" if b.get("call_schedule")
                        else "Yield to maturity")
            items.append((_y_label, f"{y:.2f}%", []))
        if spread is not None:
            items.append(("Spread to Treasury", f"{spread:+,} bp", []))
        if dur is not None:
            items.append(("Modified duration", f"{dur:.2f}", []))
        if dur is not None and basis_price is not None:
            items.append(("DV01",
                          f"${dur * basis_price:,.0f} per $1M par", []))
        _acc = _dirty = None
        if (b.get("class") in ("bond", "convertible")
                and coup and mat and basis_date and basis_price is not None):
            _settle = _dt.date.fromisoformat(basis_date)
            _mat = _dt.date.fromisoformat(mat)
            _last_c = _mat
            while _last_c > _settle:
                _last_c = _minus_6m(_last_c)
            _acc = coup / 2.0 * _d360(_last_c, _settle) / 180.0
            _dirty = basis_price + _acc
            items.append(("Accrued interest", f"{_acc:.2f}", []))
            items.append(("Dirty price", f"{_dirty:.2f}", []))
        strip = ('<dl class="bw-summary">\n' + "".join(
            f"<div class=\"bw-sum-item\"><dt>{k}</dt><dd>{v}</dd>"
            + "".join(f"<dd class=\"bw-sum-sub\">{sub}</dd>"
                      for sub in subs)
            + "</div>\n"
            for k, v, subs in items) + "</dl>\n")
        # Price and analytics block (spec 2.2): the block heading
        # carries the basis; the footnote carries the convention.
        _basis_txt = {"trade": "At last trade",
                      "mark": "At latest fund mark"}.get(basis_kind)
        price_block = ""
        if items and _basis_txt:
            price_block = (
                "<h2>Price and analytics</h2>\n"
                f"<p class=\"data-vintage\">Basis: {_basis_txt} "
                f"({_fmt_date(basis_date)}).</p>\n" + strip
                + "<p class=\"data-vintage\">Analytics settle at the "
                  "basis date; 30/360, semiannual convention.</p>\n")
        warn = ""
        if last_trade and latest_mark and latest_mark[1] < last_trade[1]:
            _lag = (_dt.date.fromisoformat(last_trade[1])
                    - _dt.date.fromisoformat(latest_mark[1])).days
            warn = (f"<p class=\"data-vintage\">The fund mark is dated "
                    f"{_fmt_date(latest_mark[1])} and the last trade "
                    f"{_fmt_date(last_trade[1])}, {_lag} days later. The gap "
                    f"mixes market repricing with the fund reporting lag; it "
                    f"is not a same-day comparison.</p>\n")
        # Fund marks and holders blocks (Stage 2, 2026-10-20): every
        # figure from the N-PORT full-universe panel, each mark dated
        # at its own modal report-ending period. The Marks block
        # renders only where a priced mark exists; the Holders block
        # only where a fund position is on record. The print-to-mark
        # gap lives in the Price strip above (one fact, one home).
        _np = _nport_panel()
        _npb = (_np.get("bonds") or {}).get(cusip)
        _np_held = (_np.get("held_latest") or {}).get(cusip)
        _np_unpriced = {u["cusip"]: u for u in
                        (_np.get("coverage") or {}).get(
                            "held_unpriced") or []}
        marks_block = ""
        holders_block = ""
        if _npb:
            _L = _npb["latest"]
            _pv = _npb.get("prev")
            _mi = [("Fund mark (median)", f"{_L['median']:.2f}",
                    [f"Period ended {_fmt_date(_L['period_end'])}"
                     + (" (modal)" if _L.get("period_modal") else ""),
                     f"Median of {_L['n_funds']} fund marks"])]
            if _L.get("p10") is not None and _L.get("p90") is not None:
                _mi.append(("Range, p10 to p90",
                            f"{_L['p10']:.2f} to {_L['p90']:.2f}", []))
            if _L.get("vw") is not None:
                _mi.append(("Value-weighted mean",
                            f"{_L['vw']:.2f}", []))
            if _pv and _pv.get("median") is not None:
                _mi.append((
                    "Change vs prior quarter",
                    f"{_L['median'] - _pv['median']:+.2f} pts",
                    [f"Prior median {_pv['median']:.2f}, period ended "
                     f"{_fmt_date(_pv['period_end'])}"]))
            _fv = _L.get("fv")
            if _fv:
                _mix = ", ".join(
                    f"Level {i + 1} {_fv[k] * 100:.0f}%"
                    for i, k in enumerate(("fv1", "fv2", "fv3"))
                    if _fv.get(k) and _fv[k] >= 0.005)
                if _mix:
                    _mi.append(("Fair value basis", _mix,
                                ["Share of reported balance by "
                                 "fair-value level"]))
            if _L.get("onloan_share") and _L["onloan_share"] >= 0.005:
                _mi.append(("Reported on loan",
                            f"{_L['onloan_share'] * 100:.0f}%",
                            ["Share of the reported balance funds "
                             "report as loaned out"]))
            marks_block = (
                "<h2>Fund marks</h2>\n"
                '<dl class="bw-summary">\n' + "".join(
                    f"<div class=\"bw-sum-item\"><dt>{k}</dt>"
                    f"<dd>{v}</dd>"
                    + "".join(f"<dd class=\"bw-sum-sub\">{s}</dd>"
                              for s in subs) + "</div>\n"
                    for k, v, subs in _mi) + "</dl>\n"
                "<p class=\"data-vintage\">Median of fund-reported "
                "marks: the middle fund-reported price per 100 of "
                "principal across every fund reporting a priced "
                "position in this bond, from SEC Form N-PORT filings. "
                "The period shown is the most common date as of "
                "which the bond's reporting funds reported their "
                "holdings that quarter; funds file about 60 days "
                "after that date, so the mark lags the market.</p>\n")
            _hn = _L.get("n_funds_any") or _L["n_funds"]
            _hi = [("Funds reporting a position", f"{_hn}",
                    [f"Of which {_L['n_funds']} report a priced "
                     "position"] if _hn != _L["n_funds"] else []),
                   ("Reported principal balance",
                    f"${_L['balance']:,.0f}",
                    [f"Period ended {_fmt_date(_L['period_end'])}"])]
            if _L.get("top1") is not None:
                _hi.append(("Largest holder share",
                            f"{_L['top1'] * 100:.1f}%", []))
            if _L.get("top5") is not None:
                _hi.append(("Top five holders share",
                            f"{_L['top5'] * 100:.1f}%", []))
            holders_block = (
                "<h2>Holders</h2>\n"
                '<dl class="bw-summary">\n' + "".join(
                    f"<div class=\"bw-sum-item\"><dt>{k}</dt>"
                    f"<dd>{v}</dd>"
                    + "".join(f"<dd class=\"bw-sum-sub\">{s}</dd>"
                              for s in subs) + "</div>\n"
                    for k, v, subs in _hi) + "</dl>\n")
            if _pv:
                _bd = ((_L["balance"] - _pv["balance"])
                       / _pv["balance"] * 100.0
                       if _pv.get("balance") else None)
                _qoq = (f"Quarter over quarter: funds reporting "
                        f"{_pv['n_funds']} to {_L['n_funds']}")
                if _bd is not None:
                    _qoq += (f"; reported balance {_bd:+.1f}%")
                holders_block += (f"<p class=\"data-vintage\">"
                                  f"{_qoq}.</p>\n")
            if _L["balance"] and _L["balance"] >= 10_000_000 \
                    and _npb.get("holders"):
                _hrows = "".join(
                    f"<tr><td>{esc(h['fund'])}</td>"
                    f"<td class=\"num\" data-v=\"{h['balance']}\">"
                    f"${h['balance']:,.0f}</td>"
                    f"<td class=\"num\" "
                    f"data-v=\"{h['share'] or 0}\">"
                    f"{h['share'] * 100:.1f}%</td></tr>"
                    for h in _npb["holders"][:5])
                holders_block += (
                    "<h3>Largest holders</h3>\n"
                    + _grid("holders", HOLDER_COLS, _hrows,
                            sortable=False)
                    + "<p class=\"data-vintage\">The five largest "
                      "fund positions at the period end, by reported "
                      "principal balance. A position is a holding at "
                      "the report date, not trading activity."
                    + _reset_btn("holders") + "</p>\n")
            if _np_held and _np_held["quarter"] != _L["quarter"]:
                holders_block += (
                    f"<p class=\"data-vintage\">Funds also report "
                    f"holding this bond in the latest quarter's "
                    f"filings ({_np_held['n_funds_any']} funds), "
                    f"with no priced position that quarter; no mark "
                    f"or balance is shown for that quarter.</p>\n")
        elif _np_held:
            _u = _np_unpriced.get(cusip) or {}
            holders_block = (
                "<h2>Holders</h2>\n"
                '<dl class="bw-summary">\n'
                f"<div class=\"bw-sum-item\"><dt>Funds reporting a "
                f"position</dt><dd>{_np_held['n_funds_any']}</dd>"
                f"<dd class=\"bw-sum-sub\">Latest filings, "
                f"{_np_held['quarter']}</dd></div>\n</dl>\n"
                "<p class=\"data-vintage\">Positions in this bond "
                "are reported in units other than principal (units: "
                + ", ".join(_u.get("units") or ["not stated"])
                + "), so no principal balance and no fund mark are "
                "published for it.</p>\n")
        # charts: price and yield
        mark_prices = [(m[0], m[1]) for m in marks]
        trade_prices = [(t[0], t[2]) for t in trades]
        mark_yields = [(m[0], _ytw(m[1], coup, mat, m[0], b))
                       for m in marks] if coup and mat else []
        trade_yields = [(t[0], t[3]) for t in trades]
        if trades or marks:
            _tt = det.get("trades_total") or len(trades)
            _red = (
                f" This bond has {_tt:,} stored trades; beyond the "
                f"most recent 90 days the chart and tape show the "
                f"last trade of each week ({len(trades):,} points). "
                f"The full tape is in the program dataset."
                if _tt > len(trades) else "")
            chart = (
                "<h2>Price and yield history</h2>\n"
                "<p class=\"data-vintage\">The line plots one point "
                "per trade date, the day's last print; the whisker "
                "at each point spans the day's high and low prints. "
                "The line breaks across gaps longer than 30 days. "
                "Fund marks are squares at each period end, "
                "joined by the dashed line. Volume is the day total "
                "of amounts reported to TRACE; capped reports count "
                "at the cap. Scroll or drag on the chart to zoom. "
                "One axis per view; a fund mark is a period-end "
                "valuation, not a trade price."
                f"{_red}</p>\n"
                "<p class=\"chart-toggle\">"
                "<button type=\"button\" id=\"btn-price\" "
                "aria-pressed=\"true\">Price</button> "
                "<button type=\"button\" id=\"btn-yield\" "
                "aria-pressed=\"false\">Yield</button></p>\n"
                f"<div class=\"bond-chart-e\" role=\"img\" "
                f"aria-label=\"Price and yield history chart for "
                f"{cusip}\">{_chart_svg(mark_prices, trade_prices, 'price')}</div>\n"
                f"<script type=\"application/json\" "
                f"class=\"bond-chart-data\">"
                f"{_chart_embed(marks, trades)}</script>\n")
        else:
            chart = (
                "<h2>Price and yield history</h2>\n"
                "<p class=\"data-vintage\">No trades and no fund marks "
                "are in the stored record for this bond.</p>\n")
        # terms
        trows = []

        def trow(k, v):
            if v not in (None, ""):
                trows.append(f"<tr><td class=\"muted\">{k}</td><td>{v}</td></tr>")

        trow("Issuer", b.get("issuer"))
        _fam = _family_of(b.get("issuer"))
        if _fam:
            trow("Group",
                 f"<a href=\"/leverage/issuer/{_fam[1]}/\">"
                 f"{esc(_fam[0])}</a>")
        trow("Security", b.get("security"))
        trow("Coupon", f"{coup:.3f}".rstrip("0").rstrip(".") + "%"
             if coup else None)
        trow("Maturity", _fmt_date(mat))
        _ia = b.get("issue_amount_usd")
        if _ia is not None:
            _iak = ("Original issue amount"
                    if b.get("issue_amount_kind") == "original_issue"
                    else "Amount outstanding")
            trow("Amount issued",
                 f"${_ia:,.0f}"
                 f"<span class=\"cell-sub\">{_iak}; "
                 f"{esc(b.get('issue_amount_source') or '')}</span>")
        if y is not None:
            trow("Analytics convention",
                 "Yields use 30/360, semiannual")
        trow("Currency", "US dollars")
        terms = ("<h2>Terms</h2>\n<table class=\"terms-table\"><tbody>\n"
                 + "\n".join(trows) + "\n</tbody></table>\n")
        sched = b.get("call_schedule") or []
        if sched:
            srows = "".join(
                f"<tr><td>{_fmt_date(cs['date'])}</td>"
                f"<td class=\"num\">{cs['price_pct']:.3f}</td></tr>"
                for cs in sched)
            terms += ("<h3>Call schedule</h3>\n"
                      "<table class=\"terms-table\"><thead><tr>"
                      "<th>Call date</th><th>Price (% of par)</th></tr>"
                      f"</thead><tbody>{srows}</tbody></table>\n")
        if b.get("call_notes"):
            terms += f"<p class=\"data-vintage\">{b['call_notes']}</p>\n"
        # Ratings block (spec 2.7): agency named, rating date
        # carried, one row per agency with a grade on record.
        _rt = []
        if b.get("sp_rating"):
            _rt.append(
                f"<tr><td>S&amp;P</td><td>{esc(b['sp_rating'])}</td>"
                f"<td class=\"muted\">"
                f"{_fmt_date(b.get('sp_rating_date')) or 'Not recorded'}"
                f"</td></tr>")
        if b.get("moodys_rating"):
            _rt.append(
                f"<tr><td>Moody's</td><td>{esc(b['moodys_rating'])}</td>"
                f"<td class=\"muted\">"
                f"{_fmt_date(b.get('moodys_rating_date')) or 'Not recorded'}"
                f"</td></tr>")
        if _rt:
            ratings_block = (
                "<h2>Ratings</h2>\n<table class=\"terms-table\"><thead>"
                "<tr><th>Agency</th><th>Rating</th><th>Rated</th></tr>"
                "</thead><tbody>\n" + "\n".join(_rt)
                + "\n</tbody></table>\n")
        else:
            ratings_block = (
                "<h2>Ratings</h2>\n<p class=\"data-vintage\">"
                "No agency rating in the dataset.</p>\n")
        # merged tape
        tape = []
        for t in trades:
            ycell = (f"{t[3]:.2f}%" if t[3] is not None else "—")
            _side = {"B": "Bought", "S": "Sold"}.get(t[5], t[5] or "—")
            tape.append((t[0], t[1] or "",
                         f"<tr data-src=\"t\"><td>{_fmt_date(t[0])} "
                         f"{(t[1] or '')[:5]}</td>"
                         "<td><span class=\"src-chip t\">TRACE trade</span></td>"
                         f"<td class=\"num\">{t[2]:.2f}</td>"
                         f"<td class=\"num\">{ycell}</td>"
                         f"<td>{_fmt_tape_vol(t[4])}</td>"
                         f"<td>{_side}</td></tr>"))
        for m in marks:
            tape.append((m[0], "",
                         f"<tr data-src=\"m\"><td>{_fmt_date(m[0])}</td>"
                         "<td><span class=\"src-chip m\">Fund mark</span></td>"
                         f"<td class=\"num\">{m[1]:.2f}</td>"
                         "<td class=\"num\">—</td>"
                         "<td>—</td><td>—</td></tr>"))
        tape.sort(key=lambda r: (r[0], r[1]), reverse=True)
        total_entries = len(tape)
        tape = tape[:240]
        tape_html = (
            "<h2>Trade and mark history</h2>\n"
            "<p class=\"data-vintage\">One chronological record. TRACE "
            "trades are executions reported to FINRA; fund marks are "
            "period-end valuations from holder filings. Volume is as "
            "reported by FINRA (amounts above $5M par are capped at "
            "“5MM+” for investment-grade and $1M for high-yield issues). "
            "Side is the reporting party's side.</p>\n"
            "<p class=\"tape-filter\">"
            "<label><input type=\"checkbox\" id=\"f-trades\" checked> "
            "TRACE trades</label> "
            "<label><input type=\"checkbox\" id=\"f-marks\" checked> "
            "Fund marks</label></p>\n"
            "<div class=\"market-table-scroll\"><table class=\"market-table "
            "tape\"><thead><tr><th>Date</th><th>Source</th><th>Price (% of par)</th>"
            "<th>Yield as reported by FINRA (%)</th><th>Volume ($)</th><th>Side</th></tr></thead>"
            "<tbody>\n" + "\n".join(r[2] for r in tape)
            + "\n</tbody></table></div>\n")
        if total_entries > 240:
            tape_html += (f"<p class=\"data-vintage\">Showing the 240 most "
                          f"recent of {total_entries} entries; the full "
                          f"record is in the program dataset.</p>\n")
        if not trades and not marks:
            tape_html = ("<h2>Trade and mark history</h2>\n"
                         "<p class=\"data-vintage\">No trades and no fund "
                         "marks are on record for this bond.</p>\n")
        elif not trades:
            tape_html = tape_html.replace(
                "One chronological record.",
                "FINRA holds a record for this bond; no trades are in the "
                "stored record. One chronological record.", 1)
        # per-fund marks
        funds_html = ""
        funds = det.get("funds") or []
        if funds:
            frows = "".join(
                f"<tr><td>{f['fund']}</td><td class=\"muted\">"
                f"{f['complex'] or ''}</td>"
                f"<td class=\"num\">${f['principal']:,}</td>"
                f"<td class=\"num\">{f['price']:.2f}</td></tr>"
                for f in funds)
            funds_html = (
                "<h2>Fund marks by holder</h2>\n"
                f"<p class=\"data-vintage\">{len(funds)} funds held this "
                f"bond at {_fmt_date(det.get('fund_period'))}. Each mark "
                f"is that fund's own period-end valuation per 100 of "
                f"principal.</p>\n"
                "<div class=\"market-table-scroll\"><table class=\"market-table\">"
                "<thead><tr><th>Fund</th><th>Complex</th><th>Principal</th>"
                "<th>Implied mark</th></tr></thead><tbody>\n"
                + frows + "\n</tbody></table></div>\n")
        # same-issuer comparables
        sibs = [x for x in reg
                if x["cusip"] != cusip and x.get("issuer") == b.get("issuer")]
        sibs.sort(key=lambda x: x.get("maturity") or "")
        comp_html = ""
        if sibs:
            crows = []
            for s in sibs[:25]:
                sp = prints.get(s["cusip"])
                sbw = bw_rows.get(s["cusip"])
                lt = (sp["last_trade_price"] if sp
                      and sp.get("last_trade_price") is not None else None)
                if sbw:
                    lm, lm_per = sbw["latest_price"], sbw.get("latest_period")
                elif sp:
                    lm = sp.get("latest_fund_mark")
                    lm_per = sp.get("mark_period")
                else:
                    lm = lm_per = None
                lp_c = f"{lt:.2f}" if lt is not None else "—"
                td_c = (_fmt_date(sp["last_trade_date"])
                        if sp and sp.get("last_trade_date") else "—")
                gap_c = (f"{lt - lm:+.2f}"
                         if lt is not None and lm is not None else "—")
                mk_c = "—"
                if lm is not None:
                    mk_c = f"{lm:.2f}"
                    if lm_per:
                        mk_c += (f"<span class=\"cell-sub\">Period ended "
                                 f"{_fmt_date(lm_per)}</span>")
                sc2 = s.get("coupon_pct")
                coup_c = ((f"{sc2:.3f}".rstrip("0").rstrip(".") + "%")
                          if sc2 else "—")
                crows.append(
                    f"<tr><td><a class=\"bond-link\" "
                    f"href=\"/leverage/bond/{s['cusip'].lower()}/\">"
                    f"{esc(s.get('security') or s['cusip'])}</a></td>"
                    f"{_issued_cell(s['cusip'])}"
                    f"<td class=\"num\">{lp_c}</td>"
                    f"<td class=\"muted\">{td_c}</td>"
                    f"<td class=\"num\">{gap_c}</td>"
                    f"<td class=\"num\">{mk_c}</td>"
                    f"<td class=\"num\">{coup_c}</td>"
                    f"<td class=\"muted\">"
                    f"{_fmt_date(s.get('maturity')) or '—'}</td>"
                    f"{_rating_cell(s['cusip'])}"
                    f"<td class=\"muted\">{s['cusip']}</td></tr>")
            comp_html = (
                "<h2>Other bonds from this issuer</h2>\n"
                "<div class=\"market-table-scroll\"><table class=\"market-table\">"
                "<thead><tr><th>Security</th><th>Issued ($M)</th><th>Last print (% of par)</th>"
                "<th>Traded</th><th>Gap (pts)</th><th>Fund mark (% of par)</th>"
                "<th>Coupon (%)</th><th>Matures</th><th>Rating</th>"
                "<th>CUSIP</th></tr></thead><tbody>\n"
                + "\n".join(crows) + "\n</tbody></table></div>\n")
            if len(sibs) > 25:
                comp_html += (f"<p class=\"data-vintage\">Showing 25 of "
                              f"{len(sibs)} bonds from this issuer.</p>\n")
        _fent = _flow_data().get("bonds", {}).get(cusip)
        flow_html = _flow_panel(_fent,
                                all_abs=(b.get("class") == "abs"))
        prev_b = ordered[idx - 1] if idx > 0 else None
        next_b = ordered[idx + 1] if idx + 1 < len(ordered) else None
        # Header block (spec 2.1): breadcrumb, then the identity
        # items as labeled lines - no value travels unlabeled.
        _fam2 = _family_of(b.get("issuer"))
        navrow = ("<p class=\"bond-navrow\">"
                  "<a href=\"/leverage/bond-watch/\">Bond Price Watch</a>")
        if _fam2:
            navrow += (f" / <a href=\"/leverage/issuer/{_fam2[1]}/\">"
                       f"{esc(_fam2[0])}</a>")
        navrow += f" / {esc(b.get('issuer') or '')}</p>\n"
        _nav2 = "<p class=\"bond-navrow\">"
        if prev_b:
            _nav2 += (f"<a href=\"/leverage/bond/{prev_b['cusip'].lower()}/\">"
                      f"&larr; {esc(prev_b['issuer'] or '')}</a>")
        if prev_b and next_b:
            _nav2 += " / "
        if next_b:
            _nav2 += (f"<a href=\"/leverage/bond/{next_b['cusip'].lower()}/\">"
                      f"{esc(next_b['issuer'] or '')} &rarr;</a>")
        _nav2 += "</p>\n"
        _cls = (b.get("class") or "bond").lower()
        _sec_l = (b.get("security") or "").lower()
        if _cls == "convertible":
            _instr = "Convertible notes"
        elif _cls == "abs":
            _instr = "Asset-backed notes"
        elif _cls == "loan":
            _instr = "Term loan"
        elif _cls == "equity":
            _instr = "Equity"
        elif "subordinated" in _sec_l:
            _instr = "Subordinated notes"
        elif "senior" in _sec_l:
            _instr = "Senior notes"
        else:
            _instr = "Notes"
        _id_items = [("CUSIP", cusip)]
        if b.get("finra_symbol"):
            _id_items.append(("FINRA symbol", esc(b["finra_symbol"])))
        _id_items.append(("Instrument", _instr))
        if b.get("is_144a") == "Y":
            _id_items.append(("Rule 144A", "Yes"))
        if b.get("twin_of"):
            _twin_label = {"Y": "Related line - registered",
                           "N": "Related line - 144A"}.get(
                               b.get("is_144a"), "Related line")
            _id_items.append(
                (_twin_label,
                 f"<a href=\"/leverage/bond/{b['twin_of'].lower()}/\">"
                 f"{b['twin_of']}</a>"))
        _ent = _entity_links()[1].get(cusip)
        if _ent:
            _id_items.append(
                ("Entity Index",
                 f"<a href=\"/entities/{_ent[0]}/\">"
                 f"{esc(_ent[1])}</a>"))
        identity = ('<dl class="bw-summary">\n' + "".join(
            f"<div class=\"bw-sum-item\"><dt>{k}</dt><dd>{v}</dd></div>\n"
            for k, v in _id_items) + "</dl>\n")
        title = f"{b.get('issuer') or ''} {b.get('security') or cusip}".strip()
        body = frontmatter(
            title,
            f"Trades, fund marks, terms and call schedule for {cusip}.",
            f"Trades to {_fmt_date(tape_stamp)}; fund marks to "
            f"{_fmt_date(marks[-1][0]) if marks else 'n/a'}")
        body += (navrow + _nav2 + identity + price_block + warn
                 + marks_block + holders_block
                 + chart + flow_html + tape_html
                 + funds_html + terms + ratings_block + comp_html
                 + "<p class=\"data-vintage\">Sources: FINRA TRACE via the "
                   "public lookup (collected by Kilambi Research); fund "
                   "marks from SEC N-PORT bulk data. A fund mark is a "
                   "period-end valuation reported by a holder; it is not "
                   "a trade price. Yield to worst takes scheduled calls "
                   "into account and treats conditional convertible "
                   "redemption as not certain.</p>\n")
        body += DETAIL_JS
        if 'data-tid="holders"' in holders_block:
            body += TABLE_ENGINE_JS
        if trades or marks:
            body += ('<script src="/js/echarts.min.js" defer></script>\n'
                     '<script src="/js/bond_chart.js" defer></script>\n')
        with open(os.path.join(outdir, f"{cusip}.md"), "w") as f:
            f.write(body)
        n += 1
    return n


def zero_holders_page():
    """Bonds with no fund holders in the latest N-PORT archive
    (Stage 2, 2026-10-20). The panel's zero-holder list carries 154
    registry rows; three are placeholders (N/A, 000000000, 999999999),
    not bonds, and are accounted for in the intro, not the table."""
    import re as _re
    np_ = _nport_panel()
    cov = np_.get("coverage") or {}
    lq = np_.get("latest_quarter", "")
    rows_all = np_.get("zero_holders") or []
    bonds = [z for z in rows_all
             if _re.fullmatch(r"[A-Z0-9]{9}", z["cusip"] or "")
             and z["cusip"] not in ("000000000", "999999999")]
    n_ph = len(rows_all) - len(bonds)
    body = frontmatter(
        "Bonds with no fund holders",
        "Registry bonds no fund reported holding in the latest "
        "N-PORT filings.",
        f"Fund holdings from the {lq} N-PORT archive")
    body += (
        f"<p>In the {lq} N-PORT archive, funds report a position in "
        f"{cov.get('held_latest', 0)} of {cov.get('registry', 0)} "
        f"registry bonds. The {len(bonds)} bonds below have no "
        f"holding rows in that quarter's filings at all, so no fund "
        f"mark exists for them; their pages carry trades and terms "
        f"only. A bond can leave this list in a later quarter if a "
        f"fund reports a position.</p>\n")
    if n_ph:
        body += (
            f"<p class=\"data-vintage\">{n_ph} further registry "
            f"rows are placeholders (N/A, 000000000, 999999999): not "
            f"bonds, and without holders by construction. Counting "
            f"them, {len(rows_all)} registry rows have no holder in "
            f"the quarter.</p>\n")
    trs = []
    for z in bonds:
        trs.append(
            "<tr>" + _ana_bond(z["cusip"])
            + f'<td data-v="{esc(z["deal"])}">{esc(z["deal"])}</td>'
            + f'<td data-v="{z["cusip"]}">{z["cusip"]}</td></tr>')
    body += _grid("zero-holders", NP_ZERO_COLS, trs)
    body += (
        "<p class=\"data-vintage\">Source: SEC Form N-PORT, full "
        "fund universe, joined to the bond registry by Kilambi "
        "Research. Holdings are positions at fund report period "
        "ends in the quarter's filings, not trading activity.</p>\n")
    body += TABLE_ENGINE_JS
    return body


def main():
    # The Macro section (spreads, central banks, economies) was removed
    # 2026-10-15 at Arvin's direction. The page functions above remain
    # for reference but are no longer written. This builder now writes
    # only the Leverage section.
    lev_out = os.path.join(SITE, "content", "leverage")
    os.makedirs(lev_out, exist_ok=True)
    # Bond Price Watch lives in the Leverage section (moved 2026-10-14,
    # Arvin); the /macro/bond-watch/ URL is kept as a frontmatter alias.
    with open(os.path.join(lev_out, "bond-watch.md"), "w") as f:
        f.write(bond_watch_page())
    print("wrote leverage/bond-watch.md")
    ana_body, ana_extras = bond_analytics_page()
    with open(os.path.join(lev_out, "bond-analytics.md"), "w") as f:
        f.write(ana_body)
    print("wrote leverage/bond-analytics.md")
    wanted = {f"bond-analytics-{k}.md" for k in ana_extras}
    for stale in os.listdir(lev_out):
        if re.fullmatch(
                r"bond-analytics-(liquidity|marks)-p\d+\.md", stale) \
                and stale not in wanted:
            os.remove(os.path.join(lev_out, stale))
    for key, ebody in ana_extras.items():
        with open(os.path.join(lev_out, f"bond-analytics-{key}.md"),
                  "w") as f:
            f.write(ebody)
    if ana_extras:
        print("wrote", len(ana_extras),
              "bond-analytics continuation pages")
    with open(os.path.join(lev_out, "zero-holders.md"), "w") as f:
        f.write(zero_holders_page())
    print("wrote leverage/zero-holders.md")
    act_body, act_extras = activity_page()
    with open(os.path.join(lev_out, "activity.md"), "w") as f:
        f.write(act_body)
    print("wrote leverage/activity.md")
    wanted = {f"activity-p{n}.md" for n in act_extras}
    for stale in os.listdir(lev_out):
        if re.fullmatch(r"activity-p\d+\.md", stale) \
                and stale not in wanted:
            os.remove(os.path.join(lev_out, stale))
    for n, ebody in act_extras.items():
        with open(os.path.join(lev_out, f"activity-p{n}.md"), "w") as f:
            f.write(ebody)
    if act_extras:
        print("wrote", len(act_extras), "activity continuation pages")
    iss_dir = os.path.join(lev_out, "issuer")
    os.makedirs(iss_dir, exist_ok=True)
    ipages = issuer_pages()
    for stale in os.listdir(iss_dir):
        if stale.endswith(".md") and stale[:-3] not in ipages:
            os.remove(os.path.join(iss_dir, stale))
    for key, content in ipages.items():
        with open(os.path.join(iss_dir, f"{key}.md"), "w") as f:
            f.write(content)
    print("wrote", len(ipages), "issuer pages")
    proj_dir = os.path.join(SITE, "content", "projects")
    os.makedirs(proj_dir, exist_ok=True)
    ppages = project_pages()
    for stale in os.listdir(proj_dir):
        if stale.endswith(".md") and stale != "_index.md" \
                and stale[:-3] not in ppages:
            os.remove(os.path.join(proj_dir, stale))
    for slug, content in ppages.items():
        with open(os.path.join(proj_dir, f"{slug}.md"), "w") as f:
            f.write(content)
    with open(os.path.join(proj_dir, "_index.md"), "w") as f:
        f.write(projects_index())
    print("wrote", len(ppages), "project pages")
    with open(os.path.join(lev_out, "monitor.md"), "w") as f:
        f.write(leverage_monitor_page())
    print("wrote leverage/monitor.md")
    print("wrote", bond_pages(), "bond detail pages")

if __name__ == "__main__":
    main()
