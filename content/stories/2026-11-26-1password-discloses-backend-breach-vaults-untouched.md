---
title: "1Password discloses breach of backend systems, says vaults untouched"
date: 2026-11-26T06:41:30-05:00
last_updated: 2026-11-26T06:41:30-05:00
beats: ["technology"]
regions: ["north-america"]
status: "developing"
developing: true
lede: "1Password says an attacker who compromised an employee's corporate GitHub account stole private source code, reached its CI/CD system and downloaded account records for a subset of users, but never accessed customer vault contents."
why_it_matters: "A password manager's own breach tests the design claim that vault secrets stay safe even when the company's servers do not, and the stolen names and email addresses give phishers a ready-made target list."
featured: false
evidence_grade: "B"
sources:
  - title: "Update on a security incident involving 1Password's backend systems"
    publisher: "1Password"
    url: "https://1password.com/blog/update-on-nov-2026-security-incident"
    published: "2026-11-26"
  - title: "Hackers help themselves to 1Password's source code and customer data"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/11/26/hackers-help-themselves-to-1passwords-source-code-and-customer-data/5312317"
    published: "2026-11-26"
tags: []
update_bump: true
data_as_of: "1Password's own incident disclosure, read in full from 1password.com; The Register's report of November 26, 2026, read in full, for outside framing. Developing item."
---

1Password began investigating on November 19 after an attacker gained access to an employee's corporate GitHub account, used it to read private source code and push malicious code to backend services, and downloaded account records for a subset of users, including names, email addresses, account identifiers and sign-in timestamps. The company says vault contents, account passwords and Secret Keys were never accessible to the attacker, that it has rotated every credential that may have been exposed in its CI/CD system, and that it found no evidence of account takeovers. As a precaution it has lengthened the codes used in emailed invitation and recovery links from six digits to ten alphanumeric characters, and it is warning users to expect phishing attempts that trade on the breach.
