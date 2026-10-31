---
title: "CISA adds two Ivanti Connect Secure flaws to exploited catalog"
date: 2026-10-31T07:06:33-04:00
last_updated: 2026-10-31T07:06:33-04:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "CISA added two Ivanti Connect Secure vulnerabilities to its Known Exploited Vulnerabilities Catalog on October 30, CVE-2026-111357, a missing authentication flaw for a critical function, and CVE-2026-118527, a generation of predictable numbers or identifiers flaw, both on evidence of active exploitation."
why_it_matters: "Connect Secure is a remote access gateway, so exploited authentication and predictability flaws in it sit on the path into corporate networks, and this is the third consecutive day of KEV additions touching widely deployed enterprise software."
featured: false
evidence_grade: "B"
sources:
  - title: "CISA adds two known exploited vulnerabilities to catalog"
    publisher: "US CISA"
    url: "https://www.cisa.gov/news-events/alerts/2026/10/30/cisa-adds-two-known-exploited-vulnerabilities-catalog"
    published: "2026-10-30"
tags: []
data_as_of: "Catalog additions dated October 30, 2026, read directly from the CISA alert, the primary source. Single primary source by construction: the catalog entry is CISA's own act, and the CVE identifiers and flaw types are as CISA lists them."
---

CISA has added two new vulnerabilities to its Known Exploited Vulnerabilities Catalog, both in Ivanti Connect Secure and both based on evidence of active exploitation. The additions, dated October 30, are CVE-2026-111357, described as a missing authentication for critical function vulnerability, and CVE-2026-118527, described as a generation of predictable numbers or identifiers vulnerability.

The catalog is the federal government's list of flaws known to be exploited in the wild, and CISA describes this class of vulnerability as a frequent attack vector posing significant risk to the federal enterprise. Under Binding Operational Directive 26-04, federal civilian agencies must prioritise rapid remediation of high risk KEV entries on publicly exposed assets that grant total control after exploitation, and must check whether threat actors compromised a system before a patch was applied. CISA encourages all organisations, not only federal agencies, to use the catalog the same way.

The product matters as much as the count. Connect Secure is a VPN and remote access gateway: an authentication bypass or predictable identifier weakness in it is not an application bug inside a network, it is a weakness in the door into the network. The additions also extend a run this week that has already put GitLab, Cisco firewall software, VMware and the Linux kernel into the catalog, a pattern of perimeter and platform software being exploited faster than patch cycles close it.
