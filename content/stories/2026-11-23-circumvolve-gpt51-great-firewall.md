---
title: "Researchers bypass Great Firewall for under $1 in tokens"
date: 2026-11-23T07:08:02-05:00
last_updated: 2026-11-23T07:08:02-05:00
beats: ["technology"]
regions: ["asia-pacific", "north-america"]
status: "story"
lede: "Researchers presenting the CircumVolve system at the ACM Conference on Computer and Communications Security found working evasions of China's Great Firewall and other state censors at a median cost of under $1 in GPT-5.1 tokens to the first successful evasion."
why_it_matters: "Censorship evasion was a slow, manual craft; automating its discovery at trivial cost changes the economics for censors and circumvention developers alike, and the same method was tested against systems in Iran, Pakistan and Kazakhstan."
featured: false
evidence_grade: "C"
sources:
  - title: "$1 of GPT-5.1 tokens finds new ways around China's Great Firewall"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/11/23/1-of-gpt-51-tokens-finds-new-ways-around-chinas-great-firewall/5311532"
    published: "2026-11-23"
tags: []
data_as_of: "Single-sourced: The Register report of November 23, 2026 on the CircumVolve paper presented the previous week at the ACM Conference on Computer and Communications Security; the paper itself is the primary document and its reported results are stated as the authors' findings. Evidence grade capped at C."
---

Six researchers from the University of Massachusetts Amherst, the University of Colorado Boulder and the activist group the Great Firewall Report have automated one of internet freedom's most laborious tasks. Their system, CircumVolve, presented last week at the ACM Conference on Computer and Communications Security in a paper titled CircumVolve: Automated Discovery of Censorship Evasion Strategies Using Large Language Models, combines large language model code generation with iterative, feedback-driven testing to produce evasion techniques across the full network stack.

The team tested the system against simulated censorship tools and live servers inside China, Iran, Pakistan and Kazakhstan. Using GPT-5.1, the median API cost to the first successful evasion was less than $1 in token spending. The authors note the system's test traffic is small, about 80KB outbound and 150KB inbound with pauses of 25 to 45 seconds between tests, which they suggest might keep it below censors' notice, while acknowledging operators of censorship infrastructure might be able to observe it at work.

The result matters less for any single technique, which censors can patch, than for the cost curve: if discovering an evasion costs under a dollar of model time, the bottleneck in the censorship contest shifts from researcher ingenuity to how fast each side can iterate.
