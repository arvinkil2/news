---
title: "Cloudflare acquires Deno to fix Workers lock-in"
date: 2026-10-11T07:11:38-0400
last_updated: 2026-10-11T07:11:38-0400
beats: ["technology"]
regions: ["north-america"]
status: "story"
featured: false
lede: "Cloudflare announced Friday it is acquiring Deno, the startup behind the JavaScript runtime founded by Node.js creator Ryan Dahl, to improve the Workers edge-compute platform."
why_it_matters: "Cloudflare is buying the tool its own engineers praised for making Workers portable, a bid to win developers from AWS Lambda and answer the lock-in criticism of edge platforms."
evidence_grade: "B"
sources:
- title: "Cloudflare acquires Deno to improve its Workers programming model"
  publisher: "TechCrunch"
  url: "https://techcrunch.com/2026/10/10/cloudflare-acquires-deno-to-improve-its-workers-programming-model/"
  published: "2026-10-10"
tags: []
data_as_of: "Acquisition announced by Cloudflare October 10, 2026, as reported by TechCrunch; financial terms not disclosed. Deno's fundraising total ($26M) is TechCrunch reporting only."
---

Cloudflare said Friday it is acquiring Deno, the startup behind the JavaScript and TypeScript runtime of the same name, co-founded by Bert Belder and Node.js creator Ryan Dahl. Cloudflare principal engineer Kenton Varda said the deal will improve the Workers programming model and platform, which lets customers build and run software across Cloudflare's network. Financial terms were not disclosed; Deno had raised a total of $26 million, including a Series A led by Sequoia.

The acquisition has an unusual rationale. Deno recently launched celld, an open-source implementation of the Workers runtime, which Varda said "delighted" the Cloudflare team. Varda argued that against the theory that Cloudflare made Workers incompatible with other clouds to create lock-in, the company believes that being open source and giving people an escape hatch is good business. Dahl wrote that his team is "joining Cloudflare to make the Workers programming model a mainstream way to build servers."

The deal is small in dollar terms but strategically pointed. Edge compute is where Cloudflare competes directly with AWS Lambda and the other hyperscalers, and developer choice there is driven by tooling. Absorbing the runtime that already reproduced Workers in open source turns a potential fork into a feature of the platform.
