---
title: "ConnectWise suspends cloud backup services after unauthorized access"
date: 2026-10-19T07:13:09-04:00
last_updated: 2026-10-22T08:42:58-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Microsoft has attributed the ConnectWise supply chain compromise to Storm-0940, a China aligned espionage group that it says used AI agents in the ARTEX framework to attempt sign-ins to more than 2,250 Microsoft 365 tenants at up to 2,900 attempts a minute and won persistent privileged access at numerous organizations."
why_it_matters: "The attribution turns a vendor service suspension into a measured espionage campaign: Microsoft says the attackers abused application credentials customers had already granted to ConnectWise, changed application credentials to keep access after the original ones were revoked, and in some cases moved from first targeting to privileged cloud access in under three hours."
featured: false
evidence_grade: "A"
sources:
  - title: "ConnectWise turns off its SaaS-y backup, security, and management services to probe security SNAFU"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/19/connectwise-turns-off-its-saas-y-backup-security-and-management-services-to-probe-security-snafu/5303758"
    published: "2026-10-19"
  - title: "AI-driven, large-scale nation-state campaign using ARTEX enables supply chain compromise"
    publisher: "Microsoft Security Blog"
    url: "https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/"
    published: "2026-10-21"
  - title: "Microsoft says ConnectWise breach let Chinese spies loose on 2,250 cloud tenants"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/22/microsoft-says-connectwise-breach-let-chinese-spies-loose-on-2250-cloud-tenants/5304687"
    published: "2026-10-22"
tags: []
data_as_of: "ConnectWise advisory October 16, 2026, covering access detected October 15; services still unavailable as of 16:00 UTC on October 18, 2026. The Register report published October 19, 2026 and read in full, reporting both ConnectWise's own advisory and Huntress's independent findings, which differ in severity. Update: Microsoft Security Blog post of October 21, 2026, read in full; the Storm-0940 attribution, the tenant and attempt counts and the attack timeline are Microsoft's own. The Register report of October 22, 2026, read in full, reporting Microsoft's disclosure and ConnectWise chief executive Manny Rivelo's comment on restoration."
update_bump: true
---

**Latest:** Microsoft has named the actor behind the ConnectWise compromise. In a post published on October 21, Microsoft said Storm-0940, a China state aligned group active since 2021, was responsible for the compromise of the ConnectWise multi-tenant application, and that the group used ARTEX, an open source penetration testing framework run by AI agents, to automate its attacks. Microsoft said the group attempted to sign in to more than 2,250 Microsoft 365 tenants at a peak of 2,900 attempts a minute, using ConnectWise application credentials that customers had already granted, so no interactive user sign-in was needed. In multiple environments the agents then carried out reconnaissance through Microsoft Graph, changed application credentials and tried to modify privileges, steps Microsoft said could keep the attackers in place after the original credentials were revoked. Microsoft said the group won persistent privileged access at numerous organizations, and that in several cases the time from first targeting to privileged access was under three hours. It cautioned that an affected application or a successful sign-in does not by itself mean customer data was accessed or taken, and it has not said how many customers were compromised or whether data was stolen.

The wider campaign predates the ConnectWise disclosure. Microsoft said Storm-0940 has used ARTEX since September against hundreds of organizations worldwide, in sectors including government, defense, banking, manufacturing and technology. Between October 10 and 14 it recorded more than 151,000 failed sign-in attempts against 327 accounts at eight organizations, with no successful logins from that password spraying. The ConnectWise application access followed on October 15. ConnectWise chief executive Manny Rivelo told The Register the company had contained the affected application connections and was gradually restoring services, while noting that closing those connections would not necessarily remove attackers who had already established a foothold in customer environments.

ConnectWise, which sells software to managed service providers, has initiated a service interruption for several of its offerings after detecting unauthorized access. In an advisory published on October 16, the company said that on October 15 it identified unauthorized access to application identities within its Cloud Backup environment, formerly known as SkyKick.

Because SaaS Security and Cloud Management are integrated with Cloud Backup, those services have also been suspended out of an abundance of caution while investigation and remediation continue, the company said. As of 16:00 UTC on October 18 the services remained unavailable, which means end users cannot back up data, access their archives, or restore data. ConnectWise said existing archives remain encrypted, isolated and preserved, with no evidence of unauthorized access to them, and that it has disabled some integrations between Cloud Backup and Exchange, Teams and SharePoint Online. It said it cannot discuss threat actor attribution at this time.

Security firm Huntress offered a starker account. It wrote that a Microsoft 365 credential, an API secret belonging to ConnectWise Cloud Backup, has been compromised and is being used to gain unauthorized access to customers' Microsoft 365 environments. In one Huntress partner tenant, it said, a second ConnectWise application gave itself Global Administrator rights and then added new credentials to two other applications in that tenant. Huntress warned that disabling the Microsoft 365 apps will not remove credentials that were already added, and that administrators must review the credentials on all of their Microsoft 365 applications.

The structure of the market is what makes the incident consequential. ConnectWise does not know its partners' customer setups, because the managed service providers manage those relationships, and end user organizations may not know ConnectWise is part of their service at all. Businesses that serve managed service providers are a frequent target precisely because compromising one platform can open a route to many providers and their customers, as the 2021 attack on Kaseya showed.
