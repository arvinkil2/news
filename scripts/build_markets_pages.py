#!/usr/bin/env python3
"""Build the Global Markets section from data/global_markets.json.
Writes content/markets/_index.md (landing) and one page per market
under content/markets/<slug>.md. Tables use the shared bw-grid
adjustable-table engine (scripts/table_engine.py), the same system
as the Leverage section. Run after fetch_global_markets.py.
"""
import datetime
import glob
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from table_engine import TABLE_ENGINE_JS, bw_open, reset_btn  # noqa: E402

SITE = os.path.expanduser("~/workspace/news-site")
OUT = os.path.join(SITE, "content", "markets")
STORIES = os.path.join(SITE, "content", "stories")

GROUPS = [("americas", "Americas"), ("europe", "Europe"),
          ("asia-pacific", "Asia-Pacific"),
          ("middle-east-africa", "Middle East and Africa")]

ALIASES = {
    "united-states": ["U.S.", "US ", "United States", "America"],
    "united-kingdom": ["UK", "Britain", "United Kingdom"],
    "united-arab-emirates": ["UAE", "Emirates"],
    "south-korea": ["South Korea", "Korea"],
    "eurozone": ["Eurozone", "euro zone", "Euro area"],
    "hong-kong": ["Hong Kong"],
    "saudi-arabia": ["Saudi Arabia", "Saudi"],
    "south-africa": ["South Africa"],
}

BLANK = '<span class="blank">-</span>'


def esc(s):
    return html.escape(str(s), quote=True)


def fmt_num(v):
    if v >= 1000:
        return f"{v:,.0f}"
    if v >= 50:
        return f"{v:,.2f}"
    return f"{v:,.4f}"


def fmt_pct(v):
    cls = "up" if v >= 0 else "down"
    return f'<span class="{cls}">{v:+.2f}%</span>'


def fmt_bp(v):
    if v is None:
        return BLANK
    cls = "up" if v >= 0 else "down"
    return f'<span class="{cls}">{v:+.1f}</span>'


def spark_svg(row):
    if not row or not row.get("spark"):
        return ""
    color = "#1a7f37" if row.get("up_1d") else "#b42318"
    return (f'<svg class="spark" width="96" height="28" viewBox="0 0 96 28" '
            f'aria-hidden="true"><polyline points="{row["spark"]}" '
            f'fill="none" stroke="{color}" stroke-width="1.5"/></svg>')


def frontmatter(title, lede, data_as_of):
    today = datetime.date.today().isoformat()
    return (f'---\ntitle: "{title}"\ndate: "{today}"\n'
            f'lede: "{lede}"\ndata_as_of: "{data_as_of}"\n---\n\n')


def load_stories():
    """(date, slug, title, regions) for every story, newest first."""
    out = []
    for path in glob.glob(os.path.join(STORIES, "*.md")):
        try:
            text = open(path, encoding="utf-8").read(6000)
        except OSError:
            continue
        fm = text.split("---", 2)
        if len(fm) < 3:
            continue
        fm = fm[1]
        t = re.search(r'^title:\s*"(.*?)"\s*$', fm, re.M)
        d = re.search(r"^date:\s*(\S+)", fm, re.M)
        r = re.search(r"^regions:\s*\[(.*?)\]", fm, re.M)
        if not t or not d:
            continue
        regions = []
        if r:
            regions = [x.strip().strip('"\'') for x in r.group(1).split(",")
                       if x.strip()]
        out.append({"date": d.group(1)[:10], "slug":
                    os.path.basename(path)[:-3], "title": t.group(1),
                    "regions": regions})
    out.sort(key=lambda s: s["date"], reverse=True)
    return out


def country_stories(country, stories, limit=8):
    """Headline matches on the country name (any region), plus
    region-tagged stories whose headline names the country. Both
    tests are headline tests; the page states the method."""
    names = ALIASES.get(country["slug"], [country["name"]])
    hits = []
    for s in stories:
        title = s["title"]
        if any(n.lower() in title.lower() for n in names):
            hits.append(s)
        if len(hits) >= limit:
            break
    return hits


def stories_html(country, stories):
    hits = country_stories(country, stories)
    if not hits:
        return ("<h2>Recent coverage</h2>\n<p>No recent stories name "
                f"{esc(country['name'])} in the headline.</p>\n")
    rows = []
    for s in hits:
        rows.append(
            f'<p class="gm-story"><span class="gm-story-date">'
            f'{esc(s["date"])}</span> <a href="/stories/{esc(s["slug"])}/">'
            f'{esc(s["title"])}</a></p>')
    return ("<h2>Recent coverage</h2>\n"
            "<p class=\"gm-method\">Stories whose headline names this "
            "market, newest first.</p>\n" + "\n".join(rows) + "\n")


def vol_strip(vol):
    vix, move = vol.get("vix"), vol.get("move")
    implied = vol.get("implied_daily_pct")

    def item(label, row, suffix=""):
        if row is None:
            return (f'<div class="gm-strip-item"><span class="stat-label">'
                    f"{label}</span><span class=\"stat-value\">{BLANK}"
                    "</span></div>")
        return (f'<div class="gm-strip-item"><span class="stat-label">'
                f"{label}</span><span class=\"stat-value\">"
                f"{row['value']:.2f}{suffix}</span>"
                f'<span class="gm-sub">1d {fmt_pct(row["change_1d"])}'
                f" / 1w {fmt_pct(row['change_1w'])}</span></div>")

    implied_html = (
        f'<div class="gm-strip-item"><span class="stat-label">Implied '
        f'daily move</span><span class="stat-value">'
        f'{implied:.2f}%</span><span class="gm-sub">S&amp;P 500, '
        f"one-day</span></div>" if implied is not None else
        f'<div class="gm-strip-item"><span class="stat-label">Implied '
        f'daily move</span><span class="stat-value">{BLANK}</span></div>')
    return ('<div class="gm-strip">\n'
            + item("VIX", vix) + "\n"
            + item("MOVE", move) + "\n"
            + implied_html + "\n</div>\n"
            '<p class="gm-note">Implied daily move: VIX divided by 16, '
            "the market's priced one-day swing in the S&amp;P 500.</p>\n")


def movers(countries):
    eq = [c for c in countries if c.get("index")]
    eq.sort(key=lambda c: abs(c["index"]["change_1d"]), reverse=True)
    yd = [c for c in countries
          if (c.get("yields", {}).get("y10") or {}).get("change_1d")
          is not None]
    yd.sort(key=lambda c: abs(c["yields"]["y10"]["change_1d"]),
            reverse=True)

    def table(title, rows):
        body = "".join(rows)
        return (f'<div class="gm-mover"><h3>{title}</h3>'
                f'<table class="market-table"><tbody>{body}</tbody>'
                "</table></div>")

    eq_rows = [
        f'<tr><td><a href="/markets/{c["slug"]}/">{esc(c["name"])}</a>'
        f'<span class="gm-sub-inline"> {esc(c["index"]["label"])}</span>'
        f'</td><td class="num" data-v="{c["index"]["change_1d"]}">'
        f'{fmt_pct(c["index"]["change_1d"])}</td></tr>'
        for c in eq[:3]]
    yd_rows = [
        f'<tr><td><a href="/markets/{c["slug"]}/">{esc(c["name"])}</a>'
        f'<span class="gm-sub-inline"> 10Y</span></td>'
        f'<td class="num" data-v="{c["yields"]["y10"]["change_1d"]}">'
        f'{fmt_bp(c["yields"]["y10"]["change_1d"])} bp</td></tr>'
        for c in yd[:3]]
    return ('<div class="gm-movers">\n'
            + table("Biggest equity moves today", eq_rows) + "\n"
            + table("Biggest 10Y yield moves today", yd_rows)
            + "\n</div>\n")


EQ_COLS = [("Country", 150, 90), ("Index", 170, 90),
           ("Last", 90, 60, 1), ("1d %", 66, 50, 1), ("1w %", 66, 50, 1),
           ("Country ETF", 190, 100), ("ETF last $", 84, 60, 1),
           ("ETF 1d %", 72, 54, 1), ("Currency", 86, 60),
           ("Rate", 92, 60, 1), ("FX 1d %", 70, 54, 1)]
BOND_COLS = [("Country", 170, 100), ("2Y %", 80, 56, 1),
             ("10Y %", 80, 56, 1), ("30Y %", 80, 56, 1),
             ("10Y 1d, bp", 92, 62, 1), ("Spread to UST, bp", 130, 80, 1)]


def eq_rows(countries):
    rows = []
    for c in countries:
        idx, etf, fx = c.get("index"), c.get("etf"), c.get("fx")
        cells = [f'<td data-v="{esc(c["name"])}"><a href="/markets/'
                 f'{c["slug"]}/">{esc(c["name"])}</a></td>']
        if idx:
            cells.append(f'<td data-v="{esc(idx["label"])}">'
                         f'{esc(idx["label"])}</td>')
            cells.append(f'<td class="num" data-v="{idx["value"]}">'
                         f'{fmt_num(idx["value"])}</td>')
            cells.append(f'<td class="num" data-v="{idx["change_1d"]}">'
                         f'{fmt_pct(idx["change_1d"])}</td>')
            cells.append(f'<td class="num" data-v="{idx["change_1w"]}">'
                         f'{fmt_pct(idx["change_1w"])}</td>')
        else:
            cells += ["<td>" + BLANK + "</td>"] * 4
        if etf:
            cells.append(f'<td data-v="{esc(etf["label"])}">'
                         f'{esc(etf["label"])}</td>')
            cells.append(f'<td class="num" data-v="{etf["value"]}">'
                         f'{etf["value"]:,.2f}</td>')
            cells.append(f'<td class="num" data-v="{etf["change_1d"]}">'
                         f'{fmt_pct(etf["change_1d"])}</td>')
        else:
            cells += ["<td>" + BLANK + "</td>"] * 3
        if fx:
            cells.append(f'<td data-v="{esc(fx["label"])}">'
                         f'{esc(fx["label"])}</td>')
            cells.append(f'<td class="num" data-v="{fx["value"]}">'
                         f'{fmt_num(fx["value"])}</td>')
            cells.append(f'<td class="num" data-v="{fx["change_1d"]}">'
                         f'{fmt_pct(fx["change_1d"])}</td>')
        else:
            cells += ["<td>" + BLANK + "</td>"] * 3
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return rows


def bond_rows(countries, us10):
    rows = []
    for c in countries:
        y = c.get("yields", {})

        def ycell(tenor):
            row = y.get(tenor)
            if not row:
                return "<td class=\"num\">" + BLANK + "</td>"
            return (f'<td class="num" data-v="{row["value"]}">'
                    f'{row["value"]:.2f}</td>')

        cells = [f'<td data-v="{esc(c["name"])}"><a href="/markets/'
                 f'{c["slug"]}/">{esc(c["name"])}</a></td>',
                 ycell("y2"), ycell("y10"), ycell("y30")]
        y10 = y.get("y10")
        if y10 and y10.get("change_1d") is not None:
            cells.append(f'<td class="num" data-v="{y10["change_1d"]}">'
                         f'{fmt_bp(y10["change_1d"])}</td>')
        else:
            cells.append("<td class=\"num\">" + BLANK + "</td>")
        if y10 and us10 is not None and c["slug"] != "united-states":
            spread = round((y10["value"] - us10) * 100)
            cells.append(f'<td class="num" data-v="{spread}">'
                         f"{spread:+d}</td>")
        else:
            cells.append("<td class=\"num\">" + BLANK + "</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return rows


def landing(data, updated_label):
    countries = data["countries"]
    by_group = {g: [c for c in countries if c["group"] == g]
                for g, _ in GROUPS}
    us = next((c for c in countries if c["slug"] == "united-states"),
              None)
    us10 = (us.get("yields", {}).get("y10", {}) or {}).get("value") \
        if us else None
    body = [f'<p class="market-table-updated">Updated as of '
            f"{updated_label} ET - refreshed hourly</p>\n"]
    body.append(vol_strip(data.get("volatility", {})))
    body.append(movers(countries))
    body.append("<h2>Equities and currencies</h2>\n")
    body.append('<p class="gm-method">FX 1d is the currency\'s own move '
                "against the US dollar: a positive figure means the "
                "currency strengthened.</p>\n")
    for g, label in GROUPS:
        body.append(f"<h3>{label}</h3>\n")
        body.append(reset_btn(f"gm-eq-{g}") + "\n")
        body.append('<div class="market-table-scroll">'
                    + bw_open(f"gm-eq-{g}", EQ_COLS, engine_sort=True))
        body.append("<tbody>\n" + "\n".join(eq_rows(by_group[g]))
                    + "\n</tbody></table></div>\n")
    body.append("<h2>Sovereign bonds</h2>\n")
    body.append('<p class="gm-method">Benchmark yields in percent. '
                "The spread is the 10Y yield less the US 10Y, in basis "
                "points. A blank cell means no reliable free ticker "
                "exists for that market and tenor; it is not a "
                "zero.</p>\n")
    for g, label in GROUPS:
        body.append(f"<h3>{label}</h3>\n")
        body.append(reset_btn(f"gm-bd-{g}") + "\n")
        body.append('<div class="market-table-scroll">'
                    + bw_open(f"gm-bd-{g}", BOND_COLS, engine_sort=True))
        body.append("<tbody>\n" + "\n".join(bond_rows(by_group[g], us10))
                    + "\n</tbody></table></div>\n")
    body.append('<p class="data-vintage">Sources: Yahoo Finance '
                "(indices, ETFs, currencies, VIX, US 30Y) and "
                "Stooq (benchmark sovereign yields). Country ETFs are "
                "the main US-listed funds. Yields refresh with the "
                "hourly market tables; benchmark yield series are "
                "end-of-day at source. MOVE is not shown: the Yahoo "
                "symbol ^MOVE resolves on the reachable feed to a "
                "Northern Trust iBoxx index, not the ICE BofA MOVE "
                "Index, and no other free feed carries it under its "
                "own name.</p>\n")
    body.append(TABLE_ENGINE_JS)
    lede = ("Benchmark equity indices, US-listed country ETFs, "
            "currencies and sovereign yields for "
            f"{len(countries)} markets, refreshed hourly.")
    return frontmatter("Global Markets", lede,
                       f"Market data as of {updated_label} ET") \
        + "".join(body)


def country_page(c, data, stories, updated_label):
    idx, etf, fx = c.get("index"), c.get("etf"), c.get("fx")
    y = c.get("yields", {})
    body = [f'<p class="market-table-updated">Updated as of '
            f"{updated_label} ET - refreshed hourly</p>\n"]
    rows = []
    for label, row, unit in (
            (idx["label"] + " (index)" if idx else None, idx, ""),
            (etf["label"] if etf else None, etf, "$"),
            (fx["label"] if fx else None, fx, "")):
        if row is None:
            continue
        rows.append(
            f'<tr><td>{esc(label)}</td><td class="num">'
            f'{unit}{fmt_num(row["value"])}</td>'
            f'<td class="num">{fmt_pct(row["change_1d"])}</td>'
            f'<td class="num">{fmt_pct(row["change_1w"])}</td>'
            f"<td>{spark_svg(row)}</td></tr>")
    body.append('<table class="market-table"><thead><tr><th>Instrument'
                "</th><th>Last</th><th>1d</th><th>1w</th><th>30-day "
                "trend</th></tr></thead><tbody>\n"
                + "\n".join(rows) + "\n</tbody></table>\n")
    if y:
        yrows = []
        for tenor, label in (("y2", "2Y"), ("y10", "10Y"),
                             ("y30", "30Y")):
            row = y.get(tenor)
            if not row:
                continue
            yrows.append(
                f'<tr><td>{label} benchmark yield</td><td class="num">'
                f'{row["value"]:.2f} <span class="unit">%</span></td>'
                f'<td class="num">{fmt_bp(row["change_1d"])} '
                f'<span class="unit">bp</span></td>'
                f'<td class="num">{fmt_bp(row["change_1w"])} '
                f'<span class="unit">bp</span></td>'
                f"<td>{spark_svg(row)}</td></tr>")
        body.append("<h2>Sovereign yields</h2>\n")
        body.append('<table class="market-table"><thead><tr><th>Tenor'
                    "</th><th>Yield</th><th>1d</th><th>1w</th>"
                    "<th>30-day trend</th></tr></thead><tbody>\n"
                    + "\n".join(yrows) + "\n</tbody></table>\n")
    body.append(stories_html(c, stories))
    body.append('<p class="data-vintage">Sources: Yahoo Finance and '
                "Stooq. A missing row means no reliable free ticker "
                "exists for that instrument.</p>\n")
    lede = (f"Benchmark index, country ETF, currency and sovereign "
            f"yields for {c['name']}, refreshed hourly.")
    title = c["name"]
    return frontmatter(title, lede, f"{updated_label} ET") \
        + "".join(body)


def main():
    data = json.load(open(os.path.join(SITE, "data",
                                       "global_markets.json")))
    updated = datetime.datetime.fromisoformat(data["updated"])
    updated_label = updated.strftime("%b %-d, %-I:%M %p")
    stories = load_stories()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "_index.md"), "w") as f:
        f.write(landing(data, updated_label))
    print("wrote markets/_index.md")
    wanted = {"_index.md"}
    for c in data["countries"]:
        name = c["slug"] + ".md"
        wanted.add(name)
        with open(os.path.join(OUT, name), "w") as f:
            f.write(country_page(c, data, stories, updated_label))
    for stale in os.listdir(OUT):
        if stale.endswith(".md") and stale not in wanted:
            os.remove(os.path.join(OUT, stale))
    print("wrote", len(data["countries"]), "country pages")


if __name__ == "__main__":
    main()
