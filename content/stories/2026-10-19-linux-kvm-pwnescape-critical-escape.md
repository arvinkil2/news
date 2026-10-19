---
title: "Linux KVM guest escape rated 9.3 and named PwnEscape"
date: 2026-10-19T07:13:09-04:00
last_updated: 2026-10-19T07:13:09-04:00
beats: ["technology"]
regions: ["global"]
status: "story"
lede: "A Linux flaw tracked as CVE-2026-99999 and rated 9.3, now named PwnEscape, lets a guest virtual machine escape to its host using malformed IPv4 packets, with an upstream kernel fix already moving into major distributions."
why_it_matters: "KVM underpins most hyperscale clouds, and the bug sits in the host networking stack rather than the hypervisor itself, so the patching obligation falls on every operator running Linux hosts, not on one cloud vendor."
featured: false
evidence_grade: "B"
sources:
  - title: "Linux KVM guest-host escape rated critical, may represent a new way to attack penguin-powered networking"
    publisher: "The Register"
    url: "https://www.theregister.com/virtualization/2026/10/19/linux-kvm-guest-host-escape-rated-critical-may-represent-a-new-way-to-attack-penguin-powered-networking/5303744"
    published: "2026-10-19"
  - title: "PwnEscape Is a Critical KVM Guest-to-Host Escape, and It Lives in Linux Networking, Not the Hypervisor"
    publisher: "Hardware Busters"
    url: "https://hwbusters.com/news/pwnescape-is-a-critical-kvm-guest-to-host-escape-and-it-lives-in-linux-networking-not-the-hypervisor/"
    published: "2026-10-19"
tags: []
data_as_of: "CVE-2026-99999 announced October 15, 2026; The Register report published October 19, 2026 and read in full, corroborated by Hardware Busters reporting on October 19. The full host takeover was demonstrated in the researchers' own lab, not in a provider production environment."
---

Researcher Paulos Yibelo, who in early October said he had found a guest to host escape flaw in Linux KVM, has named the flaw PwnEscape and warned it may represent a new way to attack Linux. The work is now tracked as CVE-2026-99999 and rated 9.3. KVM is the hypervisor used by most hyperscale clouds, and a guest to host escape breaks the isolation on which public and private clouds depend: an attacker who reaches the host could in principle reach other virtual machines on the same hardware.

The flaw does not live in KVM's own code. It sits in the host kernel's IPv4 networking path. Guests can supply checksum offload metadata saying where a checksum should start and where its result should be written. Red Hat's Michael S. Tsirkin, writing in the Linux kernel stable tree, explained that if a packet with bad checksum metadata gets into the IPv4 stack, the checksum helper can corrupt the network header. In the researchers' lab work that produced a repeatable leak of 32 bytes of host memory per case, a host crash on test machines, and controlled writes into host kernel memory that were chained into running a helper as root on the host. The researchers do not claim the full chain works against any provider's production environment.

Yibelo argues the root cause is broader than one bug: untrusted checksum metadata can rewrite security sensitive packet fields after the kernel has already validated them, so different parts of Linux were allowed to trust different versions of the same packet. Threat analysis firm SOC Prime made the same point about guest controlled metadata influencing a write after earlier validation stages had passed.

The practical position is narrower than the headline. Amazon Web Services, which runs its cloud on KVM, says its Elastic Compute Cloud is not at risk, and Google Cloud's method of using KVM means it is probably in the clear too, The Register reported. An upstream fix has been created in the Linux kernel and is moving into major distributions including Debian, RHEL and Ubuntu, and into virtualization products that rely on KVM such as Nutanix and Proxmox. Red Hat's own assessment says the impact can potentially include arbitrary code execution on the host, a system crash, or disclosure of sensitive memory, which is why host patching, not guest patching, is the urgent task.
