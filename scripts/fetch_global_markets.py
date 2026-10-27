#!/usr/bin/env python3
"""Fetch global markets data for the Global Markets section.
Writes ~/workspace/news-site/data/global_markets.json for Hugo.
Sources: Yahoo Finance (indices, ETFs, FX, VIX/MOVE, US 30Y),
Stooq daily CSV (sovereign yields). No keys needed.

Per-field routes were censused 2026-10-26: Yahoo's chart API carries
no non-US sovereign yield indices; Stooq carries 10Y benchmark
yields for US, DE, GB, FR, JP, IT, ES, AU, CA, KR, IN, CN and a US
2Y. Fields with no reliable free ticker stay null (blank on the
page), never proxied.
"""
import csv
import io
import json
import os
import sys
import urllib.parse
import urllib.request

SITE_DIR = os.path.expanduser("~/workspace/news-site")
OUT = os.path.join(SITE_DIR, "data", "global_markets.json")

# slug, name, group, story region tag, index (label, yahoo symbol),
# etf (label, yahoo symbol), fx (quote label, yahoo symbol, invert)
#   fx invert=True: symbol is USD/XXX, so the currency's own move
#   against the dollar is the inverse of the pair's move.
# yields: tenor -> (source, symbol); source "stooq" or "yahoo".
COUNTRIES = [
    ("united-states", "United States", "americas", "north-america",
     ("S&P 500", "^GSPC"), ("SPDR S&P 500 (SPY)", "SPY"),
     None,
     {"y2": ("stooq", "2usy.b"), "y10": ("stooq", "10usy.b"),
      "y30": ("yahoo", "^TYX")}),
    ("canada", "Canada", "americas", "north-america",
     ("S&P/TSX Composite", "^GSPTSE"), ("iShares MSCI Canada (EWC)", "EWC"),
     ("USD/CAD", "CAD=X", True),
     {"y10": ("stooq", "10cay.b")}),
    ("brazil", "Brazil", "americas", "latin-america",
     ("Ibovespa", "^BVSP"), ("iShares MSCI Brazil (EWZ)", "EWZ"),
     ("USD/BRL", "BRL=X", True), {}),
    ("mexico", "Mexico", "americas", "latin-america",
     ("IPC", "^MXX"), ("iShares MSCI Mexico (EWW)", "EWW"),
     ("USD/MXN", "MXN=X", True), {}),
    ("united-kingdom", "United Kingdom", "europe", "europe",
     ("FTSE 100", "^FTSE"), ("iShares MSCI United Kingdom (EWU)", "EWU"),
     ("GBP/USD", "GBPUSD=X", False),
     {"y10": ("stooq", "10gby.b")}),
    ("france", "France", "europe", "europe",
     ("CAC 40", "^FCHI"), ("iShares MSCI France (EWQ)", "EWQ"),
     ("EUR/USD", "EURUSD=X", False),
     {"y10": ("stooq", "10fry.b")}),
    ("germany", "Germany", "europe", "europe",
     ("DAX", "^GDAXI"), ("iShares MSCI Germany (EWG)", "EWG"),
     ("EUR/USD", "EURUSD=X", False),
     {"y10": ("stooq", "10dey.b")}),
    ("eurozone", "Eurozone", "europe", "europe",
     ("EURO STOXX 50", "^STOXX50E"), ("SPDR EURO STOXX 50 (FEZ)", "FEZ"),
     ("EUR/USD", "EURUSD=X", False), {}),
    ("italy", "Italy", "europe", "europe",
     ("FTSE MIB", "FTSEMIB.MI"), ("iShares MSCI Italy (EWI)", "EWI"),
     ("EUR/USD", "EURUSD=X", False),
     {"y10": ("stooq", "10ity.b")}),
    ("spain", "Spain", "europe", "europe",
     ("IBEX 35", "^IBEX"), ("iShares MSCI Spain (EWP)", "EWP"),
     ("EUR/USD", "EURUSD=X", False),
     {"y10": ("stooq", "10esy.b")}),
    ("netherlands", "Netherlands", "europe", "europe",
     ("AEX", "^AEX"), ("iShares MSCI Netherlands (EWN)", "EWN"),
     ("EUR/USD", "EURUSD=X", False), {}),
    ("switzerland", "Switzerland", "europe", "europe",
     ("SMI", "^SSMI"), ("iShares MSCI Switzerland (EWL)", "EWL"),
     ("USD/CHF", "CHF=X", True),
     {"y10": ("stooq", "10chy.b")}),
    ("sweden", "Sweden", "europe", "europe",
     ("OMX Stockholm 30", "^OMX"), ("iShares MSCI Sweden (EWD)", "EWD"),
     ("USD/SEK", "SEK=X", True), {}),
    ("poland", "Poland", "europe", "europe",
     ("WIG20", "^WIG20"), ("iShares MSCI Poland (EPOL)", "EPOL"),
     ("USD/PLN", "PLN=X", True), {}),
    ("japan", "Japan", "asia-pacific", "asia-pacific",
     ("Nikkei 225", "^N225"), ("iShares MSCI Japan (EWJ)", "EWJ"),
     ("USD/JPY", "JPY=X", True),
     {"y10": ("stooq", "10jpy.b")}),
    ("china", "China", "asia-pacific", "asia-pacific",
     ("Shanghai Composite", "^SSEC"), ("iShares MSCI China (MCHI)", "MCHI"),
     ("USD/CNY", "CNY=X", True),
     {"y10": ("stooq", "10cny.b")}),
    ("hong-kong", "Hong Kong", "asia-pacific", "asia-pacific",
     ("Hang Seng", "^HSI"), ("iShares MSCI Hong Kong (EWH)", "EWH"),
     ("USD/HKD", "HKD=X", True), {}),
    ("india", "India", "asia-pacific", "asia-pacific",
     ("Nifty 50", "^NSEI"), ("iShares MSCI India (INDA)", "INDA"),
     ("USD/INR", "INR=X", True),
     {"y10": ("stooq", "10iny.b")}),
    ("south-korea", "South Korea", "asia-pacific", "asia-pacific",
     ("KOSPI", "^KS11"), ("iShares MSCI South Korea (EWY)", "EWY"),
     ("USD/KRW", "KRW=X", True),
     {"y10": ("stooq", "10kry.b")}),
    ("taiwan", "Taiwan", "asia-pacific", "asia-pacific",
     ("TAIEX", "^TWII"), ("iShares MSCI Taiwan (EWT)", "EWT"),
     ("USD/TWD", "TWD=X", True), {}),
    ("australia", "Australia", "asia-pacific", "asia-pacific",
     ("S&P/ASX 200", "^AXJO"), ("iShares MSCI Australia (EWA)", "EWA"),
     ("AUD/USD", "AUDUSD=X", False),
     {"y10": ("stooq", "10auy.b")}),
    ("singapore", "Singapore", "asia-pacific", "asia-pacific",
     ("Straits Times", "^STI"), ("iShares MSCI Singapore (EWS)", "EWS"),
     ("USD/SGD", "SGD=X", True), {}),
    ("indonesia", "Indonesia", "asia-pacific", "asia-pacific",
     ("Jakarta Composite", "^JKSE"), ("iShares MSCI Indonesia (EIDO)", "EIDO"),
     ("USD/IDR", "IDR=X", True), {}),
    ("turkey", "Turkey", "middle-east-africa", "middle-east",
     ("BIST 100", "^XU100"), ("iShares MSCI Turkey (TUR)", "TUR"),
     ("USD/TRY", "TRY=X", True), {}),
    ("south-africa", "South Africa", "middle-east-africa", "africa",
     ("FTSE/JSE All Share", "^JN0U.JO"),
     ("iShares MSCI South Africa (EZA)", "EZA"),
     ("USD/ZAR", "ZAR=X", True), {}),
    ("saudi-arabia", "Saudi Arabia", "middle-east-africa", "middle-east",
     ("TASI", "^TASI.SR"), ("iShares MSCI Saudi Arabia (KSA)", "KSA"),
     ("USD/SAR", "SAR=X", True), {}),
    ("united-arab-emirates", "United Arab Emirates",
     "middle-east-africa", "middle-east",
     ("DFM General", "^DFMGI"), ("iShares MSCI UAE (UAE)", "UAE"),
     ("USD/AED", "AED=X", True), {}),
]


def fetch_yahoo(symbol, want_name=None):
    """Chart closes from Yahoo. If want_name is given, the series is
    accepted only when the feed's own shortName contains it: ^MOVE
    on the reachable Yahoo mirror resolves to a Northern Trust
    iBoxx index, not the ICE BofA MOVE Index, and a mislabeled
    series is worse than a blank."""
    import time
    last_err = None
    for attempt in range(2):
        for host in ("query1", "query2"):
            url = (f"https://{host}.finance.yahoo.com/v8/finance/chart/"
                   + urllib.parse.quote(symbol, safe="")
                   + "?interval=1d&range=1mo")
            req = urllib.request.Request(url,
                                         headers={"User-Agent": "Mozilla/5.0"})
            try:
                d = json.load(urllib.request.urlopen(req, timeout=12))
                r = d["chart"]["result"][0]
                closes = [c for c in r["indicators"]["quote"][0]["close"]
                          if c]
                if closes:
                    if want_name:
                        nm = (r.get("meta", {}).get("shortName") or "")
                        if want_name not in nm or "iBoxx" in nm:
                            raise ValueError(
                                f"yahoo {symbol} resolves to {nm!r}, "
                                f"not {want_name}")
                    return closes
            except Exception as e:  # noqa: BLE001
                last_err = e
        time.sleep(3)
    raise ValueError(f"yahoo {symbol}: {last_err}")


def fetch_stooq(symbol):
    """Daily history CSV from Stooq; returns close list, oldest first."""
    import time
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    last_err = None
    for attempt in range(2):
        try:
            req = urllib.request.Request(url,
                                         headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=12).read().decode()
            rows = list(csv.DictReader(io.StringIO(raw)))
            closes = [float(r["Close"]) for r in rows if r.get("Close")]
            if closes:
                return closes
            last_err = ValueError(f"stooq {symbol}: no rows")
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(3)
    raise ValueError(str(last_err))


def _run(thunk):
    try:
        return True, thunk()
    except Exception as e:  # noqa: BLE001
        return False, e


def sparkline(values, w=96, h=28):
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


def pct_row(closes, decimals, bad_move=10.0, quiet=4.0):
    # The reachable Yahoo mirror occasionally appends a corrupted final bar
    # (observed 2026-10-26: Ibovespa and EWZ final closes 14-20% below the
    # prior close with a quiet series behind them, USD/BRL off 8%). If the
    # final move is extreme while the move into the previous point was
    # quiet, drop the final point once and compute from the rest.
    if len(closes) >= 3:
        last_move = (closes[-1] / closes[-2] - 1.0) * 100.0
        prior_move = (closes[-2] / closes[-3] - 1.0) * 100.0
        if abs(last_move) >= bad_move and abs(prior_move) <= quiet:
            closes = closes[:-1]
    if len(closes) < 6:
        raise ValueError("not enough data")
    last, prev, week = closes[-1], closes[-2], closes[-6]
    c1 = round((last / prev - 1) * 100, 2)
    cw = round((last / week - 1) * 100, 2)
    hist = [round(c, decimals) for c in closes[-30:]]
    return {"value": round(last, decimals), "change_1d": c1,
            "change_1w": cw, "change_unit": "%", "history": hist,
            "spark": sparkline(hist), "up_1d": c1 >= 0}


def yield_row(closes):
    if len(closes) >= 3:
        last_bp = (closes[-1] - closes[-2]) * 100.0
        prior_bp = (closes[-2] - closes[-3]) * 100.0
        if abs(last_bp) >= 150 and abs(prior_bp) <= 40:
            closes = closes[:-1]
    if len(closes) < 1:
        raise ValueError("not enough data")
    last = closes[-1]
    if len(closes) < 2:
        # Current value only (Stooq's China 10Y history file carries
        # a single row): publish the level, leave changes blank
        # rather than inventing them.
        return {"value": round(last, 2), "change_1d": None,
                "change_1w": None, "change_unit": "bp",
                "history": [round(last, 3)], "spark": "",
                "up_1d": True}
    prev = closes[-2]
    week = closes[-6] if len(closes) >= 6 else closes[0]
    c1 = round((last - prev) * 100, 1)
    cw = round((last - week) * 100, 1)
    hist = [round(c, 3) for c in closes[-30:]]
    return {"value": round(last, 2), "change_1d": c1, "change_1w": cw,
            "change_unit": "bp", "history": hist,
            "spark": sparkline(hist), "up_1d": c1 >= 0}


def main():
    from concurrent.futures import ThreadPoolExecutor
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/Toronto")
    import datetime
    out = {"updated": datetime.datetime.now(et).isoformat(),
           "volatility": {}, "countries": [], "errors": []}
    errors = out["errors"]

    jobs = []  # (country index or -1 for vol, field, label, thunk)

    def vol_job(field, thunk):
        jobs.append((-1, field, field, thunk))

    vol_job("vix", lambda: pct_row(fetch_yahoo("^VIX"), 2))
    vol_job("move", lambda: pct_row(
        fetch_yahoo("^MOVE", want_name="MOVE"), 2))

    for ci, (slug, name, group, region, index, etf, fx,
             yields) in enumerate(COUNTRIES):
        c = {"slug": slug, "name": name, "group": group,
             "region_tag": region, "index": None, "etf": None,
             "fx": None, "yields": {}}
        out["countries"].append(c)
        for key, spec in (("index", index), ("etf", etf)):
            label, sym = spec

            def make_pct(label=label, sym=sym):
                row = pct_row(fetch_yahoo(sym), 2)
                row["label"] = label
                row["symbol"] = sym
                return row
            jobs.append((ci, key, f"{name} {key} ({sym})", make_pct))
        if fx is not None:
            label, sym, invert = fx

            def make_fx(label=label, sym=sym, invert=invert):
                row = pct_row(fetch_yahoo(sym), 4, bad_move=5.0, quiet=2.0)
                if invert:
                    row["change_1d"] = round(-row["change_1d"], 2)
                    row["change_1w"] = round(-row["change_1w"], 2)
                    row["up_1d"] = row["change_1d"] >= 0
                row["label"] = label
                row["symbol"] = sym
                return row
            jobs.append((ci, "fx", f"{name} fx ({sym})", make_fx))
        for tenor, (source, sym) in yields.items():

            def make_yield(source=source, sym=sym):
                closes = (fetch_stooq(sym) if source == "stooq"
                          else fetch_yahoo(sym))
                row = yield_row(closes)
                row["source"] = source
                row["symbol"] = sym
                return row
            jobs.append((ci, f"y:{tenor}",
                         f"{name} {tenor} ({sym})", make_yield))

    attempted = len(jobs)
    succeeded = 0
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(lambda j: (j, _run(j[3])), jobs))
    # Serial retry pass for whatever the parallel phase missed:
    # Stooq rate-limits under parallel load, and the Yahoo mirror
    # drops symbols in waves that pass within minutes. Short-circuit
    # a source family after 4 consecutive network failures so a dead
    # host cannot stretch the pass past the hourly cadence.
    import time
    final = []
    net_fails = {"yahoo": 0, "stooq": 0}
    no_retry = bool(os.environ.get("GM_NO_RETRY"))
    for job, res in results:
        if res[0]:
            final.append((job, res))
            continue
        if no_retry:
            final.append((job, res))
            continue
        label = job[2]
        fam = "stooq" if "(10" in label or "(2u" in label or "(30" in label \
            else "yahoo"
        if net_fails[fam] >= 4:
            final.append((job, res))
            continue
        time.sleep(1)
        retry = _run(job[3])
        if retry[0]:
            net_fails[fam] = 0
            final.append((job, retry))
        else:
            if "rows" not in str(retry[1]) and "404" not in str(retry[1]):
                net_fails[fam] += 1
            final.append((job, res))
    for (ci, field, label, _), (ok, val) in final:
        if not ok:
            errors.append(f"{label}: {val}")
            continue
        succeeded += 1
        if ci < 0:
            out["volatility"][field] = val
        elif field.startswith("y:"):
            out["countries"][ci]["yields"][field[2:]] = val
        else:
            out["countries"][ci][field] = val
    vix = out["volatility"].get("vix")
    out["volatility"]["implied_daily_pct"] = (
        round(vix["value"] / 16, 2) if vix else None)

    # Never overwrite the live file with a degraded fetch: if more
    # than a quarter of instruments failed, keep the previous file.
    if attempted and succeeded / attempted < 0.75:
        print(f"DEGRADED: {succeeded}/{attempted} instruments ok; "
              "keeping previous file", file=sys.stderr)
        for e in errors:
            print("FAIL", e, file=sys.stderr)
        sys.exit(2)
    tmp = OUT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, OUT)
    print(f"wrote {OUT}: {succeeded}/{attempted} instruments, "
          f"{len(errors)} errors")
    for e in errors:
        print("FAIL", e, file=sys.stderr)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
