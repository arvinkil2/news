---
title: "Microsoft unveils Maia 300 inference chip for 2027"
date: 2026-10-14T07:06:02-04:00
last_updated: 2026-10-14T07:06:02-04:00
beats: ["technology"]
regions: ["north-america", "asia-pacific"]
status: "story"
lede: "Microsoft detailed its Maia 300 custom inference accelerator at the OCP Summit, claiming a 96-chip rack delivers up to seven times the token throughput of Maia 200, with multi-gigawatt deployments planned from 2027."
why_it_matters: "Microsoft is building its own inference silicon at gigawatt scale rather than renting Nvidia capacity for every token, and the Maia 300 specs show the hyperscalers' custom-chip programs are now aimed squarely at the agentic inference workload that drives AI cost."
featured: true
evidence_grade: "B"
sources:
  - title: "Microsoft plans multi-gigawatt rollout of next-gen Azure Maia AI accelerator racks"
    publisher: "The Register"
    url: "https://www.theregister.com/systems/2026/10/13/microsoft-plans-multi-gigawatt-rollout-of-next-gen-azure-maia-ai-accelerator-racks/5302802"
    published: "2026-10-13"
  - title: "Microsoft's Clea Maia 300 inference XPU is a bandwidth beast"
    publisher: "The Next Platform"
    url: "https://www.nextplatform.com/compute/2026/10/13/microsofts-clea-maia-300-inference-xpu-is-a-bandwidth-beast/5302874"
    published: "2026-10-13"
  - title: "Microsoft unveils Azure Maia 300, says chip will be its primary inference system"
    publisher: "Datacenter Dynamics"
    url: "https://www.datacenterdynamics.com/en/news/microsoft-unveils-azure-maia-300-says-chip-will-be-its-primary-inference-system/"
    published: "2026-10-13"
tags: []
data_as_of: "Announcement Oct 13, 2026 at the OCP Summit; Maia 300 deployments planned from 2027. Performance figures are Microsoft claims from its technical disclosures, not independent benchmarks."
---

Microsoft used the Open Compute Project Summit to lay out the third generation of its in-house AI accelerator line. The Maia 300, developed under the codename Clea, is an inference-first chip complex built on TSMC's 2-nanometer N2P process, combining compute chiplets with eight HBM4 memory stacks that provide 288 GB of memory and up to 18 TB/s of peak memory bandwidth per device, according to Microsoft's disclosures reported by The Register and The Next Platform.

The system design is the story as much as the silicon. A rack packs 96 Maia 300 accelerators and, by Microsoft's account, delivers up to seven times the rack-scale token throughput of the current Maia 200 generation and 40 percent more tokens per megawatt than leading GPU-based systems. Microsoft says clusters of up to 128 racks can be linked into a single coherency domain of 12,288 accelerators, a scale aimed at agentic workloads that run many models in concert over long contexts. Those performance figures are vendor claims from Microsoft's own deep-dive material, not independently benchmarked results.

The Maia 200, unveiled in January 2026, is now serving production workloads, including Copilot inference, and GitHub Copilot and Microsoft Foundry are shifting onto it by the end of the year, cloud chief Scott Guthrie said in a companion announcement. Microsoft describes Maia as its primary inference system going forward and plans multi-gigawatt deployments of the 300 generation starting in 2027.

The strategic read is vertical integration. Microsoft told European regulators in 2024 that Google's advantage was owning every layer of its AI stack; with its own chips, rack designs and MAI models, Microsoft is now assembling the same structure. That puts sustained pressure on merchant silicon pricing for inference, where Nvidia and AMD sell the GPUs hyperscalers would otherwise buy, and it raises the execution bar: Maia 300 silicon has to arrive on schedule in 2027 and perform in production, not just in a summit deep dive.
