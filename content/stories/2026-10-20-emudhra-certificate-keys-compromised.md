---
title: "Browser makers move to distrust eMudhra certificates after key compromise"
date: 2026-10-20T22:14:28-04:00
last_updated: 2026-10-20T22:14:28-04:00
beats: ["technology"]
regions: ["asia-pacific", "global"]
status: "developing"
developing: true
lede: "Mozilla and Google have blocked eight eMudhra intermediate certificates after their private keys were reported compromised on October 17, and researchers recovered keys as small as the number 4 from the Indian authority's public certificates."
why_it_matters: "eMudhra says it has issued more than 60 million certificates, so any service that relies on its chains outside the major browsers now has to check whether it is exposed to forged certificates."
featured: false
evidence_grade: "B"
sources:
  - title: "Compromised eMudhra Intermediate Certificates"
    publisher: "Mozilla, dev-security-policy"
    url: "https://groups.google.com/a/mozilla.org/g/dev-security-policy/c/0R3XLJL6FuE/m/Kp1v6CPuAAAJ"
    published: "2026-10-20"
  - title: "Indian certification authority eMudhra's private keys compromised, one of them was the number '4'"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/20/indian-certification-authority-emudhras-private-keys-compromised-one-of-them-was-the-number-4/5304312"
    published: "2026-10-20"
tags: []
data_as_of: "Mozilla dev-security-policy post by Dennis Jackson, October 20, 2026, read in full, including the Chrome Root Program reply in the same thread. The Register, published October 20, 2026 at 22:57 UTC and read in full, for the recovered key values and the 60 million certificate figure, which is eMudhra's own count. eMudhra had not responded to The Register's inquiries at the time of that report. Developing item."
update_bump: true
---

Mozilla received a report on Saturday, October 17, at 20:06 UTC that the private keys for eight eMudhra intermediate certificates had been compromised, blocked the certificates in Firefox through its OneCRL list by 22:59 UTC the same day, and on October 20 removed the root that signed them from the NSS trusted list, which protects other users of that trust store. The Chrome Root Program, replying in the same Mozilla thread, said it received a report on October 17 and blocked the six TLS-issuing intermediates by 19:45 UTC, and that Certificate Transparency enforcement meant no fraudulent certificates from those intermediates could have been trusted by default in Chrome. The Register reported that security researcher Scott Helme recovered the private keys from eMudhra's public certificates in under a second on his laptop, one key being the number 4 and others 56 and 115, and that eMudhra has revoked the certificates.
