---
title: "CISA adds Adobe Commerce and Brotli flaws to exploited catalog"
date: 2026-10-28T07:15:09-04:00
last_updated: 2026-10-28T07:15:09-04:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "CISA added two vulnerabilities to its Known Exploited Vulnerabilities Catalog on October 27, an Adobe Commerce and Magento file upload flaw and the Google Brotli unchecked return value flaw, both on evidence of active exploitation."
why_it_matters: "The Brotli addition closes the loop on yesterday's emergency .NET fixes by putting the flaw under a federal remediation directive, while the Adobe entry puts every Magento storefront operator on the same clock."
featured: false
evidence_grade: "B"
sources:
  - title: "CISA Adds Two Known Exploited Vulnerabilities to Catalog"
    publisher: "US CISA"
    url: "https://www.cisa.gov/news-events/alerts/2026/10/27/cisa-adds-two-known-exploited-vulnerabilities-catalog"
    published: "2026-10-27"
tags: []
data_as_of: "Catalog additions dated October 27, 2026, read from the CISA alert in this run; the PHP additions of October 26 were covered in yesterday's PHP2Shell story and are not repeated."
---

The Cybersecurity and Infrastructure Security Agency has added two new vulnerabilities to its Known Exploited Vulnerabilities Catalog, based on evidence of active exploitation. The additions are CVE-2026-48356, an Adobe Commerce and Magento unrestricted upload of file with dangerous type vulnerability, and CVE-2026-111497, a Google Brotli unchecked return value vulnerability.

The Brotli entry is the federal escalation of a flaw already in yesterday's edition, when Microsoft issued emergency .NET fixes for it. A KEV listing changes the obligation: under Binding Operational Directive 26-04, federal civilian agencies must prioritise rapid remediation of high risk KEV vulnerabilities on publicly exposed assets that grant total control after exploitation, and must check whether threat actors compromised the system before the patch was applied.

The Adobe Commerce and Magento entry is the broader commercial exposure. A dangerous file upload flaw in a widely deployed storefront platform is a direct route to web shells and payment skimming, and the catalog listing is CISA's signal that exploitation is not theoretical.

CISA said these vulnerability types are a frequent attack vector and pose significant risks to the federal enterprise, and encouraged all organisations, not only federal agencies, to adopt risk based vulnerability management and prioritise remediation of catalog entries. The agency will continue adding vulnerabilities that meet its criteria of a CVE identifier, evidence of exploitation and clear mitigation guidance.
