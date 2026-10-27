---
title: "CISA lists PHP2Shell flaws as exploited, sets October 29 deadline"
date: 2026-10-27T07:00:00-04:00
last_updated: 2026-10-27T07:14:47-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "CISA added the two PHP2Shell vulnerabilities, CVE-2026-109618 and CVE-2026-109619, to its Known Exploited Vulnerabilities catalog on October 26 and set a remediation deadline of October 29 for federal civilian agencies."
why_it_matters: "KEV listing converts a disclosure story this site has followed since October 21 into a confirmed exploitation story with a three day federal clock: any organisation running unpatched PHP on web facing servers now has the government's own deadline as its benchmark."
featured: false
evidence_grade: "B"
sources:
  - title: "CISA Adds Two Known Exploited Vulnerability to Catalog"
    publisher: "U.S. Cybersecurity and Infrastructure Security Agency (CISA)"
    url: "https://www.cisa.gov/news-events/alerts/2026/10/26/cisa-adds-two-known-exploited-vulnerability-catalog"
    published: "2026-10-26"
  - title: "CVE-2026-109618 and CVE-2026-109619: Critical Unauthenticated Remote Code Execution in PHP"
    publisher: "Rapid7"
    url: "https://www.rapid7.com/blog/post/etr-cve-2026-109618-and-cve-2026-109619-critical-unauthenticated-remote-code-execution-in-php/"
    published: "2026-10-26"
tags: []
data_as_of: "CISA catalog addition of October 26, 2026 (the agency alert page itself returned access denied in this run; the listing, due date and CVE identifiers are corroborated by Rapid7 and Tenable coverage of October 26). Fixed PHP releases were published October 21, 2026."
---

The PHP2Shell episode escalated on Monday from critical flaw to confirmed exploited flaw. The Cybersecurity and Infrastructure Security Agency added CVE-2026-109618 and CVE-2026-109619 to its Known Exploited Vulnerabilities catalog, on evidence of active exploitation, and set a remediation due date of October 29 for federal civilian executive branch agencies under Binding Operational Directive 26-04, which also requires agencies to check whether exposed systems were already compromised before or while patching.

The two flaws, rated 9.2 under CVSS 4.0 by the PHP Group, allow an unauthenticated attacker to run code on servers using PHP to answer web requests. One is a memory corruption error in out of memory handling that can leave request memory partly initialized; the other leaves internal request state surviving after its memory is freed. Apache with mod_php is rated the highest risk deployment. Fixed versions, PHP 8.5.12, 8.4.27, 8.3.36 and 8.2.35, were released on October 21, and branches at 8.1 and earlier get no further project patches.

This site has covered the disclosure argument around these flaws since October 21, including The Register's warning that the episode is a lesson in disclosure practice. The KEV listing ends the argument about urgency: CISA does not list vulnerabilities on potential, and its updated alert directs organisations that cannot update immediately, or that still run unsupported versions, to take PHP based systems offline until they can be patched.

For technology teams the operational point is the calendar. A three day federal window, ending the same day Amazon and Sandisk report and a day after the Federal Reserve decision, is now the reference deadline for every private operator running the same stack, and Rapid7's advice is to treat the current difficulty of reliable exploitation as a window to patch rather than a reason to delay.
