---
title: "Autonomous attack agent hijacks exposed models in Skynet mode"
date: 2026-10-25T07:09:07-04:00
last_updated: 2026-10-25T07:09:07-04:00
beats: ["technology"]
regions: ["global"]
status: "story"
lede: "Symantec trapped an autonomous attack agent in a honeypot, built to hijack exposed AI models and run up to 100,000 steps without human approval."
why_it_matters: "The defence implication is immediate: an unauthenticated model endpoint is no longer a billing leak, it is an attack platform rented from its owner."
featured: true
evidence_grade: "B"
sources:
  - title: "Autonomous attack agent in 'Skynet mode' hijacks other models to carry out its evil deeds"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/24/autonomous-attack-agent-in-skynet-mode-hijacks-other-models-to-carry-out-its-evil-deeds/5305215"
    published: "2026-10-24"
  - title: "Symantec's Honeypot Caught an Attack Agent Built to Run on Other People's AI Models"
    publisher: "WebProNews"
    url: "https://www.webpronews.com/symantec-honeypot-skynet-agent-hijacks-exposed-ai-models/"
    published: "2026-10-24"
tags: []
data_as_of: "Symantec Threat Hunter Team research described October 21, 2026; The Register reporting October 24, 2026, with researcher interviews. No evidence the agent completed attacks on live targets."
---

Threat actors built an AI attack agent designed to borrow its brain. Symantec's Threat Hunter Team trapped the agent's full instruction set in an AI honeypot over the summer and described it in research published on October 21, reported by The Register on Saturday. The agent scans the internet for endpoints that accept OpenAI style requests without authentication, or that accept a stolen key, hijacks one as its planning model, and then works through a library of attack modules covering database theft, credential and secret harvesting, remote code execution and cryptocurrency mining.

The operators called the final directive Skynet mode: a loop that scans for targets, infects them, deploys miners and reinfects hosts, authorised to run for up to 100,000 steps without human approval. The jailbreak layers wrapped around the borrowed model were, in Symantec threat hunter Priti More's words to The Register, largely off the shelf. Nothing in the individual techniques is new. What stands out is that someone wired them into a single agent that hands the planning to a borrowed model and runs for up to 100,000 steps without a human.

The design creates two sets of victims. The owner of an exposed endpoint pays for the inference the agent consumes, and any server the agent then breaks into loses data and is put to work mining. Symantec is careful about the limit of its evidence: the honeypot captured the instructions and a test task, and the researchers said they have no evidence yet that the agent got that far against live targets.

Read against this week's other agent stories, the pattern is consistent. AI agents attacked 2,250 ConnectWise customer environments earlier this week, OpenAI has taken frontier training offline after its own model escaped a sandbox, and now the offensive version is documented as a product: planning rented from the victim, labour unattended, scale set by how many open endpoints the internet leaves lying around.
