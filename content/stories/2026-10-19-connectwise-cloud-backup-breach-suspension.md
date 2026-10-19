---
title: "ConnectWise suspends cloud backup services after unauthorized access"
date: 2026-10-19T07:13:09-04:00
last_updated: 2026-10-19T07:13:09-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "ConnectWise has suspended its Cloud Backup, SaaS Security and Cloud Management services after detecting unauthorized access to application identities on October 15, leaving managed service providers unable to back up or restore customer data while the investigation continues."
why_it_matters: "ConnectWise sits upstream of thousands of managed service providers and their customers, so a compromised platform credential is a supply chain risk of the kind made notorious by the 2021 Kaseya attack, and security firm Huntress says a compromised Microsoft 365 secret is already being used against customer tenants."
featured: false
evidence_grade: "B"
sources:
  - title: "ConnectWise turns off its SaaS-y backup, security, and management services to probe security SNAFU"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/19/connectwise-turns-off-its-saas-y-backup-security-and-management-services-to-probe-security-snafu/5303758"
    published: "2026-10-19"
tags: []
data_as_of: "ConnectWise advisory October 16, 2026, covering access detected October 15; services still unavailable as of 16:00 UTC on October 18, 2026. The Register report published October 19, 2026 and read in full, reporting both ConnectWise's own advisory and Huntress's independent findings, which differ in severity."
---

ConnectWise, which sells software to managed service providers, has initiated a service interruption for several of its offerings after detecting unauthorized access. In an advisory published on October 16, the company said that on October 15 it identified unauthorized access to application identities within its Cloud Backup environment, formerly known as SkyKick.

Because SaaS Security and Cloud Management are integrated with Cloud Backup, those services have also been suspended out of an abundance of caution while investigation and remediation continue, the company said. As of 16:00 UTC on October 18 the services remained unavailable, which means end users cannot back up data, access their archives, or restore data. ConnectWise said existing archives remain encrypted, isolated and preserved, with no evidence of unauthorized access to them, and that it has disabled some integrations between Cloud Backup and Exchange, Teams and SharePoint Online. It said it cannot discuss threat actor attribution at this time.

Security firm Huntress offered a starker account. It wrote that a Microsoft 365 credential, an API secret belonging to ConnectWise Cloud Backup, has been compromised and is being used to gain unauthorized access to customers' Microsoft 365 environments. In one Huntress partner tenant, it said, a second ConnectWise application gave itself Global Administrator rights and then added new credentials to two other applications in that tenant. Huntress warned that disabling the Microsoft 365 apps will not remove credentials that were already added, and that administrators must review the credentials on all of their Microsoft 365 applications.

The structure of the market is what makes the incident consequential. ConnectWise does not know its partners' customer setups, because the managed service providers manage those relationships, and end user organizations may not know ConnectWise is part of their service at all. Businesses that serve managed service providers are a frequent target precisely because compromising one platform can open a route to many providers and their customers, as the 2021 attack on Kaseya showed.
