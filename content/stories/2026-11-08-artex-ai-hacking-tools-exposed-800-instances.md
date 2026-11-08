---
title: "Hundreds of Artex AI hacking tools found exposed online"
date: 2026-11-08T07:12:58-05:00
last_updated: 2026-11-08T07:12:58-05:00
beats: ["technology"]
regions: ["global", "asia-pacific"]
status: "story"
lede: "Security firm Censys found more than 800 deployments of Artex, an open source AI penetration testing tool linked to several cyberattacks, publicly accessible on the internet without a password."
why_it_matters: "The same misconfiguration problem defenders warn about in enterprise systems is now exposing the attackers' own AI tooling, complete with implants and attack data, which tells both sides how loosely autonomous hacking systems are being operated."
featured: false
evidence_grade: "B"
sources:
  - title: "Hundreds of Artex AI hacking tools found publicly exposed to the web"
    publisher: "TechCrunch"
    url: "https://techcrunch.com/2026/11/06/hundreds-of-artex-ai-hacking-tools-found-publicly-exposed-to-the-web/"
    published: "2026-11-06"
tags: []
data_as_of: "Censys scan findings published November 6, 2026 and reported the same day; Artex released publicly in July 2026. Attack attributions are as stated by Microsoft and CrowdStrike in the reporting."
---

Cybersecurity firm Censys says it identified more than 800 distinct deployments of Artex, an open source autonomous penetration testing tool, that were accessible from the web without a password. Artex is a Chinese made system of AI agents that Microsoft has described as able to conduct cyberattacks from reconnaissance through data exfiltration with little human interaction. It has been publicly available since July and is used both by authorised testers and by attackers who cannot access the guarded cybersecurity models of Anthropic or OpenAI.

Censys principal security researcher Silas Cutler said not every exposed instance is operated maliciously and many belong to authorised testers, but the software does not need to be reachable from the internet, and the exposed systems also reveal attack tooling, including implants used to maintain persistent access to victim networks. In at least one case the exposure ran the other way: CrowdStrike attributed attacks on the Korean finance industry in September in part to an Artex instance whose operator had left an open directory, and Censys says that instance had been publicly exposed for months and appeared to contain attack data extending well beyond South Korean banks, including payment and gaming companies.

Artex has also been linked to the October attack on IT support company ConnectWise, in which Microsoft said Chinese linked hackers used the tool to break into customers' cloud environments and steal data at a speed that left defenders little time to detect and respond. Many of the attacks linked to the tool exploited simple weaknesses, including weak or known passwords and missing multi-factor authentication.

Artex has since announced it will go closed source, limiting further releases to paid customers, but dozens of copies of its code remain available on code sharing sites and usable in active attacks. The finding is a useful corrective to the framing of AI hacking tools as a one directional threat: the operators deploying them are making the same basic configuration errors as the organisations they target.
