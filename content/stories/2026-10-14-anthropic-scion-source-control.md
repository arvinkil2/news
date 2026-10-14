---
title: "Anthropic builds Scion source control for Claude code flood"
date: 2026-10-14T07:06:02-04:00
last_updated: 2026-10-14T07:06:02-04:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "Anthropic said merged code changes rose from about 2,500 a day in May 2026 to more than 30,000 a day by September, prompting it to build its own version control system, Scion, after Git-based tooling strained at that volume."
why_it_matters: "The bottleneck in AI-era software is shifting from writing code to reviewing, integrating and checking it, and Anthropic's internal rebuild is an early template other large engineering organizations may have to copy."
featured: false
evidence_grade: "C"
sources:
  - title: "Anthropic reinvents source control as Claude floods the world with code"
    publisher: "The Register"
    url: "https://www.theregister.com/devops/2026/10/13/anthropic-reinvents-source-control-as-claude-floods-the-world-with-code/5302943"
    published: "2026-10-13"
tags: []
data_as_of: "Anthropic engineering post Oct 13, 2026, as reported by The Register; single-sourced: The Register. Volume figures are Anthropic's own statements. Scion is internal only, with no release planned."
---

Anthropic has rebuilt its source control because its models write code faster than Git-era infrastructure can absorb it. In an engineering post published October 13, the company said merged code changes averaged about 2,500 a day in May 2026 and passed 30,000 a day by September. Its main branch holds about 100 GB, and it performs on the order of 25 million code checkouts a day for continuous integration, before counting developer machines, agent sandboxes and research jobs.

The replacement, called Scion, is a centralized system built over five months of migration. Its unit of work is a changeset recorded in a write-ahead log, storing the files changed relative to a parent plus content-addressed pointers to compressed file contents in blob storage. The client is deliberately thin: queries run through an API against the server, which suits AI agents that do not need a local copy of the repository. Alongside Scion, Claude helped build a code review interface called Antique, a code search tool and a source control permissions system. Anthropic said one early ingestion pipeline, rewritten with its Mythos Preview model, used 20 times less memory and ran four times as fast.

Anthropic is not productizing any of this; it says the system fits its own shape of problem and will not be open-sourced. The significance is the direction of travel. GitHub said in April that availability problems followed exponential growth in pull requests and commits across the industry. When the constraint moves downstream of code generation, the scarce resources become review capacity, integration throughput and engineers willing to reject plausible but wrong agent output, a role Anthropic's own engineers describe as increasingly central to their jobs.
