---
title: "LiteLLM attack traced to master key exposed on GitHub"
date: 2026-10-27T07:00:00-04:00
last_updated: 2026-10-27T07:14:47-04:00
beats: ["technology"]
regions: ["global"]
status: "story"
lede: "LiteLLM has traced last week's supply chain attack on its open source AI gateway to a master key committed to a public GitHub repository in May and never revoked, in a postmortem reported by The Register."
why_it_matters: "LiteLLM sits in front of enterprise AI traffic, routing requests and holding provider keys, and about 49,000 downloads of the poisoned release in under two hours, per Wiz figures cited in the report, makes this the clearest case yet of an AI gateway as a supply chain target."
featured: false
evidence_grade: "C"
sources:
  - title: "LiteLLM supply chain attack started with an exposed master key"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/26/litellm-supply-chain-attack-started-with-an-exposed-master-key/5305544"
    published: "2026-10-26"
tags: []
data_as_of: "Single sourced: The Register report of October 26, 2026, reporting LiteLLM's own postmortem of October 24; download count is Wiz's, as cited by The Register. Evidence grade capped at C."
---

The attack on LiteLLM began with a key that should have died in May. In its postmortem, reported by The Register, the project says a configuration file containing a master key was committed to the public LiteLLM-Labs/lite-harness repository on May 27. Developers spotted and removed the commit quickly, but did not revoke the key. On October 10, an attacker used it to enter the LiteLLM Agent Platform and extract a GitHub CLI OAuth token, which the project says gave owner level access to all its repositories, because such tokens do not trigger GitHub's additional authentication flows for high impact actions.

From there the chain ran through trust. The attacker planted malicious commits in internal repositories, including workflows designed to steal tokens available during continuous integration, and collected further tokens belonging to two engineers with maintainer privileges and to internal systems, with a primary focus on upstream inference API tokens. Last Wednesday a poisoned version 1.107.0 of the gateway was published to PyPI and container registries, carrying an infostealer and a remote access trojan. It was available for under two hours before quarantine and was downloaded about 49,000 times in that window, according to Wiz figures cited in the report.

The payload was built for exactly the environment an AI gateway runs in. The Register reports it harvested browser credentials and cookies, AWS credentials, Google Cloud service account keys, Azure tokens, and API keys for OpenAI, Anthropic, Cohere and other model providers. Anyone who installed and ran version 1.107.0 should assume credentials reachable from that system may have been stolen and rotate them.

LiteLLM says it is revoking every token associated with every internal system and vendor platform, and called the incident a strong illustration of the risks of failing to rotate a potentially exposed key. The sector lesson is structural: gateways concentrate the keys to every provider a company uses, which is why Aiven's gateway product in yesterday's edition exists, and why a gateway's own key hygiene is now a diligence question for every enterprise routing traffic through one. This story is single sourced and graded accordingly.
