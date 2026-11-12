---
title: "Yandex Cloud permanently loses 2.84 percent of attacked customer data"
date: 2026-11-12T07:19:46-05:00
last_updated: 2026-11-12T07:19:46-05:00
beats: ["technology"]
regions: ["europe"]
status: "story"
lede: "Yandex said on Tuesday it had restored 97.16 percent of the Yandex Cloud customer data affected by October drone strikes on three of its data centres, while the remaining 2.84 percent is permanently lost."
why_it_matters: "This is a rare confirmed case of a kinetic attack destroying cloud customer data outright, and it turns on a mundane control: customers who had enabled backups lost nothing, while those who had not lost everything stored on the damaged equipment, which is why Yandex is now switching backups on by default."
featured: false
evidence_grade: "B"
sources:
  - title: "Russia's Yandex says nearly 3% of cloud customer data lost after attacks"
    publisher: "Reuters, via WNCY"
    url: "https://wncy.com/2026/11/10/russias-yandex-says-nearly-3-of-cloud-customer-data-lost-after-attacks/"
    published: "2026-11-10"
  - title: "Russian cloud Yandex says drone attacks on its datacenters caused data loss"
    publisher: "The Register"
    url: "https://www.theregister.com/off-prem/2026/11/12/russian-cloud-yandex-says-drone-attacks-on-its-datacenters-caused-data-loss/5309234"
    published: "2026-11-12"
tags: []
data_as_of: "Yandex company statement of Tuesday November 10, 2026, as reported by Reuters the same day and by The Register on November 12, 2026, both read in this run; the loss figures are Yandex's own, and the strikes are described as Yandex and Reuters describe them."
---

Russian technology group Yandex said on Tuesday that it has restored 97.16 percent of the customer data in its Yandex Cloud service that was affected by drone attacks on its infrastructure in October, and that the rest cannot be recovered. "The remaining 2.84 percent cannot be recovered due to critical damage to equipment and the absence of backups on the platform by customers," the company said in its statement, carried by Reuters.

Three Yandex data centres were damaged in drone strikes in early October, causing disruption primarily to Yandex Cloud. The first attack caused a fire and an outage at the ru-central1-b availability zone, and subsequent strikes targeted further facilities and disrupted cloud and payment services, The Register reported. Yandex attributed the attacks to Ukrainian forces; Ukrainian press said the strikes were ordered by Kyiv, and responsibility has not been independently established in the reporting read for this story.

The dividing line in the losses was backup configuration. Customers who had used the platform's own backup tools lost no data, while the permanent losses fell on data held only on critically damaged equipment with no backup copy on the platform. In response, Yandex said it will enable backups by default for all new virtual machines customers create in its cloud, which means customers will consume and pay for more resources unless they opt out.

Yandex has also opened a new availability zone, ru-central1-f, in an undisclosed new location, though it has imposed quotas limiting the resources users can draw there and says the zone cannot yet handle traffic to private endpoints. The company is at the same time promoting hybrid arrangements, including its own on-premises Stackland product, as part of data protection planning, a notable posture for a cloud operator whose own facilities have now been hit three times while sanctions restrict its access to replacement technology products.
