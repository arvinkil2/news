#!/usr/bin/env python3
"""Fetch bot-blocked RSS feeds from GitHub Actions runners.

Each source below 403s the news VM's datacenter IP but serves real RSS to
other egress IPs. This script runs on GitHub's ubuntu runners every 2 hours,
saves each feed as XML under proxied-feeds/, and the workflow commits changes.
The VM poller reads them back via the GitHub contents API (github: URL scheme).

Never fails the job on a single bad feed: logs the status and keeps going.
"""
import sys
import urllib.request
import urllib.error
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

FEEDS = {
    "imf.xml": "https://www.imf.org/en/News/rss",
    "politico.xml": "https://www.politico.com/rss/politicopicks.xml",
    "usgs.xml": "https://www.usgs.gov/rss/news",
    "chathamhouse.xml": "https://www.chathamhouse.org/rss.xml",
    "iaea.xml": "https://www.iaea.org/newscenter/rss.xml",
    "spglobal.xml": "https://www.spglobal.com/commodityinsights/en/rss",
    "gao.xml": "https://www.gao.gov/rss/reports",
    "cftc-enforcement.xml": "https://www.cftc.gov/RSS/RSSENF/rssenf.xml",
}

OUT = Path(__file__).resolve().parents[2] / "proxied-feeds"


def looks_like_feed(raw: bytes) -> bool:
    head = raw[:500].lower()
    return b"<rss" in head or b"<feed" in head or b"<rdf" in head


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ok, failed = 0, []
    for name, url in FEEDS.items():
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read(4_000_000)
            if not raw or not looks_like_feed(raw):
                raise ValueError(f"not a feed (got {len(raw)} bytes, no rss/feed tag)")
            (OUT / name).write_bytes(raw)
            print(f"OK   {name} ({len(raw)} bytes)")
            ok += 1
        except Exception as e:
            print(f"FAIL {name}: {type(e).__name__} {str(e)[:150]}")
            failed.append(name)
    print(f"\n{ok} ok, {len(failed)} failed: {failed if failed else '-'}")
    return 0  # never fail the workflow on feed issues


if __name__ == "__main__":
    sys.exit(main())
