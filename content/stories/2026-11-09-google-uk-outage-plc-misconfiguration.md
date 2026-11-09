---
title: "Google traces UK cloud outage to generator control flaw"
date: 2026-11-09T07:10:38-05:00
last_updated: 2026-11-09T07:10:38-05:00
beats: ["technology"]
regions: ["europe"]
status: "story"
lede: "Google said its October 19 outage in the europe-west2 region began with an external cable fault during generator testing, when a voltage-sensing design flaw and a controller misconfiguration kept its generator plant from starting."
why_it_matters: "The failure ran through duplicate power paths, battery backup and redundant controllers at once, which is the class of incident cloud customers assume modern data centre design has engineered away."
featured: false
evidence_grade: "B"
sources:
  - title: "Google's UK data center disruption caused by 'misconfiguration' of systems"
    publisher: "Datacenter Dynamics"
    url: "https://www.datacenterdynamics.com/en/news/googles-uk-data-center-disruption-caused-by-misconfiguration-of-systems/"
    published: "2026-11-09"
tags: []
data_as_of: "Google's own incident update on the October 19, 2026 europe-west2-b outage, as reported in full by Datacenter Dynamics on November 9, 2026; the account rests on Google's disclosure, the primary source for its own incident."
---

Google has published its account of the October 19 disruption that took workloads in its europe-west2-b availability zone offline in the United Kingdom. The company attributes the incident to an external electrical power disruption, and its post-incident detail describes a chain in which each protective layer failed in sequence.

The facility runs a 2N power architecture, with complete duplicate power paths for every critical load, two independent utility feeders and a central high-voltage generator bank managed by dual-redundant programmable logic controllers. Before the incident, however, the site had been placed temporarily in a single-feed 1N configuration for generator load testing. An external underground cable then faulted on primary utility feed A, and the site's roughly five minutes of battery backup became the only bridge to generator power.

That bridge was never crossed. Google said a voltage-sensing design flaw and a PLC misconfiguration prevented the generator plant from receiving an automatic start signal: the controllers were programmed to check for voltage on the line side of the feeder, feed B remained energized upstream while its incomer was open, and both the active and standby controllers, running identical logic, read that live voltage through shared upstream sensors and concluded the utility source was healthy. The batteries carried the load until their reserves were used up, and power across the data halls was lost. Engineers restored critical load from the standby utility source and began bringing services back.

Google said it is adding an automated alert-to-communication mechanism to speed notification for location-impacting incidents. The company operates a data centre at Waltham Cross in Hertfordshire, opened in September 2025, and is reportedly considering a second UK site in Teesside.
