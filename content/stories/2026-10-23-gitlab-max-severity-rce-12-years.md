---
title: "GitLab patches maximum severity flaw spanning 12 years"
date: 2026-10-23T07:16:41-04:00
last_updated: 2026-10-23T07:16:41-04:00
beats: ["technology"]
regions: ["global", "north-america"]
status: "story"
lede: "GitLab has patched a maximum severity integer overflow flaw, CVE-2026-110264, that could let unauthenticated attackers execute arbitrary code on self managed servers, affecting releases back to GitLab 7.0 in June 2014."
why_it_matters: "GitLab servers hold source code, deployment secrets and pipeline credentials for more than 50 million registered users, so a perfect 10 severity flaw in 12 years of releases is a supply chain emergency for every team that self hosts its code."
featured: false
evidence_grade: "C"
sources:
  - title: "Max-severity GitLab bug allows remote code execution over 12 years of releases"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/22/max-severity-gitlab-bug-allows-remote-code-execution-over-12-years-of-releases/5304854"
    published: "2026-10-22"
tags: []
data_as_of: "GitLab release of Wednesday, October 22, 2026, as reported by The Register the same day, read in full. Single sourced to The Register's report of GitLab's own release notes, hence grade C. Fixed version numbers and the CVE identifier are GitLab's, as quoted there."
---
GitLab on Wednesday patched a vulnerability with the highest possible severity rating, a perfect 10, in the software that hosts source code for much of the technology industry. The flaw, tracked as CVE-2026-110264, is an integer overflow in regular expression compilation in GitLab Community Edition and Enterprise Edition. Under certain conditions, GitLab said, it could have allowed an unauthenticated user to execute arbitrary code on the GitLab server using a specially crafted regular expression.

The affected range is the alarming part: releases dating back to GitLab 7.0, released in June 2014, a full 12 years of versions. Fixes were released in versions 19.5.1, 19.4.3 and 19.3.6, and backported to 19.2.9, 19.1.9, 19.0.10 and 18.11.13. GitLab strongly recommends that all organisations running vulnerable software upgrade as soon as possible. Its own hosted services, GitLab.com and GitLab Dedicated, are already patched, and it released two threat detections for self managed customers. The flaw was reported by bug hunter Johan Carlsson through GitLab's HackerOne programme.

The exposure is what sits on the server. As threat detection firm SOC Prime put it in a warning quoted by The Register, GitLab repositories frequently contain source code, CI and CD configuration, deployment secrets, access tokens and infrastructure definitions, so server level compromise can lead to credential theft, repository manipulation, supply chain attacks and lateral movement into production environments. GitLab claims 50 million registered users and more than half of the Fortune 100.

There is no indication yet of exploitation in the wild. That reprieve is unlikely to last: last month attackers began battering another maximum severity GitLab flaw within days of its patch, according to CISA and private researchers. In a week defined by PHP2Shell exploitation at scale, self hosted GitLab instances are the next patching race.
