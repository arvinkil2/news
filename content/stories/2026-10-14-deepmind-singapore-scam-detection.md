---
title: "DeepMind and Singapore build on-device AI scam detector"
date: 2026-10-14T07:06:02-04:00
last_updated: 2026-10-14T07:06:02-04:00
beats: ["technology"]
regions: ["asia-pacific"]
status: "story"
lede: "Google DeepMind and GovTech Singapore announced a fine-tuned Gemma model that detects scam conversations entirely on a user's device, in a country that has lost more than S$4 billion to scams since 2019."
why_it_matters: "It is a working example of AI safety tooling that does not require reading private messages in the cloud, which is the design constraint that has stalled anti-scam features on encrypted platforms elsewhere."
featured: false
evidence_grade: "B"
sources:
  - title: "On-device AI against scams: Google DeepMind and MDDI"
    publisher: "Google DeepMind"
    url: "https://deepmind.google/blog/on-device-ai-scam-detection-mddi/"
    published: "2026-10-14"
tags: []
data_as_of: "Announced Oct 14, 2026 at Singapore International Cyber Week, under the National AI Partnership with the Singapore Government. Loss figures cited by DeepMind from Straits Times reporting. Rollout is phased; no deployment date given."
---

Google DeepMind and the Government Technology Agency of Singapore have built a scam detection model that runs on the phone rather than in the cloud. Announced October 14 at Singapore International Cyber Week, the system fine-tunes Google's lightweight Gemma model on local scam conversations, including impersonations of public institutions, banks and public figures, so it can recognize regional manipulation patterns that generic models miss.

The need is quantified. Scams account for more than half of Singapore's reported crimes and more than S$4 billion in losses since 2019, and social-engineering scams, where attackers build trust over a conversation before asking for money, now account for up to 80 percent of losses, according to figures DeepMind cited. The detector uses a two-stage pipeline: a low-power classifier screens incoming messages, and the fine-tuned model then analyzes a wider slice of the conversation to confirm a threat or clear a false alarm, triggering a real-time warning on the device before money or credentials move.

The governance terms are the point of the design. Training happened inside GovTech's managed cloud environment, used anonymized data from scam reports and intelligence feeds with no citizen data, and the deployed model accesses conversations only with user consent. Because analysis stays on-device, neither Google nor the Singapore government can read users' chats through the system. That addresses the standing objection to server-side scanning on encrypted messengers, and DeepMind says it is exploring deployments in other countries. The test now is accuracy in the wild: false alarms erode trust in warnings, and scammers adapt scripts faster than models are retrained.
