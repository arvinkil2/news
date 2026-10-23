---
title: "ConnectWise breach exposes 2,250 organisations to AI driven spying"
date: 2026-10-23T07:16:41-04:00
last_updated: 2026-10-23T07:16:41-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "China state aligned hackers breached ConnectWise's cloud backup service, stole application credentials linking it to customers, and used AI agents to target about 2,250 organisations at almost 3,000 attempted sign ins per minute, Microsoft researchers say."
why_it_matters: "A backup provider's credentials became a master key into thousands of Microsoft hosted environments, and the attackers' use of AI agents to compress the campaign into hours is the clearest evidence yet that AI has changed intrusion speed, not just intrusion skill."
featured: false
evidence_grade: "B"
sources:
  - title: "Chinese hackers spied on thousands of companies after breaching IT giant ConnectWise"
    publisher: "TechCrunch"
    url: "https://techcrunch.com/2026/10/22/chinese-hackers-spied-on-thousands-of-companies-after-breaching-it-giant-connectwise/"
    published: "2026-10-22"
  - title: "Microsoft says ConnectWise breach let Chinese spies loose on 2,250 cloud tenants"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/22/microsoft-says-connectwise-breach-let-chinese-spies-loose-on-2250-cloud-tenants/5304687"
    published: "2026-10-22"
tags: []
data_as_of: "Microsoft research reported October 22, 2026 by TechCrunch, read in full via search results, and The Register, read via search results the same day. Attribution to a China state aligned group, tracked by Microsoft as Storm-0940, is Microsoft's assessment. ConnectWise had not, in these reports, stated how many customers were successfully accessed."
---
The week's run of security failures widened sharply on Thursday. Microsoft security researchers say China state aligned hackers, tracked as Storm-0940, broke into ConnectWise's cloud backup service and stole the application credentials the service uses to establish data links with its corporate customers. With those credentials, the attackers could log into customers' Microsoft hosted environments as if they were an authorised application, and reach email and other files.

The scale and speed are what distinguish the campaign. Microsoft says the hackers used AI agents to target around 2,250 organisations at a rate of almost 3,000 attempted sign ins per minute, a pace that, in Microsoft's words, gives defenders little time to detect and respond. The Register reported that in some environments the attackers moved from picking a target to gaining privileged cloud access in less than three hours. The automation framework was ARTEX, an open source AI penetration testing tool that Microsoft says Storm-0940 has used since September against government agencies, defence contractors, banks, manufacturers and technology firms, and which was also used in a recent compromise of South Korea's financial systems.

ConnectWise, an IT management and remote access provider whose tools sit inside thousands of companies, said it has paused access to its cloud backup system and is investigating, and was working on restoring the service as of Thursday. The Register reported the company also pulled its SaaS Security and Cloud Management services after discovering unauthorised access to application identities. Reporting on the incident says ConnectWise's stored backup archives remain encrypted and isolated, with no indication they were compromised, which leaves each affected customer to audit its own Microsoft environment for access it did not authorise.

The structural lesson is the same one the LiteLLM attack taught on Wednesday, at larger scale. The credentials a trusted supplier holds to serve its customers are, once stolen, indistinguishable from the supplier itself. AI agents did not invent that weakness. They removed the labour constraint that used to limit how many victims it could be used against at once.
