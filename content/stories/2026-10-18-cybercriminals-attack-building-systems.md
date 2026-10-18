---
title: "Cybercriminals attack building systems for physical leverage"
date: 2026-10-18T07:08:16-04:00
last_updated: 2026-10-18T07:08:16-04:00
beats: ["technology"]
regions: ["north-america", "europe", "global"]
status: "story"
lede: "Ransomware groups are increasingly seizing building automation systems rather than data, with Armis Labs finding 73 percent of organisations run systems of a type already used in ransomware attacks and 91 percent communicate over insecure protocols."
why_it_matters: "When door locks, HVAC and refrigeration become the extortion lever, the blast radius of a cyber incident turns physical, and building systems sit largely outside the security programmes built for IT networks."
featured: false
evidence_grade: "B"
sources:
  - title: "Cybercrims go beyond stealing data to attack physical building systems"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/17/cybercrims-go-beyond-stealing-data-to-attack-physical-building-systems/5303677"
    published: "2026-10-17"
  - title: "Early Warning Insights for Building Automation Systems"
    publisher: "Armis Labs"
    url: "https://www.armis.com/research/building-automation-systems-security/"
    published: "2026-10-05"
tags: []
data_as_of: "Armis Labs report researched Q3 2026 and published October 2026; The Register reporting published October 17, 2026. Hospital incident August 10, 2026 (Shared Health, Winnipeg). Dragos industrial ransomware counts as reported by The Register."
---

Attackers are moving past stealing data and encrypting files toward seizing the physical systems that run buildings, according to reporting by The Register built on a report published this month by ServiceNow's Armis Labs. Building automation systems control HVAC, lighting, energy and water, and also badge readers, door locks, surveillance cameras and fire alarm panels, which makes them high pressure extortion targets: an operator who cannot open doors or control climate faces consequences no backup restore can fix.

The exposure figures are stark. Armis Labs found that 73 percent of organisations operate building automation systems of a type already used in ransomware attacks, that the same share carry known exploited vulnerabilities in at least one such system, and that 91 percent of building automation systems communicate over insecure protocols designed for closed networks. The August ransomware attack on facility systems at Winnipeg's Health Sciences Centre, Manitoba's largest hospital, is the worked example: door and access control, central HVAC monitoring, badge issuance and elevator service failed while the clinical record stayed up, and the hospital posted physical guards at entrances.

Incident responders describe building systems as a place to hide as well as a lever to pull. Michael Freeman, ServiceNow's senior director of threat research, told The Register that intruders evicted from a large financial institution's IT network built backdoors into its building management systems to keep persistent access to both environments, because operational technology is harder to patch or scan without causing outages. He also said attackers are using AI to learn obscure building automation protocols and legacy operating systems, eroding the obscurity that once protected them.

The wider industrial trend points the same way. Dragos tracked 119 ransomware groups affecting more than 3,300 industrial organisations in 2025, with 1,020 incidents in the first quarter of 2026 and 1,140 in the second, and estimates fewer than 10 percent of operational technology networks worldwide have sufficient monitoring. The most recent illustration came after The Register's interviews: criminals hacked remote controlled refrigeration systems across hundreds of French grocery stores, spiking temperatures and spoiling food, an attack on internet connected units that exist so owners can prove regulatory temperature compliance.
