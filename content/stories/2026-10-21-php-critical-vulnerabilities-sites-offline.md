---
title: "Critical PHP flaws force emergency patches and site shutdowns"
date: 2026-10-21T11:47:45-04:00
last_updated: 2026-10-21T11:47:45-04:00
beats: ["technology"]
regions: ["global", "europe"]
status: "developing"
developing: true
lede: "PHP developers have released emergency updates fixing two critical vulnerabilities, CVE-2026-109618 and CVE-2026-109619, that allow unauthenticated remote code execution, and Finnish government services and Dutch parliament and regulator websites were taken offline as a precaution."
why_it_matters: "PHP runs much of the public web, including WordPress, Drupal and shared hosting platforms, exploitation attempts have already been observed, and CERT-EU, which scores both flaws at 9.2, advised operators who cannot patch at once to take exposed applications off public networks."
featured: false
evidence_grade: "C"
sources:
  - title: "PHP devs publish critical bug fix as site owners warned: Pull 'em offline if you're unpatched"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/21/php-devs-publish-critical-bug-fix-as-site-owners-warned-pull-em-offline-if-youre-unpatched/5304519"
    published: "2026-10-21"
tags: []
data_as_of: "The Register, October 21, 2026, read in full, reporting the PHP project's emergency releases and CERT-EU's advisory; the US Cybersecurity and Infrastructure Security Agency issued a matching alert titled Critical Vulnerabilities in PHP Require Immediate Patching the same day, but its page could not be opened in this run, so the technical detail here rests on The Register as a single publisher and is graded C. Developing item."
update_bump: true
---

PHP developers have released emergency updates, versions 8.5.12, 8.4.27, 8.3.36 and 8.2.35, fixing two critical vulnerabilities that can allow unauthenticated remote code execution, and urged all users to update immediately. All PHP installations serving web requests are potentially affected, including PHP-FPM, Apache mod_php, php-cgi, FrankenPHP and LiteSpeed deployments, with the risk highest for mod_php, where a demonstrated exploit can trigger before any application code runs, the developers said.

The shutdowns started before the patches landed. Finnish government services and websites belonging to the Dutch parliament, cybersecurity authorities and the data protection regulator were taken offline as a precaution, the privacy campaign group noyb also withdrew its site, and watchTowr said it is already observing exploitation attempts in the wild. CERT-EU scored both flaws at 9.2 and advised organisations that cannot patch immediately to isolate internet facing applications from public networks until a fix is available.
