---
title: "Danfoss refrigeration controllers carry 9.8-rated flaw"
date: 2026-11-25T07:09:20-05:00
last_updated: 2026-11-25T07:09:20-05:00
beats: ["technology"]
regions: ["global", "europe"]
status: "story"
lede: "CISA warned on November 24 that Danfoss AK-SM 8xxA refrigeration controllers at or below version 5.4.0 carry a stack-based buffer overflow, rated 9.8, that an unauthenticated remote attacker can trigger over HTTP or HTTPS."
why_it_matters: "These controllers run refrigeration in commercial facilities worldwide, the flaw needs no authentication, and Danfoss has no patch yet, with the fix promised only in a future 5.5.x release."
featured: false
evidence_grade: "B"
sources:
  - title: "Danfoss AK-SM 8xxA Series, ICS Advisory ICSA-26-328-03"
    publisher: "US CISA"
    url: "https://www.cisa.gov/news-events/ics-advisories/icsa-26-328-03"
    published: "2026-11-24"
tags: []
data_as_of: "CISA ICS advisory ICSA-26-328-03, initial release November 24, 2026; the advisory is the source of record. CISA states no known public exploitation targeting this vulnerability had been reported to it at publication."
---

CISA published an industrial control systems advisory on November 24 for the Danfoss AK-SM 8xxA series of refrigeration controllers. A stack-based buffer overflow in an unauthenticated CGI handler allows a remote attacker to send specially crafted HTTP or HTTPS POST requests that corrupt memory, restart the webserver and, in CISA's assessment, could allow arbitrary code execution with webserver privileges. No authentication is required to exploit it.

The advisory rates the flaw 9.8 under CVSS version 3.1 and 9.3 under version 4.0, and lists all AK-SM 8xxA versions at or below 5.4.0 as affected. Danfoss, headquartered in Denmark, deploys the controllers in commercial facilities worldwide, where the AK-SM line manages refrigeration systems for food retail and cold storage.

There is no patch available. Danfoss will address the vulnerability in a future 5.5.x software release and will also remove the ability for users to disable Strict Mode in future releases. CISA reported no known public exploitation targeting the flaw at the time of publication, and its standing advice applies in the interim: keep control system devices off the public internet, place them behind firewalls isolated from business networks, and use updated virtual private networks where remote access is required.

The researcher Carlo Meijer of Midnight Blue reported the vulnerability to CISA. The advisory was one of three CISA industrial control systems advisories published the same day, alongside advisories for Schneider Electric EcoStruxure Power Build Rapsody software and AutomationDirect C-More EA9 programming software.
