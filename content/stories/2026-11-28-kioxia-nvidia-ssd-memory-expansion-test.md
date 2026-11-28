---
title: "Kioxia and Nvidia test flash drives as extra GPU memory"
date: 2026-11-28T07:06:06-05:00
last_updated: 2026-11-28T07:06:06-05:00
beats: ["technology"]
regions: ["asia-pacific", "north-america"]
status: "story"
lede: "Kioxia and Nvidia have demonstrated a GB200 NVL72 rack fitted with 144 solid-state drives providing about 1.1 petabytes of flash that GPUs can use as extended memory, roughly 80 times the rack's high-bandwidth memory."
why_it_matters: "If flash can credibly stand in for scarce, expensive HBM on some workloads, the memory bottleneck that prices AI servers would loosen, and NAND makers would gain a new claim on the AI hardware budget."
featured: false
evidence_grade: "B"
sources:
  - title: "Kioxia and NVIDIA Collaborate to Expand Effective High-Bandwidth Memory Capacity with SSDs"
    publisher: "Kioxia Corporation via Business Wire"
    url: "https://www.businesswire.com/news/home/20261125011118/en/Kioxia-and-NVIDIA-Collaborate-to-Expand-Effective-High-Bandwidth-Memory-Capacity-with-SSDs"
    published: "2026-11-26"
  - title: "Kioxia and Nvidia demo 144 SSDs that expand GPU memory past 1 petabyte in a GB200 NVL72 rack"
    publisher: "TechSpot"
    url: "https://www.techspot.com/news/114716-kioxia-nvidia-demo-144-ssds-expand-gpu-memory.html"
    published: "2026-11-26"
  - title: "Is Sandisk stock a buy after Kioxia and Nvidia tested flash drives as extra AI memory?"
    publisher: "The Motley Fool"
    url: "https://www.fool.com/investing/2026/11/28/is-sandisk-stock-a-buy-after-kioxia-and-nvidia-tested-flash-drives-as-extra-ai-memory/"
    published: "2026-11-28"
tags: []
data_as_of: "Proof of concept announced November 26, 2026, based on testing performed by Kioxia and Nvidia as of November 26, 2026; share moves are Friday, November 27, 2026 closes."
---

Kioxia said on November 26 that it is working with Nvidia under Nvidia's Storage-Next initiative to extend the effective memory capacity of GPU servers using solid-state drives. In the proof of concept, an Nvidia GB200 NVL72 rack-scale system with 18 server nodes was fitted with 144 Kioxia XD8 Series 7.68 terabyte NVMe drives, giving about 1.1 petabytes of raw flash capacity, nearly 60 terabytes of extended memory per node.

Nvidia's SCADA software, short for Scaled Accelerated Data Access, lets the GPUs reach the flash in small 512-byte blocks. The companies say the setup could support a database of 2 trillion 512-byte vectors, the kind of store AI search and recommendation systems query. The rack's own high-bandwidth memory totals 13.4 terabytes across its 72 GPUs, so the flash layer holds more than 80 times as much data, at lower speed.

This is a test, not a product. Neither company has published latency or throughput figures for the flash path, a price, or a shipping date, and Kioxia is separately developing a dedicated high-input-output drive line for direct GPU access. The commercial question is whether inference workloads with very large working sets can tolerate flash latency in exchange for capacity that HBM cannot economically provide.

Investors treated the demonstration as a demand signal anyway. Sandisk, which manufactures flash jointly with Kioxia in Japan, rose about 16 percent in Friday's shortened session, and Micron and SK hynix also gained, as the market priced a possible new role for NAND in AI servers beyond bulk storage.
