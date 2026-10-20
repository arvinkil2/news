---
title: "OpenCode breach exposes API keys, runs up users AI charges"
date: 2026-10-20T07:27:43-04:00
last_updated: 2026-10-20T07:27:43-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Attackers broke into an older OpenCode Console system, affecting 1.4 percent of the platform's users and exposing stored AI API keys that were used to run up charges on OpenAI, Anthropic and Google accounts before providers blocked them."
why_it_matters: "The incident exposes an asymmetry defenders now face: the attacking work was automated, while the frontier models OpenCode first used for defence refused to analyse the malicious code because it tripped their own safety filters."
featured: false
evidence_grade: "C"
sources:
  - title: "Hackers hit AI coding tool OpenCode, running up charges on users' AI accounts"
    publisher: "TechCrunch"
    url: "https://techcrunch.com/2026/10/19/hackers-hit-ai-coding-tool-opencode-running-up-charges-on-users-ai-accounts/"
    published: "2026-10-19"
tags: []
data_as_of: "TechCrunch report of October 19, 2026, read in full, reporting OpenCode's own disclosure of October 18. Single source, hence grade C. OpenCode's characterisation of the incident as a distillation attack is the company's; TechCrunch noted sceptics who called that framing unproven, and how the attackers entered the older system has not been detailed."
---

OpenCode, the open source AI coding agent, said on Saturday that attackers broke into an older system overnight, affecting 1.4 percent of users of OpenCode Console, its online platform where some users store the API keys they use to reach AI services. The company notified affected users by email on Sunday morning and said users who received no email were not impacted.

Developers posted spending alerts as the exposed keys were used: one wrote that OpenAI, Anthropic and Google spend alerts all fired before bed. Individual charges ran into the hundreds of dollars, with a few above 1,000 dollars. Anthropic and Google blocked keys they believed were exposed, OpenAI worked with OpenCode to restore access and refund credits used in the attack, and OpenCode said refunds for unauthorised charges are underway. Co founder Dax Raad stressed the exposure was confined to Console workspaces: the open source application and command line tool were not affected, and those keys never reach OpenCode itself.

OpenCode described the incident as a large scale distillation attack, a use leaked keys would suit, since generating model outputs at volume is how a rival model gets trained on another's behaviour. TechCrunch noted sceptics who called that framing an overstretch for a straightforward breach whose purpose remains unproven.

The response ran into a defensive wall. Raad said attackers probed the systems nonstop for 48 hours, and the AI models the team first used to analyse the attack began refusing once the malicious code activated safety filters. Access to OpenAI's Daybreak Blue programme, which gives vetted users models less likely to refuse defensive security work, improved the investigation. Hugging Face reported the same problem in July, writing that guardrails cannot distinguish an incident responder from an attacker.
