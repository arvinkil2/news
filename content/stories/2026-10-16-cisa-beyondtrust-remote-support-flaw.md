---
title: "CISA urges patch for exploited BeyondTrust remote support flaw"
date: 2026-10-16T18:42:24-04:00
last_updated: 2026-10-16T18:42:24-04:00
beats: ["technology"]
regions: ["global"]
status: "developing"
developing: true
update_bump: true
lede: "CISA on Friday urged organisations to patch a critical authentication bypass in BeyondTrust Remote Support, CVE-2026-102764, saying attackers are already exploiting it for initial access and lateral movement."
why_it_matters: "Remote Support appliances sit on trusted paths into corporate networks, and CISA says self-hosted users on versions 26.2.3 and earlier must patch or upgrade now, while hosted deployments are already patched."
featured: false
evidence_grade: "B"
sources:
  - title: "CISA Urges Patching Critical Vulnerability in BeyondTrust Remote Support"
    publisher: "US CISA"
    url: "https://www.cisa.gov/news-events/alerts/2026/10/16/cisa-urges-patching-critical-vulnerability-beyondtrust-remote-support"
    published: "2026-10-16"
tags: []
data_as_of: "CISA alert published October 16, 2026, opened and read in full; the agency is the primary authority for its own Known Exploited Vulnerabilities listing and patch guidance. Developing item, 2 to 3 sentences by design."
---

CISA said on Friday that a critical authentication bypass, CVE-2026-102764, affects BeyondTrust Remote Support versions 26.2.3 and earlier, and that threat actors are actively exploiting it to gain initial access, establish persistence, escalate privileges and move laterally. The agency added the flaw to its Known Exploited Vulnerabilities catalog the same day and urged self-hosted users to apply the BT26-05-RS patch, noting that versions older than 24.3.1 must upgrade first and that hosted deployments have already been patched.

CISA also told affected organisations to limit external access to the appliance, run network and memory forensics for signs of compromise, and, where compromise is suspected, isolate the appliance, rebuild from a known-good state and rotate every credential it stored.
