---
title: "Cisco Expressway flaw under active attack, CISA warns"
date: 2026-11-24T07:09:14-05:00
last_updated: 2026-11-24T07:09:14-05:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Attackers are exploiting CVE-2026-76466, a critical Cisco Expressway flaw rated 9.8 that gives unauthenticated root access, and CISA has added it to its Known Exploited Vulnerabilities catalog."
why_it_matters: "Expressway gateways sit at the edge of corporate voice and video networks, so an unauthenticated root flaw under active attack is an urgent patch item for every enterprise running clustered deployments."
featured: true
evidence_grade: "B"
sources:
  - title: "CISA Adds Two Known Exploited Vulnerabilities to Catalog"
    publisher: "US Cybersecurity and Infrastructure Security Agency"
    url: "https://www.cisa.gov/news-events/alerts/2026/11/23/cisa-adds-two-known-exploited-vulnerabilities-catalog"
    published: "2026-11-23"
  - title: "Critical Cisco remote code execution bug under attack"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/11/23/critical-cisco-remote-code-execution-bug-under-attack/5311722"
    published: "2026-11-23"
tags: []
data_as_of: "Cisco advisory first published October 2026; F6 exploitation report and CISA catalog addition November 23, 2026."
---

Attackers are exploiting a critical vulnerability in Cisco Expressway gateways that allows remote code execution as root without authentication, according to warnings from the US Cybersecurity and Infrastructure Security Agency and security researchers at F6. The flaw, tracked as CVE-2026-76466 and rated 9.8 out of 10, affects Cisco Expressway-C and Expressway-E gateways configured in clusters, in both virtual and physical appliances running vulnerable software.

The bug involves hard-coded authentication credentials and insufficient certificate validation in clustered Expressway deployments. Cisco disclosed it in October, issued a software update that fixes it, and said at the time that it was not aware of any abuse. Expressway provides firewall traversal, VPN-less remote access and call routing for remote users connecting to voice, video and messaging collaboration services.

That position changed late last week. F6 said it was investigating the first observed case of exploitation, shortly after a public proof-of-concept exploit became available. The attackers initially compromised two internet-facing Cisco Expressway devices, and through one of them reached two additional cluster nodes on the victim's internal network. After obtaining root access, they prepared custom Python tooling to scan for files shared over the SMB protocol, interact with SQL Server and WinRM, and search GitLab repositories for credentials. F6 said the scripts indicated the operator used an AI assistant, and flagged a nodeup "wombat@127.0.0.1" entry in the Erlang system log as an indicator of compromise.

CISA added CVE-2026-76466 to its Known Exploited Vulnerabilities catalog on November 23 and directed federal agencies to patch. Cisco updated its advisory the same day to acknowledge the catalog addition, while noting it has no direct evidence of active exploitation itself. For operators, the practical position is Cisco's October fix plus a hunt for the published indicators, because exploitation is now documented by a named security firm and listed by the federal catalog.
