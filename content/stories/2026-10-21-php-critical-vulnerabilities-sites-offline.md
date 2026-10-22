---
title: "NSA warns on critical PHP flaws as governments pull sites offline"
date: 2026-10-21T11:47:45-04:00
last_updated: 2026-10-21T22:24:09-04:00
beats: ["technology"]
regions: ["global", "europe"]
status: "developing"
developing: true
lede: "The US National Security Agency has issued a rare public warning over two critical PHP vulnerabilities, dubbed PHP2Shell, as governments in Europe and Asia take websites offline to patch flaws that allow unauthenticated remote code execution."
why_it_matters: "PHP powers more than 70 percent of websites, the flaws were found with AI assistance after sitting in the code for decades, and the PHP Foundation warns that AI tools now surface such bugs faster for attackers as well as defenders, which makes patching speed the binding constraint for the public web."
featured: false
evidence_grade: "B"
sources:
  - title: "PHP devs publish critical bug fix as site owners warned: Pull 'em offline if you're unpatched"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/21/php-devs-publish-critical-bug-fix-as-site-owners-warned-pull-em-offline-if-youre-unpatched/5304519"
    published: "2026-10-21"
  - title: "World leaders warn of security flaws found in PHP programming language"
    publisher: "Al Jazeera"
    url: "https://www.aljazeera.com/news/2026/10/22/world-leaders-warn-against-security-flaw-found-in-php-computer-programming"
    published: "2026-10-22"
  - title: "Critical web security flaws spark global alarm as Google, OpenAI and Amazon respond"
    publisher: "CNBC"
    url: "https://www.cnbc.com/2026/10/22/php-google-openai-and-amazon-cyber.html"
    published: "2026-10-21"
tags: []
data_as_of: "The Register, October 21, 2026, read in full, reporting the PHP project's emergency releases and CERT-EU's advisory; the US Cybersecurity and Infrastructure Security Agency issued a matching alert titled Critical Vulnerabilities in PHP Require Immediate Patching the same day, but its page could not be opened in this run, so the technical detail here rests on The Register as a single publisher and is graded C. Developing item. Update, 22:14 ET: Al Jazeera report of October 22, 2026, read in full, reporting the NSA warning, the wider set of government website shutdowns in Germany, France, Belgium, the Netherlands, Finland and the Czech Republic, the PHP2Shell name, and the AI assisted discovery by Calif with OpenAI and by Wiz; with two independent publishers now reporting, the grade rises to B. Further update, 22:24 ET: CNBC report of October 21, 2026, by Jenny Lee, read in full after an initial access denial was cleared, reporting Amazon's pre-disclosure exploitation detection, the FBI warning, similar alerts from authorities in Singapore, the United Kingdom, Australia, Canada and the European Union, OpenAI's two-month coordination coalition and Cloudflare's firewall protections."
update_bump: true
---

**Latest:** The US National Security Agency issued a rare public warning over the two PHP flaws on Wednesday, advising organisations using PHP to be prepared for an update addressing two critical vulnerabilities and, as Al Jazeera reported the warning, to take websites offline if they could not be updated immediately. Germany's Federal Ministry for Digital Transformation and Government Modernisation took some websites offline as a preventive measure, France's Ministry of the Interior deactivated the official websites for local administrative offices, and authorities in Belgium, the Netherlands, Finland and the Czech Republic also shut down websites to apply the patch, while Japanese Prime Minister Sanae Takaichi posted on social media to warn about the PHP risk. The flaw pair, dubbed PHP2Shell, was pinpointed with the help of AI models: researchers at security firm Calif, working with OpenAI, reported the first flaw on August 11, and Wiz, a security firm owned by Alphabet, reported the second on August 24, saying the findings rank among the most severe vulnerabilities discovered in PHP and that the underlying flaws had been present for decades. The PHP Foundation said the flaws were among the most severe it has encountered and warned that tools now find bugs faster than ever, for defenders and attackers alike.

Amazon said its threat intelligence team detected attempts to exploit the flaws before they were publicly disclosed, through its MadPot threat detection system, and that it remains unclear how the attackers obtained information about the flaws ahead of disclosure, CNBC reported. The FBI also warned that malicious actors could exploit the flaws to execute code remotely, putting sensitive data and networks at risk, and cybersecurity authorities in Singapore, the United Kingdom, Australia, Canada and the European Union issued similar alerts. OpenAI said it spent the past two months leading a coalition of software maintainers, cybersecurity researchers and security providers to coordinate fixes and protective measures ahead of the disclosure, and Cloudflare said it has deployed web application firewall protections designed to block malicious requests targeting the flaws.

PHP developers have released emergency updates, versions 8.5.12, 8.4.27, 8.3.36 and 8.2.35, fixing two critical vulnerabilities that can allow unauthenticated remote code execution, and urged all users to update immediately. All PHP installations serving web requests are potentially affected, including PHP-FPM, Apache mod_php, php-cgi, FrankenPHP and LiteSpeed deployments, with the risk highest for mod_php, where a demonstrated exploit can trigger before any application code runs, the developers said.

The shutdowns started before the patches landed. Finnish government services and websites belonging to the Dutch parliament, cybersecurity authorities and the data protection regulator were taken offline as a precaution, the privacy campaign group noyb also withdrew its site, and watchTowr said it is already observing exploitation attempts in the wild. CERT-EU scored both flaws at 9.2 and advised organisations that cannot patch immediately to isolate internet facing applications from public networks until a fix is available.
