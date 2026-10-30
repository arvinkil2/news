---
title: "Mistral releases trillion parameter model weights despite cyber risk"
date: 2026-10-30T07:07:10-04:00
last_updated: 2026-10-30T07:07:10-04:00
beats: ["technology"]
regions: ["europe", "global"]
status: "story"
lede: "Mistral AI has released the open weights of Mistral Large 4, a roughly one trillion parameter mixture of experts model pitched at coding and defensive cybersecurity, while stating plainly that it sees a potential for the model to uplift real attacks."
why_it_matters: "Open weights cannot be recalled or patched centrally, so Mistral's decision, backed by security firms and the EU agency ENISA as testers, sets the current terms of the argument over whether frontier cyber capability should be downloadable."
featured: false
evidence_grade: "B"
sources:
  - title: "Mistral releases weights for its trillion-parameter AI model, targeting cybersecurity"
    publisher: "TechCrunch"
    url: "https://techcrunch.com/2026/10/29/mistral-releases-weights-for-its-trillion-parameter-ai-model-targeting-cybersecurity/"
    published: "2026-10-29"
  - title: "Mistral open-sources AI model despite warning it could aid cyberattacks"
    publisher: "CSO Online"
    url: "https://www.csoonline.com/article/4242648/mistral-releases-large-4-weights-despite-warning-of-cyberattack-uplift.html"
    published: "2026-10-29"
tags: []
data_as_of: "Weights released October 29, 2026 after a public preview from October 6, 2026. Benchmark scores are Mistral's own, as reported by TechCrunch and CSO Online; they have not been independently validated."
---

Mistral AI on Thursday published the downloadable weights of Mistral Large 4, nicknamed Le Chonk, a mixture of experts model of about one trillion total parameters with roughly 49 billion active per token and a one million token context window, trained on 3,800 Nvidia Grace Blackwell GPUs in Mistral's European data centres. The release follows a public preview that began on October 6 and three further weeks of reinforcement learning. It is available on Hugging Face under a modified MIT licence, free to use and fine tune, with a separate commercial licence required to resell it as a hosted model service; through Mistral's own API it costs 0.70 dollars per million input tokens and 2.10 dollars per million output tokens, and Microsoft Foundry is the first cloud to carry it.

The pitch is defensive cybersecurity and coding. Mistral says the model scores 51 percent on the Artificial Analysis Cyber Index, refused 96.6 percent of malicious cyber prompts across the JailbreakBench, StrongREJECT and AgentHarm evaluations, and leads open models on coding benchmarks. CrowdStrike, Cloudflare, Cisco and the European Union's cybersecurity agency ENISA are among those testing it for defensive work such as finding vulnerabilities, auditing code and analysing logs.

The candour is the unusual part. Mistral said that during the preview it monitored cyber related use and sees "a potential for uplift to conduct real attacks," and that guardrail updates in coming months can reach only its API and hosted services, not weights already downloaded. A more capable penetration testing variant stays restricted to vetted partners such as Orange Cyberdefense.

Coming the same week as Google's Gemini 4 Carbon, released first to defenders through a controlled programme, the contrast is the story. Two frontier labs, facing the same dual use problem, chose opposite distribution models in the same week: one gated, one downloadable. The market and regulators will judge both against the incident record that follows.
