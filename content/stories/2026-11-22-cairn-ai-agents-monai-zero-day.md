---
title: "AI agents found a zero-day alone and took over a server"
date: 2026-11-22T07:05:32-05:00
last_updated: 2026-11-22T07:05:32-05:00
beats: ["technology"]
regions: ["asia-pacific", "north-america"]
status: "story"
lede: "Amazon Threat Intelligence says a China-linked operator's autonomous AI agents, given only the goal of obtaining shell access, found a previously unknown flaw in the MONAI Label medical imaging application in about 11 minutes and used it to gain root control of a university server."
why_it_matters: "This is a documented case of AI agents discovering and exploiting a zero-day without human direction against a live target, which compresses the time defenders have between a flaw existing and it being used."
featured: false
evidence_grade: "B"
sources:
  - title: "China attackers deployed AI agents that autonomously found and exploited a 0-day to take over a university server"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/11/20/china-attackers-deployed-ai-agents-that-autonomously-found-and-exploited-a-0-day-to-take-over-a-university-server/5311382"
    published: "2026-11-20"
  - title: "Hackers use autonomous AI tool Cairn to find zero-day, take over server"
    publisher: "BleepingComputer"
    url: "https://www.bleepingcomputer.com/news/security/hackers-use-autonomous-ai-tool-cairn-to-find-zero-day-take-over-server/"
    published: "2026-11-20"
tags: []
data_as_of: "Amazon Threat Intelligence report published November 20, 2026 on a campaign of September 8 to 10, 2026, reported the same day by The Register and BleepingComputer from Amazon's account; attribution to a China-linked actor is Amazon's assessment at moderate confidence. Both reports read in this run."
---

Suspected Chinese spies deployed AI agents that worked autonomously to find a zero-day in an open source application and abuse it to break into university networks, gaining full control of a server, according to Amazon chief information security officer CJ Moses. Amazon Threat Intelligence published the account on November 20; the campaign itself ran for about 48 hours beginning September 8 against universities in East Asia outside mainland China.

The operator used Cairn, an open source penetration testing framework, and left its server publicly hosted without authentication, which is how Amazon found it on September 10 and read the campaign's own records. The prompts were written in Simplified Chinese and timestamps in the executed scripts were set to China Standard Time, the basis for Amazon's moderate-confidence attribution.

The agents were persistent before they were successful. Against one university's Redis server they ran about 148 sequential actions over roughly 16 hours, abusing the replication feature, escaping the scripting sandbox, writing to configuration files and corrupting memory, and when that failed they tried a Log4Shell injection, a server-side request forgery attack against a co-located Qdrant instance and credential sprays against PostgreSQL and SSH.

The breakthrough was MONAI Label, an open source medical imaging AI application. The agents identified the framework, mapped its API endpoints and found an upload endpoint with a filename parameter carrying a path traversal flaw. In about 11 minutes they went from mapping the API to writing files arbitrarily on the server, and in a later session they used the same flaw to plant a Python reverse shell that ran as root. Amazon, which assesses with high confidence that the flaw was a genuine zero-day, notified the project's maintainers, who released a fix and a security advisory on November 18.

Amazon's discovery follows an earlier Gambit Security report documenting a Chinese operator using Cairn in at least 105 attacks against companies including a Fortune 500 hospitality firm and a major US airline. Together the cases show autonomous agents adapting for nearly a full day without human direction, which is the operational change defenders now have to plan around.
