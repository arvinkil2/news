---
title: "Microsoft final report finds some outage emails never delivered"
date: 2026-11-24T07:09:14-05:00
last_updated: 2026-11-25T06:41:55-05:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Microsoft has declared an internal Code Red over the November Microsoft 365 outage, setting one-hour worldwide recovery and fix targets it does not yet meet, after its final report confirmed some emails never reached recipients."
why_it_matters: "Microsoft's own memos describe the outage as the most customer-affecting incident in its history, and the gap between its one-hour target and the five to six days a recent urgent fix took to reach worldwide coverage measures how far its recovery process has to go."
featured: false
evidence_grade: "C"
sources:
  - title: "Microsoft mega outage: Report reveals testing gaps and emails that never arrived"
    publisher: "The Register"
    url: "https://www.theregister.com/saas/2026/11/23/microsoft-mega-outage-report-reveals-testing-gaps-and-emails-that-never-arrived/5311656"
    published: "2026-11-23"
  - title: "Microsoft declares Code Red after outage that hit email and Teams"
    publisher: "Reuters, via Tech360TV"
    url: "https://www.tech360.tv/microsoft-declares-code-red-after-outage-that-hit-email-and-teams"
    published: "2026-11-25"
tags: []
data_as_of: "Microsoft final post-incident report on the November 12 to 14, 2026 outage, reported November 23, 2026; single-sourced to The Register's account of the report. Update November 25, 2026: internal Microsoft memos reviewed by Reuters, read via Tech360TV's republication; the memos themselves are not public."
update_bump: true
---

## Latest

Microsoft has declared an internal Code Red, its highest priority designation, to rebuild how it prevents and responds to major failures, according to internal memos reviewed by Reuters. Jason Henderson, president of Microsoft 365 Core, told staff the outage affected more customers than any incident in the company's history, and set two targets the company does not yet meet: one hour to resolve a major incident worldwide and one hour to deploy an urgent security fix, against five to six days for a recent urgent fix to reach worldwide coverage. The response sets five workstreams covering load shedding, geographic traffic partitioning and faster recovery, and responders' experience during the failure, more than 11,000 messages exchanged across 11 Teams chats with diagnostic data scattered across systems, is part of what the overhaul is meant to fix. Microsoft has not said when it expects to meet the targets.

Some emails never reached their recipients during November's Microsoft 365 outage, Microsoft has confirmed in a final post-incident report that also exposes gaps in its testing and recovery procedures. The outage began on November 12 and was not fully resolved until November 14.

The report confirms the preliminary finding that a July code change, combined with a failover and reduced capacity, brought down Exchange Online and disrupted features across other Microsoft 365 services. The defect affected Microsoft's gateway server configuration rather than standard Windows deployments, and at the worst point more than 80 percent of North American gateway servers were unresponsive as US users came online. The July defect had been running worldwide for more than three months before it brought the gateways down.

On mail loss, Microsoft extended its delivery retry window to 48 hours, but some delayed messages to consumer mailboxes inactive for more than 30 days still expired and generated non-delivery reports. The company said all queued enterprise messages were eventually delivered, with none found permanently lost.

Microsoft's corrective steps include partitioning and isolation to contain failures before they spread globally, improved recovery procedures and communications, and added capacity headroom. Its load tests had used older, lower-core-count hardware, making them less likely to expose a defect that worsened on newer machines; the company now plans testing on newer hardware with more realistic traffic and peak loads, broader failover testing, and better diagnostics and change auditing so engineers can identify troublesome Windows changes faster.
