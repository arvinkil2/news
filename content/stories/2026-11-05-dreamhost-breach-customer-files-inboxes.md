---
title: "DreamHost breach exposed customer files and inboxes for months"
date: 2026-11-05T07:05:45-05:00
last_updated: 2026-11-05T07:05:45-05:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "DreamHost confirmed hackers exploited a flaw in its file manager from August until October 23, stealing FTP and SFTP credentials and webmail logins for well under 10 percent of its roughly 400,000 paying customers."
why_it_matters: "A two month dwell time inside a mainstream host's file manager, harvesting credentials as customers logged in, is the kind of quiet breach that keeps paying out long after the patch."
featured: false
evidence_grade: "B"
sources:
  - title: "Hackers stole DreamHost customer files and inboxes during months-long attack"
    publisher: "TechCrunch"
    url: "https://techcrunch.com/2026/11/04/hackers-stole-dreamhost-customer-files-and-inboxes-during-months-long-attack/"
    published: "2026-11-04"
  - title: "DreamHost says months long attack exposed customer credentials and sessions"
    publisher: "iSec News, from DreamHost breach notice to California attorney general"
    url: "https://www.isec.news/2026/11/05/dreamhost-customer-credentials-session-breach/"
    published: "2026-11-05"
tags: []
data_as_of: "DreamHost breach notice filed with California's attorney general and company notice of October 29, 2026; attack window August to October 23, 2026; TechCrunch reporting of November 4, 2026."
---

Web host DreamHost has confirmed that hackers were inside its web based File Manager from August until October 23, 2026, stealing customer credentials as people logged in. The company disclosed the breach in a notice filed with California's attorney general and in a security update on October 29, after an outage lasting several days during which it reset some customer passwords.

According to the notice, an unauthorized party exploited an unspecified vulnerability in the third party software behind the File Manager at files.dreamhost.com. The attacker captured FTP and SFTP usernames and passwords for users who logged in during the window, reached certain webmail systems and obtained login credentials for a limited number of webmail users, and in a small number of cases may have viewed mailbox contents. TechCrunch reported that the attackers also obtained session tokens, which keep users logged in after entering a password.

DreamHost told TechCrunch the affected share was well under 10 percent of its hosted accounts, against roughly 400,000 paying customers, but would not give an exact figure. It declined to say why the attack was not detected until October 23, citing its ongoing investigation. The company said it found no evidence that control panel logins or billing details were accessed, and that it does not store full card numbers.

DreamHost said it blocked the attacker, fixed the vulnerability, invalidated exposed passwords and ended active sessions, and is offering affected customers a year of credit monitoring and identity theft protection through Equifax.
