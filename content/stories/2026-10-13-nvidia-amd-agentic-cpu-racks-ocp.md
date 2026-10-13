---
title: "Nvidia and AMD race to own the agentic CPU rack"
date: 2026-10-13T07:02:17-04:00
last_updated: 2026-10-13T07:02:17-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Nvidia said its Vera CPU racks are shipping now with more than 20,000 cores per rack, while AMD unveiled its Helion rack design at the same OCP summit, with partner systems due in November."
why_it_matters: "Both chipmakers now treat the CPU, not the GPU, as the scarce resource for agentic AI, which reshapes rack design, power budgets and who captures infrastructure margin."
featured: false
evidence_grade: "B"
sources:
  - title: "Nvidia gears up to smash CPU hegemony as Vera starts shipping"
    publisher: "Datacenter Dynamics"
    url: "https://www.datacenterdynamics.com/en/news/nvidia-gears-up-to-smash-cpu-hegemony-as-vera-starts-shipping/"
    published: "2026-10-12"
  - title: "Nvidia opens up Vera Rubin rack and tray designs to OCP"
    publisher: "Datacenter Dynamics"
    url: "https://www.datacenterdynamics.com/en/news/nvidia-opens-up-vera-rubin-rack-and-tray-designs-to-ocp/"
    published: "2026-10-12"
  - title: "AMD unveils Helion racks for AI agents at OCP summit"
    publisher: "The Register"
    url: "https://www.theregister.com/systems/2026/10/12/amd-unveils-helion-racks-for-ai-agents-at-ocp-summit/5302652"
    published: "2026-10-12"
tags: []
data_as_of: "OCP Global Summit, San Jose, October 12, 2026; company briefings reported by DCD and The Register, both opened in full. Performance figures are vendor benchmark claims, not independently verified."
---

The contest at this week's Open Compute Project Global Summit in San Jose was not over GPUs. Nvidia confirmed its Vera CPU racks are shipping now in multiple form factors, as a dedicated side cabinet next to an NVL72 system, handling agentic workloads that the CPUs inside the main Vera Rubin platform have no spare cores for. Nvidia product lead Joe DeLaere said a Vera rack offers more than 20,000 cores for agents, with more than two times the performance of the previous Grace generation on agentic workloads on the SPEC CPU 2026 benchmark, a vendor claim, and 1.8 times on Terminal Bench.

Vera entered full production in the spring and replaces Grace as Nvidia's flagship CPU, using a largely in-house core design on the Arm v9.2-A architecture. Meta and CoreWeave are early customers for the standalone CPU business Nvidia announced at the turn of the year, and Amazon Web Services is in line to offer Vera as an option for agentic workloads. Nvidia also contributed its Vera Rubin rack and tray designs to the Open Compute Project under version 1.2 of its MGX reference standard, including liquid-cooled trays, a 5,000 amp busbar and support for racks up to 250 kilowatts.

AMD answered at the same summit with Helion, a rack reference design for agentic AI in CPU-only or mixed CPU and GPU configurations, in liquid-cooled or air-cooled versions. AMD advertises up to 32,768 Zen 6 CPU cores per rack using 256-core Venice Epyc processors, up to 16 Instinct MI350P accelerators and up to 102 Tbps of networking bandwidth, depending on configuration. Partner-built Helion systems from vendors including Cisco, Dell, HPE, Foxconn, Lenovo and Supermicro are scheduled for November 2026, and AMD plans to contribute the specifications to OCP.

Read together, the two launches say the same thing from opposite sides. Agent execution is CPU-bound work: tool calls, code execution and orchestration at scale. That is why Oxide, in its $445 million Series D the same week, also pointed to CPU-based systems as the next bottleneck. The GPU shortage narrative is giving way to a whole-rack contest.
