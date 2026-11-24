---
title: "Microsoft final report finds some outage emails never delivered"
date: 2026-11-24T07:09:14-05:00
last_updated: 2026-11-24T07:09:14-05:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Microsoft's final report on the November 12 to 14 Microsoft 365 outage confirms some emails never reached recipients, and finds load testing on older hardware missed a July defect that felled more than 80 percent of North American gateway servers."
why_it_matters: "The outage report shows a three-month-old change, a testing gap on newer hardware and a mail loss admission in one incident at the world's largest enterprise software provider."
featured: false
evidence_grade: "C"
sources:
  - title: "Microsoft mega outage: Report reveals testing gaps and emails that never arrived"
    publisher: "The Register"
    url: "https://www.theregister.com/saas/2026/11/23/microsoft-mega-outage-report-reveals-testing-gaps-and-emails-that-never-arrived/5311656"
    published: "2026-11-23"
tags: []
data_as_of: "Microsoft final post-incident report on the November 12 to 14, 2026 outage, reported November 23, 2026; single-sourced to The Register's account of the report."
---

Some emails never reached their recipients during November's Microsoft 365 outage, Microsoft has confirmed in a final post-incident report that also exposes gaps in its testing and recovery procedures. The outage began on November 12 and was not fully resolved until November 14.

The report confirms the preliminary finding that a July code change, combined with a failover and reduced capacity, brought down Exchange Online and disrupted features across other Microsoft 365 services. The defect affected Microsoft's gateway server configuration rather than standard Windows deployments, and at the worst point more than 80 percent of North American gateway servers were unresponsive as US users came online. The July defect had been running worldwide for more than three months before it brought the gateways down.

On mail loss, Microsoft extended its delivery retry window to 48 hours, but some delayed messages to consumer mailboxes inactive for more than 30 days still expired and generated non-delivery reports. The company said all queued enterprise messages were eventually delivered, with none found permanently lost.

Microsoft's corrective steps include partitioning and isolation to contain failures before they spread globally, improved recovery procedures and communications, and added capacity headroom. Its load tests had used older, lower-core-count hardware, making them less likely to expose a defect that worsened on newer machines; the company now plans testing on newer hardware with more realistic traffic and peak loads, broader failover testing, and better diagnostics and change auditing so engineers can identify troublesome Windows changes faster.
