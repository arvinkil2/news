---
title: "Shai-Hulud worm hits AI platform SDK in supply-chain attack"
date: 2026-10-08T16:54:14-04:00
last_updated: 2026-10-08T16:54:14-04:00
beats: ["technology"]
regions: ["global"]
status: "story"
developing: true
update_bump: true
lede: "The credential-stealing Shai-Hulud worm infected version 0.5.144 of the Tensorlake AI agent platform's npm SDK, a package with roughly 12,000 weekly downloads."
why_it_matters: "The malware sidesteps AI sandboxing entirely, running on developers' machines and build servers where it can steal cloud credentials and GitHub secrets, then resist removal by threatening to wipe the infected user's home directory."
featured: false
evidence_grade: "C"
sources:
  - title: "Shai-Hulud worm makes jump to AI infrastructure with Tensorlake compromise"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/08/shai-hulud-worm-makes-jump-to-ai-infrastructure-with-tensorlake-compromise/5302054"
    published: "2026-10-08"
tags: []
data_as_of: "The Register reporting October 8, 2026, citing security researchers at Socket and SafeDep; the infected version was flagged 11 minutes after publication and removed from npm. Impact remains unknown."
---

Security researchers at Socket and SafeDep reported Thursday that they had detected Shai-Hulud infection in version 0.5.144 of Tensorlake's npm SDK. The malicious release shares code and techniques with the ChainDrop variant used in August to compromise npm dependencies including keyv and flat-cache. It is designed to steal crypto wallets, browser passwords, GitHub Actions secrets, cloud credentials and service-account tokens, then exfiltrate them and await further instructions from its command-and-control infrastructure.

The escape from sandboxing is the sharp edge. Tensorlake is a cloud-native platform for running isolated AI agents, but its SDK's installation script can execute on the developer's machine or build server, outside the sandbox protections. Worse, this variant monitors stolen GitHub tokens and, if one is revoked, can trigger deletion of the infected user's home directory under specific conditions. Socket recommends rebuilding compromised systems from a trusted source before restoring access to secrets, and disabling the malicious token monitor before revoking affected credentials. Npm removed the infected version within the hour, and Tensorlake has published a clean 0.5.145.
