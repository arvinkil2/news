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
  * Median DSCR (market and deal pages) is over ALL reported NCF DSCR
    values up to 15, including zero and negative reports; no exclusion
    of non-positive values.
  * The publication unit is the trust page. Filing units of one trust
    that are fragments of a same-named sibling unit (at most three
    months of loan reports, sitting at the edge of the sibling's
    series, with at least 80 percent of their dated loans carrying an
    origination date that appears in the sibling's loans) are combined
    into the sibling's page, which carries Hugo aliases for the
    fragment slugs and a filing sources note. Amounts are not part of
    the identity test: fragment filings state whole-loan amounts
    where the main unit states pari passu shares of the same loans.
    Same-named units that are not fragments keep separate pages with
    segment and CIK in the title.
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
        leg = " &nbsp;&nbsp; ".join(
            f'<span style="color:{c}">&#9644;</span> {esc(l)}'
            for l, c, _ in series)
        out.append(f'<p class="bond-chart-cap">{leg}</p>')
    return "\n".join(out)


def frontmatter(title, lede, data_as_of, date_str, aliases=None):
    fm = (f"---\ntitle: \"{esc(title)}\"\ndate: \"{date_str}\"\n"
          f"lede: \"{esc(lede)}\"\ndata_as_of: \"{esc(data_as_of)}\"\n")
    if aliases:
        fm += "aliases:\n" + "".join(f'  - "{a}"\n' for a in aliases)
    return fm + "---\n\n"


_PRELIM_PAREN = re.compile(r"\(\s*prelim\s*\)", re.IGNORECASE)


def normalize_rating(raw):
    """Return the display string for a rating value from the current
    state table. Some agency files concatenate the preliminary marker
    onto the rating (S&P: "NRprelim", "AAAprelim (sf)", "NR(prelim)").
    Separate the marker and show it as a qualifier so no concatenated
    artifact prints. All other values pass through unchanged."""
    if raw is None:
        return None
    s = str(raw).strip()
    if "prelim" not in s.lower():
        return s
    prelim = True
    s = _PRELIM_PAREN.sub("", s)
    s = re.sub(r"prelim", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip(" -")
    if not s:
        return "NR (prelim.)" if prelim else s
    return f"{s} (prelim.)"


_SMALL_WORDS = {"of", "the", "and", "for", "a", "an"}


def normalize_name(name):
    """Title-case an ALL-CAPS trust name for display. Names that are
    not entirely upper case pass through unchanged. Tokens containing
    digits (2019-GC40, 5C43) and known shelf acronyms keep their
    capitals; this is display only and never changes the slug."""
    s = str(name)
    if s != s.upper() or not any(c.isalpha() for c in s):
        return s
    keep = {"GS", "MS", "UBS", "DB", "WF", "JPM", "BOA", "ML", "CS",
            "BBCMS", "CMBS", "REMIC", "LLC", "LP", "II", "III", "IV",
            "VI", "US", "USA", "NY", "DE", "TR", "MT", "SC", "NC", "GA"}
    out = []
    for i, tok in enumerate(s.split(" ")):
        if not tok:
            continue
        core = tok.strip(",.")
        if any(c.isdigit() for c in core) or core in keep:
            out.append(tok)
        elif core.lower() in _SMALL_WORDS and i > 0:
            out.append(tok.lower())
        elif "-" in core:
            parts = []
            for p in core.split("-"):
                if any(c.isdigit() for c in p) or p in keep:
                    parts.append(p)
                else:
                    parts.append(p.capitalize())
            out.append("-".join(parts))
        else:
            out.append(core.capitalize() if core == tok else tok)
    return " ".join(out)


def parse_json_list(v):
    """Return a list of strings if v is a JSON list string, else None."""
    if v is None:
        return None
    s = str(v).strip()
    if not s.startswith("["):
        return None
    try:
        items = json.loads(s)
    except Exception:
        return None
    if not isinstance(items, list):
        return None
    return [str(x).strip() for x in items if str(x).strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    from zoneinfo import ZoneInfo
    today = datetime.datetime.now(
        ZoneInfo("America/Toronto")).date().isoformat()
    con = duckdb.connect(args.db, read_only=True)
    # Single-threaded throughout: parallel float aggregation is not
    # order-stable, and the section's output must be byte-identical
    # between runs (chart tick placement is boundary-sensitive).
    con.execute("SET threads=1")

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
      COUNT(*) AS n_rows,
      COUNT(dscr) AS n_dscr,
      SUM(CASE WHEN dscr_raw <= 0 THEN 1 ELSE 0 END) AS n_dscr_nonpos,
      SUM(CASE WHEN code IS NOT NULL THEN 1 ELSE 0 END) AS n_coded
    FROM (
      SELECT date_trunc('month', CAST(period_end AS DATE))::DATE AS pmonth,
        nullif(paymentStatusLoanCode, '') AS code,
        try_cast(reportPeriodEndActualBalanceAmount AS DOUBLE) AS bal,
        coalesce(try_cast(
          totalPrincipalInterestAdvancedOutstandingAmount AS DOUBLE), 0)
          AS adv,
        try_cast(
          "property__mostRecentDebtServiceCoverageNetCashFlowpercentage"
          AS DOUBLE) AS dscr_raw,
        CASE WHEN try_cast(
               "property__mostRecentDebtServiceCoverageNetCashFlowpercentage"
               AS DOUBLE) <= 15
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
             "med_dscr", "wac", "bal_tot", "bal_coded", "n_loans", "n_rows",
             "n_dscr", "n_dscr_nonpos", "n_coded"]
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
    tot_rows = sum(r["n_rows"] for r in mkt)
    tot_coded = sum(r["n_coded"] for r in mkt)
    panel_coded_share = (tot_coded / tot_rows) if tot_rows else None
    sanity["panel_coded_share"] = (
        round(panel_coded_share * 100, 1) if panel_coded_share else None)
    by_month = {r["pmonth"]: r for r in mkt}
    for probe in ["2019-12-01", "2020-06-01", "2022-12-01"]:
        d = datetime.date.fromisoformat(probe)
        if d in by_month:
            sanity[f"dq30_{probe}"] = round(by_month[d]["dq30"] * 100, 2)
            sanity[f"dq30f_{probe}"] = round(by_month[d]["dq30f"] * 100, 2)
            sanity[f"dscr_{probe}"] = by_month[d]["med_dscr"]
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
    for d in deals:
        d["trust_name_raw"] = d["trust_name"]
        d["trust_name"] = normalize_name(d["trust_name"])

    # indicator: latest values + full series per deal
    ind_rows = con.execute("""
    SELECT cik, deal_segment, month, bal_tot, dq30_share, distressed_share,
      net_migration_valid, evidence_valid
    FROM deal_indicator_monthly ORDER BY cik, deal_segment, month
    """).fetchall()
    ind_series = {}
    ind_latest = {}
    ind_bal = {}
    for cik, seg, month, bal_tot, dq30, distr, netmig, valid in ind_rows:
        key = (cik, seg)
        ind_series.setdefault(key, []).append((month, dq30, distr))
        if bal_tot is not None:
            ind_bal.setdefault(key, []).append((month, bal_tot))
        cur = ind_latest.get(key, {})
        if bal_tot is not None:
            cur["bal_tot"] = bal_tot
            cur["bal_month"] = month
        if dq30 is not None:
            cur["dq30_share"] = dq30
            cur["dq30_month"] = month
        if netmig is not None:
            cur["net_migration"] = netmig
            cur["net_migration_month"] = month
        ind_latest[key] = cur

    # downgrade-lag facts from the indicator table
    lag_rows = con.execute("""
    SELECT cik, deal_segment,
      MIN(month) FILTER (WHERE dq_crossed_by) AS crossing,
      MIN(first_downgrade_month_valid) AS first_dg
    FROM deal_indicator_monthly GROUP BY 1, 2 ORDER BY 1, 2
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
        d["net_migration_month"] = lat.get("net_migration_month")
    deal_by_key = {(d["cik"], d["deal_segment"]): d for d in deals}

    # ever-matured split by payment code (A performing, B non-performing),
    # share of original loan balance, per deal unit
    ever_rows = con.execute("""
    WITH codes AS (
      SELECT cik, deal_segment, assetNumber,
        MAX(CASE WHEN nullif(paymentStatusLoanCode, '') = 'A'
                 THEN 1 ELSE 0 END) AS ever_a,
        MAX(CASE WHEN nullif(paymentStatusLoanCode, '') = 'B'
                 THEN 1 ELSE 0 END) AS ever_b
      FROM loans_monthly WHERE asset_class = 'cmbs'
      GROUP BY 1, 2, 3),
    amts AS (
      SELECT cik, deal_segment, assetNumber,
        try_cast(originalLoanAmount AS DOUBLE) AS amt
      FROM loans_static WHERE asset_class = 'cmbs')
    SELECT c.cik, c.deal_segment,
      SUM(CASE WHEN c.ever_a = 1 THEN a.amt ELSE 0 END)
        / NULLIF(SUM(a.amt), 0),
      SUM(CASE WHEN c.ever_b = 1 THEN a.amt ELSE 0 END)
        / NULLIF(SUM(a.amt), 0)
    FROM codes c JOIN amts a
      ON a.cik = c.cik AND a.deal_segment = c.deal_segment
     AND a.assetNumber = c.assetNumber
    GROUP BY 1, 2
    """).fetchall()
    ever_ab = {(r[0], r[1]): (r[2], r[3]) for r in ever_rows}
    sanity["ever_ab_deals"] = len(ever_ab)

    # per-deal median DSCR on the market page population: all reported
    # NCF DSCR values up to 15, no exclusion of zero or negative reports
    _dscr_lm = """
      SELECT cik, deal_segment,
        date_trunc('month', CAST(period_end AS DATE))::DATE AS pmonth,
        try_cast(
          "property__mostRecentDebtServiceCoverageNetCashFlowpercentage"
          AS DOUBLE) AS dscr
      FROM loans_monthly WHERE asset_class = 'cmbs'"""
    dd_bounds = con.execute(f"""
    WITH lm AS ({_dscr_lm})
    SELECT cik, deal_segment, MIN(pmonth), MAX(pmonth)
    FROM lm GROUP BY 1, 2
    """).fetchall()
    deal_dscr = {}
    for cik, seg, first_m, last_m in dd_bounds:
        deal_dscr[(cik, seg)] = {"first_m": first_m, "last_m": last_m}
    for cik, seg, med in con.execute(f"""
    WITH lm AS ({_dscr_lm}),
    bounds AS (
      SELECT cik, deal_segment, MAX(pmonth) AS last_m
      FROM lm GROUP BY 1, 2)
    SELECT lm.cik, lm.deal_segment, MEDIAN(lm.dscr)
    FROM lm JOIN bounds b
      ON b.cik = lm.cik AND b.deal_segment = lm.deal_segment
     AND lm.pmonth = b.last_m
    WHERE lm.dscr <= 15
    GROUP BY 1, 2
    """).fetchall():
        deal_dscr[(cik, seg)]["latest"] = med
    for cik, seg, med in con.execute(f"""
    WITH lm AS ({_dscr_lm}),
    bounds AS (
      SELECT cik, deal_segment, MIN(pmonth) AS first_m
      FROM lm GROUP BY 1, 2)
    SELECT lm.cik, lm.deal_segment, MEDIAN(lm.dscr)
    FROM lm JOIN bounds b
      ON b.cik = lm.cik AND b.deal_segment = lm.deal_segment
     AND lm.pmonth >= b.first_m
     AND lm.pmonth < b.first_m + INTERVAL 12 MONTH
    WHERE lm.dscr <= 15
    GROUP BY 1, 2
    """).fetchall():
        deal_dscr[(cik, seg)]["first_year"] = med
    sanity["deal_dscr_deals"] = len(deal_dscr)

    # ------------------------------------------- loans: names, types, top5
    loan_rows = con.execute("""
    WITH cur AS (
      SELECT cik, deal_segment, assetNumber,
        "property__propertyName" AS pname, "property__propertyCity" AS pcity,
        "property__propertyState" AS pstate,
        "property__propertyTypeCode" AS ptype,
        row_number() OVER (PARTITION BY cik, deal_segment, assetNumber
                           ORDER BY valid_from DESC, valid_to DESC,
                             valid_from_acc DESC, valid_to_acc DESC,
                             "property__propertyTypeCode",
                             "property__propertyName") AS rn
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
    ORDER BY s.cik, s.deal_segment, s.assetNumber
    """).fetchall()

    def parse_types(raw):
        vals = parse_json_list(raw)
        if vals is not None:
            codes = set(vals)
            if not codes:
                return None
            if len(codes) == 1:
                return codes.pop()
            return "Multiple property types"
        if raw is None or str(raw).strip() == "":
            return None
        return str(raw).strip()

    def clean_text(v):
        if v is None:
            return None
        v = str(v).strip()
        if v.upper() in ("", "NA", "N/A", "NONE", "NULL"):
            return None
        return v

    def clean_list(v):
        """A stored text field may be a scalar or a JSON list of values
        (multi-property loans). Return a list of cleaned values."""
        vals = parse_json_list(v)
        if vals is not None:
            return [c for c in (clean_text(x) for x in vals) if c]
        c = clean_text(v)
        return [c] if c else []

    def code_is_f(raw):
        """Defeased status code F marks a defeased loan (in the data,
        1,187 of the 1,194 loans whose latest code is F have the
        property name replaced with "Defeased" by the filer; codes N
        and X never do). Multi-property loans store the code as a
        JSON list."""
        vals = parse_json_list(raw)
        if vals is not None:
            return any(v.upper() == "F" for v in vals)
        return str(raw or "").strip().upper() == "F"

    # Defeasance is permanent once it happens, and the latest
    # versioned record does not always carry the code, so a loan is
    # defeased when any of its versioned records carries code F.
    defeased_keys = set()
    for cik, seg, asset, dsc in con.execute("""
      SELECT cik, deal_segment, assetNumber,
        "property__DefeasedStatusCode"
      FROM loans_versioned
      GROUP BY 1, 2, 3, 4""").fetchall():
        if dsc and code_is_f(dsc):
            defeased_keys.add((cik, seg, asset))
    sanity["defeased_loans"] = len(defeased_keys)

    loans_by_deal = {}
    for r in loan_rows:
        (cik, seg, asset, amt, coupon, orig, pname, pcity, pstate,
         ptype) = r
        loans_by_deal.setdefault((cik, seg), []).append({
            "asset": asset, "amt": amt, "coupon": coupon, "orig": orig,
            "pnames": clean_list(pname), "pcities": clean_list(pcity),
            "pstates": clean_list(pstate),
            "ptype": parse_types(ptype),
            "defeased": (cik, seg, asset) in defeased_keys})

    # Collapse component records: a loan and its component records
    # (asset numbers such as 1 and 1-001) can both carry the loan's
    # full original amount in the filings. Where a component record
    # repeats the parent loan's amount, count the loan once. Records
    # with a distinct amount are kept as separate loans.
    def base_asset(asset):
        m = re.fullmatch(r"(.+)-\d+", str(asset))
        return m.group(1) if m else str(asset)

    n_collapsed = 0
    for key, dl in loans_by_deal.items():
        assets = {str(l["asset"]) for l in dl}
        groups = {}
        for l in dl:
            b = base_asset(l["asset"])
            g = b if (b in assets and str(l["asset"]) != b) else str(
                l["asset"])
            groups.setdefault(g, []).append(l)
        out = []
        for g, members in groups.items():
            if len(members) == 1:
                out.append(members[0])
                continue
            members.sort(key=lambda l: (str(l["asset"]) != g,
                                        str(l["asset"])))
            keep = members[0]
            kept = [keep]
            for m in members[1:]:
                if (keep["amt"] is not None and m["amt"] is not None
                        and abs(m["amt"] - keep["amt"])
                        <= 0.01 * max(keep["amt"], 1)):
                    n_collapsed += 1
                    keep["defeased"] = keep["defeased"] or m["defeased"]
                    # fill any missing display fields from the component
                    for f in ("pnames", "pcities", "pstates"):
                        if not keep[f] and m[f]:
                            keep[f] = m[f]
                    if keep["ptype"] is None:
                        keep["ptype"] = m["ptype"]
                    elif (m["ptype"] and m["ptype"] != keep["ptype"]):
                        keep["ptype"] = "Multiple property types"
                else:
                    kept.append(m)
            out.extend(kept)
        loans_by_deal[key] = out
    sanity["component_records_collapsed"] = n_collapsed
    filed_total = {k: sum(l["amt"] for l in dl if l["amt"])
                   for k, dl in loans_by_deal.items()}

    # --------------------------------------- publication units (merges)
    # A trust that filed under more than one CIK, or whose filings were
    # split in segmentation, can appear as several units with the same
    # name. A unit is a fragment of a same-named sibling when it holds
    # few months of loan reports, all of them inside the sibling's
    # months, and its loans match the sibling's loans on amount and
    # origination date. Fragments are combined into the sibling's page.
    # Same-named units that are not fragments stay separate pages.
    unit_months = {}
    for cik, seg, pm in con.execute("""
      SELECT DISTINCT cik, deal_segment,
        date_trunc('month', CAST(period_end AS DATE))::DATE
      FROM loans_monthly WHERE asset_class = 'cmbs'""").fetchall():
        unit_months.setdefault((cik, seg), set()).add(pm)

    def loan_dates(key):
        """Origination dates of a unit's loans that carry one.
        Component records often carry no date; they take their parent
        loan's identity and are excluded here. Amounts are NOT part of
        the identity test: the fragment filings state whole-loan
        amounts where the main unit states pari passu shares of the
        same loans (Wells Fargo 2016-C37 unit 850779 D01 loan 1 is
        filed at $52.5M against $26.25M in the main unit, same
        origination date), so an amount test fails on true fragments.
        Origination dates separate cleanly: true fragments match the
        main unit's dates on 91 to 100 percent of dated loans, while
        same-named units holding a different pool match on 0 to 21
        percent."""
        return [str(l["orig"]) for l in loans_by_deal.get(key, [])
                if l["orig"]]

    def _midx(d):
        return d.year * 12 + d.month

    def months_attached(um, mm):
        """A fragment's months sit at the edge of the main unit's
        series: inside it, in a contiguous block ending the month
        before the main series starts (the depositor-CIK unit usually
        holds the first report month and the trust-CIK series starts
        the month after), straddling that start, or starting the
        month after the main series ends."""
        if not um or not mm:
            return False
        lo, hi = min(mm), max(mm)
        before = [m for m in um if m < lo]
        after = [m for m in um if m > hi]
        if after:
            if before or len(after) != len(um):
                return False
            if _midx(min(after)) - _midx(hi) != 1:
                return False
        if before:
            if _midx(lo) - _midx(max(before)) != 1:
                return False
            if _midx(max(before)) - _midx(min(before)) != len(before) - 1:
                return False
        return True

    from collections import defaultdict
    name_groups = defaultdict(list)
    for d in deals:
        name_groups[d["trust_name"]].append(d)
    absorbed = {}          # stub key -> main key
    namesakes = defaultdict(list)  # key -> [other keys with same name]
    merge_census = []
    kept_census = []
    for name, units in name_groups.items():
        if len(units) < 2:
            continue
        units_sorted = sorted(
            units,
            key=lambda d: (-len(unit_months.get(
                (d["cik"], d["deal_segment"]), set())),
                -(d["n_loans"] or 0), d["cik"]))
        main = units_sorted[0]
        main_key = (main["cik"], main["deal_segment"])
        main_months = unit_months.get(main_key, set())
        main_dates = set(loan_dates(main_key))
        for u in units_sorted[1:]:
            ukey = (u["cik"], u["deal_segment"])
            um = unit_months.get(ukey, set())
            frag = False
            date_match = None
            if len(um) <= 3 and um and main_months \
                    and months_attached(um, main_months):
                ud = loan_dates(ukey)
                if ud and main_dates:
                    date_match = sum(1 for x in ud if x in main_dates) \
                        / len(ud)
                    frag = date_match >= 0.8
            if frag:
                absorbed[ukey] = main_key
                merge_census.append({
                    "trust": name, "stub": list(ukey),
                    "main": list(main_key), "stub_months": len(um),
                    "date_match": round(date_match, 3)})
            else:
                namesakes[main_key].append(ukey)
                namesakes[ukey].append(main_key)
                kept_census.append({
                    "trust": name, "unit": list(ukey),
                    "main": list(main_key), "months": len(um),
                    "date_match": (round(date_match, 3)
                                   if date_match is not None else None)})
    sanity["kept_separate_census"] = kept_census
    published = [d for d in deals
                 if (d["cik"], d["deal_segment"]) not in absorbed]
    sanity["units_total"] = len(deals)
    sanity["units_merged"] = len(absorbed)
    sanity["pages_published"] = len(published)
    sanity["merge_census"] = merge_census
    absorbed_by_main = defaultdict(list)
    for sk, mk in absorbed.items():
        absorbed_by_main[mk].append(sk)

    # identity mismatch: a unit whose loans were originated years after
    # the trust's own vintage, with no prospectus balance and no
    # tranches, does not hold that trust's pool (the Norwest case). Its
    # loan-derived content is suppressed and the page says so.
    for d in deals:
        key = (d["cik"], d["deal_segment"])
        years = []
        for l in loans_by_deal.get(key, []):
            m = re.search(r"(19|20)\d{2}", str(l["orig"] or ""))
            if m:
                years.append(int(m.group(0)))
        years.sort()
        med_year = years[len(years) // 2] if years else None
        d["identity_mismatch"] = bool(
            d["vintage"] and med_year
            and med_year >= d["vintage"] + 5
            and not d["pool_balance_stated"]
            and not d["n_tranches"])
    sanity["identity_mismatch"] = [
        d["trust_name"] for d in deals if d["identity_mismatch"]]

    # complete the same-name cross-links: every published unit of a
    # repeated name links to every other published unit of that name
    pub_keys_by_name = defaultdict(list)
    for d in published:
        pub_keys_by_name[d["trust_name"]].append(
            (d["cik"], d["deal_segment"]))
    for _name, _keys in pub_keys_by_name.items():
        if len(_keys) > 1:
            for _k in _keys:
                namesakes[_k] = [o for o in _keys if o != _k]

    for d in deals:
        key = (d["cik"], d["deal_segment"])
        if key in namesakes:
            d["display_name"] = (f'{d["trust_name"]} (segment '
                                 f'{d["deal_segment"]}, CIK {d["cik"]})')
        else:
            d["display_name"] = d["trust_name"]
    published_keys = {(d["cik"], d["deal_segment"]) for d in published}

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
      last_action_date, knowledge_date, current_outlook, current_watch
      FROM v_tranche_current_ratings
    """).fetchall()
    ratings = {}
    ratings_ow = {}
    classes_rated = set()
    ratings_asof = {}
    for cik, seg, cls, agency, rating, lad, kd, ow_o, ow_w in rt_rows:
        ratings[(cik, seg, cls, agency)] = normalize_rating(rating)
        ratings_ow[(cik, seg, cls, agency)] = (ow_o, ow_w)
        classes_rated.add((cik, seg, cls))
        d_asof = kd or lad
        if d_asof is not None:
            cur = ratings_asof.get((cik, seg))
            if cur is None or d_asof > cur:
                ratings_asof[(cik, seg)] = d_asof
    sanity["classes_with_ratings"] = len(classes_rated)
    all_ratings_dates = [v for v in ratings_asof.values()]
    ratings_global_asof = max(all_ratings_dates) if all_ratings_dates \
        else None

    # ---- Stage 2-CMBS: current balances from Form 10-D statements.
    # Snapshot rule: the latest statement row per class with a
    # distribution date on or before the build date. Classes and
    # deals without a statement row keep the at-issuance rendering
    # (partial coverage: absence is silence, no placeholders).
    cs_by_class = {}
    cs_by_deal = {}
    _cs_path = os.path.expanduser(
        "~/workspace/abs-ee/distribution-reports/"
        "current_support.parquet")
    if os.path.exists(_cs_path):
        _today = datetime.date.today().isoformat()
        _cs_rows = con.execute(
            "SELECT cik, deal_segment, cusip, ending_balance, "
            "factor_derived, support_derived, balance_type, "
            "pool_ending_balance, dist_date FROM read_parquet('"
            + _cs_path + "') WHERE dist_date <= DATE '" + _today
            + "' ORDER BY dist_date").fetchall()
        for _r in _cs_rows:
            cs_by_class[(_r[0], _r[1], _r[2])] = {
                "bal": _r[3], "factor": _r[4], "support": _r[5],
                "btype": _r[6], "pool": _r[7], "dist": _r[8]}
            # A deal counts as covered only when at least one of
            # its classes carries an actual current figure: 55 of
            # the snapshot's 510 deals have statement rows whose
            # balance, factor and support all failed to parse, and
            # those pages keep the at-issuance rendering (and no
            # 10-D credit) rather than a table of dashes.
            if (_r[3] is not None or _r[4] is not None
                    or _r[5] is not None):
                _dk = (_r[0], _r[1])
                _cur = cs_by_deal.get(_dk)
                if _cur is None or _r[8] > _cur["dist"]:
                    cs_by_deal[_dk] = {"dist": _r[8], "pool": _r[7]}
    sanity["cmbs_10d_classes"] = len(cs_by_class)
    sanity["cmbs_10d_deals"] = len(cs_by_deal)

    def deal_data_as_of(d):
        # The deal's own latest month of loan reports is the primary
        # date. deal_features.last_pmonth is stale for many deals (it
        # freezes at the features extract's last month: for 152 of 516
        # deals it precedes the deal's latest reported month, and it
        # is never later), so it is only a fallback.
        um = unit_months.get((d["cik"], d["deal_segment"]))
        lm = max(um) if um else (d.get("cur_bal_month")
                                 or d.get("last_pmonth"))
        ra = ratings_asof.get((d["cik"], d["deal_segment"]))
        s = f"loan data through {month_label(lm)}"
        if ra is not None:
            s += f"; ratings as held in the dataset at {ra.isoformat()}" \
                if hasattr(ra, "isoformat") else \
                f"; ratings as held in the dataset at {ra}"
        csd = cs_by_deal.get((d["cik"], d["deal_segment"]))
        if csd is not None:
            s += ("; current tranche balances from the Form 10-D "
                  "distribution statement for "
                  f"{csd['dist'].isoformat() if hasattr(csd['dist'], 'isoformat') else csd['dist']}")
        return s

    data_as_of = (f"loan data through {month_label(panel_end)}; "
                  f"ratings as held in the dataset at "
                  f"{ratings_global_asof}")

    # ============================ redesign loads (2026-10-19)
    # Page groups: a published page covers its main filing unit plus
    # any absorbed units; page_key maps every unit to its page unit.
    def page_key(k):
        return absorbed.get(k, k)

    STATUS_WORDS = {
        "0": "Current", "1": "30-59 days delinquent",
        "2": "60-89 days delinquent", "3": "90+ days delinquent",
        "4": "Foreclosure", "5": "Real estate owned (REO)",
        "A": "Matured balloon, performing",
        "B": "Matured balloon, non-performing"}

    def status_word(code):
        if code is None:
            return NYR
        return STATUS_WORDS.get(str(code).strip(),
                                f"Status code {esc(code)}")

    def dparse(s):
        """Versioned and static date fields are MM-DD-YYYY strings."""
        if s is None:
            return None
        s = str(s).strip()
        if not s:
            return None
        for fmt in ("%m-%d-%Y", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(s, fmt).date()
            except ValueError:
                pass
        return None

    def rate_disp(v):
        if v is None:
            return NYR
        if v <= 1:
            return pct_frac(v)
        return f"{v:.2f}%"

    def occ_disp(v):
        if v is None:
            return NYR
        if v <= 1.5:
            return pct_frac(v, 0)
        return f"{v:.0f}%"

    def dscr_disp(v):
        if v is None:
            return NYR
        if v > 15:
            return num(v / 100.0, 2)
        return num(v, 2)

    def month_shift(d, n):
        idx = d.year * 12 + (d.month - 1) + n
        return datetime.date(idx // 12, idx % 12 + 1, 1)

    # ---- component map: component asset -> parent asset, per unit,
    # using the same rule as the loan collapse above (a component
    # record repeats its parent loan's original amount).
    comp_map = {}
    _stat_amt = {}
    for cik, seg, asset, amt in con.execute("""
      SELECT cik, deal_segment, assetNumber,
        try_cast(originalLoanAmount AS DOUBLE)
      FROM loans_static WHERE asset_class = 'cmbs'""").fetchall():
        _stat_amt[(cik, seg, str(asset))] = amt
    for (cik, seg, asset), amt in _stat_amt.items():
        b = base_asset(asset)
        if b != asset and (cik, seg, b) in _stat_amt:
            pamt = _stat_amt[(cik, seg, b)]
            if amt is not None and pamt is not None and \
                    abs(amt - pamt) <= 0.01 * max(pamt, 1):
                comp_map[(cik, seg, asset)] = b

    def parent_asset(ukey, asset):
        return comp_map.get((ukey[0], ukey[1], str(asset)), str(asset))

    # ---- loan monthly essentials, merged to page groups. Row tuple:
    # (pm, code, bal, sbal, rate, dscr_ncf, dscr_noi, occ, adv,
    # mod_ind, fin_end, rev, exp, noi, ncf, period_end)
    # A loan can be reported more than once in a month (filings with
    # different period-end dates in the same month); the row kept
    # for a month is the one with the latest period end, then the
    # latest filing date.
    _per_unit_lm = {}
    _lm_meta = {}
    for r in con.execute("""
    WITH ranked AS (
      SELECT cik, deal_segment, assetNumber,
        date_trunc('month', CAST(period_end AS DATE))::DATE AS pm,
        nullif(paymentStatusLoanCode, '') AS code,
        try_cast(reportPeriodEndActualBalanceAmount AS DOUBLE) AS bal,
        try_cast(reportPeriodEndScheduledLoanBalanceAmount AS DOUBLE)
          AS sbal,
        try_cast(reportPeriodInterestRatePercentage AS DOUBLE) AS rate,
        try_cast("property__mostRecentDebtServiceCoverageNetCashFlowpercentage"
          AS DOUBLE) AS dscr_ncf,
        try_cast("property__mostRecentDebtServiceCoverageNetOperatingIncomePercentage"
          AS DOUBLE) AS dscr_noi,
        try_cast("property__mostRecentPhysicalOccupancyPercentage"
          AS DOUBLE) AS occ,
        try_cast(totalPrincipalInterestAdvancedOutstandingAmount
          AS DOUBLE) AS adv,
        nullif(reportPeriodModificationIndicator, '') AS mod_ind,
        "property__mostRecentFinancialsEndDate" AS fin_end,
        try_cast("property__mostRecentRevenueAmount" AS DOUBLE) AS rev,
        try_cast("property__operatingExpensesAmount" AS DOUBLE) AS exp,
        try_cast("property__mostRecentNetOperatingIncomeAmount"
          AS DOUBLE) AS noi,
        try_cast("property__mostRecentNetCashFlowAmount" AS DOUBLE)
          AS ncf,
        CAST(period_end AS DATE) AS pe,
        row_number() OVER (PARTITION BY cik, deal_segment, assetNumber,
          date_trunc('month', CAST(period_end AS DATE))
          ORDER BY CAST(period_end AS DATE) DESC, filing_date DESC,
            accession DESC, asset_seq DESC) AS rn
      FROM loans_monthly WHERE asset_class = 'cmbs')
    SELECT cik, deal_segment, assetNumber, pm, code, bal, sbal, rate,
      dscr_ncf, dscr_noi, occ, adv, mod_ind, fin_end, rev, exp, noi,
      ncf, pe
    FROM ranked WHERE rn = 1
    ORDER BY cik, deal_segment, assetNumber, pm""").fetchall():
        ukey = (r[0], r[1])
        raw_asset = str(r[2])
        asset = parent_asset(ukey, raw_asset)
        k = (ukey, asset)
        ent = _per_unit_lm.setdefault(k, {})
        meta = _lm_meta.setdefault(k, {})
        cand = (1 if raw_asset == asset else 0,
                r[18] or datetime.date.min)
        if r[3] not in ent or cand >= meta[r[3]]:
            ent[r[3]] = tuple(r[4:])
            meta[r[3]] = cand
    del _lm_meta
    loan_months = {}
    for (ukey, asset), bym in _per_unit_lm.items():
        pk = page_key(ukey)
        tgt = loan_months.setdefault((pk, asset), {})
        is_main = ukey == pk
        for pm, row in bym.items():
            if pm not in tgt or is_main:
                tgt[pm] = row
    del _per_unit_lm
    loan_months = {k: [(pm,) + v[pm] for pm in sorted(v)]
                   for k, v in loan_months.items()}
    loan_latest = {}
    loan_first_dq = {}
    for k, rows in loan_months.items():
        loan_latest[k] = rows[-1]
        for row in rows:
            if row[1] in ("1", "2", "3", "4", "5"):
                loan_first_dq[k] = row[0]
                break

    # ---- versioned loan detail: latest version per loan
    _ver_cols = """
      "property__propertyName" AS pname,
      "property__propertyAddress" AS paddr,
      "property__propertyCity" AS pcity,
      "property__propertyState" AS pstate,
      "property__propertyZip" AS pzip,
      "property__propertyTypeCode" AS ptype,
      "property__unitsBedsRoomsNumber" AS units,
      "property__netRentableSquareFeetNumber" AS sqft,
      "property__yearLastRenovated" AS yreno,
      mostRecentSpecialServicerTransferDate AS ss_t,
      mostRecentMasterServicerReturnDate AS ss_r,
      lastModificationDate AS mod_d,
      postModificationInterestPercentage AS post_rate,
      postModificationMaturityDate AS post_mat,
      liquidationPrepaymentCode AS liq_code,
      liquidationPrepaymentDate AS liq_d,
      try_cast(realizedLossToTrustAmount AS DOUBLE) AS loss,
      nonRecoverabilityIndicator AS nonrecov,
      workoutStrategyCode AS workout,
      try_cast("property__mostRecentValuationAmount" AS DOUBLE)
        AS val_amt,
      "property__mostRecentValuationDate" AS val_d,
      "property__mostRecentValuationSourceCode" AS val_src,
      "property__largestTenant" AS t1,
      try_cast("property__squareFeetLargestTenantNumber" AS DOUBLE)
        AS t1_sf,
      "property__leaseExpirationLargestTenantDate" AS t1_exp,
      "property__secondLargestTenant" AS t2,
      try_cast("property__squareFeetSecondLargestTenantNumber"
        AS DOUBLE) AS t2_sf,
      "property__leaseExpirationSecondLargestTenantDate" AS t2_exp,
      "property__thirdLargestTenant" AS t3,
      try_cast("property__squareFeetThirdLargestTenantNumber"
        AS DOUBLE) AS t3_sf,
      "property__leaseExpirationThirdLargestTenantDate" AS t3_exp,
      primaryServicerName AS servicer,
      primaryLoanServicerName AS loan_servicer,
      trusteeName AS trustee,
      maturityDate AS maturity,
      "property__DefeasedStatusCode" AS def_code"""
    _ver_alias = ("pname, paddr, pcity, pstate, pzip, ptype, units, "
                  "sqft, yreno, ss_t, ss_r, mod_d, post_rate, post_mat, "
                  "liq_code, liq_d, loss, nonrecov, workout, val_amt, "
                  "val_d, val_src, t1, t1_sf, t1_exp, t2, t2_sf, "
                  "t2_exp, t3, t3_sf, t3_exp, servicer, loan_servicer, "
                  "trustee, maturity, def_code")
    _ver_rows = con.execute(f"""
    WITH cur AS (
      SELECT cik, deal_segment, assetNumber, {_ver_cols},
        row_number() OVER (PARTITION BY cik, deal_segment, assetNumber
          ORDER BY valid_from DESC, valid_to DESC, valid_from_acc DESC,
            valid_to_acc DESC, "property__propertyName") AS rn
      FROM loans_versioned WHERE asset_class = 'cmbs')
    SELECT cik, deal_segment, assetNumber, {_ver_alias}
    FROM cur WHERE rn = 1""").fetchall()
    _ver_names = ["pname", "paddr", "pcity", "pstate", "pzip", "ptype",
                  "units", "sqft", "yreno", "ss_t", "ss_r", "mod_d",
                  "post_rate", "post_mat", "liq_code", "liq_d", "loss",
                  "nonrecov", "workout", "val_amt", "val_d", "val_src",
                  "t1", "t1_sf", "t1_exp", "t2", "t2_sf", "t2_exp",
                  "t3", "t3_sf", "t3_exp", "servicer", "loan_servicer",
                  "trustee", "maturity", "def_code"]
    ver_by_unit = {}
    for r in _ver_rows:
        ver_by_unit[(r[0], r[1], parent_asset((r[0], r[1]), r[2]))] = \
            dict(zip(_ver_names, r[3:]))
    ver_latest = {}
    for (cik, seg, asset), vd in ver_by_unit.items():
        pk = page_key((cik, seg))
        if (pk, asset) not in ver_latest or (cik, seg) == pk:
            ver_latest[(pk, asset)] = vd

    # ---- special servicing spells and event dates across versions
    # For each transfer date, the return date recorded in the most
    # recent filing that reports the transfer governs: an early
    # filing shows no return date, a later one records the return.
    ss_pairs = {}
    for cik, seg, asset, t, r_ in con.execute("""
    SELECT cik, deal_segment, assetNumber,
      mostRecentSpecialServicerTransferDate,
      arg_max(mostRecentMasterServicerReturnDate, valid_from)
    FROM loans_versioned WHERE asset_class = 'cmbs'
      AND nullif(mostRecentSpecialServicerTransferDate, '')
        IS NOT NULL
    GROUP BY 1, 2, 3, 4""").fetchall():
        pk = page_key((cik, seg))
        ss_pairs.setdefault(
            (pk, parent_asset((cik, seg), asset)), set()).add(
            (dparse(t), dparse(r_)))
    ss_pairs = {k: sorted(v, key=lambda x: (x[0] or
                                            datetime.date.min))
                for k, v in ss_pairs.items()}

    def loan_ss_now(k):
        vd = ver_latest.get(k)
        if not vd:
            return False
        t = dparse(vd.get("ss_t"))
        r_ = dparse(vd.get("ss_r"))
        return bool(t and (r_ is None or t > r_))

    # ---- modification and valuation event series per loan
    mod_events = {}
    for cik, seg, asset, md, prate, pmat, ppay in con.execute("""
    WITH ranked AS (
      SELECT cik, deal_segment, assetNumber, lastModificationDate,
        try_cast(postModificationInterestPercentage AS DOUBLE)
          AS prate,
        postModificationMaturityDate AS pmat,
        try_cast(postModificationPaymentAmount AS DOUBLE) AS ppay,
        row_number() OVER (PARTITION BY cik, deal_segment,
          assetNumber, lastModificationDate
          ORDER BY valid_from DESC, valid_to DESC, valid_from_acc DESC,
            valid_to_acc DESC) AS rn
      FROM loans_versioned WHERE asset_class = 'cmbs'
        AND nullif(lastModificationDate, '') IS NOT NULL)
    SELECT cik, deal_segment, assetNumber, lastModificationDate,
      prate, pmat, ppay
    FROM ranked WHERE rn = 1""").fetchall():
        pk = page_key((cik, seg))
        mod_events.setdefault(
            (pk, parent_asset((cik, seg), asset)), {})[str(md)] = (
            dparse(md), prate, dparse(pmat), ppay)
    mod_events = {k: sorted(v.values(), key=lambda x: x[0] or
                            datetime.date.min)
                  for k, v in mod_events.items()}
    val_events = {}
    for cik, seg, asset, va, vd_, vs in con.execute("""
    WITH ranked AS (
      SELECT cik, deal_segment, assetNumber,
        try_cast("property__mostRecentValuationAmount" AS DOUBLE)
          AS va,
        "property__mostRecentValuationDate" AS vd,
        "property__mostRecentValuationSourceCode" AS vs,
        row_number() OVER (PARTITION BY cik, deal_segment,
          assetNumber, "property__mostRecentValuationDate",
          try_cast("property__mostRecentValuationAmount" AS DOUBLE)
          ORDER BY valid_from DESC, valid_to DESC, valid_from_acc DESC,
            valid_to_acc DESC) AS rn
      FROM loans_versioned WHERE asset_class = 'cmbs'
        AND nullif("property__mostRecentValuationDate", '')
          IS NOT NULL)
    SELECT cik, deal_segment, assetNumber, va, vd, vs
    FROM ranked WHERE rn = 1""").fetchall():
        pk = page_key((cik, seg))
        val_events.setdefault(
            (pk, parent_asset((cik, seg), asset)), {})[
            (str(vd_), va)] = (dparse(vd_), va, vs)
    val_events = {k: sorted(v.values(), key=lambda x: x[0] or
                            datetime.date.min)
                  for k, v in val_events.items()}

    # ---- static loan terms per loan (grouped, main unit wins)
    _static_cols = """
      s.originationDate AS orig, s.originatorName AS originator,
      try_cast(s.originalTermLoanNumber AS INTEGER) AS term_m,
      try_cast(s.originalAmortizationTermNumber AS INTEGER)
        AS amort_m,
      try_cast(s.originalInterestOnlyTermNumber AS INTEGER) AS io_m,
      s.prepaymentLockOutEndDate AS lockout_end,
      s.prepaymentPremiumsEndDate AS prepay_end,
      s.yieldMaintenanceEndDate AS ym_end,
      try_cast(s."property__valuationSecuritizationAmount" AS DOUBLE)
        AS sec_val,
      s."property__valuationSecuritizationDate" AS sec_val_d,
      s."property__valuationSourceSecuritizationCode" AS sec_val_src,
      try_cast(s."property__yearBuiltNumber" AS INTEGER) AS ybuilt,
      try_cast(s."property__physicalOccupancySecuritizationPercentage"
        AS DOUBLE) AS sec_occ,
      try_cast(s."property__netOperatingIncomeSecuritizationAmount"
        AS DOUBLE) AS sec_noi,
      try_cast(s."property__netCashFlowFlowSecuritizationAmount"
        AS DOUBLE) AS sec_ncf"""
    _st_rows = con.execute(f"""
    SELECT s.cik, s.deal_segment, s.assetNumber, {_static_cols}
    FROM loans_static s WHERE s.asset_class = 'cmbs'""").fetchall()
    _st_names = ["orig", "originator", "term_m", "amort_m", "io_m",
                 "lockout_end", "prepay_end", "ym_end", "sec_val",
                 "sec_val_d", "sec_val_src", "ybuilt", "sec_occ",
                 "sec_noi", "sec_ncf"]
    static_by_loan = {}
    for r in _st_rows:
        ukey = (r[0], r[1])
        pk = page_key(ukey)
        k = (pk, parent_asset(ukey, r[2]))
        if k not in static_by_loan or ukey == pk:
            static_by_loan[k] = dict(zip(_st_names, r[3:]))

    def loan_maturity(k):
        vd = ver_latest.get(k)
        m = dparse(vd.get("maturity")) if vd else None
        if m:
            return m
        sd = static_by_loan.get(k, {})
        od = dparse(sd.get("orig"))
        if od and sd.get("term_m"):
            return month_shift(datetime.date(od.year, od.month, 1),
                               sd["term_m"]) + datetime.timedelta(
                                   days=od.day - 1)
        return None

    # ---- group loan lists: the published loan set of each page
    group_loans = {}
    for d in published:
        pk = (d["cik"], d["deal_segment"])
        units = [pk] + sorted(absorbed_by_main.get(pk, []))
        seen_assets = {}
        for uk in units:
            for l in loans_by_deal.get(uk, []):
                a = str(l["asset"])
                if a not in seen_assets:
                    seen_assets[a] = dict(l)
                    seen_assets[a]["unit"] = uk
        group_loans[pk] = sorted(
            seen_assets.values(),
            key=lambda l: (-(loan_latest.get((pk, str(l["asset"])),
                                            (None,) * 3)[2] or 0),
                           str(l["asset"])))

    # ---- per-deal current servicing aggregates (own latest month)
    # A loan belongs to the current pool only if it reported in the
    # deal's latest reporting month; loans that left the pool keep
    # their last reported balance in the loan table but do not enter
    # current shares.
    deal_serv = {}
    for pk, loans in group_loans.items():
        deal_pm = None
        for l in loans:
            lat = loan_latest.get((pk, str(l["asset"])))
            if lat and lat[2] is not None:
                if deal_pm is None or lat[0] > deal_pm:
                    deal_pm = lat[0]
        tot = ssb = disb = 0.0
        ssn = 0
        mat24 = 0.0
        for l in loans:
            k = (pk, str(l["asset"]))
            lat = loan_latest.get(k)
            if not lat or lat[2] is None or lat[0] != deal_pm:
                continue
            bal = lat[2]
            tot += bal
            ss = loan_ss_now(k)
            if ss:
                ssb += bal
                ssn += 1
            if ss or lat[1] in ("1", "2", "3", "4", "5"):
                disb += bal
            m = loan_maturity(k)
            if m and panel_end < m <= datetime.date(
                    panel_end.year + 2, panel_end.month,
                    panel_end.day):
                mat24 += bal
        deal_serv[pk] = {
            "tot": tot, "pm": deal_pm,
            "ss_share": (ssb / tot if tot else None),
            "ss_bal": ssb, "ss_n": ssn,
            "distress_share": (disb / tot if tot else None),
            "mat24_share": (mat24 / tot if tot else None)}
    sanity["deals_with_ss"] = sum(
        1 for v in deal_serv.values() if v["ss_n"])

    # ---- rating events per deal (unit keyed) and press events
    ev_rows = con.execute("""
    SELECT cik, deal_segment, class_name, agency, action_date,
      action_class, rating, prior_rating, outlook, watch_status,
      knowledge_date, event_uid
    FROM v_deal_tranche_rating_events
    ORDER BY cik, deal_segment, class_name, agency, action_date,
      knowledge_date, event_uid""").fetchall()
    events_by_deal = {}
    for r in ev_rows:
        events_by_deal.setdefault((r[0], r[1]), []).append({
            "class": r[2], "agency": r[3], "action_date": r[4],
            "action_class": r[5],
            "rating": normalize_rating(r[6]),
            "prior": normalize_rating(r[7]),
            "outlook": r[8], "watch": r[9], "knowledge": r[10]})
    press_by_deal = {}
    for r in con.execute("""
    SELECT CAST(cik AS INTEGER), deal_segment, agency, knowledge_date,
      action_date, action_class, action_raw, instrument_name, rating,
      prior_rating, outlook, release_title, release_url
    FROM press_events WHERE cik IS NOT NULL AND deal_segment IS NOT NULL
    ORDER BY knowledge_date""").fetchall():
        press_by_deal.setdefault((r[0], r[1]), []).append({
            "agency": r[2],
            "knowledge": (dparse(r[3]) if isinstance(r[3], str)
                          else r[3]),
            "action_date": (dparse(r[4]) if isinstance(r[4], str)
                            else r[4]),
            "action_class": r[5], "action_raw": r[6], "class": r[7],
            "rating": r[8], "prior": r[9], "outlook": r[10],
            "title": r[11], "url": r[12]})
    sanity["deals_with_events"] = len(events_by_deal)

    # ---- stable loan URL slugs per deal (punctuation-safe)
    loan_slug = {}
    for pk, loans in group_loans.items():
        used = set()
        for l in sorted(loans, key=lambda x: str(x["asset"])):
            base = re.sub(r"[^A-Za-z0-9]+", "-",
                          str(l["asset"])).strip("-") or "x"
            kk = base
            n = 2
            while kk in used:
                kk = f"{base}-{n}"
                n += 1
            used.add(kk)
            loan_slug[(pk, str(l["asset"]))] = kk

    # ============================ loan page selection
    # File budget: Cloudflare Pages free plan allows 20,000 files
    # per deployment. 9,000 are reserved for the rest of the site
    # (about 2,700 files today) and its growth; the CMBS section
    # gets 11,000, of which about 1,240 are non-loan pages after
    # this redesign (deal, ratings and annex pages, indexes and
    # data files). Loan page budget: 9,700.
    LOAN_PAGE_BUDGET = 9700

    def loan_has_event(k, l):
        if k in loan_first_dq or k in ss_pairs or k in mod_events:
            return True
        if l.get("defeased"):
            return True
        vd = ver_latest.get(k, {})
        if dparse(vd.get("liq_d")) or (vd.get("loss") or 0) > 0:
            return True
        if str(vd.get("nonrecov") or "").lower() == "true":
            return True
        m = loan_maturity(k)
        lat = loan_latest.get(k)
        if m and m < panel_end and lat and (lat[2] or 0) > 0:
            return True
        return False

    _top_by_deal = {}
    for pk, loans in group_loans.items():
        ranked = sorted(
            loans,
            key=lambda l: (-(loan_latest.get(
                (pk, str(l["asset"])), (None,) * 3)[2] or 0),
                str(l["asset"])))
        _top_by_deal[pk] = [str(l["asset"]) for l in ranked]

    def loan_selection(threshold, top_n):
        sel = set()
        for pk, loans in group_loans.items():
            tops = set(_top_by_deal[pk][:top_n])
            for l in loans:
                k = (pk, str(l["asset"]))
                lat = loan_latest.get(k)
                if str(l["asset"]) in tops or loan_has_event(k, l) \
                        or (lat and (lat[2] or 0) >= threshold):
                    sel.add(k)
        return sel

    LOAN_THRESHOLD = 20_000_000
    loan_page_keys = loan_selection(LOAN_THRESHOLD, 10)
    _top_n = 10
    while len(loan_page_keys) > LOAN_PAGE_BUDGET \
            and LOAN_THRESHOLD < 200_000_000:
        LOAN_THRESHOLD += 5_000_000
        loan_page_keys = loan_selection(LOAN_THRESHOLD, _top_n)
    if len(loan_page_keys) > LOAN_PAGE_BUDGET:
        _top_n = 5
        loan_page_keys = loan_selection(LOAN_THRESHOLD, _top_n)
    while LOAN_THRESHOLD > 5_000_000:
        trial = loan_selection(LOAN_THRESHOLD - 5_000_000, _top_n)
        if len(trial) <= LOAN_PAGE_BUDGET - 250:
            LOAN_THRESHOLD -= 5_000_000
            loan_page_keys = trial
        else:
            break
    sanity["loan_pages_selected"] = len(loan_page_keys)
    sanity["loan_threshold"] = LOAN_THRESHOLD
    sanity["loan_top_n"] = _top_n

    # ============================ market aggregates (redesign)
    prev_month = month_shift(panel_end, -1)

    # ---- delinquency bucket ladder, latest and prior month
    ladder = {}
    for pm, code, n, bal in con.execute("""
    SELECT date_trunc('month', CAST(period_end AS DATE))::DATE,
      nullif(paymentStatusLoanCode, ''), COUNT(*),
      SUM(try_cast(reportPeriodEndActualBalanceAmount AS DOUBLE))
    FROM loans_monthly WHERE asset_class = 'cmbs'
      AND date_trunc('month', CAST(period_end AS DATE))::DATE
        IN (?, ?)
    GROUP BY 1, 2""", [prev_month, panel_end]).fetchall():
        ladder.setdefault(pm, {})[code] = (n, bal or 0.0)
    ladder_codes = [("0", "Current"), ("1", "30-59 days delinquent"),
                    ("2", "60-89 days delinquent"),
                    ("3", "90+ days delinquent"),
                    ("4", "Foreclosure"), ("5", "Real estate owned"),
                    ("A", "Matured balloon, performing"),
                    ("B", "Matured balloon, non-performing")]
    lad_rows = []
    for code, label in ladder_codes:
        n9, b9 = ladder.get(panel_end, {}).get(code, (0, 0.0))
        n8, b8 = ladder.get(prev_month, {}).get(code, (0, 0.0))
        coded9 = sum(v[1] for c, v in ladder.get(panel_end, {}).items()
                     if c is not None)
        share = (b9 / coded9) if coded9 else None
        chg = b9 - b8
        lad_rows.append(
            f"<tr><td>{esc(label)}</td>"
            f'<td class="num">{n9:,}</td>'
            f'<td class="num">{money(b9)}</td>'
            f'<td class="num">{pct_frac(share)}</td>'
            f'<td class="num">{"+" if chg > 0 else ""}{money(chg) if chg else "$0"}</td></tr>')
    _c9 = sum(v[1] for c, v in ladder.get(panel_end, {}).items()
              if c is not None)
    _c8 = sum(v[1] for c, v in ladder.get(prev_month, {}).items()
              if c is not None)
    _n9 = sum(v[0] for c, v in ladder.get(panel_end, {}).items()
              if c is not None)
    lad_rows.append(
        f"<tr><td><strong>Loans with a status code</strong></td>"
        f'<td class="num">{_n9:,}</td>'
        f'<td class="num">{money(_c9)}</td>'
        f'<td class="num">100.0%</td>'
        f'<td class="num">{"+" if _c9 - _c8 > 0 else ""}{money(_c9 - _c8)}</td></tr>')
    ladder_table = (
        '<div class="market-table-scroll"><table class="market-table">'
        "<thead><tr><th>Payment status</th><th>Loans</th>"
        "<th>Balance</th><th>Share of coded balance</th>"
        f"<th>Balance change vs {month_label(prev_month)}</th>"
        "</tr></thead><tbody>" + "".join(lad_rows)
        + "</tbody></table></div>")

    # ---- delinquency flows between the last two months
    flow = con.execute("""
    WITH m AS (
      SELECT cik, deal_segment, assetNumber,
        date_trunc('month', CAST(period_end AS DATE))::DATE AS pm,
        nullif(paymentStatusLoanCode, '') AS code,
        try_cast(reportPeriodEndActualBalanceAmount AS DOUBLE) AS bal
      FROM loans_monthly WHERE asset_class = 'cmbs')
    , piv AS (
      SELECT cik, deal_segment, assetNumber,
        MAX(CASE WHEN pm = ? THEN code END) AS c_prev,
        MAX(CASE WHEN pm = ? THEN code END) AS c_cur,
        MAX(CASE WHEN pm = ? THEN bal END) AS b_cur
      FROM m WHERE pm IN (?, ?) GROUP BY 1, 2, 3)
    SELECT
      COUNT(*) FILTER (WHERE c_cur IN ('1','2','3','4','5')
        AND (c_prev IS NULL
             OR c_prev NOT IN ('1','2','3','4','5'))) AS new_n,
      SUM(b_cur) FILTER (WHERE c_cur IN ('1','2','3','4','5')
        AND (c_prev IS NULL
             OR c_prev NOT IN ('1','2','3','4','5'))) AS new_bal,
      COUNT(*) FILTER (WHERE c_prev IN ('1','2','3','4','5')
        AND c_cur = '0') AS cure_n,
      SUM(b_cur) FILTER (WHERE c_prev IN ('1','2','3','4','5')
        AND c_cur = '0') AS cure_bal
    FROM piv""", [prev_month, panel_end, panel_end,
                  prev_month, panel_end]).fetchone()
    flow_txt = (
        f"<p>In {month_label(panel_end)}, {flow[0]:,} loans "
        f"({money(flow[1] or 0)}) entered 30+ day delinquency, "
        f"foreclosure or REO, counting loans delinquent in the month "
        f"that were not delinquent in {month_label(prev_month)} "
        f"(including loans reporting for the first time). "
        f"{flow[2]:,} loans ({money(flow[3] or 0)}) cured to current "
        f"from a delinquent status.</p>")

    # ---- special servicing and distress monthly series
    ss_series = con.execute("""
    WITH pairs AS (
      SELECT cik, deal_segment, assetNumber,
        strptime(mostRecentSpecialServicerTransferDate,
          '%m-%d-%Y')::DATE AS t,
        strptime(arg_max(mostRecentMasterServicerReturnDate,
          valid_from), '%m-%d-%Y')::DATE AS r
      FROM loans_versioned WHERE asset_class = 'cmbs'
        AND nullif(mostRecentSpecialServicerTransferDate, '')
          IS NOT NULL
      GROUP BY 1, 2, 3, 4),
    lm AS (
      SELECT cik, deal_segment, assetNumber,
        date_trunc('month', CAST(period_end AS DATE))::DATE AS pm,
        nullif(paymentStatusLoanCode, '') AS code,
        try_cast(reportPeriodEndActualBalanceAmount AS DOUBLE) AS bal
      FROM loans_monthly WHERE asset_class = 'cmbs'),
    flag AS (
      SELECT lm.cik, lm.deal_segment, lm.assetNumber, lm.pm, lm.code,
        lm.bal,
        MAX(CASE WHEN p.t IS NOT NULL THEN 1 ELSE 0 END) AS is_ss
      FROM lm LEFT JOIN pairs p
        ON p.cik = lm.cik AND p.deal_segment = lm.deal_segment
       AND p.assetNumber = lm.assetNumber
       AND p.t <= last_day(lm.pm)
       AND (p.r IS NULL OR p.r > last_day(lm.pm))
      GROUP BY 1, 2, 3, 4, 5, 6)
    SELECT pm, SUM(bal), SUM(bal) FILTER (WHERE code IS NOT NULL),
      SUM(bal) FILTER (WHERE is_ss = 1),
      SUM(bal) FILTER (WHERE is_ss = 1
        OR code IN ('1','2','3','4','5'))
    FROM flag GROUP BY 1 ORDER BY 1""").fetchall()
    ss_by_month = {r[0]: r for r in ss_series}
    ss_latest_row = ss_by_month.get(panel_end)
    ss_latest_share = (ss_latest_row[3] / ss_latest_row[2]
                       if ss_latest_row and ss_latest_row[2] else None)
    distress_latest_share = (ss_latest_row[4] / ss_latest_row[2]
                             if ss_latest_row and ss_latest_row[2]
                             else None)
    sanity["ss_share_latest"] = (
        round(ss_latest_share * 100, 2) if ss_latest_share else None)
    sanity["distress_share_latest"] = (
        round(distress_latest_share * 100, 2)
        if distress_latest_share else None)
    ss_chart = svg_line_chart([
        ("Specially serviced", "#1a1a1a",
         [(r[0], (r[3] / r[2] * 100 if r[2] and r[3] is not None
                  else None))
          for r in ss_series if r[0] >= chart_from]),
        ("Distress (30+ delinquent or specially serviced)", "#8a1f1f",
         [(r[0], (r[4] / r[2] * 100 if r[2] and r[4] is not None
                  else None))
          for r in ss_series if r[0] >= chart_from]),
    ], "Special servicing and distress, percent of coded balance",
        y_fmt="{:.1f}%")

    # ---- delinquency by property type (current month)
    pt_rows = con.execute("""
    WITH cur AS (
      SELECT cik, deal_segment, assetNumber,
        "property__propertyTypeCode" AS ptype,
        CASE WHEN nullif(mostRecentSpecialServicerTransferDate, '')
               IS NOT NULL
             AND (nullif(mostRecentMasterServicerReturnDate, '')
                    IS NULL
                  OR strptime(mostRecentSpecialServicerTransferDate,
                       '%m-%d-%Y')::DATE
                     > strptime(mostRecentMasterServicerReturnDate,
                       '%m-%d-%Y')::DATE)
             THEN 1 ELSE 0 END AS ss_now,
        row_number() OVER (PARTITION BY cik, deal_segment, assetNumber
          ORDER BY valid_from DESC, valid_to DESC, valid_from_acc DESC,
            valid_to_acc DESC, "property__propertyTypeCode") AS rn
      FROM loans_versioned WHERE asset_class = 'cmbs'),
    lm AS (
      SELECT cik, deal_segment, assetNumber,
        nullif(paymentStatusLoanCode, '') AS code,
        try_cast(reportPeriodEndActualBalanceAmount AS DOUBLE) AS bal
      FROM loans_monthly WHERE asset_class = 'cmbs'
        AND date_trunc('month', CAST(period_end AS DATE))::DATE = ?)
    SELECT c.ptype, COUNT(*), SUM(l.bal),
      SUM(l.bal) FILTER (WHERE l.code IN ('1','2','3')),
      SUM(l.bal) FILTER (WHERE l.code IN ('1','2','3','4','5')),
      SUM(l.bal) FILTER (WHERE c.ss_now = 1)
    FROM lm l JOIN cur c ON c.cik = l.cik
      AND c.deal_segment = l.deal_segment
      AND c.assetNumber = l.assetNumber AND c.rn = 1
    GROUP BY 1""", [panel_end]).fetchall()
    pt_data = []
    for ptype, n, bal, dq, dqf, ssb in pt_rows:
        label = parse_types(ptype)
        if label is None:
            label = "Not reported"
        elif label != "Multiple property types":
            label = PT_LABEL.get(label, label)
        pt_data.append((label, n, bal or 0.0, dq, dqf, ssb))
    pt_data.sort(key=lambda x: (-x[2], x[0]))
    pt_total = sum(x[2] for x in pt_data) or 1.0
    pt_trs = []
    for label, n, bal, dq, dqf, ssb in pt_data:
        if bal <= 0:
            continue
        pt_trs.append(
            f"<tr><td>{esc(label)}</td>"
            f'<td class="num">{n:,}</td>'
            f'<td class="num">{money(bal)}</td>'
            f'<td class="num">{pct_frac(bal / pt_total, 1)}</td>'
            f'<td class="num">{pct_frac(dq / bal if dq else 0)}</td>'
            f'<td class="num">{pct_frac(dqf / bal if dqf else 0)}</td>'
            f'<td class="num">{pct_frac(ssb / bal if ssb else 0)}</td>'
            "</tr>")
    pt_table = (
        '<div class="market-table-scroll"><table class="market-table">'
        "<thead><tr><th>Property type</th><th>Loans</th>"
        "<th>Balance</th><th>Share</th><th>30+ delinquent</th>"
        "<th>30+ incl. FC/REO</th><th>Specially serviced</th></tr>"
        "</thead><tbody>" + "".join(pt_trs) + "</tbody></table></div>")

    # property-type delinquency trend for the largest types
    pt_trend_rows = con.execute("""
    WITH cur AS (
      SELECT cik, deal_segment, assetNumber,
        "property__propertyTypeCode" AS ptype,
        row_number() OVER (PARTITION BY cik, deal_segment, assetNumber
          ORDER BY valid_from DESC, valid_to DESC, valid_from_acc DESC,
            valid_to_acc DESC, "property__propertyTypeCode") AS rn
      FROM loans_versioned WHERE asset_class = 'cmbs'),
    lm AS (
      SELECT cik, deal_segment, assetNumber,
        date_trunc('month', CAST(period_end AS DATE))::DATE AS pm,
        nullif(paymentStatusLoanCode, '') AS code,
        try_cast(reportPeriodEndActualBalanceAmount AS DOUBLE) AS bal
      FROM loans_monthly WHERE asset_class = 'cmbs')
    SELECT c.ptype, lm.pm, SUM(lm.bal),
      SUM(lm.bal) FILTER (WHERE lm.code IN ('1','2','3','4','5'))
    FROM lm JOIN cur c ON c.cik = lm.cik
      AND c.deal_segment = lm.deal_segment
      AND c.assetNumber = lm.assetNumber AND c.rn = 1
    GROUP BY 1, 2 ORDER BY 1, 2""").fetchall()
    pt_series = {}
    for ptype, pm, bal, dqbal in pt_trend_rows:
        label = parse_types(ptype)
        if label is None or label == "Multiple property types":
            continue
        label = PT_LABEL.get(label, label)
        acc = pt_series.setdefault(label, {})
        b0, d0 = acc.get(pm, (0.0, 0.0))
        acc[pm] = (b0 + (bal or 0.0), d0 + (dqbal or 0.0))
    pt_series = {label: sorted(
        (pm, (dq / bal * 100 if bal else None))
        for pm, (bal, dq) in acc.items())
        for label, acc in pt_series.items()}
    top_types = [x[0] for x in pt_data
                 if x[0] in pt_series][:4]
    pt_charts = ""
    for label in top_types:
        pts = [(pm, v) for pm, v in pt_series[label]
               if pm >= chart_from]
        if sum(1 for _p, v in pts if v is not None) >= 3:
            pt_charts += svg_line_chart(
                [("30+ incl. FC/REO", "#1a1a1a", pts)],
                f"{label}: 30+ delinquent incl. foreclosure and REO, "
                f"percent of the type's reported balance",
                y_fmt="{:.1f}%")

    # ---- liquidations and realized losses by quarter
    liq_rows = con.execute("""
    WITH cur AS (
      SELECT cik, deal_segment, assetNumber,
        strptime(liquidationPrepaymentDate, '%m-%d-%Y')::DATE AS liq_d,
        try_cast(realizedLossToTrustAmount AS DOUBLE) AS loss,
        row_number() OVER (PARTITION BY cik, deal_segment, assetNumber
          ORDER BY valid_from DESC, valid_to DESC, valid_from_acc DESC,
            valid_to_acc DESC) AS rn
      FROM loans_versioned WHERE asset_class = 'cmbs'
        AND nullif(liquidationPrepaymentDate, '') IS NOT NULL),
    liq AS (SELECT * FROM cur WHERE rn = 1),
    lastbal AS (
      SELECT l.cik, l.deal_segment, l.assetNumber,
        arg_max(try_cast(m.reportPeriodEndActualBalanceAmount
          AS DOUBLE),
          date_trunc('month', CAST(m.period_end AS DATE))) AS bal
      FROM liq l JOIN loans_monthly m
        ON m.cik = l.cik AND m.deal_segment = l.deal_segment
       AND m.assetNumber = l.assetNumber AND m.asset_class = 'cmbs'
       AND date_trunc('month', CAST(m.period_end AS DATE))
           <= date_trunc('month', l.liq_d)
      GROUP BY 1, 2, 3)
    SELECT date_trunc('quarter', l.liq_d)::DATE AS q, COUNT(*),
      SUM(b.bal), SUM(l.loss)
    FROM liq l LEFT JOIN lastbal b
      ON b.cik = l.cik AND b.deal_segment = l.deal_segment
     AND b.assetNumber = l.assetNumber
    GROUP BY 1 ORDER BY 1""").fetchall()
    liq_trs = []
    for q, n, bal, loss in liq_rows:
        if q < datetime.date(panel_end.year - 5, 1, 1):
            continue
        sev = (loss / bal) if (loss is not None and bal) else None
        liq_trs.append(
            f"<tr><td>{q.year} Q{((q.month - 1) // 3) + 1}</td>"
            f'<td class="num">{n:,}</td>'
            f'<td class="num">{money(bal or 0)}</td>'
            f'<td class="num">{money(loss or 0)}</td>'
            f'<td class="num">{pct_frac(sev)}</td></tr>')
    liq_table = (
        '<div class="market-table-scroll"><table class="market-table">'
        "<thead><tr><th>Quarter of liquidation</th><th>Loans</th>"
        "<th>Balance at liquidation</th><th>Realized losses</th>"
        "<th>Average severity</th></tr></thead><tbody>"
        + "".join(liq_trs) + "</tbody></table></div>")

    # ---- realized maturity outcomes by scheduled maturity year
    def loan_maturity_sched(k):
        sd = static_by_loan.get(k, {})
        od = dparse(sd.get("orig"))
        if od and sd.get("term_m"):
            base = month_shift(datetime.date(od.year, od.month, 1),
                               sd["term_m"])
            return base + datetime.timedelta(days=od.day - 1)
        return loan_maturity(k)

    mat_out = {}
    for pk, loans in group_loans.items():
        for l in loans:
            k = (pk, str(l["asset"]))
            m = loan_maturity_sched(k)
            if m is None or m.year < 2018 or m.year > panel_end.year - 1:
                continue
            rows = loan_months.get(k, [])
            if not rows:
                continue
            vd = ver_latest.get(k, {})
            bym = {r[0]: r for r in rows}
            mm = datetime.date(m.year, m.month, 1)
            bal_m = None
            for cand in (mm, month_shift(mm, -1), month_shift(mm, 1)):
                if cand in bym and bym[cand][2] is not None:
                    bal_m = bym[cand][2]
                    break
            if bal_m is None:
                bal_m = l["amt"] or 0.0
            liq_d = dparse(vd.get("liq_d"))
            loss = vd.get("loss")
            code_b = any(r[1] == "B" and r[0] >= month_shift(mm, -1)
                         for r in rows)
            if liq_d is not None or (loss or 0) > 0 or code_b:
                outcome = "defaulted"
            elif any(md and md >= month_shift(mm, -3)
                     for md, *_ in mod_events.get(k, [])):
                outcome = "extended"
            elif rows[-1][0] <= month_shift(mm, 1):
                outcome = "paid"
            else:
                outcome = "outstanding"
            e = mat_out.setdefault(m.year, {"paid": [0, 0.0],
                                            "extended": [0, 0.0],
                                            "defaulted": [0, 0.0],
                                            "outstanding": [0, 0.0]})
            e[outcome][0] += 1
            e[outcome][1] += bal_m
    mo_trs = []
    for y in sorted(mat_out):
        e = mat_out[y]
        tot_b = sum(v[1] for v in e.values())
        if not tot_b:
            continue
        mo_trs.append(
            f"<tr><td>{y}</td>"
            f'<td class="num">{e["paid"][0]:,}</td>'
            f'<td class="num">{pct_frac(e["paid"][1] / tot_b, 1)}</td>'
            f'<td class="num">{e["extended"][0]:,}</td>'
            f'<td class="num">{pct_frac(e["extended"][1] / tot_b, 1)}</td>'
            f'<td class="num">{e["defaulted"][0]:,}</td>'
            f'<td class="num">{pct_frac(e["defaulted"][1] / tot_b, 1)}</td>'
            f'<td class="num">{e["outstanding"][0]:,}</td>'
            f'<td class="num">{pct_frac(e["outstanding"][1] / tot_b, 1)}</td></tr>')
    mat_out_table = (
        '<div class="market-table-scroll"><table class="market-table">'
        "<thead><tr><th>Scheduled maturity year</th>"
        "<th>Paid off (loans)</th><th>Paid off (share)</th>"
        "<th>Extended or modified (loans)</th>"
        "<th>Extended (share)</th>"
        "<th>Defaulted (loans)</th><th>Defaulted (share)</th>"
        "<th>Still outstanding (loans)</th>"
        "<th>Still outstanding (share)</th></tr></thead><tbody>"
        + "".join(mo_trs) + "</tbody></table></div>")

    # ---- issuance by closing year
    iss_rows = con.execute("""
    SELECT EXTRACT(year FROM closing_date)::INTEGER AS y, COUNT(*),
      SUM(COALESCE(pool_balance_stated, pool_balance_absee))
    FROM deals WHERE asset_class = 'cmbs' AND closing_date IS NOT NULL
    GROUP BY 1 ORDER BY 1""").fetchall()
    iss_trs = "".join(
        f"<tr><td>{y}</td>"
        f'<td class="num">{n:,}</td>'
        f'<td class="num">{money(bal or 0)}</td></tr>'
        for y, n, bal in iss_rows if y)
    iss_table = (
        '<div class="market-table-scroll"><table class="market-table">'
        "<thead><tr><th>Closing year</th><th>Filing units</th>"
        "<th>Stated pool balance at closing</th></tr></thead><tbody>"
        + iss_trs + "</tbody></table></div>")

    universe_note = (
        '<p class="data-vintage"><strong>Universe.</strong> This '
        "section covers the registered securitizations that file "
        "asset-level reports with the SEC under Regulation AB II: "
        f"{len(deals)} filing units combined into {len(published)} "
        "deal pages, conduit-heavy and excluding private placements, "
        "single-borrower deals that do not file asset-level reports, "
        "and agency deals. Delinquency and servicing rates published "
        "by the rating agencies (for example KBRA and Morningstar "
        "DBRS headline delinquency rates) cover the broader rated "
        "private-label universe, including deals that file no "
        "asset-level data, and use different definitions; they are "
        "not directly comparable with the figures here. Every rate "
        "on this page is computed on the universe just described, "
        "from the loans' own monthly reports.</p>")

    market_extra = (
        "<h2>Delinquency ladder</h2>" + ladder_table + flow_txt
        + '<p class="data-vintage">Shares are of the balance of '
          "loans carrying a payment status code in the month. The "
          "30+ days delinquent figure in the summary strip is the "
          "sum of the 30-59, 60-89 and 90+ rows; adding the "
          "foreclosure and REO rows gives the 30+ incl. FC/REO "
          "figure.</p>"
        + "<h2>Special servicing and distress</h2>" + ss_chart
        + '<p class="data-vintage"><strong>Specially serviced '
          "share</strong> is the share of coded balance in loans "
          "the filings show as transferred to the special servicer "
          "and not shown as returned to the master servicer in that "
          "month. <strong>Distress share</strong> is the share of "
          "coded balance in loans 30 or more days delinquent "
          "(including foreclosure and REO) or currently with the "
          "special servicer; a loan in both groups is counted once. "
          "The asset-level filings carry special servicer transfer "
          "and return dates; they do not carry servicer watchlist "
          "flags, and no watchlist figure is shown.</p>"
        + "<h2>Delinquency by property type</h2>" + pt_table
        + pt_charts
        + '<p class="data-vintage">Property type is the latest '
          "type reported for each loan; balances and status are "
          f"for {month_label(panel_end)}. Trends show the largest "
          "property types by current balance.</p>"
        + "<h2>Liquidations and losses</h2>" + liq_table
        + '<p class="data-vintage">Liquidations are dated by the '
          "liquidation or prepayment date in the asset-level "
          "filings. Balance at liquidation is the loan's last "
          "reported balance in or before the liquidation month. "
          "Severity is the realized loss to the trust divided by "
          "that balance.</p>"
        + "<h2>Realized maturity outcomes</h2>" + mat_out_table
        + '<p class="data-vintage">Loans whose scheduled maturity '
          "(origination date plus original term in the loan terms) "
          "fell in the year, classified by what the reports show "
          "since: paid off (the loan leaves the reported set in "
          "its maturity month or the month after, with no "
          "liquidation and no loss), extended or modified (a "
          "modification is recorded at or after maturity), "
          "defaulted (liquidation, a realized loss, or a "
          "non-performing matured balloon status), or still "
          "outstanding. Shares are of the balance scheduled to "
          "mature in the year, measured at the maturity month.</p>"
        + "<h2>Issuance</h2>" + iss_table
        + '<p class="data-vintage">Filing units in the dataset by '
          "closing year as filed, at the pool balance stated in "
          "the prospectus (or the filed loan total where no stated "
          "balance is carried).</p>")

    methods2 = f"""<p><strong>Special servicing.</strong> The asset-level
filings record, for each loan, the most recent date it was transferred
to the special servicer and the most recent date it was returned to the
master servicer. A loan is counted as specially serviced in a month
when a transfer date falls in or before that month and no later return
date is recorded. The filings do not include servicer watchlist
criteria or flags, so no watchlist measure is published.</p>
<p><strong>Distress share</strong> is the share of coded balance in
loans that are 30 or more days delinquent (including foreclosure and
REO) or specially serviced, each loan counted once.</p>
<p><strong>Loan pages.</strong> Every loan appears in the loan table
of its deal page. A loan also has a page of its own when it carries a
surveillance history (delinquency of 30 or more days, special
servicing, a modification, liquidation or loss, defeasance, a
non-recoverability indicator, or a scheduled maturity in the past with
a balance still reported), when its latest reported balance is at or
above {money(LOAN_THRESHOLD)}, or when it is one of the
{"ten" if _top_n == 10 else "five"} largest loans in its deal. The
size threshold is set so the section stays within the publishing
platform's limit of 20,000 files per deployment. Every other loan has
a full detail section in its deal's loan annex, linked from the loan
table; no loan is omitted.</p>
<p><strong>Rating action dates and public knowledge.</strong> Rating
histories are published by the agencies under SEC Rule 17g-7(b). Each
action on a deal's rating history page shows the date the agency took
the action and the date of the agency's published history file in
which the action is recorded in this dataset (labeled "Publicly
knowable"). Because the dataset holds each agency's current published
history, that date is the current file's publication date and is an
upper bound on when the action first became public in this form:
earlier editions of the file carried older actions sooner. Agency
releases collected in the dataset are shown separately, with their
own publication dates.</p>"""
    sanity["market_extra_built"] = True

    os.makedirs(os.path.join(args.out, "deal"), exist_ok=True)

    # ======================================================== market page
    latest = by_month[panel_end]
    n_cmbs_units = sum(1 for d in deals if d["asset_class"] == "cmbs")
    intro = (
        f"<p>Loan-level surveillance of the registered securitization "
        f"deals in the Kilambi Research dataset that file asset-level "
        f"reports with the SEC: {len(published)} deal pages covering "
        f"{len(deals)} filing units, {n_cmbs_units} of the units "
        f"commercial mortgage trusts. Every figure is computed from "
        f"the underlying loan reports and agency rating histories. "
        f"The dataset is described in the methods note at the foot of "
        f"this page.</p>")
    strip_items = [
        ("30+ days delinquent", pct_frac(latest["dq30"])),
        ("30+ incl. foreclosure and REO", pct_frac(latest["dq30f"])),
        ("Specially serviced", pct_frac(ss_latest_share)),
        ("Distress (delinquent or specially serviced)",
         pct_frac(distress_latest_share)),
        ("Matured balloon, non-performing", pct_frac(latest["codeb"])),
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
    ], "30+ days delinquent, percent of coded balance", y_fmt="{:.1f}%")
    mat_chart = svg_line_chart([
        ("Matured balloon, non-performing", "#1a1a1a",
         [(r["pmonth"], r["codeb"] * 100) for r in mchart]),
        ("Foreclosure and REO", "#8a1f1f",
         [(r["pmonth"], r["fcre"] * 100) for r in mchart]),
    ], "Matured and defaulted loans, percent of coded balance",
        y_fmt="{:.1f}%")
    dscr_chart = svg_line_chart([
        ("Median DSCR", "#1a1a1a",
         [(r["pmonth"], r["med_dscr"]) for r in mchart]),
    ], "Median debt service coverage, times", y_min=0.0, y_fmt="{:.1f}")
    wac_chart = svg_line_chart([
        ("Weighted average coupon", "#1a1a1a",
         [(r["pmonth"], r["wac"]) for r in mchart]),
    ], "Weighted average coupon, percent", y_fmt="{:.1f}%")

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
        "<th>Matured, non-perf.</th><th>Advances</th><th>Median DSCR</th>"
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

    methods = f"""<h2>Methods and definitions</h2>
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
reported actual balances. Across the full panel,
{pct_frac(panel_coded_share, 1)} of loan-months carry a code; the coded
loans' share of reported balance for the latest month is stated above
the first table.</p>
<p><strong>30+ days delinquent</strong> is the share of coded balance
30 or more days past due, excluding foreclosure and REO. <strong>30+
incl. FC/REO</strong> adds loans in foreclosure and held as REO.
<strong>Matured balloon, non-performing</strong> is the share of
coded balance in loans currently carrying the non-performing matured
balloon status: past their scheduled maturity and not performing.
<strong>Servicer advances</strong>
are principal and interest amounts the servicer has advanced on
delinquent loans and not yet recovered, as a share of coded balance.
<strong>Median DSCR</strong> is the median of the most recently
reported debt service coverage ratios (net cash flow basis) across
all reporting loans, including loans that report zero or negative
coverage; reported values above 15 are excluded as errors. In
{month_label(panel_end)} the median covers {latest['n_dscr']:,} loan
reports, of which {latest['n_dscr_nonpos']:,} report zero or negative
coverage. Deal-page median DSCR uses the same population over the
deal's own reports, for its first twelve reported months and its
latest reported month. <strong>Weighted average coupon</strong> is
the balance-weighted average loan interest rate.</p>
<p><strong>Matured balloon, performing</strong> and <strong>matured
balloon, non-performing</strong> on deal pages are the shares of a
deal's original loan balance in loans that have carried the
performing (code A) or non-performing (code B) matured balloon status
in at least one monthly report since issuance. <strong>Past scheduled
maturity</strong> is the share in loans whose scheduled maturity date
has passed, whether or not a matured status code has been reported
for the loan.</p>
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
<p><strong>Credit support at issuance</strong> on deal pages is computed from the
class stack order in the prospectus: for each principal class, the
share of the deal's principal balance in classes junior to it.
Prospectus-stated support figures are not carried in the dataset, so
no stated figure is shown. <strong>Credit support (current)</strong>,
where shown, applies the same junior-share definition to the current
class balances reported in the deal's Form 10-D distribution
statements.</p>
<p><strong>Property types</strong> follow the codes in the asset-level
filings. Code 98 is the residual category filers use for property
types outside the standard list. One code, SE, is shown as filed: its
expansion could not be verified against the Exhibit 102 code list, so
it is not guessed.</p>
<p>Where a figure is not available for a deal or a class, the pages say
so ("not yet reported"). No figure is estimated or carried forward
silently.</p>
<p>These pages are rebuilt from the dataset each time the dataset is
republished. They do not yet update on a daily cycle.</p>"""

    market_body = (
        intro + universe_note + strip + strip_note
        + "<h2>Delinquency</h2>" + dq_chart
        + "<h2>Matured and defaulted loans</h2>" + mat_chart
        + "<h2>Debt service coverage and coupon</h2>" + dscr_chart
        + wac_chart
        + "<h2>Snapshots</h2>" + snap_table
        + "<h2>Scheduled maturities of loans still reporting</h2>"
        + mat_table + mat_note
        + market_extra
        + '<p><a href="/cmbs/deals/">Deal index</a> / '
          '<a href="/cmbs/rankings/">Rankings</a> / '
          '<a href="/cmbs/changes/">Monthly changes</a></p>'
        + methods + methods2)
    with open(os.path.join(args.out, "_index.md"), "w") as fh:
        fh.write(frontmatter(
            "CMBS market",
            "Loan-level delinquency, maturity and coverage trends for "
            "registered commercial mortgage securitizations, computed "
            "from the trusts' own monthly reports.",
            data_as_of, today) + market_body + "\n")

    # ======================================================== deal index
    shelves = sorted({d["shelf"] for d in published})
    vintages = sorted({d["vintage"] for d in published if d["vintage"]})

    # largest property type by current balance, per deal
    deal_top_type = {}
    for pk, loans in group_loans.items():
        by_type = {}
        for l in loans:
            k = (pk, str(l["asset"]))
            lat = loan_latest.get(k)
            if not lat or lat[2] is None:
                continue
            vd = ver_latest.get(k, {})
            label = parse_types(vd.get("ptype")) or l.get("ptype")
            if label and label != "Multiple property types":
                label = PT_LABEL.get(label, label)
            if not label:
                continue
            by_type[label] = by_type.get(label, 0.0) + lat[2]
        if by_type:
            deal_top_type[pk] = max(by_type.items(),
                                    key=lambda x: (x[1], x[0]))[0]

    idx_rows = []
    for d in sorted(published, key=lambda x: (x["trust_name"].upper(),
                                              x["cik"],
                                              x["deal_segment"])):
        key = (d["cik"], d["deal_segment"])
        if d["identity_mismatch"]:
            cur = dq_v = sev_v = stress_v = net_v = NYR
            ss_v = dis_v = dscr_v = mat_v = top_t = NYR
            nln = NYR
            dq_num = ""
            dscr_num = ""
        else:
            cur = money(d["cur_bal"]) if d["cur_bal"] else NYR
            dq_v = pct_frac(d["dq30_now"])
            sev_v = pct_frac(d["ever_severe_bal_share"])
            stress_v = num(d["stress_score"], 1)
            net_v = (("%+.2f" % d["net_migration"])
                     if d["net_migration"] is not None else NYR)
            nln = num(d["n_loans"], 0)
            sv = deal_serv.get(key, {})
            ss_v = pct_frac(sv.get("ss_share"))
            dis_v = pct_frac(sv.get("distress_share"))
            mat_v = pct_frac(sv.get("mat24_share"), 1)
            dd = deal_dscr.get(key, {})
            dscr_v = num(dd.get("latest"), 2)
            top_t = deal_top_type.get(key) or NYR
            dq_num = (f"{d['dq30_now'] * 100:.2f}"
                      if d["dq30_now"] is not None else "")
            dscr_num = (f"{dd['latest']:.4f}"
                        if dd.get("latest") is not None else "")
        idx_rows.append(
            f'<tr data-vintage="{d["vintage"] or ""}" '
            f'data-shelf="{esc(d["shelf"])}" '
            f'data-dq="{dq_num}" data-dscr="{dscr_num}">'
            f'<td><a href="/cmbs/deal/{d["slug"]}/">'
            f'{esc(d["display_name"])}</a></td>'
            f"<td>{esc(d['shelf'])}</td>"
            f'<td class="num">{d["vintage"] or NYR}</td>'
            f'<td class="num">{cur}</td>'
            f'<td class="num">{nln}</td>'
            f'<td class="num">{dq_v}</td>'
            f'<td class="num">{ss_v}</td>'
            f'<td class="num">{dis_v}</td>'
            f'<td class="num">{dscr_v}</td>'
            f'<td class="num">{mat_v}</td>'
            f'<td class="num">{sev_v}</td>'
            f'<td class="num">{stress_v}</td>'
            f'<td class="num">{net_v}</td>'
            f"<td>{esc(top_t)}</td></tr>")
    shelf_opts = "".join(f'<option value="{esc(s)}">{esc(s)}</option>'
                         for s in shelves)
    vint_opts = "".join(f'<option value="{v}">{v}</option>'
                        for v in vintages)
    idx_script = """<script>
(function(){
  var tbl = document.getElementById('cmbs-index');
  var vs = document.getElementById('f-vintage');
  var ss = document.getElementById('f-shelf');
  var dq = document.getElementById('f-dq');
  var ds = document.getElementById('f-dscr');
  var tx = document.getElementById('f-text');
  function band(v, spec){
    if (!spec) return true;
    if (v === '' || v === null || isNaN(v)) return false;
    if (spec === '0') return v === 0;
    if (spec === 'lt1') return v < 1.0;
    if (spec === 'gt1.5') return v > 1.5;
    var p = spec.split('-');
    if (p.length === 2) return v > parseFloat(p[0]) && v <= parseFloat(p[1]);
    if (spec === '10+') return v > 10;
    return true;
  }
  function visibleRows(){
    return Array.prototype.slice.call(
      tbl.querySelectorAll(':scope > tbody > tr')).filter(function(r){
        return r.style.display !== 'none';
      });
  }
  function apply(){
    var v = vs.value, s = ss.value, q = tx.value.toLowerCase();
    tbl.querySelectorAll(':scope > tbody > tr').forEach(function(r){
      var ok = (!v || r.getAttribute('data-vintage') === v)
        && (!s || r.getAttribute('data-shelf') === s)
        && band(parseFloat(r.getAttribute('data-dq')), dq.value)
        && band(parseFloat(r.getAttribute('data-dscr')), ds.value)
        && (!q || r.children[0].textContent.toLowerCase()
              .indexOf(q) >= 0);
      r.style.display = ok ? '' : 'none';
    });
  }
  [vs, ss, dq, ds].forEach(function(el){
    el.addEventListener('change', apply);
  });
  tx.addEventListener('input', apply);
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
  document.getElementById('csv-export').addEventListener('click',
    function(){
      var head = Array.prototype.map.call(
        tbl.querySelectorAll(':scope > thead > tr > th'),
        function(th){ return th.textContent.trim(); });
      function cell(v){
        return '"' + String(v).replace(/"/g, '""') + '"';
      }
      var lines = [head.map(cell).join(',')];
      visibleRows().forEach(function(r){
        var cells = Array.prototype.map.call(r.children,
          function(td){ return td.textContent.trim(); });
        lines.push(cells.map(cell).join(','));
      });
      var blob = new Blob([lines.join('\\n')], {type: 'text/csv'});
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'cmbs-deal-index.csv';
      a.click();
      URL.revokeObjectURL(a.href);
    });
})();
</script>"""
    idx_body = (
        f"<p>All {len(published)} deal pages in the dataset, covering "
        f"{len(deals)} filing units. Where one trust filed under more "
        f"than one CIK, its filing units are combined on a single "
        f"page; the filing sources note on the page lists them. "
        f"Click a column heading to sort. Filter by closing year, "
        f"shelf, delinquency band, coverage band, or deal name; the "
        f"export button downloads the filtered table as a CSV file. "
        f"Specially serviced and distress shares, median DSCR and "
        f"the maturing share are as of each deal's latest reported "
        f"month. Definitions are in the methods note on the "
        f'<a href="/cmbs/">market page</a>.</p>'
        '<p><label>Closing year <select id="f-vintage">'
        '<option value="">All years</option>'
        + vint_opts + "</select></label> "
        '<label>Shelf <select id="f-shelf">'
        '<option value="">All shelves</option>'
        + shelf_opts + "</select></label> "
        '<label>30+ delinquent <select id="f-dq">'
        '<option value="">Any</option>'
        '<option value="0">0%</option>'
        '<option value="0-2">0 to 2%</option>'
        '<option value="2-5">2 to 5%</option>'
        '<option value="5-10">5 to 10%</option>'
        '<option value="10+">Over 10%</option></select></label> '
        '<label>Median DSCR <select id="f-dscr">'
        '<option value="">Any</option>'
        '<option value="lt1">Below 1.00</option>'
        '<option value="1-1.25">1.00 to 1.25</option>'
        '<option value="1.25-1.5">1.25 to 1.50</option>'
        '<option value="gt1.5">Over 1.50</option></select></label> '
        '<label>Deal name <input type="text" id="f-text" '
        'size="18"></label> '
        '<button type="button" id="csv-export">Export CSV</button>'
        "</p>"
        '<div class="market-table-scroll"><table class="market-table" '
        'id="cmbs-index"><thead><tr><th>Deal</th><th>Shelf</th>'
        '<th data-num="1">Vintage</th><th data-num="1">Current '
        'balance</th><th data-num="1">Loans</th>'
        '<th data-num="1">30+ delinquent</th>'
        '<th data-num="1">Specially serviced</th>'
        '<th data-num="1">Distress</th>'
        '<th data-num="1">Median DSCR</th>'
        '<th data-num="1">Maturing in 24 months</th>'
        '<th data-num="1">Ever severe</th>'
        '<th data-num="1">Realized stress score</th>'
        '<th data-num="1">Net rating change</th>'
        "<th>Largest property type</th></tr></thead><tbody>"
        + "".join(idx_rows) + "</tbody></table></div>"
        + idx_script)
    with open(os.path.join(args.out, "deals.md"), "w") as fh:
        fh.write(frontmatter(
            "CMBS deal index",
            "Every CMBS deal page in the dataset, with current "
            "delinquency, servicing, coverage and maturity figures.",
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
                f'{esc(d["display_name"])}</a>')

    rankable = [d for d in published if not d["identity_mismatch"]]
    by_stress = sorted([d for d in rankable
                        if d["stress_score"] is not None],
                       key=lambda x: (-x["stress_score"],
                                      x["trust_name"], x["cik"]))[:25]
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
    by_size = sorted([d for d in rankable if d["cur_bal"]],
                     key=lambda x: (-x["cur_bal"], x["trust_name"],
                                    x["cik"]))[:25]
    rows = [f'<tr><td class="num">{i}</td><td>{deal_link(d)}</td>'
            f'<td class="num">{money(d["cur_bal"])}</td>'
            f'<td class="num">{num(d["n_loans"], 0)}</td>'
            f'<td class="num">{d["vintage"] or NYR}</td></tr>'
            for i, d in enumerate(by_size, 1)]
    rk += rank_table("Largest current balance", rows,
                     ["Rank", "Deal", "Current balance", "Loans",
                      "Vintage"])
    by_mod = sorted([d for d in rankable
                     if d["ever_mod_bal_share"] is not None],
                    key=lambda x: (-x["ever_mod_bal_share"],
                                   x["trust_name"], x["cik"]))[:25]
    rows = [f'<tr><td class="num">{i}</td><td>{deal_link(d)}</td>'
            f'<td class="num">{pct_frac(d["ever_mod_bal_share"], 1)}</td>'
            f'<td class="num">{pct_frac(d["ever_severe_bal_share"])}</td>'
            f'<td class="num">{money(d["cur_bal"])}</td></tr>'
            for i, d in enumerate(by_mod, 1)]
    rk += rank_table("Largest share of balance ever modified", rows,
                     ["Rank", "Deal", "Ever modified", "Ever severe",
                      "Current balance"])
    lagged = [(deal_by_key[k], v) for k, v in lag_map.items()
              if v["lag"] is not None and k in published_keys
              and not deal_by_key[k]["identity_mismatch"]]
    lagged.sort(key=lambda x: (-x[1]["lag"], x[0]["trust_name"],
                               x[0]["cik"]))
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
    # deal documentation fields not loaded with the main deal query
    deal_docs = {}
    for cik, seg, tcik, acc in con.execute("""
    SELECT cik, deal_segment, trust_cik, prospectus_accession
    FROM deals""").fetchall():
        deal_docs[(cik, seg)] = {"trust_cik": tcik, "accession": acc}

    # first filing (version) showing a defeased status code, per loan
    def_first = {}
    for cik, seg, asset, code, vf in con.execute("""
    SELECT cik, deal_segment, assetNumber,
      "property__DefeasedStatusCode", MIN(valid_from)
    FROM loans_versioned WHERE asset_class = 'cmbs'
      AND "property__DefeasedStatusCode" IS NOT NULL
    GROUP BY 1, 2, 3, 4""").fetchall():
        if not code_is_f(code):
            continue
        pk = page_key((cik, seg))
        k = (pk, parent_asset((cik, seg), asset))
        if isinstance(vf, datetime.datetime):
            vf = vf.date()
        elif isinstance(vf, str):
            vf = dparse(vf)
        if k not in def_first or (vf and def_first.get(k)
                                  and vf < def_first[k]):
            def_first[k] = vf

    def asset_key(d, asset):
        pk = (d["cik"], d["deal_segment"])
        return loan_slug.get(
            (pk, str(asset)),
            re.sub(r"[^A-Za-z0-9]+", "-", str(asset)).strip("-"))

    def loan_anchor(d, asset):
        return f"loan-{asset_key(d, asset)}"

    def loan_url(d, k, asset):
        if k in loan_page_keys:
            return f"/cmbs/loan/{d['slug']}--{asset_key(d, asset)}/"
        return f"/cmbs/deal-loans/{d['slug']}/#{loan_anchor(d, asset)}"

    def loan_name(l, vd=None):
        def pick(vals):
            vals = [v for v in vals
                    if v.strip().lower() != "defeased"]
            return vals
        vals = pick(clean_list((vd or {}).get("pname")))
        if vals:
            nm = vals[0]
            if len(vals) > 1:
                nm += f" (and {len(vals) - 1} more properties)"
            return nm
        pnames = pick(l.get("pnames") or [])
        if pnames:
            nm = pnames[0]
            if len(pnames) > 1:
                nm += (f" (and {len(pnames) - 1} more "
                       f"properties)")
            return nm
        return f"Loan {l['asset']}"

    def loan_loc(l, vd=None):
        cities = clean_list((vd or {}).get("pcity")) or \
            l.get("pcities") or []
        states = clean_list((vd or {}).get("pstate")) or \
            l.get("pstates") or []
        if cities and states:
            loc = f"{cities[0]}, {states[0]}"
            extra = max(len(cities), len(states))
            if extra > 1:
                loc += f" (and {extra - 1} more)"
            return loc
        if cities:
            return cities[0]
        if states:
            return states[0]
        return ""

    def loan_type_label(l, vd=None):
        label = parse_types((vd or {}).get("ptype")) or l.get("ptype")
        if not label:
            return NYR
        if label == "Multiple property types":
            return label
        return PT_LABEL.get(label, label)

    TABLE_SCRIPT = """<script>
(function(){
  document.querySelectorAll('table.js-sortable').forEach(function(tbl){
    tbl.querySelectorAll(':scope > thead > tr > th').forEach(
      function(th, i){
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
  });
  document.querySelectorAll('button.js-csv').forEach(function(btn){
    btn.addEventListener('click', function(){
      var tbl = document.getElementById(btn.getAttribute('data-t'));
      function cell(v){ return '"' + String(v).replace(/"/g, '""') + '"'; }
      var head = Array.prototype.map.call(
        tbl.querySelectorAll(':scope > thead > tr > th'),
        function(th){ return th.textContent.trim(); });
      var lines = [head.map(cell).join(',')];
      tbl.querySelectorAll(':scope > tbody > tr').forEach(function(r){
        var cells = Array.prototype.map.call(r.children,
          function(td){ return td.textContent.trim(); });
        lines.push(cells.map(cell).join(','));
      });
      var blob = new Blob([lines.join('\\n')], {type: 'text/csv'});
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = btn.getAttribute('data-name') || 'table.csv';
      a.click();
      URL.revokeObjectURL(a.href);
    });
  });
})();
</script>"""

    AGENCY_LABEL = {"fitch": "Fitch", "kbra": "KBRA", "sp": "S&P",
                    "moodys": "Moody's", "dbrs": "DBRS"}

    def fmt_date(v):
        if v is None:
            return NYR
        if hasattr(v, "isoformat"):
            return v.isoformat()
        s = str(v).strip()
        return s if s else NYR

    def fnum(v):
        try:
            return float(str(v).replace(",", ""))
        except (TypeError, ValueError):
            return None

    def loan_events(k, l):
        """Surveillance events for one loan: (date, label, text)."""
        evs = []
        vd = ver_latest.get(k, {})
        name = loan_name(l, vd)
        if k in loan_first_dq:
            evs.append((loan_first_dq[k],
                        month_label(loan_first_dq[k]),
                        f"{esc(name)}: first reported 30 or more "
                        f"days delinquent"))
        for t, r_ in ss_pairs.get(k, []):
            if t:
                evs.append((t, t.isoformat(),
                            f"{esc(name)}: transferred to the "
                            f"special servicer"))
            if r_:
                evs.append((r_, r_.isoformat(),
                            f"{esc(name)}: returned to the master "
                            f"servicer"))
        for md, prate, pmat, ppay in mod_events.get(k, []):
            if md is None:
                continue
            txt = f"{esc(name)}: loan modified"
            det = []
            if prate is not None:
                det.append(f"rate after modification "
                           f"{rate_disp(prate / 100 if prate > 1 else prate)}")
            if pmat:
                det.append(f"maturity after modification "
                           f"{pmat.isoformat()}")
            if ppay is not None:
                det.append(f"payment after modification "
                           f"{money(ppay)}")
            if det:
                txt += " (" + "; ".join(det) + ")"
            evs.append((md, md.isoformat(), txt))
        if k in def_first and def_first[k]:
            evs.append((def_first[k], def_first[k].isoformat(),
                        f"{esc(name)}: defeasance recorded (first "
                        f"filing showing defeased status)"))
        liq_d = dparse(vd.get("liq_d"))
        if liq_d:
            txt = f"{esc(name)}: liquidated"
            loss = vd.get("loss")
            lat = loan_latest.get(k)
            if loss is not None:
                txt += f"; realized loss {money(loss)}"
                if lat and lat[2]:
                    txt += (f" ({pct_frac(loss / lat[2], 1)} of the "
                            f"last reported balance)")
            evs.append((liq_d, liq_d.isoformat(), txt))
        evs.sort(key=lambda x: x[0] or datetime.date.min)
        return evs

    def build_loan_table(d, pk):
        loans = group_loans.get(pk, [])
        tot = deal_serv.get(pk, {}).get("tot") or 0.0
        deal_pm = deal_serv.get(pk, {}).get("pm")
        rows = []
        for l in loans:
            k = (pk, str(l["asset"]))
            vd = ver_latest.get(k, {})
            lat = loan_latest.get(k)
            bal = lat[2] if lat else None
            if bal is None and lat and lat[3] is not None \
                    and lat[3] == 0:
                bal = 0.0
            current = bool(lat and deal_pm and lat[0] == deal_pm)
            share = (bal / tot) if (bal is not None and tot
                                    and current) else None
            bal_txt = money(bal) if bal is not None else NYR
            if bal is not None and not current and lat:
                bal_txt += f" (last reported {month_label(lat[0])})"
            notes = []
            if loan_ss_now(k):
                notes.append("Specially serviced")
            if l.get("defeased"):
                notes.append("Defeased")
            if k in mod_events:
                notes.append("Modified")
            if k in ss_pairs and not loan_ss_now(k):
                notes.append("Specially serviced in the past")
            if bal is not None and bal == 0:
                notes.append("Zero balance in latest report")
            m = loan_maturity(k)
            rows.append(
                f'<tr><td><a href="{loan_url(d, k, l["asset"])}">'
                f'{esc(loan_name(l, vd))}</a></td>'
                f"<td>{esc(loan_loc(l, vd)) or NYR}</td>"
                f"<td>{esc(loan_type_label(l, vd))}</td>"
                f'<td class="num">{bal_txt}</td>'
                f'<td class="num">{pct_frac(share, 1)}</td>'
                f"<td>{esc(status_word(lat[1]) if lat else NYR)}</td>"
                f'<td class="num">{dscr_disp(lat[5]) if lat else NYR}</td>'
                f'<td class="num">{occ_disp(lat[7]) if lat else NYR}</td>'
                f'<td class="num">{rate_disp(lat[4]) if lat else NYR}</td>'
                f'<td class="num">{m.isoformat() if m else NYR}</td>'
                f"<td>{esc('; '.join(notes))}</td></tr>")
        table = (
            '<p><button type="button" class="js-csv" '
            f'data-t="loan-table-{d["slug"]}" '
            f'data-name="{d["slug"]}-loans.csv">Export loan table '
            "as CSV</button></p>"
            '<div class="market-table-scroll"><table '
            'class="market-table js-sortable" '
            f'id="loan-table-{d["slug"]}"><thead><tr><th>Loan</th>'
            "<th>Location</th><th>Property type</th>"
            '<th data-num="1">Current balance</th>'
            '<th data-num="1">Share of pool</th><th>Status</th>'
            '<th data-num="1">DSCR</th>'
            '<th data-num="1">Occupancy</th>'
            '<th data-num="1">Rate</th>'
            '<th data-num="1">Maturity</th><th>Notes</th></tr>'
            "</thead><tbody>" + "".join(rows) + "</tbody></table>"
            "</div>")
        return table

    def build_timeline(d, pk):
        evs = []
        for l in group_loans.get(pk, []):
            k = (pk, str(l["asset"]))
            for dt, lab, txt in loan_events(k, l):
                evs.append((dt, lab, txt, loan_url(d, k, l["asset"])))
        rev = []
        for e in events_by_deal.get(pk, []):
            if e["action_class"] in ("DG", "WD") and e["action_date"]:
                word = ("downgraded" if e["action_class"] == "DG"
                        else "rating withdrawn")
                rev.append((e["action_date"],
                            e["action_date"].isoformat(),
                            f"{esc(AGENCY_LABEL.get(e['agency'], e['agency']))} "
                            f"class {esc(e['class'])} {word} "
                            f"to {esc(e['rating'] or NYR)}",
                            f"/cmbs/deal-ratings/{d['slug']}/"))
        rev.sort(key=lambda x: x[0] or datetime.date.min,
                 reverse=True)
        rev = rev[:25]
        all_evs = evs + rev
        all_evs.sort(key=lambda x: x[0] or datetime.date.min,
                     reverse=True)
        if not all_evs:
            return f"<p>{NYR}: no surveillance events are recorded " \
                   f"for this deal in the dataset.</p>"
        rows = "".join(
            f'<tr><td class="num">{esc(lab)}</td>'
            f'<td><a href="{url}">{txt}</a></td></tr>'
            for _dt, lab, txt, url in all_evs)
        return ('<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Date</th>'
                "<th>Event</th></tr></thead><tbody>" + rows
                + "</tbody></table></div>"
                '<p class="data-vintage">Loan events are dated from '
                "the asset-level filings: transfer, return, "
                "modification and liquidation dates as filed, and "
                "the first month a loan is reported 30 or more days "
                "delinquent. Rating downgrades and withdrawals are "
                "dated by the agency action date; the full rating "
                "history is on the rating history page.</p>")

    def build_parties(d, pk):
        serv = {}
        lserv = {}
        trust = {}
        for l in group_loans.get(pk, []):
            k = (pk, str(l["asset"]))
            vd = ver_latest.get(k, {})
            for nm, dd in ((vd.get("servicer"), serv),
                           (vd.get("loan_servicer"), lserv),
                           (vd.get("trustee"), trust)):
                for v in clean_list(nm):
                    dd[v] = dd.get(v, 0) + 1

        def fmt(dd):
            if not dd:
                return NYR
            return "; ".join(
                f"{esc(nm)} ({n} loan{'s' if n != 1 else ''})"
                for nm, n in sorted(dd.items(),
                                    key=lambda x: (-x[1], x[0])))
        rows = [("Master servicer (primary servicer in the filings)",
                 fmt(serv)),
                ("Loan servicer", fmt(lserv)),
                ("Trustee", fmt(trust))]
        docs = deal_docs.get(pk, {})
        acc = docs.get("accession")
        links = []
        if acc:
            nodash = acc.replace("-", "")
            links.append(
                f'<a href="https://www.sec.gov/Archives/edgar/data/'
                f'{d["cik"]}/{nodash}/{esc(acc)}-index.htm">'
                f"Prospectus filing (SEC EDGAR)</a>")
        if docs.get("trust_cik"):
            links.append(
                f'<a href="https://www.sec.gov/edgar/browse/?CIK='
                f'{docs["trust_cik"]}&owner=exclude">Trust filing '
                f"index (SEC EDGAR)</a>")
        if links:
            rows.append(("Documents", " / ".join(links)))
        return ('<table class="terms-table"><tbody>' + "".join(
            f'<tr><td class="muted">{esc(k)}</td><td>{v}</td></tr>'
            for k, v in rows) + "</tbody></table>"
            '<p class="data-vintage">Servicer and trustee names are '
            "as at filing: the name on the latest asset-level record "
            "for each loan. The asset-level filings record special "
            "servicer transfer dates but not the special servicer's "
            "name.</p>")

    n_pages = 0
    for d in published:
        key = (d["cik"], d["deal_segment"])
        trs = tranches_by_deal.get(key, [])
        parts = []
        annex_exists = any(
            (key, str(l["asset"])) not in loan_page_keys
            for l in group_loans.get(key, []))
        has_ratings_page = bool(events_by_deal.get(key)) or any(
            (key[0], key[1], t["class"]) in classes_rated for t in trs)
        nav = (f'<p class="bond-navrow"><a href="/cmbs/deals/">'
               f"&larr; Deal index</a> / "
               f'<a href="/cmbs/">CMBS market</a>')
        if has_ratings_page:
            nav += (f' / <a href="/cmbs/deal-ratings/'
                    f'{d["slug"]}/">Rating history</a>')
        if annex_exists:
            nav += (f' / <a href="/cmbs/deal-loans/'
                    f'{d["slug"]}/">Loan annex</a>')
        nav += "</p>"
        parts.append(nav)
        if key in namesakes:
            others = "; ".join(
                f'<a href="/cmbs/deal/{deal_by_key[k]["slug"]}/">'
                f'{esc(deal_by_key[k]["display_name"])}</a>'
                for k in namesakes[key] if k in published_keys)
            parts.append(
                f'<p class="data-vintage">Another deal page carries '
                f"this trust name: {others}. The pages cover separate "
                f"deals; this page covers filing unit CIK {d['cik']}, "
                f"segment {esc(d['deal_segment'])}.</p>")
        if d["identity_mismatch"]:
            yrs = sorted({re.search(r"(19|20)\d{2}",
                                    str(l["orig"] or "")).group(0)
                          for l in loans_by_deal.get(key, [])
                          if re.search(r"(19|20)\d{2}",
                                       str(l["orig"] or ""))})
            yr_txt = (f"{yrs[0]} and {yrs[-1]}" if len(yrs) > 1
                      else (yrs[0] if yrs else NYR))
            no_tranche_txt = ("" if trs else
                              ", and no tranche table: the trust "
                              "predates electronic asset-level reporting")
            parts.append(
                "<h2>Loan data not shown for this trust</h2>"
                f"<p>The asset-level filings held under this trust's "
                f"CIK ({d['cik']}, segment {esc(d['deal_segment'])}) "
                f"carry loans originated in {yr_txt}. Loans of that "
                f"vintage cannot belong to a trust of "
                f"{d['vintage']}, so those records are not this "
                f"trust's pool and no pool figures are shown. The "
                f"dataset holds no reliable loan tape for this trust "
                f"itself{no_tranche_txt}.</p>")
            parts.append('<table class="terms-table"><tbody>' + "".join(
                f'<tr><td class="muted">{esc(k)}</td><td>{esc(v)}</td>'
                f"</tr>" for k, v in [
                    ("Trust", d["trust_name"]),
                    ("Filing CIK", str(d["cik"])),
                    ("Segment", str(d["deal_segment"])),
                    ("Closing date",
                     d["closing_date"].isoformat()
                     if d["closing_date"] else NYR),
                    ("Original pool balance (prospectus)",
                     money(d["pool_balance_stated"])),
                    ("Tranches in the dataset", str(len(trs))),
                ]) + "</tbody></table>")
            parts.append("<h2>Ratings</h2>")
            n_rated_here = sum(1 for (c, s, _cl) in classes_rated
                               if (c, s) == key)
            if n_rated_here:
                parts.append(
                    f"<p>{n_rated_here} classes carry a current rating "
                    f"in the dataset.</p>")
            else:
                parts.append(
                    "<p>No ratings in the data for this deal.</p>")
            path = os.path.join(args.out, "deal", d["slug"] + ".md")
            with open(path, "w") as fh:
                fh.write(frontmatter(
                    d["display_name"],
                    f"Deal facts for {d['trust_name']}.",
                    "no loan data attached to this trust in the dataset",
                    today) + "\n".join(parts) + "\n")
            n_pages += 1
            continue

        # ---- header strip: current observables only
        netmig_txt = NYR
        if d["net_migration"] is not None:
            netmig_txt = f'{d["net_migration"]:+.2f} notches'
            if d["net_migration_month"] is not None:
                netmig_txt += (f' (as of '
                               f'{month_label(d["net_migration_month"])})')
        loans_here = group_loans.get(key, [])
        pm_latest = None
        n_reporting = 0
        for l in loans_here:
            lat = loan_latest.get((key, str(l["asset"])))
            if lat and lat[2] is not None:
                if pm_latest is None or lat[0] > pm_latest:
                    pm_latest = lat[0]
                    n_reporting = 1
                elif lat[0] == pm_latest:
                    n_reporting += 1
        sv = deal_serv.get(key, {})
        dd = deal_dscr.get(key, {})
        sum_items = [
            ("Current pool balance",
             (money(d["cur_bal"]) + f' ({month_label(d["cur_bal_month"])})')
             if d["cur_bal"] else NYR),
            ("Loans reporting",
             (f"{n_reporting} ({month_label(pm_latest)})")
             if pm_latest else NYR),
            ("30+ delinquent (latest)", pct_frac(d["dq30_now"])),
            ("Specially serviced (latest)",
             pct_frac(sv.get("ss_share"))),
            ("Distress (latest)", pct_frac(sv.get("distress_share"))),
            ("Median DSCR (latest)", num(dd.get("latest"), 2)),
            ("Net rating change since issuance", netmig_txt),
        ]
        parts.append('<dl class="bw-summary">' + "".join(
            f'<div class="bw-sum-item"><dt>{esc(k)}</dt><dd>{esc(v)}</dd>'
            f"</div>" for k, v in sum_items) + "</dl>")

        # ---- parties and documents
        parts.append("<h2>Parties and documents</h2>")
        parts.append(build_parties(d, key))

        # ---- collateral today
        parts.append("<h2>Collateral today</h2>")
        bal_series = ind_bal.get(key, [])
        bal_pts = [(m, b) for m, b in bal_series if b]
        if len(bal_pts) >= 3:
            parts.append(svg_line_chart(
                [("Reported balance", "#1a1a1a", bal_pts)],
                f"Reported pool balance for {d['trust_name']}",
                y_fmt="${:,.0f}"))
        tot_now = sv.get("tot") or 0.0
        mix_now = {}
        for l in loans_here:
            k2 = (key, str(l["asset"]))
            lat = loan_latest.get(k2)
            if not lat or lat[2] is None:
                continue
            lab = loan_type_label(l, ver_latest.get(k2, {}))
            mix_now[lab] = mix_now.get(lab, 0.0) + lat[2]
        if mix_now and tot_now:
            mrows = "".join(
                f"<tr><td>{esc(lab)}</td>"
                f'<td class="num">{money(b)}</td>'
                f'<td class="num">{pct_frac(b / tot_now, 1)}</td></tr>'
                for lab, b in sorted(mix_now.items(),
                                     key=lambda x: (-x[1], x[0])))
            parts.append("<h3>Property mix, current balances</h3>")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Property type</th>'
                "<th>Current balance</th><th>Share</th></tr></thead>"
                "<tbody>" + mrows + "</tbody></table></div>")
        state_now = {}
        for l in loans_here:
            k2 = (key, str(l["asset"]))
            lat = loan_latest.get(k2)
            if not lat or lat[2] is None:
                continue
            sts = clean_list(ver_latest.get(k2, {}).get("pstate")) \
                or l.get("pstates") or []
            if sts:
                state_now[sts[0]] = state_now.get(sts[0], 0.0) + lat[2]
        if state_now and tot_now:
            srows = "".join(
                f"<tr><td>{esc(st)}</td>"
                f'<td class="num">{money(b)}</td>'
                f'<td class="num">{pct_frac(b / tot_now, 1)}</td></tr>'
                for st, b in sorted(state_now.items(),
                                    key=lambda x: (-x[1], x[0]))[:5])
            parts.append("<h3>Largest states, current balances</h3>")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>State</th>'
                "<th>Current balance</th><th>Share</th></tr></thead>"
                "<tbody>" + srows + "</tbody></table></div>")
        mat_buckets = {}
        mat_unknown = 0.0
        for l in loans_here:
            k2 = (key, str(l["asset"]))
            lat = loan_latest.get(k2)
            if not lat or lat[2] is None:
                continue
            m = loan_maturity(k2)
            if m is None:
                mat_unknown += lat[2]
            else:
                mat_buckets[m.year] = mat_buckets.get(m.year, 0.0) \
                    + lat[2]
        if (mat_buckets or mat_unknown) and tot_now:
            mrows = []
            past = sum(b for y, b in mat_buckets.items()
                       if y <= panel_end.year)
            if past:
                mrows.append((f"{panel_end.year} and earlier", past))
            for y in sorted(mat_buckets):
                if panel_end.year < y < panel_end.year + 6:
                    mrows.append((str(y), mat_buckets[y]))
            later = sum(b for y, b in mat_buckets.items()
                        if y >= panel_end.year + 6)
            if later:
                mrows.append((f"{panel_end.year + 6} and later", later))
            if mat_unknown:
                mrows.append(("Not reported", mat_unknown))
            parts.append("<h3>Scheduled maturities, current loans</h3>")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Scheduled '
                "maturity</th><th>Current balance</th><th>Share</th>"
                "</tr></thead><tbody>" + "".join(
                    f"<tr><td>{esc(lab)}</td>"
                    f'<td class="num">{money(b)}</td>'
                    f'<td class="num">{pct_frac(b / tot_now, 1)}</td>'
                    "</tr>" for lab, b in mrows)
                + "</tbody></table></div>")

        # ---- indicator chart
        parts.append("<h2>Delinquency and stress indicator</h2>")
        series = ind_series.get(key, [])
        pts_dq = [(m, (dq * 100 if dq is not None else None))
                  for m, dq, _di in series]
        pts_di = [(m, (di * 100 if di is not None else None))
                  for m, _dq, di in series]
        n_pts = sum(1 for _m, v in pts_dq if v is not None)
        if n_pts >= 3:
            parts.append(svg_line_chart([
                ("30+ days delinquent", "#1a1a1a", pts_dq),
                ("Distressed (90+, foreclosure, REO, non-performing "
                 "matured balloon)", "#8a1f1f", pts_di),
            ], f"Delinquency indicator for {d['trust_name']}",
                y_fmt="{:.1f}%"))
            parts.append(
                '<p class="data-vintage">Monthly shares of the '
                "deal's reported balance, from the deal indicator "
                "series in the dataset. Months in which fewer than "
                "half of the reported loans carry a delinquency "
                "status code are not plotted.</p>")
        elif n_pts >= 1:
            di_map = {m: v for m, v in pts_di}
            trows = "".join(
                f"<tr><td>{esc(month_label(m))}</td>"
                f'<td class="num">{pct_val(v)}</td>'
                f'<td class="num">{pct_val(di_map.get(m))}</td></tr>'
                for m, v in pts_dq if v is not None)
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Month</th>'
                "<th>30+ days delinquent</th><th>Distressed (90+, "
                "foreclosure, REO, non-performing matured balloon)</th></tr>"
                "</thead><tbody>" + trows + "</tbody></table></div>")
            parts.append(
                '<p class="data-vintage">The indicator has too few '
                "reported months to chart; the reported months are "
                "tabulated instead.</p>")
        else:
            parts.append(f"<p>{NYR}.</p>")

        # ---- full loan table
        parts.append("<h2>Loans</h2>")
        if loans_here:
            parts.append(build_loan_table(d, key))
            parts.append(
                '<p class="data-vintage">Every loan in the deal is '
                "listed, with component records of a loan counted "
                "once. Balances, status, coverage and occupancy are "
                "each loan's latest reported values; DSCR is on the "
                "net cash flow basis. Loans that have left the pool "
                "show their last reported balance with its month "
                "and carry no share of the current pool. Loans with "
                "their own page are linked to it; every other loan "
                "is linked to its detail section in the loan "
                "annex.</p>")
        else:
            parts.append(f"<p>{NYR}.</p>")

        # ---- surveillance timeline
        parts.append("<h2>Surveillance timeline</h2>")
        parts.append(build_timeline(d, key))

        # ---- tranche stack
        parts.append("<h2>Tranches</h2>")
        if trs:
            cs_deal_here = cs_by_deal.get(key)
            _has_float = any(t["cindex"] for t in trs)
            trows = []
            for t in trs:
                if t["combination"]:
                    sup = "Combination class"
                elif t["io"]:
                    sup = "Interest only"
                elif t["support"] is not None:
                    sup = pct_frac(t["support"])
                elif t["is_exch"]:
                    sup = "Exchangeable component"
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
                if t["bal"]:
                    bal = money(t["bal"])
                    if t["io"]:
                        bal += " notional"
                elif t["bal"] == 0:
                    bal = "$0"
                elif t["is_exch"]:
                    bal = "Exchangeable component"
                elif t["combination"]:
                    bal = "Combination class"
                else:
                    bal = NYR
                cs = (cs_by_class.get((key[0], key[1], t["cusip"]))
                      if t["cusip"] else None)
                cells = [f"<td>{esc(t['class'])}</td>",
                         f'<td class="num">{bal}</td>']
                if cs_deal_here is not None:
                    if cs is not None and cs["bal"] is not None:
                        _cb = money(cs["bal"])
                        if t["io"] or cs["btype"] == "notional":
                            _cb += " notional"
                        _cf = (f"{cs['factor']:.4f}"
                               if cs["factor"] is not None else "—")
                    elif cs is not None:
                        _cb, _cf = "—", "—"
                    else:
                        _cb = _cf = "—"
                    cells += [f'<td class="num">{_cb}</td>',
                              f'<td class="num">{_cf}</td>']
                cells.append(f'<td class="num">{esc(sup)}</td>')
                if cs_deal_here is not None:
                    _cs2 = (pct_frac(cs["support"])
                            if cs is not None
                            and cs["support"] is not None else "—")
                    cells.append(f'<td class="num">{_cs2}</td>')
                cells += [f'<td class="num">{esc(cpn)}</td>',
                          f"<td>{cus}</td>",
                          f'<td class="num">{fmt_date(t["expmat"])}</td>',
                          f'<td class="num">{fmt_date(t["lfinal"])}</td>']
                for ag, _label in AGENCIES:
                    r = ratings.get((key[0], key[1], t["class"], ag))
                    ow = ratings_ow.get((key[0], key[1], t["class"], ag),
                                        (None, None))
                    cell = esc(r) if r else NYR
                    extra = "; ".join(x for x in
                                      [ow[0], ow[1]] if x)
                    if r and extra:
                        cell += f"<br>{esc(extra)}"
                    cells.append(f"<td>{cell}</td>")
                trows.append("<tr>" + "".join(cells) + "</tr>")
            ag_head = "".join(f"<th>{l}</th>" for _a, l in AGENCIES)
            _cur_head = ("<th>Current balance</th><th>Factor</th>"
                         if cs_deal_here is not None else "")
            _cur_head2 = ("<th>Credit support (current)</th>"
                          if cs_deal_here is not None else "")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Class</th>'
                "<th>Original balance</th>" + _cur_head +
                "<th>Credit support at issuance</th>" + _cur_head2 +
                "<th>Coupon</th>"
                f"<th>CUSIP</th><th>Expected maturity</th>"
                f"<th>Legal final</th>{ag_head}</tr></thead><tbody>"
                + "".join(trows) + "</tbody></table></div>")
            _fn = ('<p class="data-vintage">Credit support at '
                   "issuance is computed from original balances: the "
                   "share of the deal's principal balance in classes "
                   "junior to the class, from the class stack order "
                   "in the prospectus. ")
            if cs_deal_here is not None:
                _fn += (
                    f"Current balances, factors and current credit "
                    f"support are from the Form 10-D distribution "
                    f"statement for the "
                    f"{month_label(cs_deal_here['dist'])} "
                    f"distribution (statement date "
                    f"{fmt_date(cs_deal_here['dist'])}); the pool's "
                    f"certificated balance at that statement was "
                    f"{money(cs_deal_here['pool'])}. Factor is the "
                    f"share of a class's original balance still "
                    f"outstanding. Credit support (current) applies "
                    f"the same junior-share definition to the "
                    f"current balances. ")
            else:
                _fn += ("No current credit support figure is shown: "
                        "current class balances are not in the "
                        "dataset. ")
            if _has_float:
                _fn += ("Floating-rate coupons are stated as index "
                        "+ spread; the percentage shown is the "
                        "all-in rate at issuance")
                if d["closing_date"]:
                    _fn += (f" (deal closing, "
                            f"{month_label(d['closing_date'])})")
                _fn += ". "
            _fn += (
                "Interest-only "
                "classes carry a notional balance and no principal "
                "support figure. Exchangeable component classes carry "
                "no balance of their own; their balance sits in the "
                "combination class they exchange into. Ratings are "
                "the latest held in the dataset for each class and "
                "agency, with the current outlook and watch state "
                "under the rating; NR means the agency shows the "
                "class as not rated, WR that the rating was "
                "withdrawn, PIF that the class has been paid in "
                "full. A rating marked (prelim.) is a preliminary "
                "rating assigned before closing; the rating value is "
                "shown as the agency reports it, with the preliminary "
                "marker separated from the value. A + after a CUSIP "
                "marks a class with companion CUSIPs in the "
                "dataset.</p>")
            parts.append(_fn)
        else:
            parts.append(f"<p>{NYR}: no tranche table is in the dataset "
                         "for this deal.</p>")

        # ---- ratings summary
        parts.append("<h2>Ratings</h2>")
        if not trs:
            parts.append("<p>No ratings in the data for this deal.</p>")
        n_cusip_classes = sum(1 for t in trs if t["cusip"])
        n_rated = sum(1 for t in trs
                      if (key[0], key[1], t["class"]) in classes_rated)
        n_action_classes = len({e["class"] for e in
                                events_by_deal.get(key, [])})
        lag = lag_map.get(key)
        netmig_full = NYR
        if d["net_migration"] is not None:
            netmig_full = (f'{d["net_migration"]:+.2f} notches '
                           f'(balance-weighted)')
            if d["net_migration_month"] is not None:
                netmig_full += (f'; as of '
                                f'{month_label(d["net_migration_month"])}')
        rrows = [
            ("Classes with a CUSIP", f"{n_cusip_classes} of {len(trs)}"),
            ("Classes with a current rating in the dataset",
             f"{n_rated} of {len(trs)}"),
            ("Classes with recorded rating actions",
             f"{n_action_classes} of {len(trs)}"),
            ("Net rating change since issuance", netmig_full),
            ("Delinquency threshold crossed",
             month_label(lag["crossing"]) if lag else
             "Not crossed in the dataset"),
            ("First downgrade",
             month_label(lag["first_dg"]) if lag and lag["first_dg"]
             else "None recorded"),
        ]
        if trs:
            parts.append('<table class="terms-table"><tbody>'
                         + "".join(
                             f'<tr><td class="muted">{esc(k)}</td>'
                             f'<td>{esc(v)}</td></tr>'
                             for k, v in rrows) + "</tbody></table>")
        if has_ratings_page:
            _ra = ratings_asof.get(key)
            if _ra is not None:
                _ra_s = (_ra.isoformat() if hasattr(_ra, "isoformat")
                         else str(_ra))
                parts.append(
                    f'<p class="data-vintage">Ratings as held in the '
                    f'dataset at {_ra_s}; action dates and publicly '
                    f'knowable dates are on this deal\'s '
                    f'<a href="/cmbs/deal-ratings/{d["slug"]}/">rating '
                    f'history page</a>.</p>')
            else:
                parts.append(
                    f'<p>Full rating history, with the action date and '
                    f'the publicly knowable date of every action: '
                    f'<a href="/cmbs/deal-ratings/{d["slug"]}/">rating '
                    f"history for {esc(d['trust_name'])}</a>.</p>")
        press_here = press_by_deal.get(key, [])
        if press_here:
            parts.append(
                f"<p>{len(press_here)} rating actions from agency "
                f"releases collected in the dataset are listed on "
                f"the rating history page.</p>")

        # ---- realized outcomes
        parts.append("<h2>Realized outcomes</h2>")
        ea, eb = ever_ab.get(key, (None, None))
        dd2 = deal_dscr.get(key, {})
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
            ("Matured balloon, performing (ever; share of original "
             "balance)", pct_frac(ea)),
            ("Matured balloon, non-performing (ever; share of original "
             "balance)", pct_frac(eb)),
            ("Maximum servicer advances (share of balance)",
             pct_frac(d["max_adv_pct"])),
            ("Median DSCR, first year", num(dd2.get("first_year"), 2)),
            ("Median DSCR, latest", num(dd2.get("latest"), 2)),
            ("Realized stress score", num(d["stress_score"], 1)),
        ]
        parts.append('<table class="terms-table"><tbody>' + "".join(
            f'<tr><td class="muted">{esc(k)}</td><td>{esc(v)}</td></tr>'
            for k, v in out_rows) + "</tbody></table>")
        parts.append(
            '<p class="data-vintage">The realized stress score is a '
            "0 to 100 score built from realized pool outcomes since "
            "issuance: peak and latest delinquency, the share of "
            "balance ever 90 or more days delinquent, in foreclosure "
            "or REO, the share ever modified, servicer advances, "
            "loans past maturity, and the change in median debt "
            "service coverage since the first year. Higher is more "
            "realized stress. The definition is in the methods note "
            "on the market page.</p>")

        # ---- pool at issuance (historical)
        parts.append("<h2>Pool at issuance (historical)</h2>")
        stated = d["pool_balance_stated"]
        filed = filed_total.get(key)
        if stated:
            orig_label = "Original pool balance (prospectus)"
            orig_val = money(stated)
        else:
            orig_label = "Original pool balance (filed loans)"
            orig_val = money(filed or d["total_orig_bal"])
        pool_rows = [
            (orig_label, orig_val),
            ("Loans", num(d["n_loans"], 0)),
            ("Loan balance in filings", money(filed)),
            ("Closing date",
             d["closing_date"].isoformat() if d["closing_date"] else NYR),
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
        if (stated and filed and abs(filed - stated) > 0.005 * stated):
            parts.append(
                f'<p class="data-vintage">The prospectus states an '
                f"original pool balance of {money(stated)}. The loan "
                f"amounts in the asset-level filings sum to "
                f"{money(filed)}, with component records of a loan "
                f"counted once. The difference arises because pari "
                f"passu loans are filed at their whole-loan amount, "
                f"including shares of the loan held by other "
                f"trusts.</p>")
        parts.append("<h3>Property types at issuance</h3>")
        dl = loans_by_deal.get(key, [])
        tot_amt = filed_total.get(key) or None
        typed = {}
        typed_bal = 0.0
        for l in dl:
            if l["ptype"] and l["amt"]:
                typed[l["ptype"]] = typed.get(l["ptype"], 0.0) + l["amt"]
                typed_bal += l["amt"]
        if typed and tot_amt:
            mix_rows = []
            for code, bal in sorted(typed.items(),
                                    key=lambda x: (-x[1], x[0])):
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
                f'for {pct_frac(typed_bal / tot_amt, 1)} of the filed '
                f'loan balance; shares are of the filed loan total, '
                f'with component records counted once.</p>')
        else:
            parts.append(f"<p>{NYR}.</p>")
        parts.append("<h3>Largest loans at issuance</h3>")
        top = sorted([l for l in dl if l["amt"]],
                     key=lambda x: (-x["amt"], str(x["asset"])))[:5]
        if top and tot_amt:
            lrows = []
            for l in top:
                if l["pnames"]:
                    name = l["pnames"][0]
                    if len(l["pnames"]) > 1:
                        name += (f' (and {len(l["pnames"]) - 1} more '
                                 f'properties)')
                else:
                    name = f"Loan {l['asset']}"
                if l.get("defeased") and not (
                        l["pnames"] and l["pnames"][0].lower()
                        .startswith("defeased")):
                    name += " (defeased)"
                loc = ""
                if l["pcities"] and l["pstates"]:
                    loc = f"{l['pcities'][0]}, {l['pstates'][0]}"
                    extra = max(len(l["pcities"]), len(l["pstates"]))
                    if extra > 1:
                        loc += f" (and {extra - 1} more)"
                elif l["pcities"]:
                    loc = l["pcities"][0]
                elif l["pstates"]:
                    loc = l["pstates"][0]
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

        stubs = absorbed_by_main.get(key, [])
        if stubs:
            src_rows = []
            mm = unit_months.get(key, set())
            src_rows.append(
                f"<tr><td>CIK {d['cik']}, segment "
                f"{esc(d['deal_segment'])}</td>"
                f'<td class="num">{len(mm)}</td>'
                f'<td class="num">{num(d["n_loans"], 0)}</td></tr>')
            for sk in sorted(stubs):
                su = deal_by_key[sk]
                sm = unit_months.get(sk, set())
                src_rows.append(
                    f"<tr><td>CIK {sk[0]}, segment {esc(sk[1])}</td>"
                    f'<td class="num">{len(sm)}</td>'
                    f'<td class="num">{num(su["n_loans"], 0)}</td></tr>')
            parts.append("<h2>Filing sources</h2>")
            parts.append(
                "<p>This page combines the filing units below for "
                "this trust. The figures are the main unit's (the "
                "first row); the combined units are earlier or "
                "partial filings of the same trust whose dated loans "
                "carry the same origination dates as the main unit's "
                "loans, and no month is counted twice.</p>")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Filing unit</th>'
                "<th>Months of loan reports</th><th>Loans</th></tr>"
                "</thead><tbody>" + "".join(src_rows)
                + "</tbody></table></div>")

        _src_line = ('<p class="data-vintage">Sources: SEC Form '
                     'ABS-EE asset-level reports')
        if cs_by_deal.get(key) is not None:
            _src_line += ', Form 10-D distribution reports'
        _src_line += (" and the deal prospectus; rating histories "
                      "published under SEC Rule 17g-7(b) and agency "
                      "releases. Definitions are in the methods note "
                      'on the <a href="/cmbs/">market page</a>.</p>')
        parts.append(_src_line)
        parts.append(TABLE_SCRIPT)

        lede = (f"Current collateral, loans, tranches and ratings "
                f"for {d['trust_name']}.")
        aliases = [f"/cmbs/deal/{deal_by_key[sk]['slug']}/"
                   for sk in stubs]
        path = os.path.join(args.out, "deal", d["slug"] + ".md")
        with open(path, "w") as fh:
            fh.write(frontmatter(d["display_name"], lede,
                                 deal_data_as_of(d), today,
                                 aliases=aliases)
                     + "\n".join(parts) + "\n")
        n_pages += 1

    sanity["deal_pages"] = n_pages

    # ============================ redesign page generators
    NOTCH_SP = {"AAA": 1, "AA+": 2, "AA": 3, "AA-": 4, "A+": 5,
                "A": 6, "A-": 7, "BBB+": 8, "BBB": 9, "BBB-": 10,
                "BB+": 11, "BB": 12, "BB-": 13, "B+": 14, "B": 15,
                "B-": 16, "CCC+": 17, "CCC": 18, "CCC-": 19, "CC": 20,
                "C": 21, "D": 22}
    NOTCH_MOODY = {"Aaa": 1, "Aa1": 2, "Aa2": 3, "Aa3": 4, "A1": 5,
                   "A2": 6, "A3": 7, "Baa1": 8, "Baa2": 9, "Baa3": 10,
                   "Ba1": 11, "Ba2": 12, "Ba3": 13, "B1": 14, "B2": 15,
                   "B3": 16, "Caa1": 17, "Caa2": 18, "Caa3": 19,
                   "Ca": 20, "C": 21}

    def notch_of(rating, agency):
        if not rating:
            return None
        base = str(rating).replace(" (sf)", "").replace(
            " (prelim.)", "").strip()
        if agency == "moodys":
            return NOTCH_MOODY.get(base)
        return NOTCH_SP.get(base.upper())

    ACTION_WORDS = {
        "NW": "New rating", "UP": "Upgrade", "DG": "Downgrade",
        "WD": "Rating withdrawn", "WE": "Watch action",
        "WO": "Outlook or watch action", "HS": "Review action"}

    def action_word(code):
        if code is None:
            return "No action code in source"
        return ACTION_WORDS.get(code, f"Action code {code}")

    os.makedirs(os.path.join(args.out, "deal-ratings"), exist_ok=True)
    os.makedirs(os.path.join(args.out, "deal-loans"), exist_ok=True)
    os.makedirs(os.path.join(args.out, "loan"), exist_ok=True)
    _data_dir = os.path.join(SITE, "static", "cmbs-data")
    os.makedirs(_data_dir, exist_ok=True)

    def write_csv(name, header, rows):
        import csv as _csv
        path = os.path.join(_data_dir, name)
        with open(path, "w", newline="") as fh:
            w = _csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
        return f"/cmbs-data/{name}"

    # ------------------------------------------------ rating history
    n_ratings_pages = 0
    for d in published:
        key = (d["cik"], d["deal_segment"])
        if d["identity_mismatch"]:
            continue
        evs = events_by_deal.get(key, [])
        trs = tranches_by_deal.get(key, [])
        n_rated = sum(1 for t in trs
                      if (key[0], key[1], t["class"]) in classes_rated)
        if not evs and not n_rated:
            continue
        parts = []
        parts.append(
            f'<p class="bond-navrow"><a href="/cmbs/deal/'
            f'{d["slug"]}/">&larr; {esc(d["display_name"])}</a> '
            f'/ <a href="/cmbs/">CMBS market</a></p>')
        classes_with_actions = {e["class"] for e in evs}
        parts.append(
            f"<p>Rating actions recorded in the dataset cover "
            f"{len(classes_with_actions)} of the deal's {len(trs)} "
            f"classes. Each action shows the date the agency took "
            f"the action and the date it became publicly knowable "
            f"in the published rating histories, as explained in the "
            f"note at the foot of this page.</p>")
        # migration summary
        parts.append("<h2>Migration summary</h2>")
        mig_rows = []
        for ag, ag_label in AGENCIES:
            ae = [e for e in evs if e["agency"] == ag]
            if not ae:
                continue
            n_up = sum(1 for e in ae if e["action_class"] == "UP")
            n_dg = sum(1 for e in ae if e["action_class"] == "DG")
            n_wd = sum(1 for e in ae if e["action_class"] == "WD")
            first_dg = min((e["action_date"] for e in ae
                            if e["action_class"] == "DG"
                            and e["action_date"]), default=None)
            by_class = {}
            for e in ae:
                by_class.setdefault(e["class"], []).append(e)
            net = 0
            n_cls = 0
            for cls, ce in by_class.items():
                seq = [notch_of(e["rating"], ag) for e in ce]
                seq = [x for x in seq if x is not None]
                if len(seq) >= 2:
                    net += seq[-1] - seq[0]
                    n_cls += 1
            net_txt = (f"{net:+d} notches over {n_cls} classes"
                       if n_cls else NYR)
            mig_rows.append(
                f"<tr><td>{ag_label}</td>"
                f'<td class="num">{len(ae):,}</td>'
                f'<td class="num">{n_up:,}</td>'
                f'<td class="num">{n_dg:,}</td>'
                f'<td class="num">{n_wd:,}</td>'
                f'<td class="num">{esc(net_txt)}</td>'
                f'<td class="num">{first_dg.isoformat() if first_dg else "None recorded"}</td></tr>')
        if mig_rows:
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Agency</th>'
                "<th>Actions</th><th>Upgrades</th><th>Downgrades</th>"
                "<th>Withdrawals</th><th>Net notch movement</th>"
                "<th>First downgrade</th></tr></thead><tbody>"
                + "".join(mig_rows) + "</tbody></table></div>")
            parts.append(
                '<p class="data-vintage">Net notch movement sums, '
                "over the classes with at least two recorded "
                "ratings from the agency, the difference between the "
                "last and first recorded rating in notches; a "
                "positive figure means the classes ended weaker "
                "than they began.</p>")
        # agency releases (press lane)
        press_here = press_by_deal.get(key, [])
        if press_here:
            parts.append("<h2>Agency releases in the dataset</h2>")
            prows = []
            for p in sorted(press_here,
                            key=lambda x: x["knowledge"] or
                            datetime.date.min, reverse=True):
                title = esc(p["title"] or "Agency release")
                if p["url"]:
                    title = (f'<a href="{esc(p["url"])}">{title}</a>')
                prows.append(
                    f'<tr><td class="num">{p["knowledge"].isoformat() if p["knowledge"] else NYR}</td>'
                    f"<td>{esc(AGENCY_LABEL.get(p['agency'], p['agency']))}</td>"
                    f"<td>{esc(p['class'] or NYR)}</td>"
                    f"<td>{esc(p['action_raw'] or p['action_class'] or NYR)}</td>"
                    f"<td>{esc(p['rating'] or NYR)}</td>"
                    f"<td>{title}</td></tr>")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Published</th>'
                "<th>Agency</th><th>Class</th><th>Action</th>"
                "<th>Rating</th><th>Release</th></tr></thead>"
                "<tbody>" + "".join(prows) + "</tbody></table></div>")
        # per class per agency action tables
        parts.append("<h2>Actions by class</h2>")
        class_order = [t["class"] for t in trs]
        for cls in class_order + sorted(
                classes_with_actions - set(class_order)):
            ce_all = [e for e in evs if e["class"] == cls]
            if not ce_all:
                continue
            parts.append(f"<h3>Class {esc(cls)}</h3>")
            for ag, ag_label in AGENCIES:
                ce = [e for e in ce_all if e["agency"] == ag]
                if not ce:
                    continue
                cur = ratings.get((key[0], key[1], cls, ag))
                ow = ratings_ow.get((key[0], key[1], cls, ag),
                                    (None, None))
                cur_txt = esc(cur) if cur else NYR
                extra = "; ".join(x for x in [ow[0], ow[1]] if x)
                if extra:
                    cur_txt += f" ({esc(extra)})"
                parts.append(
                    f"<h4>{ag_label}: current rating {cur_txt}</h4>")
                erows = []
                for e in ce:
                    ow_after = "; ".join(
                        x for x in [e["outlook"], e["watch"]] if x)
                    erows.append(
                        f"<tr><td>{esc(action_word(e['action_class']))}</td>"
                        f"<td>{esc(e['prior'] or NYR)}</td>"
                        f"<td>{esc(e['rating'] or NYR)}</td>"
                        f"<td>{esc(ow_after) or NYR}</td>"
                        f'<td class="num">{e["action_date"].isoformat() if e["action_date"] else NYR}</td>'
                        f'<td class="num">{e["knowledge"].isoformat() if e["knowledge"] else NYR}</td></tr>')
                parts.append(
                    '<div class="market-table-scroll"><table '
                    'class="market-table"><thead><tr><th>Action</th>'
                    "<th>Prior rating</th><th>Rating</th>"
                    "<th>Outlook / watch after</th>"
                    "<th>Action date</th><th>Publicly knowable</th>"
                    "</tr></thead><tbody>" + "".join(erows)
                    + "</tbody></table></div>")
        no_action = [t["class"] for t in trs
                     if (key[0], key[1], t["class"]) in classes_rated
                     and t["class"] not in classes_with_actions]
        if no_action:
            parts.append(
                f"<p>Classes with a current rating in the dataset "
                f"but no recorded actions: "
                f"{esc(', '.join(no_action))}.</p>")
        parts.append(
            '<p class="data-vintage">Action date is the date the '
            "agency took the rating action. Publicly knowable is "
            "the publication date of the agency's rating history "
            "file, published under SEC Rule 17g-7(b), in which the "
            "action is recorded in this dataset. The dataset holds "
            "each agency's current published history, so the "
            "publicly knowable date is the current file's date and "
            "is an upper bound on when the action first became "
            "public in this form: earlier editions of the file "
            "carried older actions sooner. Actions labeled \"No "
            "action code in source\" are records the agency's file "
            "carries without a rating action code, principally "
            "affirmations and outlook or watch updates; the rating "
            "shown is the rating recorded with the record. Outlook "
            "and watch states are shown as recorded after each "
            "action, so the state in force between two actions is "
            "the state shown on the earlier row.</p>")
        path = os.path.join(args.out, "deal-ratings",
                            d["slug"] + ".md")
        with open(path, "w") as fh:
            fh.write(frontmatter(
                f"{d['display_name']}: rating history",
                f"Rating actions, action dates and public knowledge "
                f"dates for {d['trust_name']}.",
                deal_data_as_of(d), today)
                + "\n".join(parts) + "\n")
        n_ratings_pages += 1
    sanity["ratings_pages"] = n_ratings_pages


    # ------------------------------------------------ loan detail
    def build_loan_detail(k, l, d, full):
        pk = k[0]
        vd = ver_latest.get(k, {})
        sd = static_by_loan.get(k, {})
        lat = loan_latest.get(k)
        tot = deal_serv.get(pk, {}).get("tot") or 0.0
        name = loan_name(l, vd)
        parts = []
        addr_parts = []
        for v in clean_list(vd.get("paddr")):
            addr_parts.append(v)
        loc = loan_loc(l, vd)
        zips = clean_list(vd.get("pzip"))
        addr = "; ".join(addr_parts)
        if loc:
            addr = (addr + "; " if addr else "") + loc
        if zips:
            addr += f" {zips[0]}"
        share = (lat[2] / tot) if (lat and lat[2] is not None
                                   and tot and deal_serv.get(
                                       pk, {}).get("pm") == lat[0]
                                   ) else None
        m = loan_maturity(k)
        rows = [
            ("Property", name),
            ("Address", addr or NYR),
            ("Property type", loan_type_label(l, vd)),
            ("Units, beds or keys",
             vd.get("units") if vd.get("units") else NYR),
            ("Net rentable square feet",
             f"{fnum(vd['sqft']):,.0f}" if fnum(vd.get("sqft"))
             else NYR),
            ("Year built", str(sd["ybuilt"]) if sd.get("ybuilt")
             else NYR),
            ("Year last renovated",
             str(vd["yreno"]) if vd.get("yreno") else NYR),
            ("Original balance", money(l.get("amt"))),
            ("Current balance",
             (money(lat[2]) + f" ({month_label(lat[0])})")
             if lat and lat[2] is not None else NYR),
            ("Share of deal balance", pct_frac(share, 1)),
            ("Interest rate at origination",
             pct_frac(l.get("coupon")) if l.get("coupon") else NYR),
            ("Current interest rate",
             rate_disp(lat[4]) if lat else NYR),
            ("Origination date", str(l.get("orig") or NYR)),
            ("Original term",
             f"{sd['term_m']} months" if sd.get("term_m") else NYR),
            ("Amortization term",
             f"{sd['amort_m']} months" if sd.get("amort_m") else NYR),
            ("Interest-only period",
             f"{sd['io_m']} months" if sd.get("io_m") else NYR),
            ("Scheduled maturity",
             m.isoformat() if m else NYR),
            ("Prepayment lockout end",
             str(sd["lockout_end"]) if sd.get("lockout_end") else NYR),
            ("Yield maintenance end",
             str(sd["ym_end"]) if sd.get("ym_end") else NYR),
            ("Servicer",
             "; ".join(clean_list(vd.get("servicer"))) or NYR),
            ("Loan servicer",
             "; ".join(clean_list(vd.get("loan_servicer"))) or NYR),
            ("Originator", str(sd["originator"]) if sd.get("originator")
             else NYR),
            ("Current status",
             status_word(lat[1]) if lat else NYR),
            ("Specially serviced now", "Yes" if loan_ss_now(k)
             else "No"),
            ("Defeased", "Yes" if l.get("defeased") else "No"),
        ]
        parts.append('<table class="terms-table"><tbody>' + "".join(
            f'<tr><td class="muted">{esc(a)}</td><td>{esc(b)}</td></tr>'
            for a, b in rows) + "</tbody></table>")
        # valuation
        vrows = []
        if sd.get("sec_val"):
            vrows.append(
                ("At securitization",
                 money(sd["sec_val"]), str(sd.get("sec_val_d") or NYR),
                 str(sd.get("sec_val_src") or NYR)))
        ve = val_events.get(k, [])
        cur_val = None
        if ve:
            cur_val = ve[-1]
            vrows.append(
                ("Most recent reported", money(cur_val[1]),
                 cur_val[0].isoformat() if cur_val[0] else NYR,
                 str(cur_val[2] or NYR)))
        elif vd.get("val_amt"):
            vrows.append(
                ("Most recent reported", money(vd["val_amt"]),
                 str(vd.get("val_d") or NYR),
                 str(vd.get("val_src") or NYR)))
            cur_val = (dparse(vd.get("val_d")), vd["val_amt"],
                       vd.get("val_src"))
        if vrows:
            parts.append("<h3>Valuation</h3>" if not full else
                         "<h2>Valuation</h2>")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Basis</th>'
                "<th>Amount</th><th>Date</th><th>Source (as filed)</th>"
                "</tr></thead><tbody>" + "".join(
                    f"<tr><td>{esc(a)}</td>"
                    f'<td class="num">{b}</td><td>{esc(c)}</td>'
                    f"<td>{esc(e)}</td></tr>"
                    for a, b, c, e in vrows) + "</tbody></table></div>")
            if len(vrows) == 2 and sd.get("sec_val") and cur_val \
                    and cur_val[1]:
                parts.append(
                    f'<p class="data-vintage">Change from '
                    f"securitization to the most recent reported "
                    f"valuation: "
                    f"{pct_frac(cur_val[1] / sd['sec_val'] - 1, 1)}.</p>")
            if len(ve) > 1:
                vpts = [(x[0], x[1]) for x in ve if x[0] and x[1]]
                if len(vpts) >= 3:
                    parts.append(svg_line_chart(
                        [("Reported valuation", "#1a1a1a", vpts)],
                        "Reported valuations", y_fmt="${:,.0f}"))
        # tenants
        trows = []
        for nm_f, sf_f, exp_f in (("t1", "t1_sf", "t1_exp"),
                                  ("t2", "t2_sf", "t2_exp"),
                                  ("t3", "t3_sf", "t3_exp")):
            for nm in clean_list(vd.get(nm_f)):
                trows.append(
                    f"<tr><td>{esc(nm)}</td>"
                    f'<td class="num">{vd[sf_f]:,.0f}</td>'
                    f"<td>{esc(str(vd.get(exp_f) or NYR))}</td></tr>"
                    if vd.get(sf_f) else
                    f"<tr><td>{esc(nm)}</td>"
                    f'<td class="num">{NYR}</td>'
                    f"<td>{esc(str(vd.get(exp_f) or NYR))}</td></tr>")
                break
        if trows:
            parts.append("<h3>Largest tenants</h3>" if not full else
                         "<h2>Largest tenants</h2>")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Tenant</th>'
                "<th>Square feet</th><th>Lease expiration</th></tr>"
                "</thead><tbody>" + "".join(trows)
                + "</tbody></table></div>")
            parts.append(
                '<p class="data-vintage">The three largest tenants '
                "as reported in the latest asset-level record.</p>")
        # financials
        rows_m = loan_months.get(k, [])
        if full and rows_m:
            parts.append("<h2>Monthly history</h2>")
            bal_pts = [(r[0], r[2]) for r in rows_m if r[2] is not None]
            dscr_pts = [(r[0], r[5]) for r in rows_m
                        if r[5] is not None and r[5] <= 15]
            if len(bal_pts) >= 3:
                parts.append(svg_line_chart(
                    [("Reported balance", "#1a1a1a", bal_pts)],
                    "Reported balance", y_fmt="${:,.0f}"))
            if len(dscr_pts) >= 3:
                parts.append(svg_line_chart(
                    [("DSCR (net cash flow)", "#1a1a1a", dscr_pts)],
                    "Debt service coverage, net cash flow basis",
                    y_fmt="{:.1f}"))
            hrows = []
            for r in rows_m:
                hrows.append(
                    f"<tr><td>{esc(month_label(r[0]))}</td>"
                    f'<td class="num">{money(r[2]) if r[2] is not None else NYR}</td>'
                    f"<td>{esc(status_word(r[1]))}</td>"
                    f'<td class="num">{rate_disp(r[4])}</td>'
                    f'<td class="num">{dscr_disp(r[5])}</td>'
                    f'<td class="num">{dscr_disp(r[6])}</td>'
                    f'<td class="num">{occ_disp(r[7])}</td>'
                    f'<td class="num">{money(r[8]) if r[8] is not None else NYR}</td>'
                    f"<td>{esc(str(r[10]) if r[10] else NYR)}</td>"
                    f'<td class="num">{money(r[11]) if r[11] is not None else NYR}</td>'
                    f'<td class="num">{money(r[12]) if r[12] is not None else NYR}</td>'
                    f'<td class="num">{money(r[13]) if r[13] is not None else NYR}</td>'
                    f'<td class="num">{money(r[14]) if r[14] is not None else NYR}</td></tr>')
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Month</th>'
                "<th>Balance</th><th>Status</th><th>Rate</th>"
                "<th>DSCR (NCF)</th><th>DSCR (NOI)</th>"
                "<th>Occupancy</th><th>Advances</th>"
                "<th>Financial period end</th><th>Revenue</th>"
                "<th>Expenses</th><th>NOI</th><th>NCF</th></tr>"
                "</thead><tbody>" + "".join(hrows)
                + "</tbody></table></div>")
            parts.append(
                '<p class="data-vintage">Revenue, expenses, net '
                "operating income (NOI) and net cash flow (NCF) are "
                "the most recent financials reported as of each "
                "month, for the financial period ending on the date "
                "shown. DSCR is debt service coverage on the net "
                "cash flow and net operating income bases as "
                "reported.</p>")
        elif rows_m and lat:
            frows = [
                ("Financial period end (latest)",
                 str(lat[10]) if lat[10] else NYR),
                ("Revenue", money(lat[11])),
                ("Operating expenses", money(lat[12])),
                ("Net operating income", money(lat[13])),
                ("Net cash flow", money(lat[14])),
                ("DSCR (net cash flow)", dscr_disp(lat[5])),
                ("DSCR (net operating income)", dscr_disp(lat[6])),
                ("Occupancy", occ_disp(lat[7])),
                ("Servicer advances outstanding", money(lat[8])),
            ]
            parts.append("<h3>Latest financials</h3>")
            parts.append('<table class="terms-table"><tbody>'
                         + "".join(
                             f'<tr><td class="muted">{esc(a)}</td>'
                             f"<td>{esc(b)}</td></tr>"
                             for a, b in frows) + "</tbody></table>")
        # status timeline
        evs = loan_events(k, l)
        prefix = f"{esc(name)}: "
        trows = []
        for dt, lab, txt in evs:
            if txt.startswith(prefix):
                txt = txt[len(prefix):]
                txt = txt[:1].upper() + txt[1:]
            trows.append(
                (dt or datetime.date.min,
                 f'<tr><td class="num">{esc(lab)}</td>'
                 f"<td>{txt}</td></tr>"))
        if m and m < panel_end and lat and (lat[2] or 0) > 0 \
                and not dparse(vd.get("liq_d")):
            trows.append(
                (m,
                 f'<tr><td class="num">{m.isoformat()}</td>'
                 f"<td>Scheduled maturity passed; the loan is still "
                 f"reported, with status {esc(status_word(lat[1]))} "
                 f"in {esc(month_label(lat[0]))}</td></tr>"))
        if trows:
            trows.sort(key=lambda x: x[0])
            parts.append("<h3>Status timeline</h3>" if not full else
                         "<h2>Status timeline</h2>")
            parts.append(
                '<div class="market-table-scroll"><table '
                'class="market-table"><thead><tr><th>Date</th>'
                "<th>Event</th></tr></thead><tbody>"
                + "".join(h for _dt, h in trows)
                + "</tbody></table></div>")
        return "".join(parts)

    # sibling pieces: same property name and origination date filed
    # in other trusts (pari passu pieces are filed at whole-loan
    # amounts in each trust that holds a share)
    sib_map = {}
    for d0 in published:
        if d0["identity_mismatch"]:
            continue
        pk0 = (d0["cik"], d0["deal_segment"])
        for l0 in group_loans.get(pk0, []):
            nm0 = (l0["pnames"][0].strip().lower()
                   if l0.get("pnames") else "")
            og0 = str(l0.get("orig") or "")
            if nm0 and og0:
                sib_map.setdefault((nm0, og0), []).append(
                    (pk0, str(l0["asset"])))

    # ------------------------------------------------ loan annexes
    n_annex = 0
    for d in published:
        key = (d["cik"], d["deal_segment"])
        if d["identity_mismatch"]:
            continue
        loans = group_loans.get(key, [])
        annex_loans = [l for l in loans
                       if (key, str(l["asset"])) not in loan_page_keys]
        if not annex_loans:
            continue
        parts = []
        parts.append(
            f'<p class="bond-navrow"><a href="/cmbs/deal/'
            f'{d["slug"]}/">&larr; {esc(d["display_name"])}</a> '
            f'/ <a href="/cmbs/">CMBS market</a></p>')
        parts.append(
            f"<p>Detail sections for the {len(annex_loans)} loans "
            f"of this deal that do not have a page of their own. "
            f"Loans with a surveillance history, loans at or above "
            f"the section's size threshold of "
            f"{money(LOAN_THRESHOLD)}, and the largest loans in the "
            f"deal have their own pages, linked from the loan table "
            f"on the deal page. Every loan in the deal appears "
            f"either here or on its own page.</p>")
        for l in annex_loans:
            k = (key, str(l["asset"]))
            vd = ver_latest.get(k, {})
            parts.append(
                f'<h2 id="{loan_anchor(d, l["asset"])}">'
                f'{esc(loan_name(l, vd))}</h2>')
            parts.append(build_loan_detail(k, l, d, full=False))
        path = os.path.join(args.out, "deal-loans", d["slug"] + ".md")
        with open(path, "w") as fh:
            fh.write(frontmatter(
                f"{d['display_name']}: loan annex",
                f"Loan detail for {d['trust_name']}.",
                deal_data_as_of(d), today)
                + "\n".join(parts) + "\n")
        n_annex += 1
    sanity["annex_pages"] = n_annex

    # ------------------------------------------------ loan pages
    n_loan_pages = 0
    loan_by_group = {}
    for pk, loans in group_loans.items():
        for l in loans:
            loan_by_group[(pk, str(l["asset"]))] = l
    for k in sorted(loan_page_keys,
                    key=lambda kk: (deal_by_key[kk[0]]["slug"], kk[1])):
        pk, asset = k
        d = deal_by_key[pk]
        l = loan_by_group[k]
        vd = ver_latest.get(k, {})
        name = loan_name(l, vd)
        lat = loan_latest.get(k)
        tot = deal_serv.get(pk, {}).get("tot") or 0.0
        parts = []
        annex_exists = any(
            (pk, str(x["asset"])) not in loan_page_keys
            for x in group_loans.get(pk, []))
        nav = (f'<p class="bond-navrow"><a href="/cmbs/deal/'
               f'{d["slug"]}/">&larr; {esc(d["display_name"])}</a>')
        if annex_exists:
            nav += (f' / <a href="/cmbs/deal-loans/'
                    f'{d["slug"]}/">Loan annex</a>')
        nav += ' / <a href="/cmbs/">CMBS market</a></p>'
        parts.append(nav)
        strip_items = [
            ("Deal", d["display_name"]),
            ("Current balance",
             (money(lat[2]) + f" ({month_label(lat[0])})")
             if lat and lat[2] is not None else NYR),
            ("Share of deal",
             pct_frac(lat[2] / tot, 1) if lat and lat[2] is not None
             and tot and deal_serv.get(pk, {}).get("pm") == lat[0]
             else NYR),
            ("Status", status_word(lat[1]) if lat else NYR),
            ("DSCR (latest)", dscr_disp(lat[5]) if lat else NYR),
            ("Occupancy (latest)", occ_disp(lat[7]) if lat else NYR),
            ("Scheduled maturity",
             loan_maturity(k).isoformat() if loan_maturity(k)
             else NYR),
        ]
        parts.append('<dl class="bw-summary">' + "".join(
            f'<div class="bw-sum-item"><dt>{esc(a)}</dt>'
            f"<dd>{esc(b)}</dd></div>"
            for a, b in strip_items) + "</dl>")
        parts.append("<h2>Property and terms</h2>")
        parts.append(build_loan_detail(k, l, d, full=True))
        nm0 = (l["pnames"][0].strip().lower() if l.get("pnames")
               else "")
        og0 = str(l.get("orig") or "")
        sibs = []
        if nm0 and og0:
            for dk, da in sib_map.get((nm0, og0), []):
                if dk != pk:
                    sibs.append((dk, da))
        if sibs:
            parts.append("<h2>Also filed in other trusts</h2>")
            links = []
            for dk, da in sorted(
                    sibs, key=lambda x: (deal_by_key[x[0]]["slug"],
                                         x[1]))[:10]:
                dd2 = deal_by_key[dk]
                links.append(
                    f'<a href="{loan_url(dd2, (dk, da), da)}">'
                    f'{esc(dd2["display_name"])}</a>')
            parts.append(
                "<p>Loans are sometimes split across trusts (pari "
                "passu), and each trust files the loan at its "
                "whole-loan amount. A loan with the same property "
                "name and origination date is filed in: "
                + "; ".join(links) + ".</p>")
        parts.append(
            '<p class="data-vintage">Sources: SEC Form ABS-EE '
            "asset-level reports for the deal. Definitions are in "
            'the methods note on the <a href="/cmbs/">market '
            "page</a>.</p>")
        slug = f"{d['slug']}--{loan_slug[k]}"
        path = os.path.join(args.out, "loan", slug + ".md")
        with open(path, "w") as fh:
            fh.write(frontmatter(
                f"{name} ({d['trust_name']})",
                f"Property, terms, monthly financial history and "
                f"surveillance record for a loan in "
                f"{d['trust_name']}.",
                deal_data_as_of(d), today)
                + "\n".join(parts) + "\n")
        n_loan_pages += 1
    sanity["loan_pages_written"] = n_loan_pages


    # ------------------------------------------------ monthly changes
    P = panel_end
    P0 = prev_month
    ym = f"{P.year}{P.month:02d}"

    def deal_link(pk):
        dd = deal_by_key[pk]
        return (f'<a href="/cmbs/deal/{dd["slug"]}/">'
                f'{esc(dd["display_name"])}</a>')

    def loan_link(pk, asset):
        dd = deal_by_key[pk]
        l = loan_by_group.get((pk, str(asset)))
        if l is None:
            return esc(f"Loan {asset}")
        vd = ver_latest.get((pk, str(asset)), {})
        return (f'<a href="{loan_url(dd, (pk, str(asset)), asset)}">'
                f'{esc(loan_name(l, vd))}</a>')

    def change_block(title, intro, header, rows_html, csv_name,
                     csv_header, csv_rows, balance_note=True):
        out = [f"<h2>{esc(title)}</h2>"]
        out.append(f"<p>{intro}</p>")
        if not rows_html:
            out.append(f"<p>None recorded for "
                       f"{month_label(P)}.</p>")
            return "".join(out)
        shown = rows_html[:100]
        out.append(
            '<div class="market-table-scroll"><table '
            'class="market-table"><thead><tr>'
            + "".join(f"<th>{esc(h)}</th>" for h in header)
            + "</tr></thead><tbody>" + "".join(shown)
            + "</tbody></table></div>")
        if len(rows_html) > 100:
            url = write_csv(csv_name, csv_header, csv_rows)
            out.append(
                f'<p class="data-vintage">Showing the 100 largest '
                f"by balance of {len(rows_html):,} entries. The "
                f'full list is available as a CSV file: '
                f'<a href="{url}">{esc(csv_name)}</a>.</p>')
        return "".join(out)

    # newly delinquent
    nd_rows = []
    nd_csv = []
    for (pk, asset), rows in loan_months.items():
        if pk not in published_keys:
            continue
        bym = {r[0]: r for r in rows}
        cur = bym.get(P)
        if not cur or cur[1] not in ("1", "2", "3", "4", "5"):
            continue
        prev = bym.get(P0)
        if prev and prev[1] in ("1", "2", "3", "4", "5"):
            continue
        nd_rows.append((cur[2] or 0.0,
                        f"<tr><td>{loan_link(pk, asset)}</td>"
                        f"<td>{deal_link(pk)}</td>"
                        f"<td>{esc(status_word(cur[1]))}</td>"
                        f'<td class="num">{money(cur[2])}</td></tr>'))
        l = loan_by_group.get((pk, asset), {})
        nd_csv.append([loan_name(l, ver_latest.get((pk, asset), {})),
                       deal_by_key[pk]["display_name"],
                       status_word(cur[1]), cur[2]])
    nd_rows.sort(key=lambda x: (-x[0], x[1]))

    # newly specially serviced (transfer dates in the month)
    nss_rows = []
    nss_csv = []
    for (pk, asset), pairs in ss_pairs.items():
        if pk not in published_keys:
            continue
        tin = [t for t, _r in pairs
               if t and P <= t < month_shift(P, 1)]
        if not tin:
            continue
        lat = loan_latest.get((pk, asset))
        bal = lat[2] if lat else None
        nss_rows.append(
            (bal or 0.0,
             f"<tr><td>{loan_link(pk, asset)}</td>"
             f"<td>{deal_link(pk)}</td>"
             f'<td class="num">{min(tin).isoformat()}</td>'
             f'<td class="num">{money(bal) if bal is not None else NYR}</td></tr>'))
        l = loan_by_group.get((pk, asset), {})
        nss_csv.append([loan_name(l, ver_latest.get((pk, asset), {})),
                        deal_by_key[pk]["display_name"],
                        min(tin).isoformat(), bal])
    nss_rows.sort(key=lambda x: (-x[0], x[1]))

    # new modifications: dated modifications in the month, plus
    # loans whose monthly report first carries the modification
    # indicator in the month
    nm_rows = []
    nm_csv = []
    for (pk, asset), evs in mod_events.items():
        if pk not in published_keys:
            continue
        for md, prate, pmat, ppay in evs:
            if md and P <= md < month_shift(P, 1):
                lat = loan_latest.get((pk, asset))
                bal = lat[2] if lat else None
                det = []
                if prate is not None:
                    det.append("rate "
                               + rate_disp(prate / 100 if prate > 1
                                           else prate))
                if pmat:
                    det.append("maturity " + pmat.isoformat())
                nm_rows.append(
                    (bal or 0.0,
                     f"<tr><td>{loan_link(pk, asset)}</td>"
                     f"<td>{deal_link(pk)}</td>"
                     f'<td class="num">{md.isoformat()}</td>'
                     f"<td>{esc('; '.join(det)) or NYR}</td>"
                     f'<td class="num">{money(bal) if bal is not None else NYR}</td></tr>'))
                l = loan_by_group.get((pk, asset), {})
                nm_csv.append(
                    [loan_name(l, ver_latest.get((pk, asset), {})),
                     deal_by_key[pk]["display_name"], md.isoformat(),
                     "; ".join(det), bal])
    nm_rows.sort(key=lambda x: (-x[0], x[1]))
    nmi_rows = []
    nmi_csv = []
    for (pk, asset), rows in loan_months.items():
        if pk not in published_keys:
            continue
        bym = {r[0]: r for r in rows}
        cur = bym.get(P)
        prev = bym.get(P0)
        if cur and str(cur[9]).lower() == "true" and not (
                prev and str(prev[9]).lower() == "true"):
            nmi_rows.append(
                (cur[2] or 0.0,
                 f"<tr><td>{loan_link(pk, asset)}</td>"
                 f"<td>{deal_link(pk)}</td>"
                 f"<td>{esc(status_word(cur[1]))}</td>"
                 f'<td class="num">{money(cur[2])}</td></tr>'))
            l = loan_by_group.get((pk, asset), {})
            nmi_csv.append(
                [loan_name(l, ver_latest.get((pk, asset), {})),
                 deal_by_key[pk]["display_name"], status_word(cur[1]),
                 cur[2]])
    nmi_rows.sort(key=lambda x: (-x[0], x[1]))

    # liquidations in the month
    lq_rows = []
    lq_csv = []
    for (pk, asset), vd in ver_latest.items():
        if pk not in published_keys:
            continue
        liq_d = dparse(vd.get("liq_d"))
        if not liq_d or not (P <= liq_d < month_shift(P, 1)):
            continue
        rows = loan_months.get((pk, asset), [])
        bal_at = None
        for r in rows:
            if r[0] <= datetime.date(liq_d.year, liq_d.month, 1) \
                    and r[2] is not None:
                bal_at = r[2]
        loss = vd.get("loss")
        sev = (loss / bal_at) if (loss is not None and bal_at) \
            else None
        lq_rows.append(
            (bal_at or 0.0,
             f"<tr><td>{loan_link(pk, asset)}</td>"
             f"<td>{deal_link(pk)}</td>"
             f'<td class="num">{liq_d.isoformat()}</td>'
             f'<td class="num">{money(bal_at) if bal_at is not None else NYR}</td>'
             f'<td class="num">{money(loss) if loss is not None else NYR}</td>'
             f'<td class="num">{pct_frac(sev)}</td></tr>'))
        l = loan_by_group.get((pk, asset), {})
        lq_csv.append([loan_name(l, vd),
                       deal_by_key[pk]["display_name"],
                       liq_d.isoformat(), bal_at, loss, sev])
    lq_rows.sort(key=lambda x: (-x[0], x[1]))

    # reached scheduled maturity in the month and did not pay off
    fm_rows = []
    fm_csv = []
    for (pk, asset), l in loan_by_group.items():
        if pk not in published_keys:
            continue
        k = (pk, asset)
        m = loan_maturity_sched(k)
        if not m or not (P <= m < month_shift(P, 1)):
            continue
        vd = ver_latest.get(k, {})
        if dparse(vd.get("liq_d")):
            continue
        bym = {r[0]: r for r in loan_months.get(k, [])}
        cur = bym.get(P) or loan_latest.get(k)
        if not cur or not cur[2]:
            continue
        fm_rows.append(
            (cur[2] or 0.0,
             f"<tr><td>{loan_link(pk, asset)}</td>"
             f"<td>{deal_link(pk)}</td>"
             f'<td class="num">{m.isoformat()}</td>'
             f"<td>{esc(status_word(cur[1]))}</td>"
             f'<td class="num">{money(cur[2])}</td></tr>'))
        fm_csv.append([loan_name(l, vd),
                       deal_by_key[pk]["display_name"],
                       m.isoformat(), status_word(cur[1]), cur[2]])
    fm_rows.sort(key=lambda x: (-x[0], x[1]))

    # rating downgrades: agency releases first (real publication
    # dates), then the published histories on the action-date basis
    all_press = [p for evs in press_by_deal.values() for p in evs]
    press_month = None
    if all_press:
        press_month = max(
            (p["knowledge"] for p in all_press if p["knowledge"]),
            default=None)
    pd_rows = []
    if press_month:
        pm_start = datetime.date(press_month.year, press_month.month, 1)
        for pk, evs in press_by_deal.items():
            if pk not in deal_by_key:
                continue
            dd = deal_by_key[pk]
            for p in evs:
                if not p["knowledge"] or p["knowledge"] < pm_start:
                    continue
                raw = (p["action_raw"] or "") + " " + \
                    (p["action_class"] or "")
                if "downgrad" not in raw.lower():
                    continue
                title = esc(p["title"] or "Release")
                if p["url"]:
                    title = (f'<a href="{esc(p["url"])}">{title}</a>')
                pd_rows.append(
                    f"<tr><td>{deal_link(pk)}</td>"
                    f"<td>{esc(p['class'] or NYR)}</td>"
                    f"<td>{esc(AGENCY_LABEL.get(p['agency'], p['agency']))}</td>"
                    f"<td>{esc(p['prior'] or NYR)}</td>"
                    f"<td>{esc(p['rating'] or NYR)}</td>"
                    f'<td class="num">{p["action_date"].isoformat() if p["action_date"] else NYR}</td>'
                    f'<td class="num">{p["knowledge"].isoformat()}</td>'
                    f"<td>{title}</td></tr>")
    all_actions = [e for evs in events_by_deal.values() for e in evs
                   if e["action_date"]]
    latest_action_month = None
    hd_rows = []
    hd_csv = []
    if all_actions:
        latest_action_month = max(e["action_date"] for e in all_actions)
        lam = datetime.date(latest_action_month.year,
                            latest_action_month.month, 1)
        for pk, evs in events_by_deal.items():
            if pk not in published_keys:
                continue
            dd = deal_by_key[pk]
            for e in evs:
                if e["action_class"] != "DG" or not e["action_date"] \
                        or e["action_date"] < lam:
                    continue
                hd_rows.append(
                    f"<tr><td>{deal_link(pk)}</td>"
                    f"<td>{esc(e['class'])}</td>"
                    f"<td>{esc(AGENCY_LABEL.get(e['agency'], e['agency']))}</td>"
                    f"<td>{esc(e['prior'] or NYR)}</td>"
                    f"<td>{esc(e['rating'] or NYR)}</td>"
                    f'<td class="num">{e["action_date"].isoformat()}</td>'
                    f'<td class="num">{e["knowledge"].isoformat() if e["knowledge"] else NYR}</td></tr>')
                hd_csv.append([dd["display_name"], e["class"],
                               AGENCY_LABEL.get(e["agency"],
                                                e["agency"]),
                               e["prior"], e["rating"],
                               e["action_date"].isoformat(),
                               e["knowledge"].isoformat()
                               if e["knowledge"] else ""])
    hd_rows.sort()

    ch_parts = []
    ch_parts.append(
        f"<p>What changed in the latest reporting month, "
        f"{month_label(P)}, against {month_label(P0)}, computed "
        f"from the trusts' own monthly loan reports and the rating "
        f"records in the dataset. Rating actions are shown on two "
        f"bases: agency releases carry their own publication dates, "
        f"while the complete rating histories are published under "
        f"Rule 17g-7(b) with a lag, so the history table below "
        f"covers the latest month of recorded actions and shows "
        f"when each action became publicly knowable.</p>")
    ch_parts.append(change_block(
        "Newly delinquent loans",
        f"Loans reported 30 or more days delinquent, in "
        f"foreclosure or in REO in {month_label(P)} that were not "
        f"delinquent in {month_label(P0)}, including loans "
        f"reporting for the first time.",
        ["Loan", "Deal", "Status", "Balance"],
        [h for _b, h in nd_rows], f"changes-newly-delinquent-{ym}.csv",
        ["Loan", "Deal", "Status", "Balance"], nd_csv))
    ch_parts.append(change_block(
        "Newly transferred to special servicing",
        f"Loans whose filings record a transfer to the special "
        f"servicer dated in {month_label(P)}.",
        ["Loan", "Deal", "Transfer date", "Balance"],
        [h for _b, h in nss_rows],
        f"changes-newly-special-{ym}.csv",
        ["Loan", "Deal", "Transfer date", "Balance"], nss_csv))
    ch_parts.append(change_block(
        "New modifications",
        f"Modifications dated in {month_label(P)} in the "
        f"asset-level filings, with the terms after modification "
        f"where the filings report them.",
        ["Loan", "Deal", "Modification date", "Terms after",
         "Balance"],
        [h for _b, h in nm_rows], f"changes-modifications-{ym}.csv",
        ["Loan", "Deal", "Modification date", "Terms after",
         "Balance"], nm_csv))
    if nmi_rows:
        ch_parts.append(change_block(
            "Newly reported with a modification in effect",
            f"Loans whose monthly report carries the modification "
            f"indicator in {month_label(P)} and did not in "
            f"{month_label(P0)}. Servicers report modifications in "
            f"the monthly indicator before the dated modification "
            f"record appears in the asset-level filings.",
            ["Loan", "Deal", "Status", "Balance"],
            [h for _b, h in nmi_rows],
            f"changes-modified-indicator-{ym}.csv",
            ["Loan", "Deal", "Status", "Balance"], nmi_csv))
    ch_parts.append(change_block(
        "Liquidations",
        f"Loans whose filings record a liquidation dated in "
        f"{month_label(P)}. Severity is the realized loss divided "
        f"by the last balance reported in or before the "
        f"liquidation month.",
        ["Loan", "Deal", "Liquidation date", "Balance at "
         "liquidation", "Realized loss", "Severity"],
        [h for _b, h in lq_rows], f"changes-liquidations-{ym}.csv",
        ["Loan", "Deal", "Liquidation date", "Balance", "Loss",
         "Severity"], lq_csv))
    ch_parts.append(change_block(
        "Matured and not paid off",
        f"Loans whose scheduled maturity (origination date plus "
        f"original term) fell in {month_label(P)} and that are "
        f"still reported with a balance, including loans extended "
        f"at maturity.",
        ["Loan", "Deal", "Scheduled maturity", "Status", "Balance"],
        [h for _b, h in fm_rows], f"changes-matured-{ym}.csv",
        ["Loan", "Deal", "Scheduled maturity", "Status", "Balance"],
        fm_csv))
    ch_parts.append("<h2>Rating downgrades</h2>")
    if pd_rows:
        ch_parts.append(
            f"<p>Downgrades in agency releases published in "
            f"{month_label(press_month)}, from the releases "
            f"collected in the dataset.</p>")
        ch_parts.append(
            '<div class="market-table-scroll"><table '
            'class="market-table"><thead><tr><th>Deal</th>'
            "<th>Class</th><th>Agency</th><th>From</th><th>To</th>"
            "<th>Action date</th><th>Published</th><th>Release</th>"
            "</tr></thead><tbody>" + "".join(pd_rows)
            + "</tbody></table></div>")
    else:
        ch_parts.append(
            "<p>No downgrades appear in the agency releases "
            "collected in the dataset for the latest month.</p>")
    if hd_rows:
        lam_label = month_label(
            datetime.date(latest_action_month.year,
                          latest_action_month.month, 1))
        ch_parts.append(
            f"<p>Downgrade actions dated in {lam_label}, the "
            f"latest month in the published rating histories. The "
            f"publicly knowable date is the publication date of "
            f"the agency's current history file, in which the "
            f"action is recorded; see the methods note on the "
            f"market page.</p>")
        shown = hd_rows[:100]
        ch_parts.append(
            '<div class="market-table-scroll"><table '
            'class="market-table"><thead><tr><th>Deal</th>'
            "<th>Class</th><th>Agency</th><th>From</th><th>To</th>"
            "<th>Action date</th><th>Publicly knowable</th>"
            "</tr></thead><tbody>" + "".join(shown)
            + "</tbody></table></div>")
        if len(hd_rows) > 100:
            url = write_csv(f"changes-downgrades-{ym}.csv",
                            ["Deal", "Class", "Agency", "From", "To",
                             "Action date", "Publicly knowable"],
                            hd_csv)
            ch_parts.append(
                f'<p class="data-vintage">Showing 100 of '
                f"{len(hd_rows):,} downgrades. The full list is "
                f'available as a CSV file: <a href="{url}">'
                f"changes-downgrades-{ym}.csv</a>.</p>")
    with open(os.path.join(args.out, "changes.md"), "w") as fh:
        fh.write(frontmatter(
            "CMBS monthly changes",
            f"New delinquencies, special servicing transfers, "
            f"modifications, liquidations, maturities and rating "
            f"downgrades for {month_label(P)}.",
            data_as_of, today) + "".join(ch_parts) + "\n")
    sanity["changes_blocks"] = {
        "newly_delinquent": len(nd_rows), "newly_special": len(nss_rows),
        "modifications": len(nm_rows),
        "modified_indicator": len(nmi_rows),
        "liquidations": len(lq_rows), "matured": len(fm_rows),
        "press_downgrades": len(pd_rows),
        "history_downgrades": len(hd_rows)}

    # ------------------------------------------------ section stubs
    for sub, ttl, txt in (
            ("deal-ratings", "CMBS deal rating histories",
             "Rating history pages are linked from each deal page."),
            ("deal-loans", "CMBS deal loan annexes",
             "Loan annexes are linked from each deal page."),
            ("loan", "CMBS loans",
             "Loan pages are linked from each deal's loan table.")):
        with open(os.path.join(args.out, sub, "_index.md"), "w") as fh:
            fh.write(f'---\ntitle: "{ttl}"\n---\n\n{txt}\n')

    # ------------------------------------------------ file census
    def count_files(root):
        n = 0
        for _dp, _dn, fn in os.walk(root):
            n += len(fn)
        return n
    sanity["cmbs_content_files"] = count_files(args.out)
    sanity["site_content_files"] = count_files(
        os.path.join(SITE, "content"))
    sanity["site_static_files"] = count_files(
        os.path.join(SITE, "static"))
    sanity["deployment_budget"] = 20000
    sanity["projected_files_proxy"] = (
        sanity["site_content_files"] + sanity["site_static_files"]
        + 600)
    print(json.dumps(sanity, indent=1, default=str))


if __name__ == "__main__":
    main()
