---
title: "Google says agentic AI shifts data centre demand toward CPUs"
date: 2026-10-31T07:06:33-04:00
last_updated: 2026-10-31T07:06:33-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Agentic workloads are raising the share of CPU compute in data centres from a relatively small portion to a meaningful one, Google Cloud's Mark Lohmeyer told EE Times, because agents run code, call APIs and hold state over days while bursting and idling in between."
why_it_matters: "If the agent era reprices the CPU to accelerator ratio, the beneficiaries widen beyond GPU vendors to Arm and x86 CPU makers, and the design problem shifts from raw inference throughput to cheap, secure, restartable state."
featured: false
evidence_grade: "C"
sources:
  - title: "Google: Agentic AI will drive new demands on data center CPUs"
    publisher: "EE Times"
    url: "https://www.eetimes.com/google-agentic-ai-will-drive-new-demands-on-data-center-cpus/"
    published: "2026-10-30"
tags: []
data_as_of: "Interview published October 30, 2026. Single-sourced: a direct interview with a Google Cloud executive in EE Times, the primary account of Google's stated position; the workload claims are Google's characterisation, not independently measured data, grade capped at C."
---

Google Cloud's infrastructure chief for AI and computing has set out why agents change the hardware mix. Mark Lohmeyer told EE Times that chat is relatively straightforward, a question and an answer relying heavily on inference across GPUs or TPUs, while an agent breaks a user's intent into subtasks, accesses APIs and websites, writes and runs code, and preserves context and state over potentially days or weeks. Those are CPU tasks, and sessions are bursty and often idle: an agent may do nothing for a day or two, then become highly active when a user or an API responds.

That profile breaks the assumptions of both classic cloud and training era infrastructure. Lohmeyer said the optimum ratio of CPU to GPU compute for agentic AI is still evolving, but the proportion of CPU compute is definitely increasing as the industry switches from training foundation models to agentic inference, and Google expects both workloads to keep growing rapidly. Agents are also far more numerous and faster to spin up than human users, so the existing application and data layers they touch grow with them, and locality between agents, applications and data matters for latency.

Google's answers are architectural. Because bursty agents leave CPUs idle, an agent can be hibernated, its state sent to storage and reloaded quickly when needed, which demands high performance storage attached to the server and new orchestration software. For isolation, Google uses microVMs, slimmed down virtual machines that let the same hardware run perhaps 1,000 agent sandboxes where 100 traditional virtual machines would fit, with a smaller attack surface, alongside agent gateways providing network level egress controls.

On silicon, Lohmeyer said there will be no single optimum CPU: Google Cloud runs x86 parts from Intel and AMD alongside its own Arm based Axion processor, for which he reported a lot of customer interest, including bare metal demand from larger customers. Read as a market signal, the interview supports the view behind this week's CPU related moves: the agent workload rewards core density, fast local storage and cheap idle state, a different shopping list from the accelerator only buildout of the training years.
