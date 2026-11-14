---
title: "Chinese labs trained models on Blackwell chips, report claims"
date: 2026-11-14T07:08:03-05:00
last_updated: 2026-11-14T07:08:03-05:00
beats: ["technology"]
regions: ["asia-pacific", "north-america"]
status: "story"
lede: "A forensic report by former OpenAI engineer Will DePue says the published weights of six Chinese AI models, including DeepSeek-V4-Pro, Kimi K3 and MiniMax-M3, carry the initialization fingerprint of Nvidia Blackwell systems that are barred from export to China."
why_it_matters: "If the method holds up, model weights themselves become evidence in export control enforcement, and the claim lands in the middle of the congressional push to codify tighter chip controls after the Huang resignation."
featured: true
evidence_grade: "B"
sources:
  - title: "Chinese AI labs are training models on Nvidia's Blackwell despite export controls, says ex-OpenAI engineer"
    publisher: "The Register"
    url: "https://www.theregister.com/ai-and-ml/2026/11/13/chinese-ai-labs-are-training-models-on-nvidias-blackwell-despite-export-controls-says-ex-openai-engineer/5309891"
    published: "2026-11-13"
tags: []
data_as_of: "Unemployment Labs forensic report published November 2026, reported by The Register on November 13, 2026; the report is a single researcher's analysis, attributed as such, with its stated limitations carried in the body."
---

United States export controls are not stopping Chinese AI labs from using restricted Nvidia chips, according to a forensic report by Will DePue, a former OpenAI engineer who left earlier this year to launch the research consultancy Unemployment Labs. The report says DeepSeek, Moonshot AI, MiniMax and Ant Group have gained access to Nvidia's Blackwell GPUs despite the export restrictions and are using that hardware to create their AI models, The Register reported.

The method is the story. Model weights must be initialized with starting values, and one common method uses a pseudorandom algorithm whose output pattern depends on the exact GPU and seed. DePue says traces of that pattern survive training into the published model. He says he searched more than six trillion combinations of chip layout and seed number and matched them to open weights models, finding what he calls conclusive evidence that six Chinese AI models, including DeepSeek-V4-Pro, Kimi K3 and MiniMax-M3, were initialized on Nvidia Blackwell systems. Four of the models match Grace Blackwell, the GB200 and GB300 parts in Nvidia's flagship rack scale systems. The report publishes initial seed values so others can attempt to reproduce the result, and DePue says senior researchers inside frontier labs have confirmed it.

The report carries its own limits, and they matter. Blackwell use does not prove where the GPUs were located, so some of the labs could have reached the hardware through providers outside China, a route the proposed Cloud Security Act aims to close. DePue notes this is the first time MiniMax and Ant Group have been publicly linked to Blackwell use.

A separate finding points the same way. Lava, an Israel based security company, said a few weeks ago that it had found 32 Nvidia B300 GPUs, part of the Blackwell Ultra generation, through publicly exposed monitoring endpoints with IP addresses geolocated to China. The political context is live: at least four bills aimed at limiting China's access to leading edge AI technology await consideration, including the AI Overwatch Act, the Chip Security Act, the Match Act and the Cloud Security Act, and Senators Jim Banks and Elizabeth Warren cited the Huang case on Monday as justification for passing the Overwatch Act.
