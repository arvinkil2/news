---
title: "CISA adds VMware ESX and Linux kernel flaws to exploited catalog"
date: 2026-10-29T07:15:10-04:00
last_updated: 2026-10-29T07:15:10-04:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "CISA added two vulnerabilities to its Known Exploited Vulnerabilities Catalog on October 28, a Broadcom VMware ESX insufficient logging flaw, CVE-2026-41709, and a Linux kernel missing initialisation flaw, CVE-2026-46300, both on evidence of active exploitation."
why_it_matters: "The VMware entry puts hypervisor logging under the federal remediation directive a day after the Adobe and Brotli additions, extending this week's catalog run from applications into the virtualisation and kernel layers."
featured: false
evidence_grade: "B"
sources:
  - title: "CISA Adds Two Known Exploited Vulnerabilities to Catalog"
    publisher: "US CISA"
    url: "https://www.cisa.gov/news-events/alerts/2026/10/28/cisa-adds-two-known-exploited-vulnerabilities-catalog"
    published: "2026-10-28"
tags: []
data_as_of: "Catalog additions dated October 28, 2026, read from the CISA alert in this run; these are different vulnerabilities from the October 27 Adobe Commerce and Brotli additions covered in yesterday's edition. Single primary source, the catalog itself, hence grade B."
---

CISA added two new vulnerabilities to its Known Exploited Vulnerabilities Catalog on October 28, based on evidence of active exploitation: CVE-2026-41709, a Broadcom VMware ESX insufficient logging vulnerability, and CVE-2026-46300, a Linux kernel missing initialisation of a variable vulnerability.

The catalog operates under Binding Operational Directive 26-04, which requires federal civilian agencies to prioritise rapid remediation of high risk vulnerabilities on publicly exposed assets that grant total control after exploitation, and to check whether threat actors compromised a system before a patch was applied. CISA encourages all organisations to adopt the same risk based approach.

The additions continue a dense week for the catalog. Yesterday's edition covered the October 27 additions, an Adobe Commerce and Magento file upload flaw and the Google Brotli flaw. The October 28 pair sits lower in the stack, in the hypervisor that hosts virtual machines and in the Linux kernel beneath them, which widens the set of systems operators need to check even though neither entry is an application flaw of the kind that dominated earlier in the week.
