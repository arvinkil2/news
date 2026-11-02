---
title: "Torvalds backs healthier model for AI patches in Linux 7.4"
date: 2026-11-02T07:12:42-05:00
last_updated: 2026-11-02T07:12:42-05:00
beats: ["technology"]
regions: ["global"]
status: "story"
lede: "Linus Torvalds released the first candidate of Linux kernel 7.4 with almost 20,000 commits against a usual 15,000, and said AI generated fixes are becoming part of normal development rather than flooding the stabilisation phase."
why_it_matters: "The kernel is the load bearing open source project of the AI buildout itself, and its maintainer's verdict is the clearest signal yet of how AI written code is being absorbed into production software practice: early, reviewed, and often rewritten."
featured: false
evidence_grade: "C"
sources:
  - title: "Linus Torvalds says Linux kernel is out of stabilization phase and using much healthier model for AI contributions"
    publisher: "The Register"
    url: "https://www.theregister.com/os-platforms/2026/11/01/linus-torvalds-says-linux-kernel-is-out-of-stabilization-phase-and-using-much-healthier-model-for-ai-contributions/5306852"
    published: "2026-11-01"
tags: []
data_as_of: "Torvalds' state of the kernel post releasing 7.4-rc1, reported by The Register on November 1, 2026 and read in full in this run. Single-sourced to The Register's account of the LKML post, grade C."
---

The Linux kernel has had its biggest merge window in recent memory, and its maintainer is crediting AI for part of it, approvingly. Releasing the first candidate of kernel 7.4, Linus Torvalds noted almost 20,000 commits against the usual roughly 15,000, and wrote that he is much happier with the flood of AI triggered work going into the merge window than he was with it showing up mainly as extra fixes during the release candidate period.

His reasoning is about workflow rather than volume. AI found fixes arriving during the stabilisation phase destabilised the release; the same work arriving as part of normal development can be reviewed like any other patch. He called that a much healthier model, while hedging that 7.4 is also expected to be the next long term support release, which independently tends to draw larger submissions. His description of the release was precise: large, and full of fixes for issues found by AI, with more and more of the patches also suggested by AI, although they often get rewritten.

The contents underline where the hardware pressure sits. About a third of the changes are AMD GPU register offsets and bit masks. Kernel watchers at Phoronix, cited by The Register, rate the headline inclusions as improved support for processors from AMD, Apple and Google, better security for virtual machines, and more work on Qualcomm's Snapdragon X2 for PCs.

For an industry arguing about whether AI coding tools produce durable output, the kernel's standard is the demanding one: patches survive maintainer review or they do not ship. Torvalds' position, that AI contributions are welcome when they enter through the same discipline as human ones and are rewritten when they fall short, is a more useful benchmark than either vendor productivity claims or the task level gains the Productivity Institute reported yesterday.
