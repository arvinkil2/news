---
title: "CISA urges urgent patch for exploited Ivanti VPN flaw"
date: 2026-10-13T19:47:08-04:00
last_updated: 2026-10-13T19:47:08-04:00
beats: ["technology"]
regions: ["global"]
status: "story"
developing: true
update_bump: true
lede: "CISA added a zero-day authentication bypass in Ivanti Connect Secure, CVE-2026-104935, to its Known Exploited Vulnerabilities catalog on October 13 and urged organisations to update affected appliances immediately."
why_it_matters: "Connect Secure gateways sit at the edge of corporate networks, and CISA says attackers are already using the flaw for credential theft and data exfiltration, with in-memory commands that the vendor's own integrity checker may miss."
featured: false
evidence_grade: "B"
sources:
  - title: "CISA Urges Patching Newly Exploited Vulnerability in Ivanti Connect Secure"
    publisher: "CISA"
    url: "https://www.cisa.gov/news-events/alerts/2026/10/13/cisa-urges-patching-newly-exploited-vulnerability-ivanti-connect-secure"
    published: "2026-10-13"
tags: []
data_as_of: "Tuesday, October 13, 2026, evening. CISA alert opened in full at cisa.gov. Developing item, 2 to 3 sentences by design."
---

CISA said on October 13 that attackers are exploiting a zero-day authentication bypass, CVE-2026-104935, in Ivanti Connect Secure versions 25.1.1.1 and prior, 25.1.2.2 and prior, and 22.8R2.4 and prior, allowing remote unauthenticated execution of arbitrary commands for credential theft and data exfiltration. The agency added the flaw to its Known Exploited Vulnerabilities catalog the same day and urged organisations to update to the latest version at once.

CISA warned that suspected compromises need network and memory forensics, because the commands run in memory and Ivanti's Integrity Checker Tool may not detect the exploitation, and it set out recovery steps that include a factory reset, an upgrade, and resetting passwords, certificates and API keys.
