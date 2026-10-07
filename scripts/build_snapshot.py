#!/usr/bin/env python3
"""Build ~/workspace/news-site/data/macro/snapshot.json for the Economies page (/macro/economies/).

Backbone: IMF World Economic Outlook (WEO) via ElkassabgiData econdl, annual series:
  NGDP_RPCH : real GDP growth, annual % change
  PCPIPCH   : inflation, average consumer prices, annual % change
  LUR       : unemployment rate, %
2025 = latest actual, 2026 = estimate, 2027+ = forecast.
Plus OECD quarterly real GDP y/y (oecd:GDP_GROWTH_YOY) where available for timeliness
(10 countries, through Q2 2026), as the latest quarterly read.

WEO updates twice yearly (April/October). Vintage inferred from data structure
(2025 complete as actual => October 2026 release); the library does not name the release.

Run: python3 build_snapshot.py
"""
import csv, json, os, subprocess

ECONDl = os.path.expanduser("~/workspace/skills/elkassabgidata/bin/econdl")
OUT = os.path.expanduser("~/workspace/news-site/data/macro/snapshot.json")
TMP = "/tmp/macro_snapshot_dl"

COUNTRIES = [
    ("US", "United States", "USA"), ("CA", "Canada", "CAN"), ("MX", "Mexico", "MEX"),
    ("CL", "Chile", "CHL"), ("DE", "Germany", "DEU"), ("GB", "United Kingdom", "GBR"),
    ("FR", "France", "FRA"), ("IT", "Italy", "ITA"), ("ES", "Spain", "ESP"),
    ("PL", "Poland", "POL"), ("BE", "Belgium", "BEL"), ("CH", "Switzerland", "CHE"),
    ("JP", "Japan", "JPN"), ("KR", "South Korea", "KOR"), ("AU", "Australia", "AUS"),
    ("IL", "Israel", "ISR"), ("ZA", "South Africa", "ZAF"),
    ("CN", "China", "CHN"), ("IN", "India", "IND"), ("BR", "Brazil", "BRA"),
]

OECD_GDP = {"USA", "CAN", "DEU", "ESP", "FRA", "GBR", "ITA", "JPN", "KOR", "AUS"}

WEO_SRC = "International Monetary Fund, World Economic Outlook (WEO). Retrieved from https://www.imf.org. Compiled and redistributed by the Elkassabgi Data Library."
OECD_SRC = "OECD Data Explorer, GDP real growth year-on-year (%, s.a.), quarterly"

INDICATORS = [
    ("gdp", "NGDP_RPCH", "Real GDP growth, annual % change"),
    ("inflation", "PCPIPCH", "Inflation, average consumer prices, annual % change"),
    ("unemployment", "LUR", "Unemployment rate, %"),
]


def fetch_series(series):
    os.makedirs(TMP, exist_ok=True)
    safe = series.replace(":", "_").replace(".", "_")[:120]
    out = os.path.join(TMP, safe + ".csv")
    if not os.path.exists(out):
        r = subprocess.run([ECONDl, "fetch", series, "--out", out],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(out):
            return {}
    vals = {}
    with open(out) as f:
        rows = [l for l in f if not l.startswith("#") and l.strip()]
    for row in csv.reader(rows[1:]):  # skip header series_id,obs_date,value
        if len(row) >= 3 and row[2].strip():
            try:
                vals[row[1][:4]] = (row[1], float(row[2]))
            except ValueError:
                continue
    return vals


def main():
    economies = []
    errors = []
    weo = {}
    for iso2, name, geo3 in COUNTRIES:
        e = {"country": name, "country_code": iso2}
        for short, code, label in INDICATORS:
            ns = f"imf_weo:{code}:{geo3}"
            if ns not in weo:
                try:
                    weo[ns] = fetch_series(ns)
                except Exception as ex:
                    errors.append((iso2, short, str(ex)[:150]))
                    weo[ns] = {}
            d = weo[ns]
            actual = d.get("2025", (None, None))[1]
            est = d.get("2026", (None, None))[1]
            fc = d.get("2027", (None, None))[1]
            e[short] = {
                "label": label,
                "actual_2025": round(actual, 1) if actual is not None else None,
                "estimate_2026": round(est, 1) if est is not None else None,
                "forecast_2027": round(fc, 1) if fc is not None else None,
                "source": WEO_SRC,
                "vintage": "IMF WEO October 2026 (inferred: 2025 is latest complete actual year; library metadata does not name the release)",
            }
            if actual is None:
                errors.append((iso2, short, "missing 2025 actual"))
        # Timely quarterly GDP where OECD has it
        if geo3 in OECD_GDP:
            q = fetch_series(f"oecd:GDP_GROWTH_YOY:{geo3}")
            if q:
                latest_y = max(q)
                qdate, qval = q[latest_y]
                qlabel = {"01": "Q1", "04": "Q2", "07": "Q3", "10": "Q4"}.get(qdate[5:7], qdate[:7])
                e["gdp_latest_quarter"] = {
                    "value": round(qval, 2),
                    "quarter": f"{latest_y} {qlabel}",
                    "source": OECD_SRC,
                    "note": "Latest quarterly y/y read; WEO annual above is the comparable cross-country series.",
                }
        economies.append(e)
        g = e["gdp"]
        print(f"{iso2}: gdp {g['actual_2025']}/{g['estimate_2026']} "
              f"infl {e['inflation']['actual_2025']}/{e['inflation']['estimate_2026']} "
              f"unemp {e['unemployment']['actual_2025']}/{e['unemployment']['estimate_2026']}")

    doc = {
        "page": "Economies",
        "url": "/macro/economies/",
        "updated": "2026-10-07",
        "refresh": "live",
        "method": ("Backbone: IMF World Economic Outlook annual series (NGDP_RPCH real GDP growth, "
                   "PCPIPCH average CPI inflation, LUR unemployment rate), pulled live via ElkassabgiData "
                   "econdl on 2026-10-07. 2025 = latest actual, 2026 = estimate, 2027 = forecast. "
                   "WEO publishes twice yearly (April/October). OECD quarterly real GDP y/y included where "
                   "available for timeliness (10 countries, through Q2 2026)."),
        "unit": "percent",
        "economies": economies,
        "fetch_errors": errors,
    }
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=1)
    print(f"\nwrote {OUT} ({len(economies)} economies, {len(errors)} errors)")


if __name__ == "__main__":
    main()
