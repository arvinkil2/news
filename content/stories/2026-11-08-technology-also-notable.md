---
title: "Technology also notable: ITU governance test, PyTorch 2.15, Meta terms pause"
date: 2026-11-08T07:12:58-05:00
last_updated: 2026-11-08T07:12:58-05:00
beats: ["technology"]
regions: ["global", "europe", "north-america"]
status: "story"
lede: "The ITU's quadrennial plenipotentiary opens Monday with 278 proposals on the table, PyTorch 2.15 rewrites its GPU communications backend, and Meta has paused the commercial terms that drew injunctions in Norway and Brazil and a UK competition investigation."
why_it_matters: "Each item is a governance fight over who controls a layer of the stack, state bodies versus multi-stakeholder institutions at the ITU, publishers versus a platform at Meta, and framework maintainers versus cluster failures in PyTorch."
featured: false
evidence_grade: "B"
sources:
  - title: "Internet governance about to get its quadrennial stress test at ITU meeting"
    publisher: "The Register"
    url: "https://www.theregister.com/networks/2026/11/08/internet-governance-about-to-get-its-quadrennial-stress-test-at-itu-meeting/5308031"
    published: "2026-11-08"
  - title: "PyTorch 2.15 tackles the 'one bad GPU' problem"
    publisher: "The Register"
    url: "https://www.theregister.com/devops/2026/11/06/pytorch-215-tackles-the-one-bad-gpu-problem/5308227"
    published: "2026-11-06"
  - title: "Everyone Everywhere Hated Meta's New AI Training Terms. Now, They're On Pause"
    publisher: "404 Media"
    url: "https://www.404media.co/meta-generative-ai-commercial-terms-on-pause/"
    published: "2026-11-05"
tags: []
data_as_of: "ITU meeting opens Monday November 9, 2026 and runs 18 days; PyTorch 2.15 released and reported November 6, 2026; Meta pause announced November 5, 2026 and reported by Reuters on November 6, 2026."
---

The International Telecommunication Union opens its quadrennial plenipotentiary conference on Monday, November 9, with 278 proposals before it and internet governance bodies watching for attempts to expand the UN agency's role into areas run by ICANN, the IETF and the regional internet registries. The Internet Society says it is actively challenging proposals that could affect the internet's technical architecture or increase fragmentation, and notes that oversight of low earth orbit constellations, submarine cable resilience and spectrum policy remains undecided. ICANN told The Register that proposals expanding the ITU's role in IP based networks, the domain name system and internet resources raise concerns about overlapping mandates. Most proposals at ITU meetings are settled by consensus, but amendments during the 18 day meeting leave room for significant changes.

PyTorch 2.15, reported November 6, rewrites the framework's backend for Nvidia's Collective Communications Library so that one bad GPU no longer has to mean restarting an entire training job. The new backend enforces one communicator per process group, lets an orchestrator exclude a crashed or slow GPU and assign a replacement, and adds a flight recorder that captures operations before a failure so administrators can diagnose stalls instead of receiving a generic timeout. The release drew 3,117 commits from 583 contributors; the legacy backend remains as a rollback option and is due to be removed in version 2.16 early next year.

Meta has paused the update to its commercial terms that would have let it use content from websites linked to business accounts, after courts in Norway and Brazil issued preliminary injunctions in suits brought by media groups and the UK Competition and Markets Authority opened a formal investigation on October 30. The updates to the Commercial Terms, Product Catalog Terms, Self-Serve Ad Terms and Ad Creative Generative AI Terms will not take effect on November 20 as scheduled, existing terms remain in force, and Meta says it is continuing to consult stakeholders. Reuters reported the pause on November 6. Separately, Fox's completion of its $22 billion acquisition of Roku, and the Justice Department's closure of its investigation of that merger, were covered on this site on November 6 and are carried by the infra-deals beat.
