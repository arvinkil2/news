---
title: "Attackers hijacked 333 Tor exit nodes to steal SSH passwords"
date: 2026-10-22T08:17:27-04:00
last_updated: 2026-10-22T08:17:27-04:00
beats: ["technology"]
regions: ["global"]
status: "developing"
developing: true
lede: "Attackers who had quietly compromised 333 Tor exit relays, about a tenth of the network's roughly 3,000 exits, redirected SSH logins to interception servers for three days in early October, stealing passwords and harvesting unencrypted email before the Tor Project shut the relays down."
why_it_matters: "Anyone who accepted a changed host key warning and logged in by password through Tor between October 2 and 5 may have handed attackers their credentials and had their server infected, so affected passwords need rotating even though the network has already removed the relays."
featured: false
evidence_grade: "B"
sources:
  - title: "How I got over 300 Tor exit nodes removed"
    publisher: "Kaba (researcher account, kaba.cx)"
    url: "https://kaba.cx/posts/20261020_Tor/"
    published: "2026-10-20"
  - title: "333 Tor exit nodes hijacked to intercept SSH traffic and retrieve plaintext email"
    publisher: "Ars Technica"
    url: "https://arstechnica.com/information-technology/2026/10/300-tor-exit-nodes-hijacked-to-intercept-ssh-traffic-and-retrieve-plaintext-email/"
    published: "2026-10-22"
  - title: "Attackers hijacked over 300 Tor exit relays to intercept SSH connections"
    publisher: "The Hacker News"
    url: "https://thehackernews.com/2026/10/attackers-hijacked-over-300-tor-exit.html"
    published: "2026-10-21"
tags: []
data_as_of: "Researcher Kaba's account of October 20, 2026, read in full at kaba.cx, corroborated by The Hacker News of October 21 and Ars Technica of October 22, 2026. How the attackers first entered the servers, and who they are, remain unknown. Developing item."
update_bump: true
---

Attackers gained access to the servers behind 333 Tor exit relays in August and quietly installed Ebury 1.8.3, an OpenSSH backdoor and credential stealer for Linux, then launched the interception on October 2. The relays forwarded encrypted web traffic normally, but an SSH connection on port 22 was redirected to one of 12 interception servers, while the relays' port settings steered them unencrypted email traffic to collect.

A user who ignored the changed host key warning and logged in anyway had their password stolen, their session watched command by command, and their server infected with Ebury through a second connection. The researcher who found the campaign, publishing as Kaba, tested all of the network's roughly 3,000 exit relays, reported the results to the Tor Project's network health team on October 2, and the relays were flagged BadExit on October 4 and shut down by October 5.
