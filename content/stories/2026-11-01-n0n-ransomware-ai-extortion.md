---
title: "Ransomware crew spent 7,216 dollars on AI, entered by passwords"
date: 2026-11-01T07:18:40-05:00
last_updated: 2026-11-01T07:18:40-05:00
beats: ["technology"]
regions: ["global"]
status: "story"
lede: "SOCRadar researchers who found the n0n ransomware operator's own server exposed say the crew spent more than 7,216 dollars on AI services to write attack scripts, yet breached 23 organisations in 14 countries using only weak or stolen credentials, exploiting no vulnerability at all."
why_it_matters: "It is the clearest documented case yet of what AI actually does for working criminals: it industrialises the scripting around ordinary credential theft, while the entry point defenders must fix remains the password, not the exploit."
featured: false
evidence_grade: "C"
sources:
  - title: "Crim spent $7K+ on AI services in extortion attacks, then left evidence for all to see"
    publisher: "The Register, reporting SOCRadar research"
    url: "https://www.theregister.com/security/2026/10/30/crim-spent-7k-on-ai-services-in-extortion-attacks-then-left-evidence-for-all-to-see/5306754"
    published: "2026-10-30"
tags: []
data_as_of: "Single research origin: SOCRadar investigation as reported by The Register, October 30, 2026, read in full in this run; victim counts, spend and methods are SOCRadar's findings from the exposed server, evidence capped at C. n0n's own victim claims (108 claimed victims) are the gang's, unverified on chain per SOCRadar."
---

The most instructive AI attacker of the season left his own front door open. Threat intelligence firm SOCRadar found the workspace of the n0n ransomware operator running as a publicly accessible file server in Sweden, and documented 1,719 files across snapshots on September 25 and 26: attack scripts, ransomware source code, extortion infrastructure and an AI coding agent environment. The operator, a newcomer that has claimed 108 victims since emerging last month, had spent more than 7,216 dollars on AI services by October 22, using an open source coding agent configured with 154 model entries across seven providers, including Gemini, Mistral, Claude, GPT-5.x, Grok, DeepSeek and several models marketed as uncensored.

What the AI did not do is get him in. SOCRadar's chief information security officer Ensar Seker told The Register that in every documented compromise in the investigation, 23 organisations across 14 countries, access relied on weak or stolen credentials, through Remote Desktop Protocol scanning, automated FortiGate VPN credential stuffing, exposed cloud keys and reused hosting sessions, and that the firm found no evidence of vulnerability exploitation in any case. In one intrusion, an exposed AWS key let the crew pull data from 40 S3 buckets, up to 110 gigabytes each, and delete data including bank transaction archives across 12 sensitive buckets. The AI's role was downstream: writing and debugging hundreds of scripts that turned basic access into tailored operations, including data theft, encryption, deletion of backups and, in one case, firewall changes that a decryption key alone cannot undo.

The group's largest single action was listing 38 maritime, port and logistics organisations across 18 countries on October 12, at least 21 of them linked by other researchers to customers of South Korean maritime software provider CyberLogitec, with ransom demands from 400,000 to 28 million dollars. After the October 19 deadline none of the 38 was marked settled and no payment address showed a transaction; the stolen data was published. SOCRadar rates the gang 10 out of 10 for aggressiveness and zero for lethality, and has validated no ransom payments on chain despite a handful of victims marked as having paid.

Seker's verdict frames the defensive lesson: a striking gap between operational ambition and security discipline. The operation had hardcoded encryption keys, reused across victims, and an exposed server, while spending thousands on AI assistance. For defenders the priority order is unchanged by the AI layer: credential hygiene, exposed keys and VPN access are where these intrusions begin.
