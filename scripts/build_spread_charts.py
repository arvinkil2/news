#!/usr/bin/env python3
"""Generate inline SVG charts for the macro spreads page from the
sovereign-spreads research dataset. No PNG screenshots.
"""
import csv, os

SRC = os.path.expanduser("~/workspace/sovereign-spreads/data")
PANEL = os.path.join(SRC, "panel_10y_monthly.csv")
SPREADS = os.path.join(SRC, "spreads_bp_monthly.csv")

COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b", "#e377c2"]

def load_csv(path):
    with open(path) as f:
        r = csv.DictReader(f)
        rows = list(r)
    dates = [row["date"][:7] for row in rows]
    series = {}
    for col in r.fieldnames[1:]:
        vals = []
        for row in rows:
            v = row[col].strip()
            vals.append(float(v) if v else None)
        series[col] = vals
    return dates, series

def svg_line(dates, series_dict, title, ylabel, width=900, height=320):
    """Multi-series line chart as inline SVG."""
    pad_l, pad_r, pad_t, pad_b = 56, 16, 28, 36
    iw, ih = width - pad_l - pad_r, height - pad_t - pad_b
    allv = [v for s in series_dict.values() for v in s if v is not None]
    lo, hi = min(allv), max(allv)
    span = (hi - lo) or 1
    lo -= span * 0.05; hi += span * 0.05; span = hi - lo
    n = len(dates)
    def x(i): return pad_l + i / max(n - 1, 1) * iw
    def y(v): return pad_t + ih - (v - lo) / span * ih
    # y ticks
    ticks = 5
    grid = ""
    for t in range(ticks + 1):
        v = lo + span * t / ticks
        yy = y(v)
        grid += f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{width-pad_r}" y2="{yy:.1f}" stroke="#e5e5e5" stroke-width="1"/>'
        grid += f'<text x="{pad_l-8}" y="{yy+4:.1f}" text-anchor="end" font-size="11" fill="#666">{v:.0f}</text>'
    # x labels: every ~3 years
    xlabels = ""
    step = max(1, n // 8)
    for i in range(0, n, step):
        xlabels += f'<text x="{x(i):.1f}" y="{height-10}" text-anchor="middle" font-size="11" fill="#666">{dates[i][:4]}</text>'
    paths = ""
    for idx, (name, vals) in enumerate(series_dict.items()):
        pts = []
        started = False
        d = ""
        for i, v in enumerate(vals):
            if v is None:
                started = False
                continue
            cmd = "M" if not started else "L"
            d += f"{cmd}{x(i):.1f},{y(v):.1f} "
            started = True
        color = COLORS[idx % len(COLORS)]
        paths += f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.8"/>'
    legend = ""
    lx = pad_l
    for idx, name in enumerate(series_dict.keys()):
        color = COLORS[idx % len(COLORS)]
        legend += f'<rect x="{lx}" y="6" width="14" height="10" fill="{color}"/><text x="{lx+18}" y="15" font-size="12" fill="#333">{name}</text>'
        lx += 18 + len(name) * 7 + 22
    return (
        f'<svg viewBox="0 0 {width} {height}" class="macro-chart" role="img" aria-label="{title}">'
        f'<text x="{pad_l}" y="18" font-size="14" font-weight="600" fill="#111">{title}</text>'
        f"{grid}{xlabels}{paths}{legend}"
        f'<text x="14" y="{pad_t + ih/2}" font-size="11" fill="#666" transform="rotate(-90 14 {pad_t + ih/2})" text-anchor="middle">{ylabel}</text>'
        "</svg>"
    )

def svg_bars(items, title, xlabel, width=900, height=300):
    """Horizontal bar chart as inline SVG. items: [(label, value)]."""
    pad_l, pad_r, pad_t, pad_b = 130, 60, 34, 30
    iw, ih = width - pad_l - pad_r, height - pad_t - pad_b
    vals = [v for _, v in items]
    mx = max(abs(v) for v in vals) or 1
    bh = ih / len(items)
    zero_x = pad_l + iw / 2
    scale = (iw / 2) / mx
    bars = ""
    for i, (label, v) in enumerate(items):
        yc = pad_t + i * bh + bh / 2
        w = abs(v) * scale
        x0 = zero_x if v >= 0 else zero_x - w
        color = "#1a7f37" if v >= 0 else "#b42318"
        bars += f'<rect x="{x0:.1f}" y="{yc - bh*0.32:.1f}" width="{w:.1f}" height="{bh*0.64:.1f}" fill="{color}" rx="2"/>'
        bars += f'<text x="{pad_l - 8}" y="{yc + 4:.1f}" text-anchor="end" font-size="12" fill="#333">{label}</text>'
        lx = x0 + w + 6 if v >= 0 else x0 - 6
        anchor = "start" if v >= 0 else "end"
        bars += f'<text x="{lx:.1f}" y="{yc + 4:.1f}" text-anchor="{anchor}" font-size="11" fill="#555">{v:+.0f}</text>'
    bars += f'<line x1="{zero_x:.1f}" y1="{pad_t}" x2="{zero_x:.1f}" y2="{pad_t + ih}" stroke="#999" stroke-width="1"/>'
    return (
        f'<svg viewBox="0 0 {width} {height}" class="macro-chart" role="img" aria-label="{title}">'
        f'<text x="{pad_l}" y="20" font-size="14" font-weight="600" fill="#111">{title}</text>'
        f"{bars}"
        f'<text x="{zero_x:.1f}" y="{height - 8}" text-anchor="middle" font-size="11" fill="#666">{xlabel}</text>'
        "</svg>"
    )

def main():
    dates, panel = load_csv(PANEL)
    _, spreads = load_csv(SPREADS)
    out = os.path.expanduser("~/workspace/news-site/data/macro/spread_charts.json")
    charts = {}
    # Europe spreads vs Bund
    eu = {k: spreads[k] for k in ["FR", "IT", "ES", "GB", "BE", "PL"] if k in spreads}
    charts["europe"] = svg_line(dates, eu, "Sovereign 10Y spreads vs German Bund", "bp")
    # Benchmark yields
    bench = {"United States": panel["US"], "Germany": panel["DE"], "Japan": panel["JP"]}
    charts["benchmarks"] = svg_line(dates, bench, "10-year benchmark yields", "%")
    # 12m change bars (from latest spreads.json)
    import json
    s = json.load(open(os.path.expanduser("~/workspace/news-site/data/macro/spreads.json")))
    movers = sorted(
        [(c["name"], c["change_12m_bp"]) for c in s["countries"] if c["code"] != c.get("benchmark_code", "")],
        key=lambda t: t[1],
    )
    charts["movers12m"] = svg_bars(movers, "12-month spread change", "basis points")
    json.dump(charts, open(out, "w"))
    print("wrote", out, "keys:", list(charts.keys()))

if __name__ == "__main__":
    main()
