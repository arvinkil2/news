---
title: "Meta holds over a tenth of Prometheus GPUs in reserve"
date: 2026-10-21T07:17:19-04:00
last_updated: 2026-10-21T07:17:19-04:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "More than 11 percent of the GPUs at Meta's Prometheus supercluster in Ohio are dead or held idle as spares, Meta disclosed in an engineering account of the gigawatt scale cluster it plans to grow to about one million accelerators."
why_it_matters: "Prometheus is the first hard public accounting of what reliability costs at frontier scale: roughly 13 percent extra hardware provisioned so a single training run survives constant component failure."
featured: false
evidence_grade: "B"
sources:
  - title: "Tens of thousands of Nvidia GPUs sit idle in Meta's Prometheus supercluster, just waiting for a failure"
    publisher: "The Register"
    url: "https://www.theregister.com/systems/2026/10/20/tens-of-thousands-of-nvidia-gpus-sit-idle-in-metas-prometheus-supercluster-just-waiting-for-a-failure/5304269"
    published: "2026-10-20"
  - title: "Meta Details Prometheus, Its Gigawatt AI Cluster"
    publisher: "Technology.org"
    url: "https://www.technology.org/2026/10/20/meta-prometheus-gigawatt-supercluster-ohio-muse/"
    published: "2026-10-20"
tags: []
data_as_of: "Meta engineering disclosure published the week of October 19, 2026, reported in full by The Register on October 20, 2026 and by Technology.org the same day. Goodput, interruption and provisioning figures are Meta's own as reported."
---

Meta has published an unusually detailed account of Prometheus, its supercluster in New Albany, Ohio, and of what it costs to keep a frontier training run alive. More than 11 percent of the cluster's GPUs are either dead or sitting idle as spares waiting to replace the next failure, the company disclosed.

Prometheus is among Meta's largest compute deployments. It runs Nvidia Grace Blackwell systems today, GB200 and GB300 NVL72 racks, with Vera Rubin racks to follow, and Meta says it will eventually scale to a gigawatt of capacity spanning about one million accelerators across buildings linked over distances from 2 kilometres to more than 100 kilometres. The completed first phase trained Meta's Muse models, including Muse Wonder.

The failure arithmetic is the point. When Prometheus began operating in mid 2025, Meta was seeing roughly 1,000 interruptions per day for every 8,000 GPUs, where an interruption means something crashed, failed or timed out and forced a rollback to the last checkpoint. Meta says it has cut that rate by 99 percent, to about 11 per day per 8,000 GPUs. Part of the method is redundancy: running a 64 GPU slice in each 72 GPU rack and holding the rest as in-rack spares, plus reserve racks, means provisioning about 37,656 GPUs to sustain a 32,768 active GPU job, roughly 13 percent above the active footprint.

During Muse Wonder training, Meta reports more than 85 percent goodput in pre-training and more than 90 percent in reinforcement learning, with mean time between interruptions of about 47,000 GPU hours, since raised past 54,000. It also described power swings of 30 to 40 percent as tens of thousands of GPUs pause and resume in unison, managed with software that lowers GPU power limits near the site's electrical ceiling. All figures are Meta's own, published in its engineering account.
