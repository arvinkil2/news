#!/usr/bin/env python3
"""Build the three Macro pages from data/macro/*.json.
Writes content/macro/{spreads,central-banks,economies}.md with HTML tables.
Charts live in static/macro/.
"""
import json, os, datetime

SITE = os.path.expanduser("~/workspace/news-site")
DATA = os.path.join(SITE, "data", "macro")
OUT = os.path.join(SITE, "content", "macro")

REGION_LABEL = {
    "north-america": "North America", "latin-america": "Latin America",
    "europe": "Europe", "middle-east": "Middle East", "africa": "Africa",
    "asia-pacific": "Asia-Pacific",
}

def frontmatter(title, lede, vintage):
    return f"""---
title: "{title}"
lede: "{lede}"
data_as_of: "{vintage}"
---

"""

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

def main():
    os.makedirs(OUT, exist_ok=True)
    pages = {
        "spreads.md": spreads_page(),
        "central-banks.md": central_banks_page(),
        "economies.md": economies_page(),
    }
    for fn, content in pages.items():
        with open(os.path.join(OUT, fn), "w") as f:
            f.write(content)
        print("wrote", fn)

if __name__ == "__main__":
    main()
