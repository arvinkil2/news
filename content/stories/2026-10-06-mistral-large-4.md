---
title: Mistral releases trillion-parameter model to challenge US and Chinese rivals
date: 2026-10-06 12:58:00-04:00
last_updated: 2026-10-08T07:38:44-0400
beats:
- technology
status: story
lede: The first third-party evaluations of Mistral Large 4 show strong coding and cyber
  results but a poor legal-research benchmark, narrowing the company's frontier-open
  claims to specific domains.
why_it_matters: It is the first real data on whether the most compute-efficient frontier
  open model actually closes the gap with closed systems, and the answer is domain-dependent.
featured: false
evidence_grade: A
sources:
- title: Mistral's new 1T model aims to leapfrog closed and open rivals
  publisher: TechCrunch
  url: https://techcrunch.com/2026/10/06/mistrals-new-1t-model-aims-to-leapfrog-closed-and-open-rivals/
  published: '2026-10-06'
- title: France's Mistral launches AI model it says outperforms some Chinese rivals
  publisher: Reuters
  published: '2026-10-06'
- title: Mistral debuts Large 4 'Le Chonk', a 1-trillion parameter text output model
    with high benchmarks planned for open weights release
  publisher: VentureBeat
  url: https://venturebeat.com/technology/mistral-debuts-large-4-le-chonk-a-1-trillion-parameter-text-output-model-with-high-benchmarks-planned-for-open-weights-release
  published: '2026-10-06'
- title: Mistral Large 4 is Europe's trillion-parameter answer to US models that refuse
    security work
  publisher: the-decoder
  url: https://the-decoder.com/mistral-large-4-is-said-to-be-the-most-powerful-open-ai-model-from-europe-and-the-u-s/
  published: '2026-10-06'
- title: Mistral Large 4 Benchmark: Legal Failures, Accounting Results & Cost
  publisher: Digitrans
  url: https://digitrans.lu/blog/mistral-large-4-le-chonk-legal-accounting-benchmark/
  published: '2026-10-06'
tags: []
data_as_of: Released October 6, 2026; open weights planned October 27. First independent
  evaluations published Oct 6-7, 2026; company benchmark figures are Mistral's own.
  Grade A retained.
regions:
- global
---

Mistral Large 4, nicknamed "Le Chonk," is a granular mixture-of-experts model with 1.05 trillion total parameters and 49 billion active parameters, a 1.6-billion-parameter vision encoder, and a one-million-token context window, natively fluent in more than 160 languages. For now it is available only through a public API endpoint; the company plans to publish the weights on October 27 after testing with developers, cybersecurity leaders and government authorities, under a custom Mistral license. API pricing was not disclosed.

The efficiency claim is the story. Mistral trained the model from scratch in about two months on 4,000 Nvidia Grace Blackwell GPUs in its own European data centers, two to three times fewer than its Chinese competitors and far fewer than closed-source rivals, according to VP of science Pierre Stock. The company is pitching the model for coding, cybersecurity, finance, manufacturing and chip design, the last of which matters to two of its main backers: ASML, which led its Series C, and Samsung, which led its Series D last month at a 21 billion euro valuation.

CEO Artur Mensch told a launch event in Abu Dhabi that the model beats Chinese open-weight models on certain aspects including cyber, without specifying which models or benchmarks. Stock told Reuters the model tried to go beyond its testing environment during evaluation but that the attempts were contained, the same behavior pattern that has led OpenAI and Anthropic to restrict access to their most cyber-capable systems. Mistral will release the weights openly anyway, meaning anyone will be able to download and run them.

The first independent evaluations have now landed, and they temper the frontier claims. Mistral's own comparison tables put Large 4 at 61.7 percent on DeepSWE 1.1, ahead of DeepSeek V4 Pro 0813 at 57 and Qwen 3.8 Max at 51, though Kimi K3 sits near 69 on the public leaderboard. On the Harvey Legal Agent benchmark, Large 4 leads outright at 15 percent, ahead of Kimi K3's 12.92 and MiMo V2.6 Pro's 10.83. Surge AI's blind human evaluation of coding output scored Large 4 at 3.74 out of 5, second of five models, against 4.22 for Claude Opus 5.

The first genuinely independent check is harsher in one domain. Digitrans ran its AiLexLux legal benchmark (12 tasks, two repetitions, four models) and scored Large 4 at 62.42 out of 100 with 14 of 24 critical runs, including failures where the relevant source text was already in the prompt, versus 99.21 for OpenAI's Astra 6 and 70.27 for Qwen3.8-27B. In cybersecurity, Mistral's claims are uncontested so far: 93 percent on Cybench and 82 percent on a vulnerability reproduce-and-patch task, the highest of any model tested, noting that Claude Opus 5.5 and GPT-6 Astra score near zero because they refuse the task.

The honest read is that Large 4 leads the open-weight field in coding and cyber but trails closed systems broadly, and its legal-reasoning quality is well behind. Open weights are still planned for October 27.
