---
title: "Chainalysis breach exposes credentials and live tokens for all users"
date: 2026-11-07T07:14:12-05:00
last_updated: 2026-11-07T07:14:12-05:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Chainalysis now says names, usernames, password hashes and live tokens for all of its users were exposed in a cyberattack, a far wider disclosure than its first notice on October 30."
why_it_matters: "Chainalysis supplies blockchain tracing to law enforcement and exchanges worldwide, so working credentials for every account put investigative infrastructure itself at risk until all tokens are rotated."
featured: false
evidence_grade: "B"
sources:
  - title: "Chainalysis confirms user credentials exposed in cyberattack, takes services offline"
    publisher: "crypto.news"
    url: "https://crypto.news/chainalysis-confirms-user-credentials-exposed-in-cyberattack-takes-services-offline/"
    published: "2026-11-06"
  - title: "Chainalysis, which watches the blockchain, says hackers took credentials for every user"
    publisher: "Rews"
    url: "https://rews.cc/a/chainalysis-which-watches-the-blockchain-says-hackers-took-c-ddb2f8"
    published: "2026-11-06"
tags: []
data_as_of: "Chainalysis incident disclosures of October 30 to November 4, 2026, as reported November 6, 2026; the all users scope rests on the company's November 4 update."
---

Chainalysis, the blockchain analytics firm whose tracing tools are used by police forces, tax authorities and crypto exchanges, has disclosed that a cyberattack exposed credentials belonging to every one of its users. In an update this week the company said it discovered on Monday, November 2 that customer information including names, usernames, password hashes and live tokens for all Chainalysis users had been exposed to a malicious actor.

The disclosure is a sharp escalation from the company's first notice. When Chainalysis confirmed the intrusion on October 30, it said an external actor had used what it described as offensive agentic techniques, meaning AI agent assisted intrusion methods, to reach its systems and internal tools, and that the data accessed was limited to non-sensitive profile details such as user IDs, names, email addresses and organisation role labels, with no sign that authentication credentials or session tokens had been touched. A separate on-path attack, in which traffic between endpoints is intercepted, also exposed a subset of customer passwords; the company says that route has been found and closed.

Chainalysis took its login portal and several products offline after detecting abnormal activity, including the Reactor investigations tool, Data Solutions, the KYT transaction monitoring interface and API, and its address screening products. Customers are being required to reset passwords and rotate API keys before returning, with access restored through approved IP addresses. Live tokens matter because they are bearer credentials: whoever holds a still valid token is treated by the platform as the legitimate user, with no password needed.

The company says it has no evidence that investigation data was accessed or that its attribution data, the labels tying wallet addresses to real world entities, was manipulated, and it has not named the attacker or said how many accounts were improperly accessed. It also says the incident has no link to the 6.3 billion dollar Binance theft that the FBI attributed to North Korea. The hashing algorithm used for the exposed passwords has not been disclosed.
