---
title: "Transcription firm left police interviews and recordings open online"
date: 2026-11-22T07:05:32-05:00
last_updated: 2026-11-22T07:05:32-05:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "Tigerfish, a San Francisco transcription firm serving police departments, prosecutors and tech companies, left transcriptions of police interviews, body-cam footage and raw customer audio and video exposed on a public Amazon S3 server until TechCrunch contacted it."
why_it_matters: "The exposure is a basic access-control failure at a vendor holding some of the most sensitive material in the justice system, and the company has not said whether affected customers have been notified."
featured: false
evidence_grade: "C"
sources:
  - title: "A transcription firm used by police, prosecutors, and tech giants exposed customer data online"
    publisher: "TechCrunch"
    url: "https://techcrunch.com/2026/11/20/a-transcription-firm-used-by-police-prosecutors-and-tech-giants-exposed-customer-data-online/"
    published: "2026-11-20"
tags: []
data_as_of: "TechCrunch investigation published November 20, 2026, read in full in this run. Single-sourced to TechCrunch, which says it verified the exposed data itself before contacting the company; Tigerfish's confirmation is quoted in the same report. The number of affected customers and the duration of exposure are not established."
---

A transcription company that caters to law enforcement, government departments and Silicon Valley tech giants has closed a security lapse that left a large amount of internal data, including customer transcriptions and their source materials, exposed to the web. The lapse at San Francisco-based Tigerfish exposed transcriptions of police interviews, body-cam footage and customers' raw audio and video, along with invoices identifying police departments and prosecutors' offices among its customers.

The files sat on an Amazon-hosted S3 cloud server that was openly listed and accessible to anyone through an easy-to-guess web address, with no password required, according to security researcher Anurag Sen, who found the data. Sen discovered the exposure in October and alerted the company but heard nothing back; he later gave the details to TechCrunch, which verified the source of the leak and the data before contacting Tigerfish. The company said Sen's email had been caught in its spam filter.

Soon after TechCrunch made contact, Tigerfish secured the bucket. "We've blocked all public access to the bucket you identified, including directory listings and individual files," president Adam Goldberg said in an email, adding that the company had verified all of its other S3 buckets are blocked to public access and is continuing to review its storage security.

What remains unknown is the part that matters most to the firm's customers: how many of them were affected, how long the data was open, whether anyone else downloaded it, and whether Tigerfish has notified the police departments and prosecutors whose interview material it held. The company did not respond to a follow-up email asking about customer notification.
