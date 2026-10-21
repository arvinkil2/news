---
title: "Meta pauses Muse sharing after 6,800 chats exposed"
date: 2026-10-21T07:17:20-04:00
last_updated: 2026-10-21T07:17:20-04:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Meta has paused conversation sharing on its Muse AI platform after Claroc researchers enumerated 6,800 shared chat links through public DNS records and found personal and business secrets in them."
why_it_matters: "The flaw was in the link design itself, with conversation titles written into public DNS, and it undercuts the privacy pitch for a fast growing agent product at the moment enterprises are deciding what agents may touch."
featured: false
evidence_grade: "B"
sources:
  - title: "GhostShares: A Shared Muse Chat Exposed Prep for a Confidential Call With a Frontier AI Lab Leader"
    publisher: "Claroc"
    url: "https://blog.claroc.io/ghostshares-muse-passive-dns/"
    published: "2026-10-20"
  - title: "Meta suspends Muse chats sharing feature after it left private details exposed"
    publisher: "Engadget"
    url: "https://www.engadget.com/2292281/meta-suspends-muse-chats-sharing-feature-after-it-left-private-details-exposed/"
    published: "2026-10-20"
  - title: "Meta Muse exposes users' personal and business secrets when they share conversations"
    publisher: "Ars Technica"
    url: "https://arstechnica.com/security/2026/10/meta-muse-exposes-users-personal-and-business-secrets-when-they-share-conversations/"
    published: "2026-10-20"
tags: []
data_as_of: "Claroc research published October 2026 and updated October 20, 2026, reported first by Ars Technica on October 20, 2026 and corroborated by Engadget the same day. Ars Technica could not be opened directly in this run; its reporting is corroborated by Engadget and by Claroc's own post, both read via search results in full. Muse download figure is from separate TechCrunch reporting of October 20, 2026."
---

Meta has paused the sharing feature of Muse, its personal AI agent platform launched last month, after security researchers showed that shared conversations could be found by anyone. Researchers at Claroc searched passive DNS records for Muse's content domain and enumerated 6,800 shared conversation links.

The design flaw is specific. Muse names each share's web address after the conversation's own title, and that address is written into public DNS. "One passive-DNS search brings back thousands of them, listed by name, like a table of contents," Claroc wrote, calling the exposed links GhostShares. The firm said it reported the issue through Meta's bug bounty programme on October 8 and received no reply before publication.

In a sample of the links, Claroc found material plainly not meant to be public: a candidate's confidential preparation for an executive search call with a frontier AI lab, including the lab's internal contact and the meeting time, alongside a small business loan application, a bank fraud alert with partial account details, a company vacation calendar and other internal documents, as summarised by Engadget's reporting of the same research.

Meta told Ars Technica it has "paused this functionality while we review this report and consider changes to how these links can be discovered." Claroc said that when it rechecked 40 shares on October 20 that had previously opened without an account, none opened, although the hostnames, titles included, remain in passive DNS history. The exposure arrives while Muse is growing quickly: TechCrunch reported it reached 10 million US downloads in 40 days.
