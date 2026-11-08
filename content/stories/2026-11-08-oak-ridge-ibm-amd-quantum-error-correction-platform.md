---
title: "Oak Ridge, IBM and AMD unveil quantum error correction platform"
date: 2026-11-08T07:12:58-05:00
last_updated: 2026-11-08T07:12:58-05:00
beats: ["technology"]
regions: ["north-america"]
status: "story"
lede: "The Quantum Science Center at Oak Ridge National Laboratory, IBM and AMD have unveiled a co-design platform pairing IBM's 120-qubit Nighthawk quantum processors with an AMD powered HPC system to develop quantum error correction at scale."
why_it_matters: "Error correction is the binding constraint on useful quantum computing, and putting quantum processors and classical supercomputing in one low latency environment is the architecture the field has mostly had to simulate through cloud connections until now."
featured: false
evidence_grade: "B"
sources:
  - title: "Oak Ridge labs gets hybrid quantum-HPC system to test qubit error correction"
    publisher: "The Register"
    url: "https://www.theregister.com/hpc/2026/11/06/oak-ridge-labs-gets-hybrid-quantum-hpc-system-to-test-qubit-error-correction/5308187"
    published: "2026-11-06"
  - title: "IBM, AMD, And Oak Ridge Unveil Quantum Error Correction Platform"
    publisher: "The Next Platform"
    url: "https://www.nextplatform.com/compute/2026/11/06/ibm-amd-and-oak-ridge-unveil-quantum-error-correction-platform/5308284"
    published: "2026-11-06"
tags: []
data_as_of: "Platform unveiled November 6, 2026 by the Quantum Science Center at Oak Ridge National Laboratory with IBM and AMD, as reported the same day. Performance figures for hierarchical error correction are from IBM research cited by both reports, not measured results from this platform."
---

The Quantum Science Center at Oak Ridge National Laboratory, a US Department of Energy funded centre, has unveiled a co-design platform for quantum error correction built with IBM and AMD. The platform combines an IBM Quantum System Two equipped with 120-qubit Nighthawk r2 processors with Umbra, a classical high performance computing system powered by AMD fifth generation Epyc CPUs and Instinct MI355X GPU accelerators, with AMD Versal chips providing the low latency control, readout and decoding for the quantum circuitry. The integrated platform is housed at IBM's facility in Poughkeepsie, New York.

Co-location is the technical point. Quantum and classical processors are usually connected through the cloud, which adds complexity and delay, while error correction requires classical machines to measure qubits, decode errors and feed corrections back in real time. "Solving the challenges of quantum error correction is essential to making quantum computing a practical tool for scientific discovery," said Quantum Science Center director Travis Humble. IBM Research director Jay Gambetta said the question is no longer whether error correction works, but how to accelerate and optimise it into systems scientists can use.

One approach the platform is built to explore is hierarchical error correction, in which an inner code protects qubits within a module and an outer code wraps the inner code's logical qubits in a second layer. IBM research suggests the approach could reach a trillion logical operations at a physical error rate of one in a thousand, but it depends on powerful classical compute working at low latency, which is what the AMD system supplies. Nighthawk's square lattice connectivity, with most qubits connected directly to four neighbours, is also designed for compatibility with standard surface codes.

The platform sits inside a federal timetable. The Department of Energy's Quantum Genesis Mission includes a Q Competition targeting a system with 100 logical qubits performing hundreds of millions of fault tolerant operations, following an executive order to develop a full quantum system by 2028. IBM says work on the platform will also feed its Quantum Starling fault tolerant system, expected in 2029. None of that makes fault tolerant quantum computing near, and gate error rates across the industry still run between one error per 100 and per 1,000 operations, but the platform gives researchers a single environment in which to test what the classical side of that problem actually requires.
