---
title: "Topgolf says VMware exit saved over $11.3 million"
date: 2026-10-14T07:06:02-04:00
last_updated: 2026-10-14T07:06:02-04:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "Topgolf told Ars Technica it has cut or eliminated more than $11.3 million in infrastructure costs after migrating 12,000 virtual machines off VMware to VergeIO, avoiding a projected 400 percent cost increase under Broadcom's licensing model."
why_it_matters: "It is one of the largest quantified VMware exits yet disclosed, and it gives every enterprise facing a Broadcom renewal a named reference case with a savings figure attached."
featured: false
evidence_grade: "C"
sources:
  - title: "Topgolf saved over $11.3 million after leaving VMware"
    publisher: "Ars Technica"
    url: "https://arstechnica.com/information-technology/2026/10/topgolf-saved-over-11-3-million-after-leaving-vmware/"
    published: "2026-10-13"
tags: []
data_as_of: "Reported Oct 13, 2026; single-sourced: Ars Technica, based on Topgolf's own account. Savings figure is the company's reported number, not independently audited. Full exit expected by the second week of December 2026."
---

Topgolf has put a number on leaving VMware. The sports entertainment company, which runs more than 100 venues, told Ars Technica that Broadcom's licensing changes would have raised its VMware costs by about 400 percent. Instead it migrated 12,000 virtual machines to VergeIO's VergeOS platform and says it has reduced or eliminated more than $11.3 million in combined infrastructure costs so far, before counting wider hardware price increases.

The dependency being unwound was deep. Topgolf used vSphere and ESXi for decades, adopted the Dell co-engineered VxRail platform in 2017, and its staff sat on VMware customer councils. Twenty venues still run VxRail with VMware Cloud Foundation, and the company expects to be fully off VMware by the second week of December. The migration ran alongside a wider rebuild: game compute moved from venue servers to edge panels in the bays, wired into a new Kubernetes-based gaming architecture, and the company had to work through integration gaps with third-party tools such as Rubrik and LogicMonitor that the newer platform does not yet match.

Broadcom ended perpetual VMware licenses and bundled products into fewer, larger subscriptions after acquiring the company, and exit stories have accumulated since. What is new here is the scale and the disclosed arithmetic: a 12,000-virtual-machine estate and an eight-figure saving, stated on the record by the customer. Treat the figure as Topgolf's own accounting, reported by a single outlet, but expect it to be quoted in renewal negotiations across the enterprise market this quarter, to Broadcom's cost.
