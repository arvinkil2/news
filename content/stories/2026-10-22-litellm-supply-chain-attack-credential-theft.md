---
title: "LiteLLM attack steals credentials through poisoned AI gateway release"
date: 2026-10-22T07:09:53-04:00
last_updated: 2026-10-22T07:09:53-04:00
beats: ["technology"]
regions: ["global", "north-america"]
status: "story"
lede: "Attackers compromised LiteLLM's release process and shipped version 1.107.0 through PyPI and Docker on Wednesday with a credential stealer and a remote access trojan, in a package downloaded about 23 million times a week that sits next to cloud and AI provider keys."
why_it_matters: "LiteLLM is the gateway many teams put between their applications and every major model provider, so one poisoned release concentrates exactly the secrets, AWS, Google Cloud, Azure, OpenAI and Anthropic keys, that the malware was built to harvest."
featured: false
evidence_grade: "B"
sources:
  - title: "LiteLLM supply chain attack hoovers up passwords and secrets"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/21/litellm-supply-chain-attack-hoovers-up-passwords-and-secrets/5304548"
    published: "2026-10-21"
  - title: "LiteLLM suspects GitHub token leak in AI gateway logs behind malicious package release"
    publisher: "The Hacker News"
    url: "http://thehackernews.com/2026/10/litellm-suspects-github-token-leak-in.html"
    published: "2026-10-22"
tags: []
data_as_of: "Attack of October 21, 2026. The Register report of October 21, 2026, read in full, reporting analyses by Aikido Security, Wiz and Socket; corroborated by The Hacker News on October 22, 2026, read in full via search results, including BerriAI's statement that actions were taken through three engineers' GitHub accounts, apparently via stolen GitHub CLI OAuth tokens. Exposure window for unpinned installs: 11:39 to 13:23 UTC on October 21, per The Hacker News. This item was flagged single source in the morning gap check; an Event Registry search returned independent corroboration, including a Cloudsmith advisory of October 22, 2026 on the 1.107.0 compromise, alongside the targeted search corroboration above, which is what lifts it to grade B."
---

Unknown attackers compromised the release process of LiteLLM, the open source AI gateway built by BerriAI, and on Wednesday distributed a malicious version, 1.107.0, through PyPI and Docker registries. PyPI quarantined the release within hours and the Docker images were removed from Docker Hub and GHCR, but anyone who ran the compromised package should assume their secrets were stolen, security firms warned. The last safe version is 1.106.2.

The mechanics were designed for persistence. The payload came from malicious commits in a lookalike GitHub repository, Berri-AI with a hyphen, which fed three files into the release pipeline. One, cook.pth, makes Python run the second file, cook.py, every time the interpreter starts. That file is an infostealer with 16 modules targeting browsers, cloud providers and AI services: it harvests Chrome, Firefox, Edge and Safari credentials and cookies, AWS credentials and instance metadata, Google Cloud service account keys, Azure tokens, OpenAI, Anthropic and Cohere API keys, SSH and GPG keys and shell histories, encrypts the haul and posts it to an attacker controlled domain dressed up as a LiteLLM health check. The third file is a remote access trojan that spawns a daemon polling the attacker's infrastructure every hour for new commands.

BerriAI later said the release actions were taken through three engineers' GitHub accounts, apparently using stolen GitHub CLI OAuth tokens, with one account triggering the release run and another approving it. The exposure window was short because detection was fast: Socket's scanner flagged all seven wheels seven minutes after publication, and unpinned installs between 11:39 and 13:23 UTC are the affected population.

This is the second LiteLLM compromise of 2026, after a March incident that CloudSEK estimated potentially exposed more than 2,500 organisations and 434,000 CI and CD pipelines. A gateway downloaded about 23 million times a week, whose whole purpose is to hold every provider key in one place, is now a demonstrated repeat target, and the defence that worked this time was automated scanning speed, not prevention.
