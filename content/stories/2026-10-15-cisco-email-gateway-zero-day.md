---
title: "Cisco email gateway flaw exploited as zero day"
date: 2026-10-15T07:04:48-04:00
last_updated: 2026-10-15T07:04:48-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Cisco urged customers to patch a critical Secure Email Gateway flaw rated 9.8 out of 10 after attackers exploited it as a zero day to gain root access by sending a malicious email."
why_it_matters: "Email gateways sit in front of corporate mail for thousands of organisations, and a second exploited root flaw in the same product in two months points to a product line attackers are actively mining."
featured: false
evidence_grade: "B"
sources:
  - title: "Cisco make-me-root email bug exploited as a 0-day by unknown crims"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/14/cisco-make-me-root-email-bug-exploited-as-a-0-day-by-unknown-crims/5303168"
    published: "2026-10-14"
  - title: "CISA Adds Four Known Exploited Vulnerabilities to Catalog"
    publisher: "CISA"
    url: "https://www.cisa.gov/news-events/alerts/2026/10/14/cisa-adds-four-known-exploited-vulnerabilities-catalog"
    published: "2026-10-14"
tags: []
data_as_of: "Advisories Oct 14, 2026. Cisco says exploitation began in October and affected a limited number of customers; the count of compromised appliances has not been disclosed."
---

Cisco has disclosed another critical vulnerability in its Secure Email Gateway that attackers were already exploiting before a fix existed. The flaw, tracked as CVE-2026-76519 and rated 9.8 out of 10, sits in the Advanced Malware Protection feature's handling of email attachments. A remote attacker with no credentials can send a malicious email and, on a successful exploit, write files and run commands with root privileges on the appliance operating system.

The exposure is conditional but common in enterprise deployments. Both physical and virtual gateways are affected when the File Reputation service is enabled and assigned to a mail policy, and the Content Scanner Tools version is earlier than 25.3.0.5525. Cisco said it became aware of active exploitation in October, that a limited number of customers were affected, and that there is no workaround: upgrading to a fixed AsyncOS release is the only remedy, with customers on releases earlier than version 16.5 advised to migrate to 16.5.0-780.

The US Cybersecurity and Infrastructure Security Agency added the flaw to its Known Exploited Vulnerabilities catalog on October 14 and set a Saturday deadline for federal agencies to remediate it, an unusually short fuse that reflects the root level of access involved.

This is the second exploited zero day in the same product in as many months. A similar malicious email to root flaw was exploited in mid-September, and attackers exploited another critical AsyncOS flaw in January to install persistence mechanisms. For defenders, the pattern matters as much as this single patch: internet facing mail appliances from one vendor have now produced three exploited critical flaws in ten months, which argues for treating the gateway tier as a priority patching and compromise assessment surface, not routine infrastructure.
