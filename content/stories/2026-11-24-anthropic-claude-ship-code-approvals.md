---
title: "Anthropic launches Claude Ship to review and approve code"
date: 2026-11-24T07:09:14-05:00
last_updated: 2026-11-24T07:09:14-05:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "Anthropic has launched Claude Ship, a suite of agents that review pull requests, fix failing checks and, under a team-written policy, approve routine code changes automatically."
why_it_matters: "Delegating code approval itself, not just code writing, to an agent moves AI further into the control points of software production and tests how much sign-off teams will automate."
featured: false
evidence_grade: "B"
sources:
  - title: "Anthropic launches Claude Ship, letting AI agents review, fix, and approve code changes"
    publisher: "TechCrunch"
    url: "https://techcrunch.com/2026/11/23/anthropic-launches-claude-ship-letting-ai-agents-review-fix-and-approve-code-changes/"
    published: "2026-11-23"
  - title: "Claude Ship announcement"
    publisher: "Anthropic"
    url: "https://claude.com"
    published: "2026-11-23"
tags: []
data_as_of: "Anthropic product announcement November 23, 2026; availability and beta status as announced."
---

Anthropic on Monday announced Claude Ship, a suite of AI agents for automating code reviews, fixes and approvals of routine code changes. The launch moves the company from having Claude write code to helping developers decide when that code is ready to ship.

The suite consists of Code Review, which is already generally available, and two new agents now in beta. PR Steward addresses failing continuous integration checks, merge conflicts and feedback from Code Review, and comments after every push on what it changed and how to roll it back. Claude Approvals then applies an approval policy the team writes as a file in the repository, in natural language, drawing on signals including Code Review findings and the company's own classifiers.

Anthropic's case is that AI coding agents now generate code faster than humans can review it, creating a bottleneck after the pull request. "Most teams want a person to approve every change, and that's easy to keep up with when people write every line. But a lot of developers build with agents now," the company wrote, adding that on the Claude Code team, Claude writes most of the code.

Because the product is in beta, Anthropic suggests running the approval function in observe-only mode first, starting with a single repository and setting monthly spending limits. Teams keep control of where Claude Ship runs, the review depth, and which changes escalate to a human. Claude Ship is rolling out to Claude Team and Enterprise plans for repositories on GitHub.
