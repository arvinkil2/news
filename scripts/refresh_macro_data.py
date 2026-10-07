#!/usr/bin/env python3
"""Refresh all three Macro page datasets: spreads, central banks, economies snapshot.

Usage: python3 refresh_macro_data.py [--skip-snapshot]

1. spreads.json        Rebuilt from the static research dataset
                       ~/workspace/sovereign-spreads/data/{panel_10y_monthly,spreads_bp_monthly}.csv
                       (FRED OECD-harmonized 10Y yields, Jan 2006 - Aug 2026).
                       LIVE REFRESH BLOCKED: no FRED API key exists (checked env and
                       connected skills 2026-10-07). When a key is available, pull the 17
                       FRED OECD-harmonized series listed in sovereign-spreads/data/countries.txt
                       and regenerate the panel CSVs.
2. central_banks.json  Manual table (policy rates verified 2026-10-07 against official
                       announcements). This step re-validates schema and prints the
                       re-verification checklist; rates and meeting dates CANNOT be refreshed
                       automatically and must be re-checked by hand after each decision.
3. snapshot.json       Live pull via build_snapshot.py (ElkassabgiData econdl:
                       IMF WEO annual backbone + OECD quarterly GDP where available).

Run: python3 refresh_macro_data.py
"""
import csv, datetime, json, os, subprocess, sys

DATA = os.path.expanduser("~/workspace/news-site/data/macro")
SRC = os.path.expanduser("~/workspace/sovereign-spreads/data")
TODAY = datetime.date.today().isoformat()

REGIONS = {
    "US": ("north-america", "US Treasury", "US"), "CA": ("north-america", "US Treasury", "US"),
    "MX": ("latin-america", "US Treasury", "US"), "CL": ("latin-america", "US Treasury", "US"),
    "DE": ("europe", "German Bund", "DE"), "GB": ("europe", "German Bund", "DE"),
    "FR": ("europe", "German Bund", "DE"), "IT": ("europe", "German Bund", "DE"),
    "ES": ("europe", "German Bund", "DE"), "PL": ("europe", "German Bund", "DE"),
    "BE": ("europe", "German Bund", "DE"), "CH": ("europe", "German Bund", "DE"),
    "JP": ("asia-pacific", "JGB", "JP"), "KR": ("asia-pacific", "JGB", "JP"),
    "AU": ("asia-pacific", "JGB", "JP"),
    "IL": ("middle-east", "US Treasury", "US"), "ZA": ("africa", "US Treasury", "US"),
}
NAMES = {"US": "United States", "CA": "Canada", "MX": "Mexico", "CL": "Chile",
         "DE": "Germany", "GB": "United Kingdom", "FR": "France", "IT": "Italy",
         "ES": "Spain", "PL": "Poland", "BE": "Belgium", "CH": "Switzerland",
         "JP": "Japan", "KR": "South Korea", "AU": "Australia", "IL": "Israel",
         "ZA": "South Africa"}


def refresh_spreads():
    panel = list(csv.DictReader(open(f"{SRC}/panel_10y_monthly.csv")))
    dt = panel[-1]["date"]
    countries = []
    for code, (region, bench_name, bench_code) in REGIONS.items():
        # last available observation for this country (CL/PL lag one month)
        rows = [r for r in panel if r[code] not in ("", None)]
        last, prev, yoy = rows[-1], rows[-2], rows[-13]
        y = float(last[code])
        # spread vs benchmark in the same month (IL/ZA computed vs US; the
        # dataset's spreads_bp_monthly.csv carries them as 0.0)
        spread = round((y - float(last[bench_code])) * 100)
        countries.append({
            "code": code, "name": NAMES[code], "region": region,
            "yield_10y": round(y, 2), "spread_bp": spread, "benchmark": bench_name,
            "change_1m_bp": round((y - float(prev[code])) * 100, 1),
            "change_12m_bp": round((y - float(yoy[code])) * 100, 1),
            "data_through": last["date"],
        })
    doc = {
        "title": "Sovereign 10-year yields and spreads",
        "data_through": dt,
        "source": "FRED, OECD harmonized 10-year government bond yields (monthly)",
        "refresh_note": ("Static vintage from KR-WP-2026-17 research dataset. "
                         "Live refresh blocked: no FRED API key."),
        "refreshed": TODAY,
        "countries": countries,
    }
    out = f"{DATA}/spreads.json"
    json.dump(doc, open(out, "w"), indent=1)
    print(f"spreads.json: rebuilt from static CSVs (data through {dt})")


def refresh_central_banks():
    path = f"{DATA}/central_banks.json"
    doc = json.load(open(path))
    required = ["bank", "bank_short", "country", "current_rate", "last_change",
                "policy_rate_name", "source", "verified"]
    for r in doc["rates"]:
        missing = [k for k in required if k not in r]
        assert not missing, f"{r.get('bank_short')}: missing {missing}"
    doc["last_refresh_check"] = TODAY
    doc["refresh_note"] = ("Manual table. Rates and next-meeting dates were hand-verified "
                           "2026-10-07 and CANNOT be refreshed automatically. Re-verify each "
                           "bank after its next decision; meeting dates must be confirmed against "
                           "official central-bank calendars, never guessed.")
    json.dump(doc, open(path, "w"), indent=1)
    print("central_banks.json: schema validated; MANUAL re-verification still required")
    print("  Re-verify after these upcoming decisions:")
    for r in doc["rates"]:
        nm = r.get("next_meeting") or r.get("next_meeting_verification", "?")
        print(f"    {r['bank_short']:6s} {r['current_rate']:>6}%  next: {nm}")


def refresh_snapshot():
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_snapshot.py")
    r = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=900)
    print(r.stdout[-1500:] if r.stdout else "")
    if r.returncode != 0:
        print("SNAPSHOT REFRESH FAILED:", r.stderr[-500:], file=sys.stderr)
        return False
    return True


def main():
    print(f"=== Macro data refresh ({TODAY}) ===")
    refresh_spreads()
    refresh_central_banks()
    if "--skip-snapshot" not in sys.argv:
        ok = refresh_snapshot()
        print("snapshot.json:", "live refresh OK" if ok else "FAILED")
    print("done.")


if __name__ == "__main__":
    main()
