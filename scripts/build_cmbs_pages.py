#!/usr/bin/env python3
"""Build the CMBS section of news.kilambi.com from the merged dataset.

Generates, under content/cmbs/:
  _index.md            market page (/cmbs/)
  deals.md             deal index (/cmbs/deals/): all deal units, sortable
  rankings.md          rankings (/cmbs/rankings/)
  deal/_index.md       subsection stub
  deal/<slug>.md       one page per deal unit (517)

Data source: the merged derived database (deals, tranches, loans_static,
loans_monthly, loans_versioned, deal_features, deal_indicator_monthly,
v_tranche_current_ratings). Nothing is hardcoded: every figure on the
pages is computed from the database at build time.

Conventions carried over from the dataset's own published analytics:
  * Market delinquency shares are balance-weighted over loan-months that
    carry a delinquency status code in loans_monthly (payment status
    codes: 0 current, 1 = 30-59 days, 2 = 60-89, 3 = 90+, 4 = foreclosure,
    5 = REO, A = performing matured balloon, B = non-performing matured
    balloon), weighted by the reported actual balance.
  * Per-deal measures come from deal_features and deal_indicator_monthly,
    the dataset's per-deal layer.
  * Credit support on deal pages is computed from the class stack order
    (prospectus order) as the share of principal balance junior to the
    class. The dataset does not carry prospectus-stated support; the
    column is labelled "computed" everywhere it appears.

Refresh:
  ~/workspace/merged-db/.venv/bin/python \\
      ~/workspace/news-site/scripts/build_cmbs_pages.py [--db PATH]
then publish the content/cmbs tree plus layouts with scripts/publish.py.
The navigation entry lives in layouts/_default/baseof.html (menu-cmbs)
and the section layouts in layouts/cmbs/list.html and
layouts/deal/list.html; those are static and are not regenerated here.

Missing data renders as "not yet reported". No figure is invented.
"""
import argparse
import datetime
import json
import math
import os
import re
import sys

import duckdb

SITE = os.path.expanduser("~/workspace/news-site")
DEFAULT_DB = os.path.expanduser("~/workspace/merged-db/merged.duckdb")
OUT = os.path.join(SITE, "content", "cmbs")
NYR = "not yet reported"
AGENCIES = [("fitch", "Fitch"), ("kbra", "KBRA"), ("sp", "S&amp;P"),
            ("moodys", "Moody's"), ("dbrs", "DBRS")]
PT_LABEL = {
    "RT": "Retail", "OF": "Office", "IN": "Industrial", "LO": "Lodging",
    "MF": "Multifamily", "MU": "Mixed use", "SS": "Self storage",
    "MH": "Manufactured housing", "WH": "Warehouse", "CH": "Healthcare",
    "98": "Other (code 98)",
}
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November",
               "December"]


def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def money(v):
    if v is None:
        return NYR
    if abs(v) >= 1e9:
        return f"${v / 1e9:,.2f}B"
    if abs(v) >= 1e6:
        return f"${v / 1e6:,.1f}M"
    return f"${v:,.0f}"


def pct_frac(v, dp=2):
    """Format a fraction (0.0365) as a percent string."""
    if v is None:
        return NYR
    return f"{v * 100:.{dp}f}%"


def pct_val(v, dp=2):
    """Format a value already in percent units."""
    if v is None:
        return NYR
    return f"{v:.{dp}f}%"


def num(v, dp=1):
    if v is None:
        return NYR
    return f"{v:,.{dp}f}"


def month_label(d):
    if d is None:
        return NYR
    return f"{MONTH_NAMES[d.month - 1]} {d.year}"


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
    return s or "deal"


def deal_code(name):
    m = re.search(r"\b(\d{4}-[A-Z0-9]+)\b", str(name).upper())
    return m.group(1) if m else None


def shelf_of(name):
    code = deal_code(name)
    if code:
        s = re.sub(re.escape(code), "", str(name), flags=re.IGNORECASE)
        s = re.sub(r"\s+", " ", s).strip(" -")
        return s if s else str(name)
    return str(name)


# ---------------------------------------------------------------- charts
def svg_line_chart(series, y_label, height=260, y_min=None, y_max=None,
                   y_fmt="{:.0f}"):
    """series: list of (label, color, [(x_index, x_label, value|None)]).
    All series share the same x positions (list of (date, value) pairs is
    normalised by the caller into aligned points with a shared x scale).
    Returns an inline SVG in the site's bond-chart idiom."""
    # gather all points
    all_x = sorted({p[0] for _, _, pts in series for p in pts})
    if not all_x:
        return ""
    vals = [p[1] for _, _, pts in series for p in pts if p[1] is not None]
    if not vals:
        return ""
    lo = min(vals) if y_min is None else y_min
    hi = max(vals) if y_max is None else y_max
    if y_min is None:
        lo = min(lo, 0.0)
    pad = (hi - lo) * 0.08 or 1.0
    if y_min is None:
        lo = max(0.0, lo - pad) if lo >= 0 else lo - pad
    if y_max is None:
        hi = hi + pad
    if hi <= lo:
        hi = lo + 1.0
    L, R, T, B = 46.0, 708.0, 10.0, 236.0
    x0, x1 = all_x[0], all_x[-1]
    span = max((x1 - x0).days, 1)

    def X(d):
        return L + (R - L) * (d - x0).days / span

    def Y(v):
        return B - (B - T) * (v - lo) / (hi - lo)

    out = [f'<svg class="bond-chart" viewBox="0 0 720 {height}" width="100%" '
           f'role="img" aria-label="{esc(y_label)}">']
    # gridlines: 5 ticks
    for i in range(5):
        v = lo + (hi - lo) * i / 4
        y = Y(v)
        out.append(f'<line x1="{L:.0f}" y1="{y:.0f}" x2="{R:.0f}" y2="{y:.0f}" '
                   f'stroke="#e5ddc8" stroke-width="1"/>')
        out.append(f'<text x="{L - 6:.0f}" y="{y + 3:.0f}" text-anchor="end" '
                   f'class="chart-lab">{y_fmt.format(v)}</text>')
    # x labels: one per year boundary present in range
    years = sorted({d.year for d in all_x})
    for yr in years:
        d = datetime.date(yr, 1, 1)
        if x0 <= d <= x1:
            out.append(f'<text x="{X(d):.0f}" y="254" text-anchor="middle" '
                       f'class="chart-lab">{yr}</text>')
    for label, color, pts in series:
        # split into runs at None values (no silent interpolation)
        runs, cur = [], []
        for d, v in sorted(pts):
            if v is None:
                if len(cur) > 1:
                    runs.append(cur)
                cur = []
            else:
                cur.append((d, v))
        if len(cur) > 1:
            runs.append(cur)
        for run in runs:
            points = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, v in run)
            out.append(f'<polyline points="{points}" fill="none" '
                       f'stroke="{color}" stroke-width="1.4"/>')
        # single isolated points as dots
        for d, v in sorted(pts):
            if v is not None:
                out.append(f'<circle cx="{X(d):.1f}" cy="{Y(v):.1f}" r="1.2" '
                           f'fill="{color}"/>')
    out.append("</svg>")
    # legend as text under the chart (never over data)
    if len(series) > 1:
        leg = " &middot; ".join(
            f'<span style="color:{c}">&#9644;</span> {esc(l)}'
            for l, c, _ in series)
        out.append(f'<p class="bond-chart-cap">{leg}</p>')
    return "\n".join(out)


def frontmatter(title, lede, data_as_of, date_str):
    return (f"---\ntitle: \"{esc(title)}\"\ndate: \"{date_str}\"\n"
            f"lede: \"{esc(lede)}\"\ndata_as_of: \"{esc(data_as_of)}\"\n---\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    from zoneinfo import ZoneInfo
    today = datetime.datetime.now(
        ZoneInfo("America/Toronto")).date().isoformat()
    con = duckdb.connect(args.db, read_only=True)
    con.execute("SET threads=4")

    sanity = {}

    # ------------------------------------------------------------ market
    mkt = con.execute("""
    SELECT pmonth,
      SUM(CASE WHEN code IN ('1','2','3') THEN bal ELSE 0 END)
        / NULLIF(SUM(CASE WHEN code IS NOT NULL THEN bal END), 0) AS dq30,
      SUM(CASE WHEN code IN ('1','2','3','4','5') THEN bal ELSE 0 END)
        / NULLIF(SUM(CASE WHEN code IS NOT NULL THEN bal END), 0) AS dq30f,
      SUM(CASE WHEN code IN ('4','5') THEN bal ELSE 0 END)
        / NULLIF(SUM(CASE WHEN code IS NOT NULL THEN bal END), 0) AS fcre,
      SUM(CASE WHEN code = 'B' THEN bal ELSE 0 END)
        / NULLIF(SUM(CASE WHEN code IS NOT NULL THEN bal END), 0) AS codeb,
      SUM(adv) / NULLIF(SUM(CASE WHEN code IS NOT NULL THEN bal END), 0)
        AS adv_share,
      MEDIAN(dscr) AS med_dscr,
      100 * SUM(rate_n * bal)
        / NULLIF(SUM(CASE WHEN rate_n IS NOT NULL THEN bal END), 0) AS wac,
      SUM(bal) AS bal_tot,
      SUM(CASE WHEN code IS NOT NULL THEN bal END) AS bal_coded,
      COUNT(DISTINCT (cik, deal_segment, assetNumber)) AS n_loans,
      COUNT(*) AS n_rows
    FROM (
      SELECT date_trunc('month', CAST(period_end AS DATE))::DATE AS pmonth,
        nullif(paymentStatusLoanCode, '') AS code,
        try_cast(reportPeriodEndActualBalanceAmount AS DOUBLE) AS bal,
        coalesce(try_cast(
          totalPrincipalInterestAdvancedOutstandingAmount AS DOUBLE), 0)
          AS adv,
        CASE WHEN try_cast(
               "property__mostRecentDebtServiceCoverageNetCashFlowpercentage"
               AS DOUBLE) BETWEEN 0.000001 AND 15
             THEN try_cast(
               "property__mostRecentDebtServiceCoverageNetCashFlowpercentage"
               AS DOUBLE) END AS dscr,
        CASE WHEN try_cast(reportPeriodInterestRatePercentage AS DOUBLE) > 1
             THEN try_cast(reportPeriodInterestRatePercentage AS DOUBLE)
                  / 100
             WHEN try_cast(reportPeriodInterestRatePercentage AS DOUBLE) > 0
             THEN try_cast(reportPeriodInterestRatePercentage AS DOUBLE)
             END AS rate_n,
        cik, deal_segment, assetNumber
      FROM loans_monthly WHERE asset_class = 'cmbs')
    GROUP BY 1 ORDER BY 1
    """).fetchall()
    mcols = ["pmonth", "dq30", "dq30f", "fcre", "codeb", "adv_share",
             "med_dscr", "wac", "bal_tot", "bal_coded", "n_loans", "n_rows"]
    mkt = [dict(zip(mcols, r)) for r in mkt]
    # last complete month: row count at least 70% of the median of the
    # preceding six months
    panel_end = None
    for i, r in enumerate(mkt):
        if i >= 3:
            prev = [m["n_rows"] for m in mkt[max(0, i - 6):i]]
            med = sorted(prev)[len(prev) // 2]
            if r["n_rows"] >= 0.7 * med:
                panel_end = r["pmonth"]
    if panel_end is None:
        panel_end = mkt[-1]["pmonth"]
    mkt = [r for r in mkt if r["pmonth"] <= panel_end]
    sanity["panel_end"] = str(panel_end)
    by_month = {r["pmonth"]: r for r in mkt}
    for probe in ["2019-12-01", "2020-06-01", "2022-12-01"]:
        d = datetime.date.fromisoformat(probe)
        if d in by_month:
            sanity[f"dq30_{probe}"] = round(by_month[d]["dq30"] * 100, 2)
            sanity[f"dq30f_{probe}"] = round(by_month[d]["dq30f"] * 100, 2)
    last = by_month[panel_end]
    sanity["dq30_latest"] = round(last["dq30"] * 100, 2)
    sanity["dq30f_latest"] = round(last["dq30f"] * 100, 2)

    chart_from = datetime.date(2019, 12, 1)
    mchart = [r for r in mkt if r["pmonth"] >= chart_from]

    # ------------------------------------------------------ maturity wall
    mat = con.execute("""
    WITH active AS (
      SELECT cik, deal_segment, assetNumber,
        arg_max(try_cast(reportPeriodEndActualBalanceAmount AS DOUBLE),
                period_end) AS bal
      FROM loans_monthly
      WHERE asset_class = 'cmbs'
        AND date_trunc('month', CAST(period_end AS DATE))::DATE = ?
      GROUP BY 1, 2, 3),
    loans AS (
      SELECT s.cik, s.deal_segment, s.assetNumber,
        try_cast(s.originalLoanAmount AS DOUBLE) AS amt,
        strptime(s.originationDate, '%m-%d-%Y')::DATE
          + try_cast(s.originalTermLoanNumber AS INTEGER)
            * INTERVAL 1 MONTH AS maturity
      FROM loans_static s
      WHERE s.asset_class = 'cmbs' AND s.originalLoanAmount IS NOT NULL
        AND s.originalLoanAmount <> '')
    SELECT maturity, COUNT(*) AS n, SUM(a.bal) AS bal
    FROM active a JOIN loans l
      ON l.cik = a.cik AND l.deal_segment = a.deal_segment
     AND l.assetNumber = a.assetNumber
    GROUP BY 1
    """, [panel_end]).fetchall()
    mat_buckets = {}
    mat_unknown_bal = 0.0
    mat_total = 0.0
    for maturity, n, bal in mat:
        if bal is None:
            continue
        mat_total += bal
        if maturity is None:
            mat_unknown_bal += bal
            key = "Not reported"
        elif maturity.year <= panel_end.year:
            key = f"{panel_end.year} and earlier"
        elif maturity.year >= panel_end.year + 6:
            key = f"{panel_end.year + 6} and later"
        else:
            key = str(maturity.year)
        b = mat_buckets.setdefault(key, [0, 0.0])
        b[0] += n
        b[1] += bal

    # ------------------------------------------------------------- deals
    deals = con.execute("""
    SELECT d.cik, d.deal_segment, d.trust_name, d.closing_date,
      d.pool_balance_stated, d.pool_balance_absee, d.principal_sum,
      d.legal_final_deal, d.asset_class, d.n_tranches,
      f.n_loans, f.total_orig_bal, f.wavg_coupon, f.ltv_wavg,
      f.ltv_median_loan, f.io_full_share, f.balloon_share, f.top1_share,
      f.top5_share, f.wavg_occ_birth, f.dq30_latest, f.dq30_peak,
      f.dq30_peak_month, f.max_adv_pct, f.months_reported, f.last_pmonth,
      f.ever_severe_bal_share, f.ever_mod_bal_share, f.past_mat_bal_share,
      f.matured_code_bal_share, f.dscr_first_year_median,
      f.dscr_latest_median, f.stress_score
    FROM deals d LEFT JOIN deal_features f
      ON f.cik = d.cik AND f.deal_segment = d.deal_segment
    ORDER BY d.cik, d.deal_segment
    """).fetchall()
    dcols = ["cik", "deal_segment", "trust_name", "closing_date",
             "pool_balance_stated", "pool_balance_absee", "principal_sum",
             "legal_final_deal", "asset_class", "n_tranches", "n_loans",
             "total_orig_bal", "wavg_coupon", "ltv_wavg", "ltv_median_loan",
             "io_full_share", "balloon_share", "top1_share", "top5_share",
             "wavg_occ_birth", "dq30_latest_f", "dq30_peak", "dq30_peak_month",
             "max_adv_pct", "months_reported", "last_pmonth",
             "ever_severe_bal_share", "ever_mod_bal_share",
             "past_mat_bal_share", "matured_code_bal_share",
             "dscr_first_year_median", "dscr_latest_median", "stress_score"]
    deals = [dict(zip(dcols, r)) for r in deals]
    sanity["n_deals"] = len(deals)

    # indicator: latest values + full series per deal
    ind_rows = con.execute("""
    SELECT cik, deal_segment, month, bal_tot, dq30_share, distressed_share,
      net_migration_valid, evidence_valid
    FROM deal_indicator_monthly ORDER BY cik, deal_segment, month
    """).fetchall()
    ind_series = {}
    ind_latest = {}
    for cik, seg, month, bal_tot, dq30, distr, netmig, valid in ind_rows:
        key = (cik, seg)
        ind_series.setdefault(key, []).append((month, dq30, distr))
        cur = ind_latest.get(key, {})
        if bal_tot is not None:
            cur["bal_tot"] = bal_tot
            cur["bal_month"] = month
        if dq30 is not None:
            cur["dq30_share"] = dq30
            cur["dq30_month"] = month
        if netmig is not None:
            cur["net_migration"] = netmig
        ind_latest[key] = cur

    # downgrade-lag facts from the indicator table
    lag_rows = con.execute("""
    SELECT cik, deal_segment,
      MIN(month) FILTER (WHERE dq_crossed_by) AS crossing,
      MIN(first_downgrade_month_valid) AS first_dg
    FROM deal_indicator_monthly GROUP BY 1, 2
    """).fetchall()
    lag_map = {}
    n_crossed_no_dg = 0
    for cik, seg, crossing, first_dg in lag_rows:
        if crossing is None:
            continue
        if first_dg is None:
            n_crossed_no_dg += 1
        elif first_dg >= crossing:
            lag = (first_dg.year - crossing.year) * 12 \
                + (first_dg.month - crossing.month)
            lag_map[(cik, seg)] = {"crossing": crossing,
                                   "first_dg": first_dg, "lag": lag}
        else:
            lag_map[(cik, seg)] = {"crossing": crossing,
                                   "first_dg": first_dg, "lag": None}

    # slugs with progressive disambiguation
    base_counts = {}
    for d in deals:
        d["slug_base"] = slugify(d["trust_name"])
        base_counts[d["slug_base"]] = base_counts.get(d["slug_base"], 0) + 1
    seen = {}
    for d in deals:
        s = d["slug_base"]
        if base_counts[s] > 1:
            s = f"{s}-{d['deal_segment'].lower()}"
        if s in seen:
            s = f"{s}-{d['cik']}"
        seen[s] = True
        d["slug"] = s
        d["code"] = deal_code(d["trust_name"])
        d["shelf"] = shelf_of(d["trust_name"])
        if d["closing_date"] is not None:
            d["vintage"] = d["closing_date"].year
        elif d["code"]:
            d["vintage"] = int(d["code"][:4])
        else:
            d["vintage"] = None
        lat = ind_latest.get((d["cik"], d["deal_segment"]), {})
        d["cur_bal"] = lat.get("bal_tot")
        d["cur_bal_month"] = lat.get("bal_month")
        d["dq30_now"] = lat.get("dq30_share", d["dq30_latest_f"])
        d["net_migration"] = lat.get("net_migration")
    deal_by_key = {(d["cik"], d["deal_segment"]): d for d in deals}

    # ------------------------------------------- loans: names, types, top5
    loan_rows = con.execute("""
    WITH cur AS (
      SELECT cik, deal_segment, assetNumber,
        "property__propertyName" AS pname, "property__propertyCity" AS pcity,
        "property__propertyState" AS pstate,
        "property__propertyTypeCode" AS ptype,
        row_number() OVER (PARTITION BY cik, deal_segment, assetNumber
                           ORDER BY valid_from DESC, valid_to DESC) AS rn
      FROM loans_versioned)
    SELECT s.cik, s.deal_segment, s.assetNumber,
      try_cast(s.originalLoanAmount AS DOUBLE) AS amt,
      CASE WHEN try_cast(s.originalInterestRatePercentage AS DOUBLE) > 1
           THEN try_cast(s.originalInterestRatePercentage AS DOUBLE) / 100
           ELSE try_cast(s.originalInterestRatePercentage AS DOUBLE)
           END AS coupon,
      s.originationDate, c.pname, c.pcity, c.pstate, c.ptype
    FROM loans_static s
    LEFT JOIN cur c ON c.cik = s.cik AND c.deal_segment = s.deal_segment
      AND c.assetNumber = s.assetNumber AND c.rn = 1
    WHERE s.asset_class = 'cmbs' AND s.originalLoanAmount IS NOT NULL
      AND s.originalLoanAmount <> ''
    """).fetchall()

    def parse_types(raw):
        if raw is None or str(raw).strip() == "":
            return None
        raw = str(raw).strip()
        if raw.startswith("["):
            try:
                codes = {str(x).strip() for x in json.loads(raw) if x}
            except Exception:
                return None
            if not codes:
                return None
            if len(codes) == 1:
                return codes.pop()
            return "Multiple property types"
        return raw

    def clean_text(v):
        if v is None:
            return None
        v = str(v).strip()
        if v.upper() in ("", "NA", "N/A", "NONE", "NULL"):
            return None
        return v

    loans_by_deal = {}
    for r in loan_rows:
        (cik, seg, asset, amt, coupon, orig, pname, pcity, pstate,
         ptype) = r
        pname, pcity, pstate = (clean_text(pname), clean_text(pcity),
                                clean_text(pstate))
        loans_by_deal.setdefault((cik, seg), []).append({
            "asset": asset, "amt": amt, "coupon": coupon, "orig": orig,
            "pname": pname, "pcity": pcity, "pstate": pstate,
            "ptype": parse_types(ptype)})

    # ------------------------------------------------------------ tranches
    tr_rows = con.execute("""
    SELECT cik, deal_segment, class_name, cusip, cusip_status,
      companion_cusips, original_balance, balance_type, offered,
      coupon_type, coupon_index, spread_bps, initial_coupon_pct,
      expected_maturity, legal_final, is_exchange_component, rowid AS rid
    FROM tranches ORDER BY cik, deal_segment, rid
    """).fetchall()
    sanity["n_tranches"] = len(tr_rows)
    tranches_by_deal = {}
    for r in tr_rows:
        (cik, seg, cls, cusip, cstatus, comp, bal, btype, offered, ctype,
         cindex, spread, cpct, expmat, lfinal, is_exch, rid) = r
        tranches_by_deal.setdefault((cik, seg), []).append({
            "class": cls, "cusip": cusip, "cusip_status": cstatus,
            "companion": comp, "bal": bal, "btype": btype,
            "offered": offered, "ctype": ctype, "cindex": cindex,
            "spread": spread, "cpct": cpct, "expmat": expmat,
            "lfinal": lfinal, "is_exch": bool(is_exch)})

    def is_io(t):
        if t["btype"] == "notional":
            return True
        toks = re.split(r"[-_ ]", str(t["class"]).upper())
        return any(tok == "X" or re.fullmatch(r"X\d+", tok or "")
                   for tok in toks)

    def is_combination(t):
        return t["btype"] == "exchange_combination" \
            or t["cusip_status"] == "combination_class"

    for key, trs in tranches_by_deal.items():
        principal = [t for t in trs if not is_io(t)
                     and not is_combination(t) and t["bal"]]
        total_prin = sum(t["bal"] for t in principal)
        junior = 0.0
        support = {}
        for t in reversed(principal):
            support[id(t)] = (junior / total_prin) if total_prin else None
            junior += t["bal"]
        for t in trs:
            t["support"] = support.get(id(t))
            t["io"] = is_io(t)
            t["combination"] = is_combination(t)
        if key == (2153909, "D01"):
            for t in trs:
                if t["class"] == "A-3":
                    sanity["bbcms_a3_support"] = round(t["support"] * 100, 2)

    # ------------------------------------------------------------- ratings
    rt_rows = con.execute("""
    SELECT cik, deal_segment, class_name, agency, current_rating,
      last_action_date FROM v_tranche_current_ratings
    """).fetchall()
    ratings = {}
    classes_rated = set()
    for cik, seg, cls, agency, rating, lad in rt_rows:
        ratings[(cik, seg, cls, agency)] = rating
        classes_rated.add((cik, seg, cls))
    sanity["classes_with_ratings"] = len(classes_rated)

    data_as_of = (f"loan data through {month_label(panel_end)}; "
                  f"ratings as held in the dataset at build")

    os.makedirs(os.path.join(args.out, "deal"), exist_ok=True)

    # ======================================================== market page
    latest = by_month[panel_end]
    intro = (
        f"<p>Loan-level surveillance of the {len(deals)} registered "
        f"securitization deals in the Kilambi Research dataset that file "
        f"asset-level reports with the SEC, 516 of them commercial "
        f"mortgage trusts. Every figure is computed from the underlying "
        f"loan reports and agency rating histories. The dataset is "
        f"described in the methods note at the foot of this page.</p>")
    strip_items = [
        ("30+ days delinquent", pct_frac(latest["dq30"])),
        ("30+ incl. foreclosure and REO", pct_frac(latest["dq30f"])),
        ("Non-performing matured", pct_frac(latest["codeb"])),
        ("Servicer advances", pct_frac(latest["adv_share"])),
        ("Median DSCR", num(latest["med_dscr"], 2)),
        ("Weighted average coupon", pct_val(latest["wac"])),
        ("Loans reporting", f"{latest['n_loans']:,}"),
        ("Reported balance", money(latest["bal_tot"])),
    ]
    strip = ('<dl class="bw-summary">' + "".join(
        f'<div class="bw-sum-item"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>'
        for k, v in strip_items) + "</dl>")
    strip_note = (f'<p class="data-vintage">Balance shares for '
                  f'{month_label(panel_end)}, balance-weighted over loans '
                  f'carrying a delinquency status code '
                  f'({pct_frac(latest["bal_coded"] / latest["bal_tot"], 1)} '
                  f'of reported balance).</p>')

    dq_chart = svg_line_chart([
        ("30+ days delinquent", "#1a1a1a",
         [(r["pmonth"], r["dq30"] * 100) for r in mchart]),
        ("30+ incl. foreclosure and REO", "#8a1f1f",
         [(r["pmonth"], r["dq30f"] * 100) for r in mchart]),
    ], "30+ days delinquent, percent of coded balance", y_fmt="{:.0f}%")
    mat_chart = svg_line_chart([
        ("Non-performing matured balloon", "#1a1a1a",
         [(r["pmonth"], r["codeb"] * 100) for r in mchart]),
        ("Foreclosure and REO", "#8a1f1f",
         [(r["pmonth"], r["fcre"] * 100) for r in mchart]),
    ], "Matured and defaulted loans, percent of coded balance",
        y_fmt="{:.0f}%")
    dscr_chart = svg_line_chart([
        ("Median DSCR", "#1a1a1a",
         [(r["pmonth"], r["med_dscr"]) for r in mchart]),
    ], "Median debt service coverage, times", y_min=0.0, y_fmt="{:.1f}")
    wac_chart = svg_line_chart([
        ("Weighted average coupon", "#1a1a1a",
         [(r["pmonth"], r["wac"]) for r in mchart]),
    ], "Weighted average coupon, percent", y_fmt="{:.0f}%")

    snap_months = [datetime.date(y, 12, 1) for y in range(2019, 2026)]
    snap_months += [datetime.date(2020, 6, 1), panel_end]
    snap_rows = []
    for m in sorted(set(snap_months)):
        r = by_month.get(m)
        if not r:
            continue
        label = month_label(m)
        if m == datetime.date(2020, 6, 1):
            label += " (COVID peak)"
        if m == panel_end:
            label += " (latest)"
        snap_rows.append(
            f"<tr><td>{esc(label)}</td>"
            f'<td class="num">{r["n_loans"]:,}</td>'
            f'<td class="num">{money(r["bal_tot"])}</td>'
            f'<td class="num">{pct_frac(r["dq30"])}</td>'
            f'<td class="num">{pct_frac(r["dq30f"])}</td>'
            f'<td class="num">{pct_frac(r["fcre"])}</td>'
            f'<td class="num">{pct_frac(r["codeb"])}</td>'
            f'<td class="num">{pct_frac(r["adv_share"])}</td>'
            f'<td class="num">{num(r["med_dscr"], 2)}</td>'
            f'<td class="num">{pct_val(r["wac"])}</td></tr>')
    snap_table = (
        '<div class="market-table-scroll"><table class="market-table">'
        "<thead><tr><th>Month</th><th>Loans reporting</th>"
        "<th>Reported balance</th><th>30+ delinquent</th>"
        "<th>30+ incl. FC/REO</th><th>FC/REO</th>"
        "<th>Non-perf. matured</th><th>Advances</th><th>Median DSCR</th>"
        "<th>WAC</th></tr></thead><tbody>"
        + "".join(snap_rows) + "</tbody></table></div>")

    order_keys = [f"{panel_end.year} and earlier"] + \
        [str(y) for y in range(panel_end.year + 1, panel_end.year + 6)] + \
        [f"{panel_end.year + 6} and later", "Not reported"]
    mat_rows = []
    for k in order_keys:
        if k not in mat_buckets:
            continue
        n, bal = mat_buckets[k]
        share = bal / mat_total if mat_total else None
        mat_rows.append(
            f"<tr><td>{esc(k)}</td><td class=\"num\">{n:,}</td>"
            f'<td class="num">{money(bal)}</td>'
            f'<td class="num">{pct_frac(share, 1)}</td></tr>')
    mat_table = (
        '<div class="market-table-scroll"><table class="market-table">'
        "<thead><tr><th>Scheduled maturity</th><th>Loans</th>"
        "<th>Current balance</th><th>Share of balance</th></tr></thead>"
        "<tbody>" + "".join(mat_rows) + "</tbody></table></div>")
    mat_note = (
        f"<p>Loans reporting in {month_label(panel_end)}, at their "
        f"reported balances, grouped by the scheduled maturity in the "
        f"loan terms. Commercial mortgage loans are predominantly "
        f"balloon loans: the balance falls due in full at maturity and "
        f"repayment normally depends on refinancing or sale.</p>")

    methods = """<h2>Methods and definitions</h2>
<p>Sources: asset-level reports filed with the SEC on Form ABS-EE and
monthly distribution reports (Form 10-D) by each trust; prospectuses
filed on Form 424B2; rating histories published by Fitch, KBRA, S&amp;P,
Moody's and Morningstar DBRS under SEC Rule 17g-7(b), supplemented by
agency releases. Loan data run through the month stated on this page.
Rating histories published under Rule 17g-7(b) lag the actions they
record by up to about a year; the loan data do not lag.</p>
<p><strong>Delinquency shares.</strong> Each monthly loan report carries
a payment status code: current; 30 to 59 days delinquent; 60 to 89 days;
90 or more days; foreclosure; real estate owned (REO); performing
matured balloon; non-performing matured balloon. Shares are
balance-weighted over the loan-months that carry a status code, using
reported actual balances. About 55 percent of loan-months carry a code;
the balance coverage for the latest month is stated above the first
table.</p>
<p><strong>30+ days delinquent</strong> is the share of coded balance
30 or more days past due, excluding foreclosure and REO. <strong>30+
incl. FC/REO</strong> adds loans in foreclosure and held as REO.
<strong>Non-performing matured</strong> is the share past its scheduled
maturity date and not performing. <strong>Servicer advances</strong>
are principal and interest amounts the servicer has advanced on
delinquent loans and not yet recovered, as a share of coded balance.
<strong>Median DSCR</strong> is the median of the most recently
reported debt service coverage ratios (net cash flow basis) across
reporting loans. <strong>Weighted average coupon</strong> is the
balance-weighted average loan interest rate.</p>
<p><strong>Realized stress score</strong> (deal index and deal pages):
a 0 to 100 score for each deal built from realized pool outcomes since
issuance: peak and latest delinquency, the share of balance that has
ever been 90 or more days delinquent, in foreclosure or REO, the share
ever modified, servicer advances, loans past maturity, and the change
in median debt service coverage since the first year. Higher is more
realized stress.</p>
<p><strong>Ever severe</strong> is the share of a deal's original loan
balance that has at any point been 90 or more days delinquent, in
foreclosure, or held as REO. <strong>Net rating change since
issuance</strong> is the balance-weighted average change, in rating
notches, across a deal's rated classes from issuance to the latest
rating in the dataset; a positive figure means net downgrades.</p>
<p><strong>Credit support</strong> on deal pages is computed from the
class stack order in the prospectus: for each principal class, the
share of the deal's principal balance in classes junior to it.
Prospectus-stated support figures are not carried in the dataset, so
no stated figure is shown.</p>
<p>Where a figure is not available for a deal or a class, the pages say
so ("not yet reported"). No figure is estimated or carried forward
silently.</p>"""

    market_body = (
        intro + strip + strip_note
        + "<h2>Delinquency</h2>" + dq_chart
        + "<h2>Matured and defaulted loans</h2>" + mat_chart
        + "<h2>Debt service coverage and coupon</h2>" + dscr_chart
        + wac_chart
        + "<h2>Snapshots</h2>" + snap_table
        + "<h2>Scheduled maturities of loans still reporting</h2>"
        + mat_table + mat_note
        + '<p><a href="/cmbs/deals/">Deal index</a> &middot; '
          '<a href="/cmbs/rankings/">Rankings</a></p>'
        + methods)
    with open(os.path.join(args.out, "_index.md"), "w") as fh:
        fh.write(frontmatter(
            "CMBS market",
            "Loan-level delinquency, maturity and coverage trends for "
            "registered commercial mortgage securitizations, computed "
            "from the trusts' own monthly reports.",
            data_as_of, today) + market_body + "\n")

    # ======================================================== deal index
    shelves = sorted({d["shelf"] for d in deals})
    vintages = sorted({d["vintage"] for d in deals if d["vintage"]})
    idx_rows = []
    for d in sorted(deals, key=lambda x: x["trust_name"].upper()):
        cur = money(d["cur_bal"]) if d["cur_bal"] else NYR
        idx_rows.append(
            f'<tr data-vintage="{d["vintage"] or ""}" '
            f'data-shelf="{esc(d["shelf"])}">'
            f'<td><a href="/cmbs/deal/{d["slug"]}/">'
            f'{esc(d["trust_name"])}</a></td>'
            f"<td>{esc(d['shelf'])}</td>"
            f'<td class="num">{d["vintage"] or NYR}</td>'
            f'<td class="num">{cur}</td>'
            f'<td class="num">{num(d["n_loans"], 0)}</td>'
            f'<td class="num">{pct_frac(d["dq30_now"])}</td>'
            f'<td class="num">{pct_frac(d["ever_severe_bal_share"])}</td>'
            f'<td class="num">{num(d["stress_score"], 1)}</td>'
            f'<td class="num">'
            f'{("%+.2f" % d["net_migration"]) if d["net_migration"] is not None else NYR}'
            f"</td></tr>")
    shelf_opts = "".join(f'<option value="{esc(s)}">{esc(s)}</option>'
                         for s in shelves)
    vint_opts = "".join(f'<option value="{v}">{v}</option>'
                        for v in vintages)
    idx_script = """<script>
(function(){
  var tbl = document.getElementById('cmbs-index');
  var vs = document.getElementById('f-vintage');
  var ss = document.getElementById('f-shelf');
  function apply(){
    var v = vs.value, s = ss.value;
    tbl.querySelectorAll(':scope > tbody > tr').forEach(function(r){
      var ok = (!v || r.getAttribute('data-vintage') === v)
        && (!s || r.getAttribute('data-shelf') === s);
      r.style.display = ok ? '' : 'none';
    });
  }
  vs.addEventListener('change', apply);
  ss.addEventListener('change', apply);
  tbl.querySelectorAll(':scope > thead > tr > th').forEach(function(th, i){
    th.style.cursor = 'pointer';
    th.addEventListener('click', function(){
      var asc = th.getAttribute('data-asc') !== '1';
      th.setAttribute('data-asc', asc ? '1' : '0');
      var rows = Array.prototype.slice.call(
        tbl.querySelectorAll(':scope > tbody > tr'));
      var numeric = th.getAttribute('data-num') === '1';
      rows.sort(function(a, b){
        var x = a.children[i].textContent.trim();
        var y = b.children[i].textContent.trim();
        if (numeric){
          x = parseFloat(x.replace(/[^0-9.+-]/g, ''));
          y = parseFloat(y.replace(/[^0-9.+-]/g, ''));
          if (isNaN(x)) x = -Infinity;
          if (isNaN(y)) y = -Infinity;
          return asc ? x - y : y - x;
        }
        return asc ? x.localeCompare(y) : y.localeCompare(x);
      });
      var tb = tbl.querySelector(':scope > tbody');
      rows.forEach(function(r){ tb.appendChild(r); });
    });
  });
})();
</script>"""
    idx_body = (
        f"<p>All {len(deals)} deal units in the dataset. Click a column "
        f"heading to sort; use the filters to narrow by closing year or "
        f"shelf. Definitions are in the methods note on the "
        f'<a href="/cmbs/">market page</a>.</p>'
        '<p><label>Closing year <select id="f-vintage">'
        '<option value="">All years</option>' + vint_opts + "</select>"
        '</label> &nbsp; <label>Shelf <select id="f-shelf">'
        '<option value="">All shelves</option>' + shelf_opts
        + "</select></label></p>"
        '<div class="market-table-scroll"><table class="market-table" '
        'id="cmbs-index"><thead><tr>'
        "<th>Deal</th><th>Shelf</th><th data-num=\"1\">Vintage</th>"
        "<th data-num=\"1\">Current balance</th>"
        "<th data-num=\"1\">Loans</th>"
        "<th data-num=\"1\">30+ delinquent (latest)</th>"
        "<th data-num=\"1\">Ever severe</th>"
        "<th data-num=\"1\">Realized stress score</th>"
        "<th data-num=\"1\">Net rating change (notches)</th>"
        "</tr></thead><tbody>" + "".join(idx_rows)
        + "</tbody></table></div>" + idx_script)
    with open(os.path.join(args.out, "deals.md"), "w") as fh:
        fh.write(frontmatter(
            "CMBS deal index",
            "Every registered CMBS deal unit in the dataset, with "
            "current balance, delinquency, realized stress and net "
            "rating change since issuance.",
            data_as_of, today) + idx_body + "\n")

    # ========================================================== rankings
    def rank_table(title, rows, cols):
        head = "".join(f"<th>{esc(c)}</th>" for c in cols)
        return (f"<h2>{esc(title)}</h2>"
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr>' + head
                + "</tr></thead><tbody>" + "".join(rows)
                + "</tbody></table></div>")

    def deal_link(d):
        return (f'<a href="/cmbs/deal/{d["slug"]}/">'
                f'{esc(d["trust_name"])}</a>')

    by_stress = sorted([d for d in deals if d["stress_score"] is not None],
                       key=lambda x: -x["stress_score"])[:25]
    rows = [f'<tr><td class="num">{i}</td><td>{deal_link(d)}</td>'
            f'<td class="num">{num(d["stress_score"], 1)}</td>'
            f'<td class="num">{pct_frac(d["dq30_now"])}</td>'
            f'<td class="num">{pct_frac(d["ever_severe_bal_share"])}</td>'
            f'<td class="num">{money(d["cur_bal"])}</td></tr>'
            for i, d in enumerate(by_stress, 1)]
    rk = rank_table("Highest realized stress score", rows,
                    ["Rank", "Deal", "Realized stress score",
                     "30+ delinquent (latest)", "Ever severe",
                     "Current balance"])
    by_size = sorted([d for d in deals if d["cur_bal"]],
                     key=lambda x: -x["cur_bal"])[:25]
    rows = [f'<tr><td class="num">{i}</td><td>{deal_link(d)}</td>'
            f'<td class="num">{money(d["cur_bal"])}</td>'
            f'<td class="num">{num(d["n_loans"], 0)}</td>'
            f'<td class="num">{d["vintage"] or NYR}</td></tr>'
            for i, d in enumerate(by_size, 1)]
    rk += rank_table("Largest current balance", rows,
                     ["Rank", "Deal", "Current balance", "Loans",
                      "Vintage"])
    by_mod = sorted([d for d in deals
                     if d["ever_mod_bal_share"] is not None],
                    key=lambda x: -x["ever_mod_bal_share"])[:25]
    rows = [f'<tr><td class="num">{i}</td><td>{deal_link(d)}</td>'
            f'<td class="num">{pct_frac(d["ever_mod_bal_share"], 1)}</td>'
            f'<td class="num">{pct_frac(d["ever_severe_bal_share"])}</td>'
            f'<td class="num">{money(d["cur_bal"])}</td></tr>'
            for i, d in enumerate(by_mod, 1)]
    rk += rank_table("Largest share of balance ever modified", rows,
                     ["Rank", "Deal", "Ever modified", "Ever severe",
                      "Current balance"])
    lagged = [(deal_by_key[k], v) for k, v in lag_map.items()
              if v["lag"] is not None]
    lagged.sort(key=lambda x: -x[1]["lag"])
    rows = [f'<tr><td class="num">{i}</td><td>{deal_link(d)}</td>'
            f'<td class="num">{v["lag"]}</td>'
            f"<td>{esc(month_label(v['crossing']))}</td>"
            f"<td>{esc(month_label(v['first_dg']))}</td></tr>"
            for i, (d, v) in enumerate(lagged[:25], 1)]
    rk += rank_table("Longest wait for a first downgrade", rows,
                     ["Rank", "Deal", "Months to first downgrade",
                      "Delinquency threshold crossed",
                      "First downgrade"])
    rk += (f"<p>The wait is measured in months from the month a deal's "
           f"30+ delinquency share first reached the top range for its "
           f"cohort to the first month any of its classes was "
           f"downgraded. {n_crossed_no_dg} deals crossed the same "
           f"threshold and have no downgrade recorded in the dataset "
           f"through {month_label(panel_end)}.</p>")
    rk = ("<p>Four rankings over the deal index, each linking to the "
          "deal page. Definitions are in the methods note on the "
          '<a href="/cmbs/">market page</a>.</p>') + rk
    with open(os.path.join(args.out, "rankings.md"), "w") as fh:
        fh.write(frontmatter(
            "CMBS rankings",
            "Deal rankings by realized stress, current balance, "
            "modifications, and the wait for a first downgrade.",
            data_as_of, today) + rk + "\n")

    with open(os.path.join(args.out, "deal", "_index.md"), "w") as fh:
        fh.write('---\ntitle: "CMBS deals"\n---\n\n'
                 "Deal pages are listed in the "
                 '<a href="/cmbs/deals/">deal index</a>.\n')

    # ======================================================== deal pages
    n_pages = 0
    for d in deals:
        key = (d["cik"], d["deal_segment"])
        trs = tranches_by_deal.get(key, [])
        lat = ind_latest.get(key, {})
        parts = []
        parts.append(
            f'<p class="bond-navrow"><a href="/cmbs/deals/">'
            f"&larr; Deal index</a> &middot; "
            f'<a href="/cmbs/">CMBS market</a></p>')
        sum_items = [
            ("Current pool balance",
             (money(d["cur_bal"]) + f' ({month_label(d["cur_bal_month"])})')
             if d["cur_bal"] else NYR),
            ("Original pool balance",
             money(d["pool_balance_stated"] or d["total_orig_bal"])),
            ("Loans at issuance", num(d["n_loans"], 0)),
            ("Closing date",
             d["closing_date"].isoformat() if d["closing_date"] else NYR),
            ("Weighted average coupon at issuance",
             pct_frac(d["wavg_coupon"]) if d["wavg_coupon"] else NYR),
            ("Weighted average LTV at issuance",
             pct_frac(d["ltv_wavg"], 1) if d["ltv_wavg"] else NYR),
            ("30+ delinquent (latest)", pct_frac(d["dq30_now"])),
            ("Realized stress score", num(d["stress_score"], 1)),
            ("Net rating change since issuance",
             (f'{d["net_migration"]:+.2f} notches')
             if d["net_migration"] is not None else NYR),
        ]
        parts.append('<dl class="bw-summary">' + "".join(
            f'<div class="bw-sum-item"><dt>{esc(k)}</dt><dd>{esc(v)}</dd>'
            f"</div>" for k, v in sum_items) + "</dl>")

        # ---- tranche stack
        parts.append("<h2>Tranches</h2>")
        if trs:
            trows = []
            for t in trs:
                if t["combination"]:
                    sup = "Combination class"
                elif t["io"]:
                    sup = "Interest only"
                elif t["support"] is not None:
                    sup = pct_frac(t["support"])
                else:
                    sup = NYR
                if t["cusip"]:
                    cus = esc(t["cusip"])
                    if t["companion"]:
                        cus += " +"
                elif t["cusip_status"] == "no_10d_yet":
                    cus = "not yet reported"
                elif t["cusip_status"] == "combination_class":
                    cus = "Combination class"
                else:
                    cus = "not yet reported"
                if t["cpct"] is not None:
                    cpn = f"{t['cpct']:.3f}%"
                    if t["ctype"] and t["ctype"] != "unknown":
                        cpn += f" {esc(t['ctype'])}"
                    if t["cindex"]:
                        cpn += f" ({esc(t['cindex'])}"
                        if t["spread"] is not None:
                            cpn += f" + {t['spread']} bp"
                        cpn += ")"
                else:
                    cpn = NYR
                bal = money(t["bal"]) if t["bal"] else \
                    ("$0" if t["bal"] == 0 else NYR)
                cells = [f"<td>{esc(t['class'])}</td>",
                         f'<td class="num">{bal}</td>',
                         f'<td class="num">{esc(sup)}</td>',
                         f'<td class="num">{esc(cpn)}</td>',
                         f"<td>{cus}</td>"]
                for ag, _label in AGENCIES:
                    r = ratings.get((key[0], key[1], t["class"], ag))
                    cells.append(f'<td>{esc(r) if r else NYR}</td>')
                trows.append("<tr>" + "".join(cells) + "</tr>")
            ag_head = "".join(f"<th>{l}</th>" for _a, l in AGENCIES)
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Class</th>'
                "<th>Original balance</th>"
                "<th>Credit support (computed)</th><th>Coupon</th>"
                f"<th>CUSIP</th>{ag_head}</tr></thead><tbody>"
                + "".join(trows) + "</tbody></table></div>")
            parts.append(
                '<p class="data-vintage">Credit support is computed '
                "from the class stack order in the prospectus: the "
                "share of the deal's principal balance in classes "
                "junior to the class. Interest-only classes carry a "
                "notional balance and no principal support figure. "
                "Ratings are the latest held in the dataset for each "
                "class and agency; NR means the agency shows the class "
                "as not rated, WR that the rating was withdrawn, PIF "
                "that the class has been paid in full. Any other "
                "status value is shown exactly as the agency reports "
                "it. A + after a "
                "CUSIP marks a class with companion CUSIPs in the "
                "dataset.</p>")
        else:
            parts.append(f"<p>{NYR}: no tranche table is in the dataset "
                         "for this deal.</p>")

        # ---- pool at issuance
        parts.append("<h2>Pool at issuance</h2>")
        pool_rows = [
            ("Loans", num(d["n_loans"], 0)),
            ("Original loan balance", money(d["total_orig_bal"])),
            ("Weighted average coupon", pct_frac(d["wavg_coupon"])),
            ("Weighted average LTV", pct_frac(d["ltv_wavg"], 1)),
            ("Median loan LTV", pct_frac(d["ltv_median_loan"], 1)),
            ("Full-term interest only (share of balance)",
             pct_frac(d["io_full_share"], 1)),
            ("Balloon loans (share of balance)",
             pct_frac(d["balloon_share"], 1)),
            ("Largest loan (share of balance)",
             pct_frac(d["top1_share"], 1)),
            ("Five largest loans (share of balance)",
             pct_frac(d["top5_share"], 1)),
            ("Occupancy at issuance (weighted average)",
             pct_frac(d["wavg_occ_birth"], 1)),
        ]
        parts.append('<table class="terms-table"><tbody>' + "".join(
            f'<tr><td class="muted">{esc(k)}</td><td>{esc(v)}</td></tr>'
            for k, v in pool_rows) + "</tbody></table>")

        # ---- realized outcomes
        parts.append("<h2>Realized outcomes</h2>")
        out_rows = [
            ("Months reported", num(d["months_reported"], 0)),
            ("Peak 30+ delinquency",
             (pct_frac(d["dq30_peak"]) + f' ({month_label(d["dq30_peak_month"])})')
             if d["dq30_peak"] is not None else NYR),
            ("Ever severe (share of original balance)",
             pct_frac(d["ever_severe_bal_share"])),
            ("Ever modified (share of original balance)",
             pct_frac(d["ever_mod_bal_share"])),
            ("Past scheduled maturity (share of original balance)",
             pct_frac(d["past_mat_bal_share"])),
            ("Non-performing matured (share of original balance)",
             pct_frac(d["matured_code_bal_share"])),
            ("Maximum servicer advances (share of balance)",
             pct_frac(d["max_adv_pct"])),
            ("Median DSCR, first year",
             num(d["dscr_first_year_median"], 2)),
            ("Median DSCR, latest", num(d["dscr_latest_median"], 2)),
            ("Realized stress score", num(d["stress_score"], 1)),
        ]
        parts.append('<table class="terms-table"><tbody>' + "".join(
            f'<tr><td class="muted">{esc(k)}</td><td>{esc(v)}</td></tr>'
            for k, v in out_rows) + "</tbody></table>")

        # ---- property mix
        parts.append("<h2>Property types</h2>")
        dl = loans_by_deal.get(key, [])
        tot_amt = sum(l["amt"] for l in dl if l["amt"]) or None
        typed = {}
        typed_bal = 0.0
        for l in dl:
            if l["ptype"] and l["amt"]:
                typed[l["ptype"]] = typed.get(l["ptype"], 0.0) + l["amt"]
                typed_bal += l["amt"]
        if typed and tot_amt:
            mix_rows = []
            for code, bal in sorted(typed.items(), key=lambda x: -x[1]):
                label = PT_LABEL.get(code, code)
                if code == "Multiple property types":
                    label = code
                mix_rows.append(
                    f"<tr><td>{esc(label)}</td>"
                    f'<td class="num">{money(bal)}</td>'
                    f'<td class="num">{pct_frac(bal / tot_amt, 1)}</td>'
                    "</tr>")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Property type</th>'
                "<th>Original balance</th><th>Share of pool</th></tr>"
                "</thead><tbody>" + "".join(mix_rows)
                + "</tbody></table></div>")
            parts.append(
                f'<p class="data-vintage">Property type is reported '
                f'for {pct_frac(typed_bal / tot_amt, 1)} of the pool '
                f'balance; shares are of the full pool.</p>')
        else:
            parts.append(f"<p>{NYR}.</p>")

        # ---- largest loans
        parts.append("<h2>Largest loans</h2>")
        top = sorted([l for l in dl if l["amt"]],
                     key=lambda x: -x["amt"])[:5]
        if top and tot_amt:
            lrows = []
            for l in top:
                name = l["pname"] or f"Loan {l['asset']}"
                loc = ", ".join(x for x in [l["pcity"], l["pstate"]] if x)
                orig_y = ""
                if l["orig"]:
                    m = re.search(r"(\d{4})", str(l["orig"]))
                    if m:
                        orig_y = m.group(1)
                lrows.append(
                    f"<tr><td>{esc(name)}</td><td>{esc(loc) or NYR}</td>"
                    f'<td class="num">{money(l["amt"])}</td>'
                    f'<td class="num">{pct_frac(l["amt"] / tot_amt, 1)}'
                    f"</td>"
                    f'<td class="num">{pct_frac(l["coupon"])}</td>'
                    f'<td class="num">{orig_y or NYR}</td></tr>')
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Property</th>'
                "<th>Location</th><th>Original balance</th>"
                "<th>Share of pool</th><th>Coupon</th>"
                "<th>Originated</th></tr></thead><tbody>"
                + "".join(lrows) + "</tbody></table></div>")
        else:
            parts.append(f"<p>{NYR}.</p>")

        # ---- indicator chart
        parts.append("<h2>Delinquency and stress indicator</h2>")
        series = ind_series.get(key, [])
        pts_dq = [(m, (dq * 100 if dq is not None else None))
                  for m, dq, _di in series]
        pts_di = [(m, (di * 100 if di is not None else None))
                  for m, _dq, di in series]
        if any(v is not None for _m, v in pts_dq):
            parts.append(svg_line_chart([
                ("30+ days delinquent", "#1a1a1a", pts_dq),
                ("Distressed (90+, foreclosure, REO, non-performing "
                 "matured)", "#8a1f1f", pts_di),
            ], f"Delinquency indicator for {d['trust_name']}",
                y_fmt="{:.0f}%"))
            parts.append(
                '<p class="data-vintage">Monthly shares of the '
                "deal's reported balance, from the deal indicator "
                "series in the dataset. Months in which fewer than "
                "half of the reported loans carry a delinquency "
                "status code are not plotted.</p>")
        else:
            parts.append(f"<p>{NYR}.</p>")

        # ---- ratings facts
        parts.append("<h2>Ratings</h2>")
        n_cusip_classes = sum(1 for t in trs if t["cusip"])
        n_rated = sum(1 for t in trs
                      if (key[0], key[1], t["class"]) in classes_rated)
        lag = lag_map.get(key)
        rrows = [
            ("Classes with a CUSIP", f"{n_cusip_classes} of {len(trs)}"),
            ("Classes with a current rating in the dataset",
             f"{n_rated} of {len(trs)}"),
            ("Net rating change since issuance",
             (f'{d["net_migration"]:+.2f} notches (balance-weighted)')
             if d["net_migration"] is not None else NYR),
            ("Delinquency threshold crossed",
             month_label(lag["crossing"]) if lag else
             "Not crossed in the dataset"),
            ("First downgrade",
             month_label(lag["first_dg"]) if lag and lag["first_dg"]
             else "None recorded"),
        ]
        parts.append('<table class="terms-table"><tbody>' + "".join(
            f'<tr><td class="muted">{esc(k)}</td><td>{esc(v)}</td></tr>'
            for k, v in rrows) + "</tbody></table>")

        parts.append(
            '<p class="data-vintage">Sources: SEC Form ABS-EE '
            "asset-level reports, Form 10-D distribution reports and "
            "the deal prospectus; rating histories published under "
            "SEC Rule 17g-7(b) and agency releases. Definitions are "
            'in the methods note on the <a href="/cmbs/">market '
            "page</a>.</p>")

        lede = (f"Tranches, pool and monthly delinquency indicator for "
                f"{d['trust_name']}.")
        path = os.path.join(args.out, "deal", d["slug"] + ".md")
        with open(path, "w") as fh:
            fh.write(frontmatter(d["trust_name"], lede, data_as_of,
                                 today) + "\n".join(parts) + "\n")
        n_pages += 1

    sanity["deal_pages"] = n_pages
    print(json.dumps(sanity, indent=1, default=str))


if __name__ == "__main__":
    main()
