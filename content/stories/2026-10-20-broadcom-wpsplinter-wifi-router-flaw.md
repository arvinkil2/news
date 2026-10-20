---
title: "Broadcom Wi-Fi flaw WPSplinter leaves older routers without fix"
date: 2026-10-20T07:27:43-04:00
last_updated: 2026-10-20T07:27:43-04:00
beats: ["technology"]
regions: ["europe", "global"]
status: "story"
lede: "Researcher Quentin Kaiser has disclosed WPSplinter, two flaws in Broadcom's Wi-Fi Protected Setup implementation dating to at least 2010 that let an attacker within range run code on a router and steal its password, with an estimated 1.56 million Belgian gateways alone potentially affected."
why_it_matters: "Kaiser's account says Broadcom knew in 2018, shipped a partial fix without public disclosure, and declined this year to assign a CVE, leaving owners of older eCos based chips with what he calls a forever day vulnerability."
featured: false
evidence_grade: "B"
sources:
  - title: "Broadcom Wi-Fi bug turns sweet 16, still lets strangers hijack your router"
    publisher: "The Register"
    url: "https://www.theregister.com/networks/2026/10/19/broadcom-wi-fi-bug-turns-sweet-16-still-lets-strangers-hijack-your-router/5303771"
    published: "2026-10-19"
  - title: "One parser, two bugs"
    publisher: "Quentin Kaiser"
    url: "https://quentinkaiser.be/security/2026/10/16/one-parser-two-bugs/"
    published: "2026-10-16"
tags: []
data_as_of: "The Register report of October 19, 2026, read in full, reporting Kaiser's disclosure of October 16, 2026. Affected device counts for Belgium are Kaiser's rough estimates as he presented them. Broadcom's position is as reported by The Register from its July responses to the researcher; the company declined to assign a CVE."
---

Security researcher Quentin Kaiser has disclosed two bugs, dubbed WPSplinter, in Broadcom's proprietary Wi-Fi Protected Setup implementation, dating back to at least 2010. Specially crafted WPS messages can corrupt a router's memory, letting someone within Wi-Fi range run their own code on the device without the network password and without the owner doing anything.

Kaiser demonstrated working exploits against routers supplied by Belgian providers Proximus and Orange, in one case running code on an ASKEY gateway, pulling its Wi-Fi password from memory and joining the network with the stolen credentials. He also found the flaw in Netgear and Technicolor routers supplied by VOO, and estimates about 850,000 Proximus gateways, 500,000 at VOO and 210,000 at Orange Belgium could be affected, 1.56 million in Belgium alone, while stressing the figures are rough. Broadcom Wi-Fi technology ships in dozens of manufacturers' products worldwide, so the global total could be considerably higher.

According to Kaiser, Broadcom knew about the vulnerability in 2018 and released a partial fix without publicly disclosing the problem, later recommending manufacturers move to the open source hostapd software. He reported the flaws again on July 18 and July 27 this year. Broadcom replied on July 28 that a patch was available, then declined to assign a CVE identifier. CERT/CC closed his case on August 4 because Broadcom is itself a CVE numbering authority and had declined to register the flaw. By October 15 none of the affected devices he identified had received a patch, he said.

The worst position belongs to routers on older eCos based Broadcom chips, which Kaiser calls a forever day with no fix expected. He reported no evidence of attacks in the wild.
