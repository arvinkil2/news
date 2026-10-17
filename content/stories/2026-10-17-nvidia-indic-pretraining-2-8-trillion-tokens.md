---
title: "Nvidia releases 2.8 trillion token Indic pretraining corpus"
date: 2026-10-17T07:04:16-04:00
last_updated: 2026-10-17T07:04:16-04:00
beats: ["technology"]
regions: ["asia-pacific"]
status: "story"
lede: "Nvidia and AI4Bharat at IIT Madras have built a pretraining corpus of about 2.8 trillion tokens across 22 Indian languages, and are releasing the open data generation pipeline used to create it."
why_it_matters: "Indic languages are the largest under served language group in model training; an open corpus and recipe at this scale lowers the barrier for every builder targeting India's users."
featured: false
evidence_grade: "B"
sources:
  - title: "Scaling Indic Pretraining: 2.8 Trillion Tokens and an Open Data Generation Pipeline"
    publisher: "Hugging Face"
    url: "https://huggingface.co/blog/nvidia/scaling-indic-pretraining"
    published: "2026-10-16"
tags: []
data_as_of: "Corpus announced October 16, 2026 (Nvidia and AI4Bharat, via Hugging Face). Token counts use the Gemma-4 tokenizer as stated by the authors; benchmark gains are from the Nemotron 3.5 Super VL technical report as cited in the release."
---

Nvidia, working with AI4Bharat at IIT Madras, has introduced Nemotron-pretraining-Indic-v1, a corpus of approximately 2.8 trillion tokens across the 22 languages listed in India's constitution, the first languages of nearly 1.2 billion people at the 2011 census. The corpus contains 2,601.0 billion native script tokens and 224.6 billion romanized tokens across 34 language and script configurations, and the team is also releasing the open, GPU accelerated pipeline used to generate it.

The pipeline translates curated English source material, including mathematics, code and question answering content, then scores each output for meaning, fluency, terminology, style and formatting, retaining only outputs scoring at least 75 out of 100 and repairing lower scoring ones. The repair process recovered 438.4 billion tokens already included in the total. The authors are explicit about limits: translated data does not replace text originally written in Indian languages, and quality assessment is primarily automated with sampled human review.

In a continued pretraining stage for Nemotron 3.5 Super VL, 10 billion Indic tokens drawn from the corpus and natural text were included in a 100 billion token budget, and scores rose on all five reported Indic benchmarks, with gains from 4.98 to 9.82 percentage points. The release frames the comparison carefully as a stage level result for the combined synthetic and natural mixture, not an isolated effect of the synthetic corpus.
