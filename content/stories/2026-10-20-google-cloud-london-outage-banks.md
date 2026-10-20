---
title: "Google Cloud power failure disrupts UK banks and payments"
date: 2026-10-20T08:07:13-04:00
last_updated: 2026-10-20T08:07:13-04:00
beats: ["technology"]
regions: ["europe"]
status: "developing"
developing: true
lede: "A power event in Google Cloud's London region took multiple cloud services offline from 2:08 a.m. ET on Tuesday, disrupting card payments, transfers and account access at Revolut, with Lloyds, Halifax, DPD and Royal Mail also hit, and full recovery of existing workloads tentatively expected by 9:00 a.m. ET."
why_it_matters: "A single zone power failure rippling into banking and payments at several large UK consumer brands is a live demonstration of single region concentration risk in cloud infrastructure."
featured: false
evidence_grade: "B"
sources:
  - title: "Multiple services are experiencing issues in the europe-west2 region"
    publisher: "Google Cloud Service Health"
    url: "https://status.cloud.google.com/incidents/Xs2XTHzAVC9YnafnPyzj"
    published: "2026-10-20"
  - title: "Google experiences service disruption in UK cloud region"
    publisher: "Datacenter Dynamics"
    url: "https://www.datacenterdynamics.com/en/news/google-experiences-service-disruption-in-uk-cloud-region/"
    published: "2026-10-20"
tags: []
data_as_of: "Google Cloud Service Health incident page read on October 20, 2026, latest update 04:58 PDT (7:58 a.m. ET); affected customer reporting via the BBC as carried by Datacenter Dynamics, and Revolut's statement as carried by PA Media reporting. Developing item."
update_bump: true
---

Google said a power event caused an outage in the europe-west2-b zone of its London cloud region beginning at 11:08 p.m. PDT on Monday (2:08 a.m. ET), leaving services in that zone unavailable and causing elevated errors and intermittent network failures across the region, and its latest update at 4:58 a.m. PDT said the power event is mitigated, services are recovering with priority given to existing workloads, customers may not yet be able to create new workloads, and full recovery of existing workloads should tentatively be complete by 6:00 a.m. PDT (9:00 a.m. ET). The BBC reported that Lloyds Bank, Revolut, Halifax and delivery services DPD and Royal Mail were among those affected, and Revolut confirmed a disruption spanning card payments, money transfers, ATM withdrawals and account sign-ins while saying customer money and data are safe. Google advised affected customers to migrate workloads to another zone or region where feasible, and said it would post its next update by 6:00 a.m. PDT.
