---
title: "Applebee's app shipped with password to its customer database"
date: 2026-10-31T07:06:33-04:00
last_updated: 2026-10-31T07:06:33-04:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "Applebee's has fixed a flaw that left a password to its internal customer database inside its own Android app, exposing names, email addresses, dates of birth, phone numbers and login IP addresses, after a researcher found the credential and TechCrunch verified it by decompiling the app."
why_it_matters: "Hardcoded credentials are a basic, preventable failure, and the exposed fields are the identity theft set, names, birth dates and phone numbers, for a rewards programme with at least 8.5 million members as of last year."
featured: false
evidence_grade: "B"
sources:
  - title: "Applebee's exposed customers personal data after leaving database password in app"
    publisher: "TechCrunch"
    url: "https://techcrunch.com/2026/10/30/applebees-exposed-customers-personal-data-after-leaving-database-password-in-app/"
    published: "2026-10-30"
  - title: "Applebee's fixes security flaw that left customer data exposed"
    publisher: "Hacks.gr"
    url: "https://en.hacks.gr/ta-applebee-s-diorthosan-keno-asfaleias-poy-afine-ektetheimena-stoicheia-pelaton/"
    published: "2026-10-30"
tags: []
data_as_of: "Flaw reported and confirmed fixed October 30, 2026; TechCrunch withheld publication until the fix was confirmed. The number of affected customers is unknown: the researcher declined to count records and Dine Brands would not give a figure. No payment card data was in the exposed field list in the reporting."
---

Applebee's shipped the keys to its own customer database inside its app. Security researcher Robert Wiggins of What Security found a password for an internal database buried in the source code of Applebee's Android app, which has more than a million downloads on Google Play, earlier this month. TechCrunch verified the finding itself: it downloaded and decompiled the app, confirmed the credential was in the code, created a test account, and watched Wiggins retrieve that dummy record from the company's database.

The database held customer names, email addresses and whether they were verified, dates of birth, phone numbers and ZIP codes, plus veteran status, login counts, account creation dates and the IP addresses of most recent logins, which can reveal approximate location. No payment card fields were listed. TechCrunch describes hardcoded credentials as one of the most severe vulnerability types, because anyone with the app can extract the key and log in to a remote system as an authorised user; the researcher also assessed that the access could have allowed customer data to be changed, not only read.

Dine Brands, Applebee's parent, confirmed on Thursday that it had acted to close the issue. A spokesperson said on Friday that the security team promptly launched an investigation and has not currently found any evidence of unauthorised access, and that the investigation is ongoing. The company would not say how many customers were affected. Applebee's had at least 8.5 million rewards members as of last year, which bounds the programme's scale without establishing an exposure count.

One detail in the disclosure path is its own finding: Wiggins used AI tooling to search thousands of lines of app code for the credential, and, finding no security reporting channel at Applebee's or Dine Brands, routed the report through a newsroom. The same class of tooling that finds hardcoded secrets in shipped apps is now cheap and widely available, which shortens the life of every credential still sitting in a production binary.
