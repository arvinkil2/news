#!/usr/bin/env python3
"""Fetch daily market data for the news site tables.
Writes ~/workspace/news-site/data/market_tables.json for Hugo.
Sources: Yahoo Finance (no key needed).
"""
import json, urllib.request, urllib.parse, datetime, os, sys

SITE_DIR = os.path.expanduser("~/workspace/news-site")
OUT = os.path.join(SITE_DIR, "data", "market_tables.json")

INSTRUMENTS = {
    "commodities": [
        ("Brent crude", "BZ=F", "$/bbl", 2),
        ("WTI crude", "CL=F", "$/bbl", 2),
        ("Natural gas", "NG=F", "$/mmBtu", 2),
        ("Gold", "GC=F", "$/oz", 1),
        ("Silver", "SI=F", "$/oz", 2),
        ("Copper", "HG=F", "$/lb", 2),
        ("Wheat", "ZW=F", "¢/bu", 1),
        ("Corn", "ZC=F", "¢/bu", 1),
        ("Soybeans", "ZS=F", "¢/bu", 1),
        ("Dry bulk freight", "BDRY", "$", 2),
        ("Tanker freight", "BWET", "$", 2),
    ],
    "rates": [
        ("US 5Y", "^FVX", "%", 2, True),
        ("US 10Y", "^TNX", "%", 2, True),
        ("US 30Y", "^TYX", "%", 2, True),
        ("Dollar index", "DX-Y.NYB", "idx", 2),
        ("EUR/USD", "EURUSD=X", "", 4),
        ("USD/JPY", "JPY=X", "", 2),
    ],
    "mining": [
        ("Gold miners", "GDX", "$", 2),
        ("Silver miners", "SIL", "$", 2),
        ("Copper miners", "COPX", "$", 2),
        ("Uranium miners", "URA", "$", 2),
        ("Lithium & battery", "LIT", "$", 2),
        ("Rare earth miners", "REMX", "$", 2),
        ("BHP", "BHP", "$", 2),
        ("Rio Tinto", "RIO", "$", 2),
    ],
}

def fetch(symbol):
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           + urllib.parse.quote(symbol, safe="") + "?interval=1d&range=1mo")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=20))
    r = d["chart"]["result"][0]
    closes = [c for c in r["indicators"]["quote"][0]["close"] if c]
    return closes

def sparkline(values, w=96, h=28):
    """Return SVG polyline points string for a sparkline."""
    if not values or len(values) < 2:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    pts = []
    n = len(values)
    for i, v in enumerate(values):
        x = round(i / (n - 1) * w, 1)
        y = round(h - (v - lo) / span * (h - 4) - 2, 1)
        pts.append(f"{x},{y}")
    return " ".join(pts)

def build_row(name, symbol, unit, decimals, is_yield=False):
    closes = fetch(symbol)
    if len(closes) < 6:
        raise ValueError(f"not enough data for {symbol}")
    last, prev, week_ago = closes[-1], closes[-2], closes[-6]
    if is_yield:
        chg_1d = round((last - prev) * 100, 1)   # basis points
        chg_1w = round((last - week_ago) * 100, 1)
        chg_unit = "bp"
    else:
        chg_1d = round((last / prev - 1) * 100, 2)
        chg_1w = round((last / week_ago - 1) * 100, 2)
        chg_unit = "%"
    return {
        "name": name,
        "value": round(last, decimals),
        "unit": unit,
        "change_1d": chg_1d,
        "change_1w": chg_1w,
        "change_unit": chg_unit,
        "history": [round(c, decimals) for c in closes[-30:]],
        "spark": sparkline(closes[-30:]),
        "up_1d": chg_1d >= 0,
    }

def main():
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/Toronto")
    out = {"updated": datetime.datetime.now(et).isoformat()}
    for section in INSTRUMENTS:
        out[section] = []
    errors = []
    for section, items in INSTRUMENTS.items():
        for item in items:
            name, sym = item[0], item[1]
            try:
                out[section].append(build_row(*item))
                print(f"ok {name:12s} {out[section][-1]['value']}")
            except Exception as e:
                errors.append(f"{name}: {e}")
                print(f"FAIL {name}: {e}", file=sys.stderr)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {OUT}")
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
