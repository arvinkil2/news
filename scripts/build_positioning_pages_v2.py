#!/usr/bin/env python3
"""Positioning section builder: DISABLED 2026-11-04.

The Positioning section of news.kilambi.com was removed at Arvin's
direct order on 2026-11-04. The pages and their navigation entries are
gone from the site; the underlying CFTC/positioning data collection
continues untouched. This stub exists so the daily positioning-pages
refresh job, whose body still invokes this script with --if-changed,
ends quietly with NOCHANGE and never recreates the section.

The full builder (5,490 lines, v2 showcase build of 2026-10-28) is
preserved alongside as build_positioning_pages.py.bak-20261104-removed.
"""
import sys

print("NOCHANGE")
sys.exit(0)
