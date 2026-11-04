---
title: "Smugglers route banned HBM into China on dummy processors"
date: 2026-11-04T07:16:46-05:00
last_updated: 2026-11-04T07:16:46-05:00
beats: ["technology"]
regions: ["asia-pacific", "north-america"]
status: "story"
lede: "Smugglers are bonding restricted Samsung and SK hynix high-bandwidth memory to deliberately weak processors so the packages clear export controls as ordinary chips, then stripping the memory off in China, where an HBM3E stack now sells for about $4,000, The Information reported."
why_it_matters: "The scheme exploits the text of the December 2024 controls, which judge a co-packaged chip by its processor rather than its memory, and it shows the memory bottleneck, not logic, is where the export regime is leaking."
featured: false
evidence_grade: "C"
sources:
  - title: "AI chip smugglers exploit trade control loophole to bring banned HBM from South Korea into China"
    publisher: "Tom's Hardware"
    url: "https://www.tomshardware.com/tech-industry/semiconductors/ai-chip-smugglers-exploit-trade-control-loophole-to-bring-banned-hbm-from-south-korea-into-china-expensive-memory-chips-packaged-with-cheap-unsanctioned-processors-to-become-legal-exports"
    published: "2026-11-03"
  - title: "Smugglers reportedly pair top-tier HBM with throwaway server chips to dodge US export controls"
    publisher: "Wccftech"
    url: "https://wccftech.com/smugglers-hbm-throwaway-server-chips-us-export-controls-loophole-china-south-korea/amp/"
    published: "2026-11-03"
tags: []
data_as_of: "Investigation by The Information, published November 2 to 3, 2026, relayed by Tom's Hardware and Wccftech; the account rests on anonymous sources and neither Samsung nor SK hynix has confirmed any diversion. SK hynix stated on November 3 that it strictly complies with export regulations and has no commercial relationship with Huawei. Single-origin investigation, graded C."
---

Smugglers are moving restricted high-bandwidth memory from South Korea into China by bonding Samsung and SK hynix HBM stacks to deliberately weak, cheap processors, exporting the combined package as an ordinary low-performance chip, and desoldering the memory on arrival, The Information reported. One operator at the centre of the trade runs a chip design firm whose processors are built to be too weak for any data centre to want, which gives the firm a reason to order top-tier memory to package alongside them.

The route works because of how the rules are written. The Bureau of Industry and Security rules of December 2024 require a licence to ship standalone HBM above a bandwidth density of 2 gigabytes per second per square millimetre to China, but a technical note excludes co-packaged products where the dominant function is processing. A package is then judged by its processor's performance, so fast memory paired with a slow processor clears as an unsanctioned part. Packaging houses in Taiwan, South Korea and Southeast Asia bond the parts onto a single substrate, the packages are shipped to Hong Kong declared under the processor's classification, and couriers and daily commuters carry them into Shenzhen in luggage and car trunks, according to the reporting.

The economics explain the effort. A Shenzhen broker quoted in the investigation said a single HBM3E stack changed hands for a few hundred dollars a year ago and now sells for about $4,000. An AI accelerator needs six to eight stacks, putting the memory alone at $24,000 to $32,000 per chip before the processor, server and power are counted. SemiAnalysis estimated in September 2025 that China had amassed about 13 million HBM stacks, including 11.4 million from Samsung, with some 7 million acquired in the month between the December 2024 rule's announcement and its enforcement.

The memory is reported to flow mainly toward Huawei's supply chain. Huawei has told some customers that a significant share of the HBM in its next flagship AI processor, the Ascend 960DT, unveiled on September 17 with 288 gigabytes of memory capacity, will be Samsung and SK hynix product, according to people familiar with the supply chain cited in Korean reporting of the investigation. SK hynix said on November 3 that it strictly complies with export regulations and has not supplied Huawei since United States restrictions took effect in 2020.

Domestic supply is not yet closing the gap. China's CXMT has reportedly begun risk production of HBM3E with mass production expected by the end of this year, but yields are said to be low, keeping its output scarce and expensive. Until that changes, the price spread between controlled memory outside China and the $4,000 Shenzhen price is the incentive the loophole leaves open.
