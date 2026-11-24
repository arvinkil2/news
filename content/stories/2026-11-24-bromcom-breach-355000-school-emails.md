---
title: "Bromcom breach exposed 355,051 school email addresses"
date: 2026-11-24T07:09:14-05:00
last_updated: 2026-11-24T07:09:14-05:00
beats: ["technology"]
regions: ["europe"]
status: "story"
lede: "More than 355,000 school staff and pupil email addresses were taken in September's attack on UK education software supplier Bromcom, according to Have I Been Pwned, which added the breach on Monday."
why_it_matters: "A superseded login component left running is a common enterprise failure mode, and 355,051 exposed school addresses are now a phishing risk across more than 5,000 UK schools."
featured: false
evidence_grade: "B"
sources:
  - title: "Education software supplier's legacy login system left 355,000 school email addresses exposed"
    publisher: "The Register"
    url: "https://www.theregister.com/cyber-crime/2026/11/24/education-software-suppliers-legacy-login-system-left-355000-school-email-addresses-exposed/5311622"
    published: "2026-11-24"
  - title: "Bromcom breach FAQ"
    publisher: "Bromcom"
    url: "https://docs.bromcom.com"
    published: "2026-11-24"
tags: []
data_as_of: "Breach discovered September 6, 2026; Have I Been Pwned listing November 23, 2026; Bromcom investigation complete per its FAQ."
---

More than 355,000 school staff and pupil email addresses ended up in the hands of hackers who broke into UK education software supplier Bromcom in September. The breach was added to Have I Been Pwned on Monday, putting the count at 355,051 unique email addresses. The data also included single sign-on registration reference numbers, although Bromcom says no passwords or authentication tokens were stolen.

The attackers entered through a legacy single sign-on registration component in Bromcom's Communications Server environment. The technology had already been superseded but was still running because an internal system continued to use it. Bromcom discovered the intrusion on September 6 after customers reported problems accessing its single sign-on service, and its completed investigation confirms the intruders used a script to extract registration information from the compromised server.

Bromcom says its Management Information System, used by schools for attendance and pupil records, was untouched, and that the compromised service could not be used to reach Microsoft or Google accounts. The company has removed the old component, tightened authorization checks and added security logging, and says it has found no evidence of accounts being hijacked. It has not reported the breach to the Information Commissioner's Office, reasoning that as data processor rather than controller, that decision belongs to the affected schools and academy trusts.

Bromcom's software is used by more than 5,000 schools and 390 multi-academy trusts across the UK, though it has not said how many were affected in this incident. It considers the risk to staff and pupils low, and schools have been advised to watch for phishing messages and suspicious password reset or sign-in approval requests.
