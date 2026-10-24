---
title: "NSA warns on critical PHP flaws as governments pull sites offline"
date: 2026-10-21T11:47:45-04:00
last_updated: 2026-10-24T07:07:38-04:00
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
  - title: "PHP blames supply chain security biz Chainguard for putting huge chunks of the web at risk"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/22/php-blames-supply-chain-security-biz-chainguard-for-putting-huge-chunks-of-the-web-at-risk/5304611"
    published: "2026-10-22"
  - title: "Hackers pile on PHP2Shell as AWS reveals attacks began before disclosure"
    publisher: "The Register"
    url: "https://www.theregister.com/cyber-crime/2026/10/22/hackers-pile-on-php2shell-as-aws-reveals-attacks-began-before-disclosure/5304749"
    published: "2026-10-22"
  - title: "Critical web security flaws spark global alarm as Google, OpenAI and Amazon respond"
    publisher: "CNBC"
    url: "https://www.cnbc.com/2026/10/22/php-google-openai-and-amazon-cyber.html"
    published: "2026-10-21"
  - title: "There's a third PHP2Shell bug, but it won't get an emergency fix"
    publisher: "The Register"
    url: "https://www.theregister.com/security/2026/10/23/theres-a-third-php2shell-bug-but-it-wont-get-an-emergency-fix/5305208"
    published: "2026-10-23"
tags: []
data_as_of: "The Register, October 21, 2026, read in full, reporting the PHP project's emergency releases and CERT-EU's advisory; the US Cybersecurity and Infrastructure Security Agency issued a matching alert titled Critical Vulnerabilities in PHP Require Immediate Patching the same day, but its page could not be opened in this run, so the technical detail here rests on The Register as a single publisher and is graded C. Developing item. Update, 22:14 ET: Al Jazeera report of October 22, 2026, read in full, reporting the NSA warning, the wider set of government website shutdowns in Germany, France, Belgium, the Netherlands, Finland and the Czech Republic, the PHP2Shell name, and the AI assisted discovery by Calif with OpenAI and by Wiz; with two independent publishers now reporting, the grade rises to B. Further update, 22:24 ET: CNBC report of October 21, 2026, by Jenny Lee, read in full after an initial access denial was cleared, reporting Amazon's pre-disclosure exploitation detection, the FBI warning, similar alerts from authorities in Singapore, the United Kingdom, Australia, Canada and the European Union, OpenAI's two-month coordination coalition and Cloudflare's firewall protections."
update_bump: true
---

**Latest:** The US National Security Agency issued a rare public warning over the two PHP flaws on Wednesday, advising organisations using PHP to be prepared for an update addressing two critical vulnerabilities and, as Al Jazeera reported the warning, to take websites offline if they could not be updated immediately. Germany's Federal Ministry for Digital Transformation and Government Modernisation took some websites offline as a preventive measure, France's Ministry of the Interior deactivated the official websites for local administrative offices, and authorities in Belgium, the Netherlands, Finland and the Czech Republic also shut down websites to apply the patch, while Japanese Prime Minister Sanae Takaichi posted on social media to warn about the PHP risk. The flaw pair, dubbed PHP2Shell, was pinpointed with the help of AI models: researchers at security firm Calif, working with OpenAI, reported the first flaw on August 11, and Wiz, a security firm owned by Alphabet, reported the second on August 24, saying the findings rank among the most severe vulnerabilities discovered in PHP and that the underlying flaws had been present for decades. The PHP Foundation said the flaws were among the most severe it has encountered and warned that tools now find bugs faster than ever, for defenders and attackers alike.

Amazon said its threat intelligence team detected attempts to exploit the flaws before they were publicly disclosed, through its MadPot threat detection system, and that it remains unclear how the attackers obtained information about the flaws ahead of disclosure, CNBC reported. The FBI also warned that malicious actors could exploit the flaws to execute code remotely, putting sensitive data and networks at risk, and cybersecurity authorities in Singapore, the United Kingdom, Australia, Canada and the European Union issued similar alerts. OpenAI said it spent the past two months leading a coalition of software maintainers, cybersecurity researchers and security providers to coordinate fixes and protective measures ahead of the disclosure, and Cloudflare said it has deployed web application firewall protections designed to block malicious requests targeting the flaws.

PHP developers have released emergency updates, versions 8.5.12, 8.4.27, 8.3.36 and 8.2.35, fixing two critical vulnerabilities that can allow unauthenticated remote code execution, and urged all users to update immediately. All PHP installations serving web requests are potentially affected, including PHP-FPM, Apache mod_php, php-cgi, FrankenPHP and LiteSpeed deployments, with the risk highest for mod_php, where a demonstrated exploit can trigger before any application code runs, the developers said.

The shutdowns started before the patches landed. Finnish government services and websites belonging to the Dutch parliament, cybersecurity authorities and the data protection regulator were taken offline as a precaution, the privacy campaign group noyb also withdrew its site, and watchTowr said it is already observing exploitation attempts in the wild. CERT-EU scored both flaws at 9.2 and advised organisations that cannot patch immediately to isolate internet facing applications from public networks until a fix is available.

**Update, October 22, 2026:** The disclosure itself is now in dispute. In a post patch blog, the PHP maintainers accused supply chain security company Chainguard of breaking the coordinated embargo by publishing built images containing the fix on October 21 at 07:41 UTC, more than six hours before the coordinated release, which let any attacker study the fix in binary form while other users still waited. The maintainers said CVE identifiers and rumours began circulating on Tuesday around 15:00 UTC, which forced them to bring disclosure forward a day from Thursday to Wednesday, and that Calif mistakenly published a proof of concept video hours later. The flaws are now tracked as CVE-2026-109618 and CVE-2026-109619, and Wiz says every PHP version released in the last decade is affected by at least one of them.

Chainguard chief executive Dan Lorenc told The Register the company did not leak. He said Chainguard independently found the same memory corruption vulnerabilities on Friday using an AI harness and a frontier model with, in his words, a basic prompt to find bad vulnerabilities in PHP, helped test the patches from Saturday, and decided on Tuesday night to ship the fixes because people were already being hit in advance of disclosure. "It's coordinated vulnerability disclosure, unless there's evidence of active exploits in the wild," Lorenc said, adding that Chainguard honeypots caught IP addresses from China and Russia targeting the vulnerabilities on Wednesday and that he would make the same call again.

**Update, October 23:** Exploitation is now running at scale, and it started before disclosure. Cloudflare says it recorded thousands of exploitation attempts in the 10 hours before the vulnerabilities were publicly announced, tens of thousands within 45 minutes of disclosure, hundreds of thousands within two hours, and millions since, with attackers adapting payloads against its firewall protections. Amazon Threat Intelligence says it detected an attempt to exploit PHP2Shell on October 17, four days before patches were released, through its MadPot honeypot network, and multiple proof of concept exploits on October 21 from different infrastructure, pointing to multiple attackers rather than a single group. Amazon advises organisations to investigate suspicious activity dating back to at least October 17, rather than assuming their systems were safe until disclosure. Security firm Hadrian reported on October 21 that PHP2Shell was being exploited in the wild at scale, mostly through PHP's session upload progress path. Both flaws carry a critical 9.2 severity rating.

**Update, October 24:** A third related flaw will not get an emergency fix. The PHP Foundation told The Register on Friday that it has reserved CVE-2026-115560 for a third remote code execution flaw alongside the two PHP2Shell bugs, and will ship the fix with the next regular PHP release, because exploitation requires what executive director Elizabeth Barron called a very unlikely combination of configuration and application code: the session upload progress feature enabled, a session serialize handler set to php_binary or php_serialize in configuration, and then switched to php at runtime before session start. An informational advisory advises setting session.upload_progress.enabled=0 until the regular release. Barron also said the Foundation has no evidence of successful exploitation of the original two vulnerabilities before disclosure, and no evidence of exploitation on patched versions, a position other researchers qualified on Friday: Mandiant chief technology officer Charles Carmakal said validated proof of concept exploits are capable of remote code execution against default mod_php deployments, though not PHP-FPM, and that the threat remains viable and serious.
