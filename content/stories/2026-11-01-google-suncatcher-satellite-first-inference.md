---
title: "Google Suncatcher satellite runs first inference in orbit"
date: 2026-11-01T07:18:40-05:00
last_updated: 2026-11-01T07:18:40-05:00
beats: ["technology"]
regions: ["north-america", "global"]
status: "story"
lede: "Google's prototype Suncatcher orbital data center satellite has completed commissioning and answered its first prompt from the ground, running the Gemma 4 model on one of four onboard TPUs and returning a haiku from low Earth orbit."
why_it_matters: "It is the first working demonstration of Google's orbital compute thesis, and the test campaign now turns to the question that decides whether the idea scales: how the chips hold up under real radiation and thermal stress."
featured: false
evidence_grade: "B"
sources:
  - title: "Google's first data center satellite is online and writing poetry"
    publisher: "TechCrunch"
    url: "https://techcrunch.com/2026/10/30/googles-first-data-center-satellite-is-online-and-writing-poetry/"
    published: "2026-10-30"
  - title: "Google's AI satellite sends a very expensive haiku to Earth"
    publisher: "The Register"
    url: "https://www.theregister.com/ai-and-ml/2026/10/31/googles-ai-satellite-sends-a-very-expensive-haiku-to-earth/5306818"
    published: "2026-10-31"
tags: []
data_as_of: "Satellite launched earlier in October 2026 on a SpaceX Falcon 9 rideshare; first prompt exchange reported October 30 to 31, 2026, both reports read in full in this run. Power and operating detail is Google's own account via the two reports."
---

Google's first experimental orbital data center is working. The Suncatcher prototype, launched earlier this month on a SpaceX Falcon 9 alongside more than 100 other spacecraft, finished a commissioning process of about three weeks and this week answered its first prompt from the ground: engineers asked the onboard Gemma 4 model to write a haiku about being in space, and the satellite replied over a pass above Svalbard, Norway. A Google spokesperson told TechCrunch the spacecraft is operating nominally.

The hardware is modest by design. The satellite carries four Google Tensor Processing Units and generates up to 1 kilowatt of electricity, and the power budget means it can run only one TPU at a time, for about 20 minutes at a stretch. After the poetry, Google tested space themed limericks and telemetry prompts asking the payload to report on its own condition. The substantive campaign comes next: measuring how the chips behave under thermal stress and in the real radiation environment, where radiation induced bit flips can corrupt data silently. Ground testing in particle accelerators suggested the impact would be minimal for inference and more of a problem for training; the orbit tests will replace simulation with measurement.

Google's own research, published earlier this month, puts the silent data corruption rate at roughly one event per 17 rad against an estimated orbital dose of about 150 rad per year, which the researchers translate to a failure probability on the order of one per 3 million inferences, a rate they call likely acceptable for inference while training remains an open question. The economics are equally conditional: Google calculates that if launch costs to low Earth orbit fall to about 200 dollars per kilogram, the amortised launch cost per kilowatt per year could rival what terrestrial data centers spend on electricity, and it expects that threshold could be reached around 2035.

If this spacecraft's TPUs prove out, the next step is two more satellites in 2027 with higher power generation and inter satellite optical links, the feature that separates Suncatcher's design from rival orbital compute plans: Google wants close flying satellites that share distributed workloads coherently, rather than isolated machines doing inference alone. The whole programme still depends on cheap, rapidly reusable heavy lift, which in practice means SpaceX's Starship; a peer reviewed Suncatcher analysis estimated SpaceX would need to fly Starship some 1,800 times to achieve the learning driven cost reductions of its earlier vehicles. Suncatcher is infrastructure designed for the 2030s, being prototyped while launch economics are still an order of magnitude away.
