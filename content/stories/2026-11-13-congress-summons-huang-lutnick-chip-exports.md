---
title: "Congress summons Huang and Lutnick over China chip exports"
date: 2026-11-13T07:12:25-05:00
last_updated: 2026-11-13T17:23:20-05:00
beats: ["politics"]
regions: ["north-america", "asia-pacific"]
status: "story"
lede: "A forensic analysis of published model weights says six Chinese frontier models, including models from DeepSeek, Moonshot AI and MiniMax, were initialised on Nvidia Blackwell systems that US export controls bar from China, adding weight-level evidence to the chip diversion fight now before Congress."
why_it_matters: "If the fingerprint analysis holds, restricted Blackwell hardware sits behind the training of China's leading open models, not only behind the Megaspeed shipments under investigation, and the December testimony from Huang and Lutnick will be asked to explain how it got there."
featured: true
evidence_grade: "B"
sources:
  - title: "Chinese AI labs are training models on Nvidia's Blackwell despite export controls, says ex-OpenAI engineer"
    publisher: "The Register"
    url: "https://www.theregister.com/ai-and-ml/2026/11/13/chinese-ai-labs-are-training-models-on-nvidias-blackwell-despite-export-controls-says-ex-openai-engineer/5309891"
    published: "2026-11-13"
  - title: "Congress summons ex-Nvidia CEO Jensen Huang, Lutnick over chip exports to China"
    publisher: "Decrypt"
    url: "https://decrypt.co/383211/congress-summons-ex-nvidia-ceo-jensen-huang-lutnick-over-chip-exports-to-china"
    published: "2026-11-13"
  - title: "Senate seeks Huang, Lutnick testimony"
    publisher: "AJP News Agency"
    url: "https://www.ajupress.com/view/20261113132308710"
    published: "2026-11-13"
  - title: "China warns tougher US chip curbs could disrupt global supply chain"
    publisher: "DevDiscourse, syndicated wire report"
    url: "https://www.devdiscourse.com/article/international/4006396-china-warns-tougher-us-chip-curbs-could-disrupt-global-supply-chain"
    published: "2026-11-13"
  - title: "Malaysia warns against AI chip transshipment loopholes as Nvidia leadership shakeup deepens scrutiny"
    publisher: "Twentytwo13"
    url: "https://twentytwo13.my/malaysia-warns-against-ai-chip-transshipment-loopholes-as-nvidia-leadership-shakeup-deepens-scrutiny/"
    published: "2026-11-13"
  - title: "Bessent Faults Commerce Dept. for Failing to Blacklist Megaspeed"
    publisher: "The New York Times, via FXNews24 syndication"
    url: "https://fxnews24.co.uk/politics/us-politics/bessent-faults-commerce-dept-for-failing-to-blacklist-megaspeed/"
    published: "2026-11-13"
  - title: "Bessent Says Commerce 'Has the Pen' on Megaspeed as Lutnick Agrees to Testify Over Nvidia Chip Diversion"
    publisher: "The Private Banker"
    url: "https://leprivatebanker.com/2026/11/13/bessent-says-commerce-has-the-pen-on-megaspeed-as-lutnick-agrees-to-testify-over-nvidia-chip-diversion/"
    published: "2026-11-13"
tags: []
update_bump: true
data_as_of: "Senate Banking Committee letters dated November 12, 2026, as reported November 12 and 13; Decrypt report of November 13 and AJP report of November 13, both read in full in this pass. Updated November 13, 2026, with foreign ministry spokesperson Mao Ning's remarks at the ministry's regular Friday briefing, as carried the same day by a syndicated wire report read in full; the ministry's own briefing transcript was not read directly in this run and China's foreign ministry is already logged in this operation's sources-to-implement list. The underlying allegations about Megaspeed and Alice Huang are US officials' suspicions as reported, not findings; the Justice Department investigation is unresolved. Updated November 13, 2026, 13:05 Toronto, with Malaysia's Ministry of Investment, Trade and Industry statement of the same day, as reported in full by Twentytwo13 and read in full in this run; the ministry's own statement was not read directly, and MITI is not yet in this operation's sources-to-implement list, so it is logged there in this run. Updated November 13, 2026, 13:21 Toronto, with Treasury Secretary Bessent's CNBC remarks of the same day blaming the Commerce Department for the stalled Megaspeed Entity List listing, as reported in full by The New York Times (read via syndication) and corroborated by The Private Banker's account read in full in this run; Commerce's denial of the reported Situation Room confrontation is the department spokeswoman's statement as carried in that reporting. Updated November 13, 2026, 17:23 Toronto, with The Register's report of the same day, read in full in this run, on the Unemployment Labs forensic analysis by former OpenAI engineer Will DePue: the analysis is one consultancy's work, its claimed confirmations by senior researchers are DePue's own statement as reported, and Blackwell initialisation does not by itself prove where the GPUs were located, since access through providers outside China would leave the same fingerprint."
---

**Latest.** A forensic report published on Friday says China's leading AI labs trained their frontier models on the Nvidia Blackwell hardware that US export controls were written to keep out of China. Will DePue, a former OpenAI engineer who now runs the research consultancy Unemployment Labs, said he searched more than six trillion combinations of chip layout and seed number and matched the initialisation patterns in published model weights to specific Nvidia hardware, a fingerprint he says survives training. On that analysis, six Chinese models, including DeepSeek-V4-Pro, Moonshot AI's Kimi K3 and MiniMax-M3, were initialised on Blackwell systems, four of them on Grace Blackwell GB200 and GB300 rack-scale systems, and the report names DeepSeek, Moonshot AI, MiniMax and Ant Group as labs that gained access to the restricted GPUs. DePue said it is the first time MiniMax and Ant Group have been publicly linked to Blackwell use, and that senior researchers, independent and inside frontier labs including OpenAI and Anthropic, have confirmed the result. The report carries its own central caveat: a Blackwell fingerprint proves which hardware initialised a model, not where that hardware sits, so the labs could in principle have reached the chips through providers outside China, a remote access route that one of the pending chip bills, the Cloud Security Act, is written to close. The Register's report of the analysis was read in full for this update; the underlying Unemployment Labs report itself was not read directly in this run.

Treasury Secretary Scott Bessent took the administration's internal fight over Megaspeed public on Friday. Speaking on CNBC, Bessent said the Treasury, Defense and State departments and the US trade representative had all been in favour of putting Megaspeed on the Entity List, the trade blacklist administered by the Commerce Department's Bureau of Industry and Security, for months. "Commerce has the pen," he said. "You will have to ask them about their internal processes," adding that Treasury and his deputy had been pushing for the listing at the deputies level for months. Bessent also turned the question back on the chipmaker: the real story, he said, is whether Nvidia knew its client and had a robust effort to make sure there was no leakage of its processors to what were obviously pass-through shell companies. The New York Times had reported on Wednesday that Bessent confronted Lutnick in the White House Situation Room last week over why Megaspeed had not already been banned, and that Lutnick said he would move quickly to put restrictions in place; a Commerce Department spokeswoman denied that the conversation between the two men took place.

Malaysia widened the inquiry on its side of the supply chain on Friday. The Ministry of Investment, Trade and Industry said it has never cleared Megaspeed or its Malaysian affiliate Speedmatrix of regulatory scrutiny, that routine verification visits to data centres were regular monitoring and not clearance, and that it is working with the Royal Malaysian Customs Department to determine whether AI chips Speedmatrix brought into Malaysia were later re-exported and whether any such shipments complied with the law. Importing AI chips into Malaysia needs no licence, the ministry said, but since July 2025 exporting, re-exporting, transshipping or transiting high performance US AI chips from or through Malaysia has required a permit under the Strategic Trade Act 2010, and the ministry said it is coordinating with authorities in Singapore and the United States and reviewing further measures to close regulatory gaps.

Congress moved within hours of Jensen Huang's resignation as Nvidia chief executive to demand testimony on how advanced American chips may have reached China. In letters dated November 12, Senate Banking Committee chairman Tim Scott asked Huang to appear voluntarily at a public hearing on December 3, citing public reports that raise significant national security concerns, and warned that the committee would consider a subpoena if he does not appear. Scott asked Commerce Secretary Howard Lutnick to testify on December 10, on the Commerce Department's authority to issue and enforce export controls. A Commerce spokesman told NBC News that Lutnick has agreed to testify.

The Senate request is one layer of a widening inquiry. The chairs of three House committees want Huang and Nvidia general counsel Tim Teter to sit for closed door transcribed interviews on December 1 and 2, and House Foreign Affairs chairman Brian Mast said Huang had agreed to brief lawmakers before Thanksgiving, with the timing still being negotiated. Politico reported that Huang has agreed to testify before Congress. Separately, Senate Finance ranking member Ron Wyden and House Ways and Means ranking member Richard Neal wrote to Lutnick on November 12 opening an investigation into the approval and tax treatment of exports of advanced Nvidia chips to Chinese companies, including the H200 arrangement under which chips entered the United States for a security review and export licence before re-export, with a 25 percent Section 232 tariff collected on entry. Those are the letter writers' descriptions, not findings.

At the centre of the inquiries is Megaspeed, a Singapore based Nvidia customer whose former executive Alice Huang US officials suspect was recruited by Chinese intelligence and which officials suspect helped Chinese firms obtain restricted chips. The Justice Department is investigating whether she is a spy and has not reached a conclusion, and China denies the allegation. Nvidia has said its board opened an independent investigation and has no reason to believe company secrets or national security were compromised. Lawmakers have not accused Huang of a crime.

The political stakes extend beyond one company. Three chip bills are in play for the defence package, including the Chip Security Act, which would require location verification technology on advanced processors, and measures that would give Congress a review role over licences for advanced AI chip sales. President Trump has separately pitched Apple chief executive Tim Cook as a successor at Nvidia, a suggestion with no corporate standing that the technology beat covers in its own reporting on the resignation.

Beijing answered the pressure on Friday. Asked about tougher chip curbs the United States is preparing to advance, and whether they would violate the trade truce, foreign ministry spokesperson Mao Ning said China has always opposed the abuse of export control measures, that such measures would disrupt the stability of global industrial and supply chains and are not in line with any party's interests, and that China and the United States should work to implement the consensus reached by their two heads of state and maintain the steady development of trade and economic ties.
