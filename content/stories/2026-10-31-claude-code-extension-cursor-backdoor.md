---
title: "Trojanised Claude Code extension on Cursor planted SSH backdoor"
date: 2026-10-31T07:06:33-04:00
last_updated: 2026-11-01T07:18:40-05:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "A malicious version of Anthropic's official Claude Code extension, version 2.1.313, was distributed through the Cursor marketplace for about 11 hours on October 29, affecting at most 5,000 users and attempting to install a persistent SSH backdoor, Cursor said in its own security notice."
why_it_matters: "The compromised package carried the legitimate publisher identity of the most widely used AI coding tool, which means the trust developers place in marketplace updates, not a fake lookalike, was the attack surface."
featured: false
evidence_grade: "B"
sources:
  - title: "Security notice: malicious version of Anthropic.claude-code identified in the Cursor VS Code Extension Marketplace"
    publisher: "Cursor"
    url: "https://cursor.com/blog/claude-code-extension-security-notice?ref=metacurity.com"
    published: "2026-10-29"
  - title: "Official Claude Code extension on Cursor marketplace trojanized with persistent SSH backdoor"
    publisher: "The Hacker News"
    url: "http://thehackernews.com/2026/10/official-claude-code-vs-code-extension.html"
    published: "2026-10-30"
  - title: "Anthropic: That Claude Code extension compromise couldnt be us"
    publisher: "The Register"
    url: "https://www.theregister.com/cyber-crime/2026/10/30/anthropic-that-claude-code-extension-compromise-couldnt-be-us/5306682"
    published: "2026-10-30"
tags: []
data_as_of: "Incident window October 29, 2026, about 2:27 a.m. to 1:35 p.m. Pacific Time, per Cursor's security notice, the primary source. Technical detail (66 line loader, svc-telemetry SSH key) is from OpenSourceMalware's analysis as reported by The Hacker News on October 30, 2026. Anthropic's position, that the malicious build was not developed by Anthropic, is Cursor's statement, reported by The Register."
---

**Latest, November 1:** Anthropic has now denied directly that its own systems were breached. After security figures alleged the tampered extension reached Cursor's marketplace through a compromise at Anthropic, technical staff member Felix Rieseberg said the company is working with Cursor on the incident, but it was not a compromise of Anthropic's systems or employee laptops: a malicious actor used access to Cursor's marketplace to publish a tampered copy of the extension, which Anthropic did not build or publish, and versions on its official channels are unaffected. Neither company has yet explained how the actor obtained that marketplace access. The Register's account of the implant, first spotted by EDR vendor Phorion, adds a technical limit: the script that opens the SSH tunnel required administrator rights on macOS and Windows and in the vast majority of cases did not have them, so the tunnel failed, though the implant still forwarded collected host and user data, dropped the attacker's SSH key and installed persistence, which is why updating alone does not remediate an affected machine.

For about 11 hours on October 29, anyone who installed or updated the Claude Code extension from Cursor's own marketplace received a trojanised build. Cursor's security notice says versions 2.1.312 and 2.1.313 for Windows and macOS were maliciously modified, were not developed by Anthropic, and affected at most 5,000 users who installed the extension between about 2:27 a.m. and 1:35 p.m. Pacific Time.

The malicious code attempted to install a persistent SSH backdoor. Cursor says it collected host and user information, including hostname, username, operating system, Git email and public IP address, attempted to add an attacker controlled SSH key to the authorised keys file, enable the local SSH service and open a reverse SSH tunnel, and set up persistence through a LaunchAgent on macOS or a scheduled task on Windows, retrying roughly every 60 seconds. OpenSourceMalware's analysis, reported by The Hacker News, identified a 66 line loader placed before the legitimate extension code in the main JavaScript bundle, with the attacker's key labelled svc-telemetry.

Cursor removed the malicious version, shut its whole marketplace down, audited access and confirmed no other extensions were tampered with, rotated its keys, rebuilt the marketplace and worked with the hosting provider to take the attacker's server offline. It directs affected users to update to version 2.1.314. The Register reported Anthropic's position that the compromise was not in its own release: the malicious version numbers were never official Anthropic releases, and there is no evidence the build reached Microsoft's VS Code Marketplace or Open VSX.

Two limits in the official account deserve noting. Cursor says that, outside unusual cases where Cursor ran with administrator privileges, the backdoor step would fail because of errors in the malicious code, which bounds but does not eliminate the exposure. And updating the extension replaces its files without necessarily removing an SSH key or persistence script already placed on a machine, so the notice's manual checks, not the update alone, are the remediation for anyone in the window.
