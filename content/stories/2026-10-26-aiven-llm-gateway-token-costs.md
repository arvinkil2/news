---
title: "Aiven builds gateway to cut enterprise token bills"
date: 2026-10-26T07:11:29-04:00
last_updated: 2026-10-26T07:11:29-04:00
beats: ["technology"]
regions: ["europe", "global"]
status: "story"
lede: "Finland's Aiven says an internal gateway built on open source LiteLLM cut its heavy users' AI token spend by roughly 80 percent, and it plans to sell the gateway as a service."
why_it_matters: "A vendor selling metering and routing, rather than another model, is the demand side of the AI returns argument: enterprises are now spending effort on controlling token costs."
featured: false
evidence_grade: "C"
sources:
  - title: "Euro open source specialist proposes LLM gateway to ease token bills"
    publisher: "The Register"
    url: "https://www.theregister.com/ai-and-ml/2026/10/26/euro-open-source-specialist-proposes-llm-gateway-to-ease-token-bills/5305170"
    published: "2026-10-26"
tags: []
data_as_of: "Aiven statements to The Register, published October 26, 2026. Single sourced and self reported: the 80 percent figure is Aiven's account of its own internal usage, not independently verified, grade capped at C."
---

A Finnish open source company says it cut its own AI bill by routing developers away from frontier models, and now wants to sell the routing layer. Aiven, which built its business hosting open source databases as a service, told The Register that an internal gateway it built on the open source LiteLLM framework, adding budgeting and access management, reduced heavy users' token spend by roughly 80 percent by letting them work with open weight models that Aiven rents GPU capacity for and self hosts.

The design principle is triage. Aiven's vice president of strategy Ville Lehto said the company still uses frontier models, but mainly to plan work, while the majority of execution runs on open weight models, Western and Asian, because performance varies by task and the right metric is cost per task rather than cost per token. A minority of very heavy users accounted for a disproportionate share of spend, which is where the savings concentrated. The alternative Aiven rejected was strict token budgets for developers.

Aiven plans to offer the gateway as a service, positioning it for enterprises that want to swap models in and out of workflows as prices and capabilities move. Its existing customers include Conrad, Dojo, Sophos and Avaya.

The claim is a vendor's account of its own internal numbers, unverified independently, and it is graded accordingly. But it aligns with the demand side evidence in today's Apollo story: if mainstream companies increasingly treat token spending as a cost centre, the market that grows is the one that meters, routes and cuts that spending.
