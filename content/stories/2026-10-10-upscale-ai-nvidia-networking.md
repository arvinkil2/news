---
title: "Upscale AI buys Nvidia networking gear while competing with it"
date: 2026-10-10T07:15:25-0400
last_updated: 2026-10-10T07:15:25-0400
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "Upscale AI disclosed its SkyHammer scale-up switch ASIC while also buying Nvidia Spectrum-X networking silicon, a hedge that makes it Nvidia's customer and competitor at once."
why_it_matters: "The disclosure shows how the AI networking stack is fragmenting: startups are building NVSwitch alternatives for the scale-up tier while conceding the scale-out tier to Nvidia Ethernet, and Nvidia is an investor in one of its own challengers."
featured: false
evidence_grade: "B"
sources:
  - title: "Upscale AI Partners With Nvidia While Competing With It"
    publisher: "The Next Platform"
    url: "https://www.nextplatform.com/connect/2026/10/09/upscale-ai-partners-with-nvidia-while-competing-with-it/5302456"
    published: "2026-10-09"
tags: []
data_as_of: "Disclosure week of October 5, 2026, via company webinar; reported October 9. Details from The Next Platform's October 9 reporting (article read in full) based on company presentations and interviews with Upscale AI leadership; independent coverage by HPCwire. Company claims (bandwidth, valuation) are Upscale AI's own."
---

Upscale AI this week disclosed its "SkyHammer" scale-up switch ASIC, offering 115.2 terabits per second of aggregate bandwidth and supporting up to 576 accelerators per networking tier, alongside its "SkyFabriX" architecture running the UALoE and ESUN protocols. The company says it has raised about $500 million in total at a $2 billion valuation, roughly double its January valuation, and employs more than 300 people.

At the same time, Upscale is buying Nvidia Spectrum-X ASICs and building its own scale-out switches from them, porting its SkyOS, an AI-optimized SONiC/SAI stack, to run on Spectrum-X at 400, 800, and 1,600 gigabit-per-second ports. The catch: Nvidia does not support SkyHammer or SkyOS as an alternative to NVSwitch for scale-up networking with Nvidia GPUs, so Upscale has no scale-up path with Nvidia silicon yet. Nvidia is itself an investor in Upscale.

The straddle captures the state of the AI interconnect market. Scale-out Ethernet is converging on Nvidia's Spectrum-X; scale-up, the intra-rack GPU-to-GPU fabric, remains contested, with startups like Upscale building alternatives to NVSwitch that currently can only pair with non-Nvidia accelerators. The Next Platform's reporting speculates AMD could acquire Upscale to strengthen its rack-scale story.
