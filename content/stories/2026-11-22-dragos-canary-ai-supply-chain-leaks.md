---
title: "Two million bait prompts expose leaks across AI supply chain"
date: 2026-11-22T07:05:32-05:00
last_updated: 2026-11-22T07:05:32-05:00
beats: ["technology"]
regions: ["global"]
status: "story"
lede: "Dragos researchers sent nearly two million prompts carrying unique trackable secrets to AI providers over five months and found evidence that at least three providers were breached and that privacy settings were widely ignored."
why_it_matters: "Prompts routinely carry source code, credentials and customer data, and this is the first large-scale evidence that the inference supply chain leaks them through breaches, reseller logging and ignored retention flags."
featured: false
evidence_grade: "B"
sources:
  - title: "AI Supply Chain Security: What Canary Tokens Found"
    publisher: "Dragos"
    url: "https://www.dragos.com/blog/ai-supply-chain-security-canary-tokens"
    published: "2026-11-19"
  - title: "Researcher plants 2m canaries into the AI supply chain. A privacy disaster surfaced."
    publisher: "Ars Technica"
    url: "https://arstechnica.com/security/2026/11/a-leaky-ai-supply-chain-is-exposing-secret-user-data-at-an-alarming-rate/"
    published: "2026-11-20"
tags: []
data_as_of: "Dragos research published November 19, 2026 covering prompts sent July through November 2026, read in full in this run; Ars Technica's independent write-up of November 20, 2026. Findings are Dragos's own observations; the breached providers are not named in the report."
---

Security firm Dragos has published the results of a five-month experiment in which it sent approximately two million AI prompts, each carrying a unique trackable secret such as an AWS key, a URL or a DNS name, to widely used AI services and watched where the secrets surfaced. The findings, published November 19, are threefold: attackers had breached at least three hosting providers, marketplace resellers could read and retain customer prompts through ordinary logging, and providers repeatedly failed to honor privacy settings including Zero Data Retention flags.

The breach finding is the most serious. In the largest case, a couple of hundred of Dragos's bait AWS keys were stolen, each sent in exactly one request to one provider within a few short windows in late October, and every request sent during those windows was taken, including some the provider rejected before a model ever ran. That pattern told the researchers the attacker was copying requests at the provider's front door. The stolen keys were then tested, used to list S3 buckets and search Secrets Manager, and used in tens of thousands of AWS API calls. None of the three providers knew it had been breached until Dragos notified it, and the earliest incident dates to mid-July.

The second finding required no exploit. Sellers on an AI inference marketplace could list a model at the lowest price, enable request logging and wait; in one case, someone on a home broadband connection opened both secret URLs from two prompts about a day and a half later and began guessing usernames at the login page they pointed to.

The third finding concerns privacy flags that customers pay for in trust. One Chinese AI lab's systems fetched the secret URLs from more than half of the prompts sent to its models between July and October, including roughly two-thirds of those marked as no data collection or Zero Data Retention. Prompts sent to US hosting providers that resell that lab's models triggered the same scraper, so a customer who chose a US provider to keep data in the US did not get what it paid for. In the strangest incident, a secret link was posted into a company Feishu chat 24 days after the prompt was sent, and opened from three desktops and three phones in Beijing and Shanghai within two minutes.

Dragos's conclusion is blunt: Zero Data Retention is supposed to mean something, and in practice these prompts were retained, shared with other companies and read by people. The providers involved are not named in the report, which limits how far customers can act on it, but the method, seeding one unique secret per prompt so any use identifies the leaking link in the chain, is reproducible by any large AI buyer.
