---
title: "AWS agent platform flaws let prompts steal cloud credentials"
date: 2026-10-10T07:14:35-0400
last_updated: 2026-10-10T07:14:35-0400
beats: ["technology"]
regions: ["global"]
status: "story"
lede: "Researchers showed a single chat prompt could steal temporary cloud credentials from AWS Bedrock AgentCore agents by tricking them into querying their own instance metadata endpoint."
why_it_matters: "It is a concrete supply-chain-scale flaw in the agent layer AWS is selling to enterprises: overpermissioned default roles meant one compromised agent could read other agents' sessions, pull container images, and fetch secrets."
featured: false
evidence_grade: "B"
sources:
  - title: "AWS AgentCore security undone by prompt requesting credentials"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/09/aws-agentcore-security-undone-by-prompt-requesting-credentials/5302436"
    published: "2026-10-09"
tags: []
data_as_of: "Flaws disclosed by Zenity Labs October 9, 2026, after private disclosure to AWS in December 2025; fixes confirmed September 29, 2026. Details from The Register's October 9 reporting (article read in full) based on Zenity Labs' write-up. AWS disputed the characterization after publication; The Register asked for clarification and it had not arrived at publish time."
---

Zenity Labs researchers Tamir Ishay Sharbat and Lana Salameh demonstrated that AWS Bedrock AgentCore had a server-side request forgery flaw allowing credential theft with a single chat prompt. An attacker could ask an exposed agent to fetch its instance metadata endpoint, then harvest temporary IAM credentials. Firecracker MicroVM network isolation proved insufficient, and the default AgentCore IAM role was overpermissioned: scoped to all AgentCore resources in the region rather than a single agent.

That scope meant the attack could go much further than one set of credentials. Zenity found an attacker could enumerate agents, read sessions and conversations, pull container images, write agent memories, fetch Secrets Manager secrets, and persistently hijack agent behavior. The researchers disclosed the issues to AWS in December 2025 and followed up in January 2026; AWS called the report "informative" and closed it on April 12, 2026, after making IMDSv2 exclusive that February. The overprivileged default role remained until a September 29, 2026 review confirmed the fixes.

Amazon told The Register after publication that the research misrepresents documented behavior and that developer error would be required for the attack to work. The Register asked for clarification and had not received it at publish time. The disclosure adds to a growing file of agent-infrastructure flaws discovered this year, and it lands as enterprises are being asked to trust managed agent runtimes with production data.
