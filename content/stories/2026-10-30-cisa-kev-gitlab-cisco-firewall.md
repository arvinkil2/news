---
title: "CISA adds GitLab and Cisco firewall flaws to exploited catalog"
date: 2026-10-30T07:07:10-04:00
last_updated: 2026-10-30T07:07:10-04:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "CISA added two vulnerabilities to its Known Exploited Vulnerabilities Catalog on October 29, CVE-2026-97229 in GitLab Community and Enterprise editions and CVE-2026-76418 in Cisco Secure Firewall ASA and Secure FTD software, both on evidence of active exploitation."
why_it_matters: "The pair hits the code pipeline and the network perimeter in one day, extending a catalog run this week that has already reached hypervisors and the Linux kernel, and federal agencies must prioritise both under Binding Operational Directive 26-04."
featured: false
evidence_grade: "B"
sources:
  - title: "CISA adds two known exploited vulnerabilities to catalog"
    publisher: "US CISA"
    url: "https://www.cisa.gov/news-events/alerts/2026/10/29/cisa-adds-two-known-exploited-vulnerabilities-catalog"
    published: "2026-10-29"
tags: []
data_as_of: "Catalog additions dated October 29, 2026, read from the CISA alert in this run. Single issuing authority as source of record for its own catalog, hence grade B. Distinct from the October 28 VMware and Linux kernel additions covered yesterday."
---

CISA added two vulnerabilities to its Known Exploited Vulnerabilities Catalog on October 29, each on evidence of active exploitation. CVE-2026-97229 is an integer overflow or wraparound vulnerability in GitLab Community Edition and Enterprise Edition. CVE-2026-76418 is an unchecked return value leading to a null pointer dereference in Cisco Secure Firewall Adaptive Security Appliance software and Cisco Secure Firewall Threat Defense software.

The pairing is awkward for defenders. GitLab sits inside the software supply chain, where a compromised instance can reach source code, credentials and build pipelines. Cisco firewall software sits at the perimeter, where exploitation can hand an attacker the network edge itself. CISA describes these vulnerability classes as a frequent attack vector posing significant risk to the federal enterprise.

Under Binding Operational Directive 26-04, federal civilian agencies must prioritise rapid remediation of catalog vulnerabilities on publicly exposed assets that grant total control after exploitation, and must check whether threat actors compromised a system before a patch was applied. CISA encourages all organisations to adopt the same risk based approach.

This is the third catalog addition covered here this week, after the October 27 Adobe and Brotli entries and the October 28 VMware ESX and Linux kernel entries. The pattern across the week runs from applications through virtualisation and kernels to, now, the firewall and the code repository, which is most of the enterprise stack in four days.
