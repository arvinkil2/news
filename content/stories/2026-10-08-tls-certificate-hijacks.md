---
title: "Attackers minted fake Google certificates after hijacking country domains"
date: 2026-10-08T07:38:44-0400
last_updated: 2026-10-08T07:38:44-0400
beats: ["technology"]
regions: ["global"]
status: "story"
lede: "Attackers hijacked Ghana's, Sierra Leone's and American Samoa's country-code domains and minted fraudulent HTTPS certificates for several Google domains, Google warned on Tuesday."
why_it_matters: "Domain-registry hijacking defeats the two strongest web defenses at once, DNS trust and certificate trust, and Chrome's fix only protects Chrome users."
featured: false
evidence_grade: "B"
sources:
  - title: "Attackers hijacked top-level domains, minted fake security certs for Google and other orgs"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/07/attackers-hijacked-top-level-domains-minted-fake-security-certs-for-google-and-other-orgs/5301718"
    published: "2026-10-07"
  - title: "Hackers obtain counterfeit TLS certificates for Google and other large services"
    publisher: "Ars Technica"
    url: "https://arstechnica.com/security/2026/10/hackers-obtain-counterfeit-tls-certificates-for-google-and-other-large-services/"
    published: "2026-10-06"
tags: []
data_as_of: "Detected 'last week'; disclosed by Google Oct 6, 2026. Ars Technica page policy-blocked to this writer; cited via feed-provided URL, attack details verified against The Register's full report."
---

Google said it became aware last week of attacks in the .gh (Ghana), .sl (Sierra Leone) and .as (American Samoa) country-code top-level namespaces. During the hijacks, attackers modified authoritative DNS records and obtained unauthorized HTTPS certificates covering several Google domains, as well as domains belonging to other organizations, Google security warned in a blog post on Tuesday. Google did not name the specific domains or organizations affected.

The attack is dangerous precisely because it is invisible to users. Controlling the traffic routing via DNS and the private key of an unauthorized certificate lets criminals impersonate legitimate organizations without triggering browser security alerts, and potentially intercept or modify user data or distribute malware under a trusted brand. Google said its own systems were not compromised and that the certification authorities "did nothing wrong."

Chrome blocked suspected counterfeit certificates across the affected ccTLDs, so Chrome users are protected, but Google warned that browser-side intervention "should not be relied on" because it cannot guarantee every affected domain was identified and it does not protect non-Chrome users. Google recommends domain owners monitor Certificate Transparency logs across all domains, including parked and regional ccTLD properties, and publish CAA records restricting which certificate authorities can issue for their domains.
