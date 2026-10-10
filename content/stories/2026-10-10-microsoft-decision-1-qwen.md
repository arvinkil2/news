---
title: "Microsoft ships decision model on Chinese open-weights base"
date: 2026-10-10T07:16:10-0400
last_updated: 2026-10-10T07:16:10-0400
beats: ["technology"]
regions: ["north-america", "asia-pacific"]
status: "story"
lede: "Microsoft launched Microsoft-Decision-1, a non-text decision model built on Alibaba's open-weights Qwen3.5-9B, to compete with TypeSafe's Jev."
why_it_matters: "Microsoft is using a Chinese lab's open model to attack a US startup's $7.5 billion valuation: open weights have become the fastest way to ship competing AI products, and model provenance is becoming a supply-chain question."
featured: false
evidence_grade: "C"
sources:
  - title: "Microsoft leans on open weight model from Chinese AI lab to challenge Jev"
    publisher: "The Register"
    url: "https://www.theregister.com/ai-and-ml/2026/10/10/microsoft-leans-on-open-weight-model-from-chinese-ai-lab-to-challenge-jev/5302473"
    published: "2026-10-10"
tags: []
data_as_of: "Announced October 10, 2026, via a Microsoft blog post by Achint Srivastava, VP of software engineering in Microsoft's Office of the CTO (company primary, quoted in The Register's reporting, article read in full). Single-sourced to The Register; performance claims (2.5x faster, 83.5% accuracy) are Microsoft's own and not independently verified."
---

Microsoft has launched "Microsoft-Decision-1," a decision model that outputs calibrated probabilities rather than text, offered via Microsoft Foundry and soon on OpenRouter. The twist: it is based on Qwen3.5-9B, developed by Alibaba Cloud, and Microsoft says it will soon rebase the model on its own and OpenAI's models.

The launch is a direct shot at TypeSafe AI's Jev, which raised $870 million at a $7.5 billion valuation this week on the promise of fast, token-cheap task automation. Microsoft claims Decision-1 is 2.5 times faster than H2O-Lightning-4B and 2.8 times faster than Jev in latency, hits 83.5 percent accuracy across 36 benchmarks, and costs more than 20 times less than OpenAI's GPT-6 Sol on text classification, with input priced at $0.042 per million tokens and output free.

The field is crowding fast. The Register counts more than 100 decision models now on Hugging Face, with this week's announcements including OpenAI's Decisions API in public beta, Cloudflare Clef, and offerings from Liquid AI, Perplexity, and Snowflake. Researchers are studying how errors compound in decision models, a caveat The Register flags as the category races to production.
