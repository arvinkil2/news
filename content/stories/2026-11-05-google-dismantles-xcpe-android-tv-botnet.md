---
title: "Google dismantles botnet hidden in 1.3 million TV boxes"
date: 2026-11-05T07:05:45-05:00
last_updated: 2026-11-05T07:05:45-05:00
beats: ["technology"]
regions: ["asia-pacific", "global"]
status: "story"
lede: "Google and partners dismantled the XCPE botnet, a firmware backdoor in more than 1.3 million Android TV boxes that Google says maker Videostrong built deliberately and sold to criminal affiliates."
why_it_matters: "The case moves the Android supply chain risk from careless vendors to a manufacturer accused of building the backdoor itself, and the backdoor remains on boxes already in homes."
featured: false
evidence_grade: "B"
sources:
  - title: "Google, partners disrupt 1.3 million device strong XCPE botnet"
    publisher: "Dark Reading"
    url: "https://www.darkreading.com/endpoint-security/google-13-million-device-strong-xcpe-botnet"
    published: "2026-11-04"
  - title: "Google dismantles XCPE botnet that infected 1.3 million Android TV devices"
    publisher: "GBHackers, from Google Threat Intelligence Group report"
    url: "https://gbhackers.com/google-dismantles-xcpe-botnet/"
    published: "2026-11-03"
tags: []
data_as_of: "Google Threat Intelligence Group report published November 2, 2026, on a takedown carried out the preceding week; device counts are Google's and TrendAI's as cited."
---

Google said on November 2 that it and industry partners had dismantled XCPE, a botnet built into the firmware of more than 1.3 million Android set top boxes. Google's Threat Intelligence Group assessed with high confidence that Videostrong Technology, a Shenzhen based Android device maker, intentionally developed and operated the backdoor, called x.cpe, for profit, selling access to criminal affiliates and loading their malware modules onto infected devices.

The partners, including Japan's National Police Agency, Lumen, HUMAN Security, Plume, Synthient and TrendAI, took legal action against the command and control domains and servers for the botnet and for more than a dozen affiliate malware families. Google expects that disruption to sever affiliate access to at least 10 million additional compromised devices. TrendAI counted 1,472,554 infected devices across 206 models between June 3 and October 1, concentrated in Malaysia, Brazil, Iraq, Mexico and Taiwan, and called that a lower bound. Most devices were Android TV boxes; telehealth devices, karaoke machines and digital signage were also found infected.

Google cut ties with Videostrong and banned the company and any future subsidiaries or affiliates from building certified Android devices or supplying software to certified makers. It also changed its OEM review process, after the malware was loaded only after a device's first boot and so was absent during certification checks.

The takedown severed the botnet's control links but removed nothing from devices already sold. The backdoor sits in firmware with system privileges and cannot be removed by owners, and Google has not published a consumer list of affected brands or models.
