---
title: "Cisco and Nvidia design 12.8 terabit pluggable optic"
date: 2026-10-15T07:06:15-04:00
last_updated: 2026-10-15T07:06:15-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Cisco and Nvidia unveiled the USFP open standard at the OCP Summit, a pluggable optic packing up to 32 lanes of 400 gigabits for 12.8 terabits per port, eight times today's best pluggables."
why_it_matters: "Networking, not compute, is becoming the cabling and power bottleneck inside AI clusters, and an open ultra dense pluggable standard is Cisco's bid to stay in the fabric as Nvidia pushes its own co-packaged optics."
featured: false
evidence_grade: "C"
sources:
  - title: "Cisco, Nvidia team up to build fatter, faster pluggable"
    publisher: "The Register"
    url: "https://www.theregister.com/networks/2026/10/14/cisco-nvidia-team-up-to-build-fatter-faster-pluggable/5302970"
    published: "2026-10-14"
tags: []
data_as_of: "Announced at the OCP Summit, reported Oct 14, 2026; single-sourced: The Register. Specifications are the initial USFP spec as described by Cisco; power and density figures are design targets."
---

Cisco and Nvidia are jointly designing a much denser optical link for AI data centers. Their ultra dense small form factor pluggable, USFP, shown at the Open Compute Project Summit this week, targets up to 32 lanes of 400 gigabits per second in a module about the size of today's OSFP optics, for 12.8 terabits per port. The best current pluggables reach about 1.6 terabits. One USFP could replace the cabling for eight GPUs, and Cisco says a future 204.8 terabit switch would need only 16 such ports to serve 128 endpoints at 1.6 terabits each.

The engineering trade offs are real. The specification allows up to 100 watts per pluggable against roughly 20 watts today, needs four times as many electrical contacts seated reliably through a two phase insertion mechanism, and concentrates failure risk: one bad laser or signal processor can take out far more than a single accelerator link. Cisco argues that is still safer than co-packaged optics, where one failure can drop a whole rack.

Nvidia's participation is the strategic tell. Its newest Spectrum X and Quantum X switches have moved to co-packaged optics for roughly 30 percent power savings, but its network cards still use pluggables, and its Vera Rubin Ultra racks are heading toward 600 kilowatts with per GPU bandwidth in the same range the initial USFP specification targets. USFP will be an open standard, which suits Cisco's model of selling pieces of the stack to everyone.

Cisco also disclosed that Microsoft is using its Silicon One P200 routing chips to link workloads across multiple data centers, the scale across pattern Microsoft adopted to work around local power limits at its Fairwater clusters, and added security patching support for the open SONiC network operating system, due next year. Together the announcements position Cisco inside the AI fabric at the pluggable, routing and software layers at once, rather than ceding the cluster to Nvidia's integrated stack.
