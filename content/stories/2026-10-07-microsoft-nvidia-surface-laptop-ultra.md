---
title: Microsoft and Nvidia unveil AI-focused Surface Laptop Ultra, shipping October 16
date: 2026-10-07 16:45:50-04:00
last_updated: 2026-10-08T07:38:44-0400
beats:
- technology
status: story
developing: true
update_bump: true
lede: Independent event coverage confirms the Surface Laptop Ultra starts at $2,599 and
  tops out at $5,899, clarifies the GB10-based N1X chip, and adds Microsoft's Copilot
  "hybrid intelligence" rollout to GitHub Copilot next week.
why_it_matters: The detail turns the launch into a measurable competitive offer against
  Apple's MacBook Pro and shows Microsoft routing AI work between local and cloud
  models based on privacy and cost.
featured: false
evidence_grade: B
sources:
- title: Microsoft and Nvidia are teaming up on a supercharged AI laptop
  publisher: MarketWatch
  url: https://www.marketwatch.com/story/microsoft-and-nvidia-are-teaming-up-on-a-supercharged-ai-laptop-f58b28d8
  published: '2026-10-07'
- title: Microsoft N1Xes Intel in favor of Nvidia's shiny new SoCs in Surface Laptop Ultra
  publisher: The Register
  url: https://www.theregister.com/personal-tech/2026/10/07/microsoft-n1xes-intel-in-favor-of-nvidias-shiny-new-socs-in-surface-laptop-ultra/5301722
  published: '2026-10-07'
- title: Microsoft is about to let Copilot loose on your file system
  publisher: The Register
  url: https://www.theregister.com/personal-tech/2026/10/07/microsoft-is-about-to-let-copilot-loose-on-your-file-system/5301763
  published: '2026-10-07'
tags: []
data_as_of: Launch Oct 7, 2026; pricing, chip detail and Copilot rollout from The Register's
  independent event coverage, Oct 7. Single-source grade C from the launch pass raised
  to B.
regions:
- north-america
---

Microsoft and Nvidia unveiled the Surface Laptop Ultra on Wednesday, a laptop designed for AI workloads and powered by Nvidia's RTX Spark chip, a processor built for tasks like coding, consumer agents and gaming that can run complex AI models directly on the device. The top configuration carries 128 gigabytes of unified memory and one petaflop of AI processing power, with the base model priced at $2,599 and shipments starting October 16.

Independent coverage of the launch event filled in the pricing tiers: $2,599 for the gray base model with the lower-end 18-core N1X chip, 24GB of unified memory and a 512GB SSD, rising to $5,899 for the 20-core chip with 128GB of memory and 1TB of storage. The N1X is based on Nvidia's year-old GB10 platform with some CPU and GPU cores fused off on lower-end models: an 18- or 20-core CPU designed by MediaTek and Arm paired with a Blackwell-based RTX GPU of 5,120 to 6,144 cores. Microsoft and Nvidia market a peak of 1 petaFLOPS at 4-bit precision, but that figure leans on 2:4 sparsity that almost no real inference workloads exploit, so practical throughput is closer to 500 teraFLOPS. With up to 128GB of unified memory, Microsoft says the machine can serve language models up to 284 billion parameters.

Nvidia CEO Jensen Huang said the companies had "reinvented the computer as we know it" at the San Francisco launch. Microsoft said the machine delivers up to 4.3 times faster image generation and 6.2 times faster video generation than Apple's MacBook Pro M5 Pro, and paired the launch with a cybersecurity push for AI agents, including Windows Microsoft Execution Containers for sandboxing agents, now generally available in Windows 11.

Microsoft also announced a mini-PC development kit based on the N1X at $5,999, cheaper than the similarly specced DGX Spark at $6,950, and Lenovo, Asus, Dell, MSI and HP all plan similarly specced systems over the next week. Separately, Microsoft detailed "hybrid intelligence": a HydraFusion model router that sends simple or privacy-sensitive tasks to local models and complex ones to cloud models such as OpenAI's GPT-6 or Anthropic's Claude, with local agents sandboxed in Microsoft Execution Containers. Microsoft is extending Windows ML to Llama.cpp to broaden accelerator support. The functionality rolls out to GitHub Copilot next week and to the Copilot app over the coming months, and Copilot is getting access to the file system for agent tasks such as finding tax documents and drafting an email to an accountant.
