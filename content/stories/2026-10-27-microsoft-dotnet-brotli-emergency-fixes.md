---
title: "Microsoft issues emergency .NET fixes for Brotli compression flaw"
date: 2026-10-27T07:00:00-04:00
last_updated: 2026-10-27T07:14:47-04:00
beats: ["technology"]
regions: ["global"]
status: "story"
lede: "Microsoft released out of band security updates for .NET 8, 9, 10 and 11 to patch CVE-2026-111497, a buffer overflow in Google's Brotli compression library rated 8.1, and urged users to update as soon as possible, The Register reported."
why_it_matters: "Brotli is embedded across the modern software stack, in runtimes, proxies and cloud services, so a memory corruption flaw in it is a fleet wide patching event rather than a single product bug, with one researcher estimate putting vulnerable components in 91 percent of cloud environments."
featured: false
evidence_grade: "C"
sources:
  - title: "Microsoft releases emergency .NET security fixes for Google Brotli bug"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/26/microsoft-releases-emergency-net-security-fixes-for-google-brotli-bug/5305515"
    published: "2026-10-26"
tags: []
data_as_of: "Single sourced: The Register report of October 26, 2026, which cites Microsoft's October 25 release notes and its MSRC advisory for CVE-2026-111497 and Wiz research; those primary documents were not read directly in this run. Evidence grade capped at C."
---

Microsoft has joined the maintainers scrambling to patch a flaw in Google's Brotli compression library. The company released out of band updates for .NET 8, 9, 10 and 11 and urged users to update as soon as possible, The Register reported. The vulnerability, CVE-2026-111497, is a buffer overflow that could let an unauthenticated attacker read or corrupt process memory by supplying malicious Brotli compressed data, with potential information disclosure, denial of service or elevation of privilege. Microsoft rates it 8.1 under CVSS v3.1 and assesses exploitation as more likely, while noting working exploits have been demonstrated by researchers and there is no suggestion criminals are yet using them successfully.

The flaw, nicknamed Broccoli2Shell in some coverage, was disclosed on October 21 by the Node.js team, which credited Khai Tran and Sylvie Mayer of OpenAI's Codex Security with the discovery. The underlying bug had been fixed in Brotli's own source in February without being recognised as a security issue, and because Brotli is compiled into other software, every embedding project must ship its own update: Node.js, Python, Bun, Envoy and Istio have all released patches, and JFrog researchers demonstrated an exploit path through FFmpeg's JPEG XL handling.

The exposure estimate is what makes this a sector story. Wiz researcher Merav Bar said 91 percent of cloud environments rely on components vulnerable to the flaw and 82 percent have publicly exposed Node.js instances, pointing to containerised applications, Kubernetes clusters, API gateways and serverless workloads. OpenAI's Patch the Planet advisory recommends blocking untrusted Brotli compressed data where practical until patches are applied, and rebuilding and restarting deployments so fixes take effect.

Coming in the same week as the PHP2Shell KEV listing in today's edition, the Brotli event is the second compression and runtime layer emergency in days. Neither flaw is in application code companies wrote; both are in the shared plumbing underneath it, which is why the patching burden lands on platform teams everywhere at once. This story is single sourced and graded accordingly.
