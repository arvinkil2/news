---
title: "CISA urges urgent patch for exploited Ivanti VPN flaw"
date: 2026-10-13T19:47:08-04:00
last_updated: 2026-10-15T07:04:48-04:00
beats: ["technology"]
regions: ["global"]
status: "story"
developing: true
update_bump: true
lede: "Ivanti released updates on Tuesday for the exploited Connect Secure authentication bypass, CVE-2026-104935, after Volexity confirmed in the wild attacks by a previously unknown actor, with a third privilege escalation flaw still awaiting a fix."
why_it_matters: "Connect Secure gateways sit at the edge of corporate networks, and CISA says attackers are already using the flaw for credential theft and data exfiltration, with in-memory commands that the vendor's own integrity checker may miss."
featured: false
evidence_grade: "B"
sources:
  - title: "CISA Urges Patching Newly Exploited Vulnerability in Ivanti Connect Secure"
    publisher: "CISA"
    url: "https://www.cisa.gov/news-events/alerts/2026/10/13/cisa-urges-patching-newly-exploited-vulnerability-ivanti-connect-secure"
    published: "2026-10-13"
  - title: "Ivanti patches Connect Secure zero-day after researchers confirm in-the-wild attacks"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/14/ivanti-patches-connect-secure-zero-day-after-researchers-confirm-in-the-wild-attacks/5303095"
    published: "2026-10-14"
tags: []
data_as_of: "Tuesday, October 13, 2026, evening. CISA alert opened in full at cisa.gov. Developing item, 2 to 3 sentences by design."
---

CISA said on October 13 that attackers are exploiting a zero-day authentication bypass, CVE-2026-104935, in Ivanti Connect Secure versions 25.1.1.1 and prior, 25.1.2.2 and prior, and 22.8R2.4 and prior, allowing remote unauthenticated execution of arbitrary commands for credential theft and data exfiltration. The agency added the flaw to its Known Exploited Vulnerabilities catalog the same day and urged organisations to update to the latest version at once.

CISA warned that suspected compromises need network and memory forensics, because the commands run in memory and Ivanti's Integrity Checker Tool may not detect the exploitation, and it set out recovery steps that include a factory reset, an upgrade, and resetting passwords, certificates and API keys.

**Update, October 15:** Ivanti released updates on Tuesday that address the authentication bypass and remote code execution stages of the attack chain. Volexity, which discovered the flaw, says the intrusions are the work of a previously unknown actor it now tracks as UTA0576, assessed as criminally motivated, with post exploitation activity focused on credential theft, data exfiltration, log tampering and network reconnaissance, using only commands available on the appliance rather than deployed malware or web shells. Volexity assesses with high confidence that the activity signalled preparation for lateral movement. A third vulnerability in the chain, allowing privilege escalation, is separate from CVE-2026-104935 and Ivanti plans to publish a fix in the coming weeks, so patched systems are not yet fully closed. Ivanti said a portion of the vulnerability had been identified and patched in the July 25.1.3.0 update, and attackers began exploiting the remaining exposure before backporting was complete. This is the third year running in which Connect Secure has faced exploited undisclosed flaws.
