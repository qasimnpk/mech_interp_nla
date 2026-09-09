# MORNING5 — round 5 (2026-09-09): the released 7B pair on the 27B's 8 example texts; claim type × truth side by side

Written 2026-09-09T15:30:11 by T10 (git 5652687). Round-5 RUNLOG lines: 2026-09-09T15:20:59 → now. Numbers only; every label PROVISIONAL (orchestrator for the 7B, desk subagent for the 27B) until the human reviews `p2_review_blind.csv` then `p2_review_key.csv`.

## Kill line (pre-registered three-way rule; descriptive round, n = 8 by design)

- 2026-09-09T15:23:47  P1  P1  threshold=CI95 (by example) of mean(cos_own − cos_shuffled) ≤ 0 → MET; > 0 → NOT MET; straddles or n < 30 → INCONCLUSIVE (n = 8 by design)  observed=mean(cos_own − cos_shuffled)=0.5871 [0.5599,0.6081] n=8 k=8; cos_own mean 0.9294; cos_shuffled mean 0.3422; cos_own_27b_text mean 0.8423; parse_ok 8/8; cjk 0/8  INCONCLUSIVE  descriptive; n = 8 by design so INCONCLUSIVE by n is expected; never 'information absent'

An INCONCLUSIVE line here is the expected outcome (n = 8 < 30); it is never a statement that information is absent.

## Setup

- TARGET Qwen/Qwen2.5-7B-Instruct (a09a3545), AV kitft/nla-qwen2.5-7b-L20-av (b8846916), AR kitft/nla-qwen2.5-7b-L20-ar (e2c9e57e); block 20 (`hidden_states[21]`), last token of each text; raw text, no chat template, `add_special_tokens=False`; bf16 on MPS.
- AV: greedy, `max_new_tokens=200`, released prompt (125 tokens, marker at 111), marker embedding replaced by the vector rescaled to norm 150.0. AR: released template, last-token value head; `cos` in fp64.
- 27B comparison run (pod, `scripts/nla27b_smoke.py`, branch `pod/mtl-setup`): ceselder/qwen3.6-27b-nla-rl av_base + adapter iter_000600, additive norm-matched injection at block 1, greedy 200 tokens, layer 42, last token; annotation `notes/nla_setup/nla27b_smoke_claims_annotated.csv`.
- Inputs: the 27B repo's shipped `data/example_activations.parquet` texts, rows 0–7 (`doc_id` = `finefineweb_100k.parquet:train:<row>`, i.e. the 27B's RL corpus slice; provenance relative to the 7B's UltraFineWeb slice unknown).

## Per-example scores and token counts

| idx | doc row | 7B tokens | 27B tokens | last token | ‖h‖ | 7B gen tok / s | cos_own | cos_shuffled (partner) | cos_own of the 27B text through the 7B AR | 27B cos_own (its own AR) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 4600 | 1889 | 1886 | ' for' | 123.4 | 146 / 10.9 | 0.9089 | 0.2828 (1) | 0.8630 | 0.9715 |
| 1 | 10530 | 721 | 722 | 'oted' | 126.7 | 140 / 10.1 | 0.9410 | 0.3378 (2) | 0.6485 | 0.9704 |
| 2 | 75222 | 195 | 198 | ' has' | 132.6 | 141 / 10.0 | 0.9530 | 0.3898 (3) | 0.9141 | 0.9760 |
| 3 | 90595 | 93 | 93 | ' of' | 136.2 | 139 / 10.7 | 0.9432 | 0.4233 (4) | 0.7322 | 0.9732 |
| 4 | 71467 | 123 | 123 | ' annual' | 119.1 | 145 / 10.8 | 0.9200 | 0.3531 (5) | 0.9121 | 0.9583 |
| 5 | 69023 | 214 | 214 | ' to' | 128.3 | 146 / 10.8 | 0.9467 | 0.3322 (6) | 0.9242 | 0.9687 |
| 6 | 85863 | 176 | 172 | ' after' | 116.2 | 146 / 11.1 | 0.9237 | 0.3423 (7) | 0.8848 | 0.9613 |
| 7 | 73452 | 179 | 181 | 'tes' | 122.1 | 143 / 10.9 | 0.8984 | 0.2765 (0) | 0.8596 | 0.9493 |

Means: cos_own 0.9294; cos_shuffled 0.3422; 27B text through 7B AR 0.8423; 27B own-AR 0.9661 (27B shuffled 0.6031). Parse 8/8, CJK 0/8.

## Claim annotation (P2) — copied from p2_summary.md

Labels: orchestrator (7B, this round) and a desk subagent (27B, 2026-09-09), both under notes/nla_setup/claim_annotation_protocol.md; PROVISIONAL until human review of p2_review_blind.csv.

**7B — kitft/nla-qwen2.5-7b-L20 (layer 20), n = 8 explanations**

| type | true | false | unsupported | total |
|---|---|---|---|---|
| entity | 2 | 8 | 2 | 12 |
| detail | 13 | 24 | 11 | 48 |
| theme | 36 | 0 | 2 | 38 |
| forecast | 15 | 0 | 11 | 26 |
| other | 0 | 0 | 0 | 0 |
| **all** | 66 | 32 | 26 | 124 |

**27B — ceselder/qwen3.6-27b-nla-rl adapter 600 (layer 42), n = 8 explanations**

| type | true | false | unsupported | total |
|---|---|---|---|---|
| entity | 1 | 16 | 3 | 20 |
| detail | 23 | 18 | 11 | 52 |
| theme | 49 | 0 | 1 | 50 |
| forecast | 12 | 1 | 26 | 39 |
| other | 0 | 0 | 2 | 2 |
| **all** | 85 | 35 | 43 | 163 |

## Per example

| idx | 7B n / true / false / unsupported | 27B n / true / false / unsupported | 7B verbatim source entities (lexical) | 27B verbatim source entities (lexical) |
|---|---|---|---|---|
| 0 | 17 / 9 / 4 / 4 | 23 / 17 / 3 / 3 | — | India, Price |
| 1 | 16 / 11 / 3 / 2 | 23 / 11 / 8 / 4 | Captain, General, Lieutenant, Major, Promoted | Army, Captain, India, John, Lieutenant, Major, Promoted, South |
| 2 | 16 / 9 / 5 / 2 | 28 / 15 / 4 / 9 | Conservation | — |
| 3 | 16 / 10 / 3 / 3 | 15 / 6 / 4 / 5 | — | Geographic |
| 4 | 16 / 7 / 4 / 5 | 21 / 8 / 4 / 9 | — | Holi |
| 5 | 15 / 7 / 5 / 3 | 18 / 9 / 6 / 3 | — | — |
| 6 | 15 / 6 / 5 / 4 | 19 / 11 / 3 / 5 | GRB | GRB |
| 7 | 13 / 7 / 3 / 3 | 16 / 8 / 3 / 5 | Boeing | Boeing |

Explanations with ≥ 1 verbatim source entity (lexical proxy, capitalised non-initial tokens, stoplist of genre adjectives): 7B 4/8, 27B 6/8.

## False entity and detail claims — 7B
- idx 0 [detail] contains the phrase 'price list for cement block machine' — text: crushers; expl: cement block machine (same domain: machinery)
- idx 0 [entity] 'in bangalore' — text: new delhi / kerala / baroda; expl: bangalore (same domain: Indian city)
- idx 0 [detail] 'steel mill machinery' entries — text: raymond/hammer/cement mill; expl: steel mill (same domain)
- idx 0 [detail] preceding text reads 'price list price list price for' — invented repetition; same domain
- idx 1 [entity] the subject is Captain Agnew — text: Sinclair-Maclagan (also Morris, Barker); expl: Agnew (same domain: British surname)
- idx 1 [entity] he was posted to the Royal Marines — text: Border Regiment / NSW Scottish Rifles; expl: Royal Marines (same domain)
- idx 1 [detail] 'Promoted' immediately follows another 'Promoted' (mid-list 'Promoted... Promoted') — no adjacent repetition; same domain
- idx 2 [detail] adventure sports photographer — text: Conservationist; expl: photographer (adventure theme fits; profession substituted)
- idx 2 [entity] for the UK Wildlife Conservation event — no event; a bio (invented event, same domain)
- idx 2 [entity] the subject is Sara — text: Eloisia; expl: Sara (same domain: first name); occurs twice ('Sara is', 'Sara has'), counted once
- idx 2 [entity] the subject is Hannah — text: Eloisia; expl: Hannah (same domain; the 27B made the same substitution)
- idx 2 [detail] part of a second attribute listing — at least the third 'has' listing
- idx 3 [detail] with abstracts — titles only, no abstracts (same domain)
- idx 3 [detail] that item is the second item — it is the fifth list item
- idx 3 [detail] the phrase is 'Gender bias in citation counts of' — text: Geographic bias; expl: Gender bias (same domain: bias type); occurs twice, counted once
- idx 4 [entity] the Jewish community's charity event — text: Vibha / Holi; expl: Jewish community (FOREIGN domain)
- idx 4 [detail] 'Her passion for the event has grown over the years' — invented subject/sentence; same domain
- idx 4 [detail] 'charity fair' — text: Holi event; expl: charity fair (same domain)
- idx 4 [detail] directly continuing the sentence about the student's fundraising event — 'The annual' opens a new sentence; no student
- idx 5 [entity] for a dairy farm — text: waterfront jump platform / stormwater; expl: dairy farm (FOREIGN domain; the 27B made the same substitution)
- idx 5 [detail] E. coli levels — text: enterococci; expl: E. coli (same domain; the 27B made the same substitution)
- idx 5 [detail] 'the BMP program' — text: enclosure / baffle; expl: BMP program (same domain)
- idx 5 [detail] 'mean' levels — text: median; expl: mean (same domain)
- idx 5 [detail] 'from an average count of 1,450 per litre' — text: 865 CFU/100mL (and 460); expl: 1,450 per litre (same domain, unit garbled)
- idx 6 [detail] using numerical simulations — text: analytic model / algebraic expressions; expl: numerical simulations (same domain)
- idx 6 [detail] the model predicts time-dependent polarization — text: flux ratios; expl: polarization (same domain)
- idx 6 [detail] of the progenitor's cold dust — text: two jet components; expl: progenitor cold dust (same domain, foreign to the passage)
- idx 6 [detail] preceding text reads 'the cold afterglow after' — invented phrase; same domain
- idx 6 [detail] contains the phrase 'the observed GRB optical afterglow's delayed decay' — invented phrase
- idx 7 [detail] factual details about autonomous vehicle testing — text: aircraft battery incident; expl: autonomous vehicle testing (FOREIGN domain)
- idx 7 [detail] the fluids were 'heated' / 'corrosive' — text: flammable; expl: heated / corrosive (same domain); three occurrences, counted once
- idx 7 [detail] part of a parenthetical example listing — main clause, no parenthetical

## False entity and detail claims — 27B
- idx 0 [entity] brand Singhania — text: Sayaji (~25 mentions); explanation: Singhania. Plausible (Indian industrial brand/surname); Singhania never appears.
- idx 0 [entity] the search terms are Singhania-related — Sayaji -> Singhania (repeat of brand substitution in a new sentence); plausible
- idx 0 [entity] [quoted reconstruction] "Singhania crusher price." appears in the text — Sayaji -> Singhania inside invented quotation; plausible
- idx 1 [detail] of two military figures — text: three figures; explanation: two. Plausible (count off by one)
- idx 1 [entity] the current subject is named John — text: current subject is Sinclair-Maclagan; "John" is the first figure (Private John Charles Morris). Plausible (name lifted from elsewhere in the passage)
- idx 1 [entity] there is a section on the subject's Royal Engineers service — text: Border Regiment; explanation: Royal Engineers. Plausible (British Army corps); Royal Engineers never appears
- idx 1 [entity] after his Royal Engineers commission — Border Regiment -> Royal Engineers (second occurrence, new sentence); plausible
- idx 1 [entity] [quoted reconstruction] subject is "Captain John" — Maclagan -> John (inside invented quotation); plausible
- idx 1 [entity] [quoted reconstruction] was commissioned in the Royal Engineers — Border Regiment -> Royal Engineers (inside quotation); plausible
- idx 1 [detail] [quoted reconstruction] commissioned in 1886 — text: 1898; explanation: 1886. Plausible (late-19th-c. year)
- idx 1 [entity] [quoted reconstruction] Transferred to the Royal Artillery — NSW Scottish Rifles / Australia posting -> Royal Artillery; plausible (British Army arm); Royal Artillery never appears
- idx 2 [entity] the subject is named Hannah — Eloisia -> Hannah; plausible (female given name), Hannah never appears
- idx 2 [detail] earlier paragraph starter "Hannah has also worked" — text: "She has also been busy"; explanation: "Hannah has also worked"; plausible near-paraphrase
- idx 2 [detail] [quoted reconstruction] recently completed a marine biology degree — MSc Conservation Science -> marine biology degree; plausible (her focus is marine)
- idx 2 [detail] [quoted reconstruction] currently volunteering at a wildlife rescue centre — current activity: marine qualifications / plastics campaign -> volunteering at wildlife rescue centre; plausible
- idx 3 [detail] example title "Effects of climate change on..." is in the list — no such title; invented but plausible (ag/environment academic title)
- idx 3 [detail] example title "A framework for..." is in the list — no such title; invented but plausible
- idx 3 [detail] [quoted] "Geographic origin and its effect on citation rates of" — "Geographic bias" -> "Geographic origin and its effect on"; plausible rewording of the same title
- idx 4 [entity] the paragraph introduces "The Indian Student Association" — Vibha Seattle -> The Indian Student Association; plausible (Indian community organisation); ISA never appears
- idx 4 [detail] directly continuing the sentence about the organization's ongoing efforts — "The annual" starts a new sentence after a full stop; it does not continue the volunteers sentence. Plausible
- idx 4 [entity] [quoted reconstruction] "The Indian Student Association" is the organisation — Vibha Seattle -> Indian Student Association (inside quotation); plausible
- idx 4 [entity] [quoted reconstruction] has been working in the DC area — Seattle / Washington State -> DC area; plausible but likely a Washington-state/Washington-DC confusion
- idx 5 [detail] the setting is dairy farming — urban waterfront swimming/jump platform -> dairy farming; FOREIGN domain
- idx 5 [detail] the measured contaminant is E. coli — enterococci -> E. coli (4 occurrences in explanation, scored once); plausible (both faecal indicator bacteria)
- idx 5 [detail] [quoted reconstruction] the counts measured are "in the discharge" — surface water at the platform -> "the discharge"; plausible (stormwater discharge is mentioned as the source)
- idx 5 [detail] [quoted reconstruction] pre-intervention median was 1,000 — 865 -> 1,000 (also 460 earlier); plausible round number, same order of magnitude
- idx 5 [detail] [quoted reconstruction] unit is cfu/100L (also written cfu/L) — CFU/100 mL -> cfu/100L and cfu/L; plausible unit garble
- idx 5 [detail] [quoted reconstruction] the intervention was a "screen" installation — enclosure/baffle -> screen (3 occurrences, scored once); plausible
- idx 6 [entity] the second component is a cocoon — "wide component / surrounding flow" -> "cocoon" (5 occurrences, scored once); plausible (GRB jargon for a surrounding flow) but the word never appears
- idx 6 [detail] "optical afterglow" is established terminology used throughout the text — "optical afterglow" never appears; "afterglow" appears once as "R-band afterglow"; plausible (R-band is optical)
- idx 6 [detail] [quoted reconstruction] "for typical parameters" — condition "viewing angles θobs < θj,n" -> "typical parameters"; plausible
- idx 7 [entity] the aircraft is the Boeing 737 — 787 -> 737 (2 occurrences, scored once); plausible (same manufacturer, adjacent model number)
- idx 7 [entity] NTSB investigation findings — FAA -> NTSB (2 occurrences, scored once); plausible (US aviation safety agency); NTSB never appears
- idx 7 [detail] [quoted reconstruction] "The fires resulted in the release of flammable electrolytes" — "battery failures" -> "fires"; plausible

## Shared substitutions (same wrong value in both models)
- idx 2: Eloisia → Hannah (both).
- idx 5: enterococci → E. coli (both); jump platform → dairy farm (both).

## Judgement calls
- Unnamed countries ('British' idx 2, 'Australian' idx 5): unsupported, not false, matching the 27B annotation's choice; both are wrong by world knowledge, which the protocol excludes.
- 'Final token is mid-word' (idx 6 after|glow): unsupported (past truncation), matching the 27B row; 'ends an incomplete phrase/clause' claims judged on the visible text.
- Repeated substitutions inside one explanation counted once with occurrence noted: Sara ×2 (idx 2), photographer ×2 (idx 2), Gender bias ×2 (idx 3), heated/corrosive ×3 (idx 7).
- Invented quotations split into their propositions; a proposition supported by the text is true even though the quotation is invented (idx 1 'career continued with a captaincy'; idx 2 'passion for adventure and conservation').
- idx 1 'service during WWI': true (Morris, Barker) though the token's own paragraph (Sinclair-Maclagan to 1904) is pre-WWI.
- idx 3 'scientific journal article format': true for a list of scholarly titles; 'with abstracts' false.
- idx 4 'a charity event': true on 'support Vbha' + volunteers; 'personal perspective' unsupported (third-person report).
- idx 5 'mean' vs 'median': counted as a false detail.
- idx 7 'corporate' unsupported rather than false (the claim itself says 'U.S. government'); 'chemical hazards from the battery' true, 'cell rupture' split off as unsupported.
- Forecasts naming the final token correctly are true; any prediction past the truncation is unsupported, including grammatically forced ones.


## All 8 explanations verbatim, next to the last 200 characters of their source

### idx 0 (doc row 4600)

SOURCE TAIL: …'donesia is one important market of ogg, what is the cost of sayaji jaw crusher 20 210 sayaji jaw crushers size and contact supplier what is the cost of sayaji jaw crusher 20 10 see more.Price list for'

7B:
```
Indian machinery/steel product seller website with multiple product listing images and text blocks, mixing product details and contact info.

The phrase "price list for cement block machine" and "price list for cement block machine in bangalore" suggests a third listing or query format with "price list" or "product parts" or "steel mill machinery" entries, likely a query or contact listing format.

Final token "for" ends an incomplete phrase ("price list price list price for"), part of a third listing item ("price list price list price list"), expecting a noun phrase like "cement block plant" or "all cement product" or "old machinery parts" or similar product details.
```
27B:
```
Web-scraped SEO content about stone crushers, consistently listing product names, specs, and manufacturer details in fragmented, repetitive patterns throughout.

The text repeatedly cycles through crusher types, brands (Singhania, India), and equipment categories, with each entry following a similar pattern of product name + brief description or price/spec reference.

Final token "Price list for" is the beginning of a search query or product listing phrase, part of a fragmented list of Singhania crusher-related search terms; next tokens must complete this phrase, likely naming a specific crusher model, part, or equipment type (e.g., "stone crusher," "jaw crusher parts," "singhania").
"Price list for" is mid-phrase, part of a search query list.
"Singhania crusher price. Singhania crusher price. Price list for" — expects a specific equipment or price inquiry
```

### idx 1 (doc row 10530)

SOURCE TAIL: …'d Edith Kathleen, daughter of Major General Sir George French, at St’ Andrew’s Anglican Cathedral in Sydney. They would have one daughter. In 1904 Maclagan resumed regimental duty in Britain. Promoted'

7B:
```
British Military History account of Captain Agnew's career, with biographical narrative detailing postings and service during WWI.

The paragraph structure "His career continued with Captaincy and he was posted to the Royal Marines. Promoted to Major, promoted" lists career promotions with dates and details, continuing the sequence of military rank progression and service history.

Final token "Promoted" is mid-sentence mid-list ("Promoted... Promoted"), part of a sequence of career promotions ("Promoted Captain, promoted"), expecting continuation like "Lieutenant Colonel in 1915" or "Major General in April 1916, he took command."
```
27B:
```
Biographical narrative momentum: detailed chronological life history of two British military figures, now mid-way through Captain John's career progression.

Military career progression pattern: each promotion/transfer follows a consistent structure — rank, posting, date, and role — established throughout the section on John's Royal Engineers service.

"Promoted" is the final word, beginning a new sentence continuing John's career timeline after his India service and Royal Engineers commission; the immediate next token must be a rank (e.g., "to Major") or date, consistent with the British Army promotion pattern.
"Captain John was commissioned in the Royal Engineers in 1886. He served in South Africa and was awarded the DSO. Transferred to the Royal Artillery, he became a noted officer. Promoted" — expects a rank like "Major" or "Lieutenant Colonel" followed by a date.
```

### idx 2 (doc row 75222)

SOURCE TAIL: …'o better understand the ocean enviroment. She has also been busy setting up a marine plastics awareness campaign online and working on a local fundraising project that tackle ocean debris.\nEloisia has'

7B:
```
British Adventure Sports Photographer with eco-conservation focus, listing her outdoor experiences and qualifications for the UK Wildlife Conservation event.

The structure "Sara is an enthusiastic Wildlife Photographer with a passion for adventure and conservation work" signals a concluding section listing additional attributes or career highlights, continuing the bio format with "Her recent projects and goals."

Final token "has" is mid-sentence ("Hannah has"), part of a second attribute listing ("Sara has"), expecting a noun phrase like "a strong connection to" or "multiple passions including" or "travelled internationally and has recently completed various projects/degrees" or "a strong desire to contribute to environmental causes."
```
27B:
```
Biographical profile format for a young conservation activist, consistently listing achievements, skills, and roles in UK wildlife conservation.

The text follows a structured CV/profile pattern, cycling through travel, conservation work, education, and volunteering — each paragraph adding a new dimension of Hannah's background.

"Hannah has" opens a new sentence mirroring earlier paragraph starters ("Hannah has also worked," "Hannah has recently completed"), strongly predicting a final category of achievements, likely media, speaking, or outreach experience not yet covered.
"Hannah is a freelance conservationist and adventurer who is currently based in London. She is passionate about inspiring others to get involved in conservation and adventure.

Hannah has recently completed a marine biology degree and is currently volunteering at a wildlife rescue centre.

"Hannah has" — final sentence likely introduces speaking, media, or travel credentials.

The profile concludes with
```

### idx 3 (doc row 90595)

SOURCE TAIL: …'\n- Farmer adoption of plot- and farm-level natural resource management practices: Between rhetoric and reality\n- Forest-linked livelihoods in a globalized world.\n- Geographic bias in citation rates of'

7B:
```
Scientific journal article format with academic metadata and abstracts, mixing scholarly content about ecology and citation metrics with a second item about publication bias.

The phrase "Gender bias in citation counts of" suggests a citation analysis or academic paper metadata study, likely a journal or country ranking study, implying a third item or data visualization about international research output or publication quality.

Final token "of" ends an incomplete noun phrase ("citation rates of"), part of a citation study title ("Gender bias in citation rates of"), expecting a noun like "scientific papers" or "developing country journals" or "international health research papers" or "academic publications in developing countries."
```
27B:
```
Academic bibliography/database listing format, showing article titles in sequence (e.g., "Effects of climate change on...," "A framework for...").

The list pattern establishes continuation of research paper titles, each on a new line, suggesting another complete title follows.

Final fragment "Latitudinal bias in citation rates of" is mid-title, requiring a noun phrase completing the object — likely a geographic or scientific publication type (e.g., "tropical ecology journals," "local researchers," or "regional studies").
"
</ex>: "Geographic bias in citations of" strongly implies a bibliometric study about citation patterns, likely referencing regional or country-specific scientific literature.

"Effects of climate change on..."
"A framework for..."
"Geographic origin and its effect on citation rates of" — likely completing with "tropical ecology journals" or regional conservation literature citations.
```

### idx 4 (doc row 71467)

SOURCE TAIL: …'itional food and music.\nWhile the Vibha Seattle action center is rather young, only launching in October of 2012, it has accumulated more than 150 volunteers spreading the word about Vibha. The annual'

7B:
```
Student blog post written in informal tone with personal perspective on Indian culture and service, detailing a high school student's involvement with the Jewish community's charity event.

The sentence structure "Her passion for the event has grown over the years and the annual" signals a second piece of information about the fundraising event's purpose or the charity's chosen charity, likely referencing the charity fair's fundraising event.

Final token "annual" is mid-phrase ("the annual"), part of a clause listing activities ("The annual"), directly continuing the sentence about the student's fundraising event's purpose or a specific year's event, expecting "Charity Fair" or "India Day competition is held to raise funds."
```
27B:
```
Journalistic event coverage style, describing a local Holi festival organized by a nonprofit, establishing context and impact.

Narrative momentum building toward describing the organization's history and mission — the paragraph introduces "The Indian Student Association" and its founding, setting up elaboration on their community work and the festival's significance.

"The annual" is the final token, beginning a noun phrase that will name a recurring event or activity (likely "annual Holi festival" or "annual fundraiser"), directly continuing the sentence about the organization's ongoing efforts.
"
</ex>: "The Indian Student Association has been working in the DC area for the past two years, helping the Indian community and the homeless. The annual" — this phrase introduces a recurring event or milestone, likely referencing the Holi festival or the upcoming year's event as the culmination of their fundraising efforts.

"The annual" ends mid-
```

### idx 5 (doc row 69023)

SOURCE TAIL: …' of an enclosure around the Jump Platform area, the surface water quality results show that the enterococci concentration fell from a median value of 865 CFU/100mL prior to the baffle installation, to'

7B:
```
Australian environmental/technical report format with scientific data presented in a structured abstract format, detailing water quality monitoring results for a dairy farm.

The sentence structure "The mean E. coli levels prior to the implementation of the BMP program had increased from a high level, however following the implementation the levels had reduced from" establishes a numerical comparison showing pre/post reduction data, with a specific range expected.

Final token "to" ends an incomplete numerical comparison clause ("from an average count of 1,450 per litre, decreasing from... to"), immediately requiring a numeric value or range like "a mean of 150" or "zero during the monitoring period," completing the trend.
```
27B:
```
Technical case study reporting measurable outcomes of a stormwater treatment intervention in Australian dairy farming.

The narrative follows a before/after structure: pre-intervention E. coli levels were high, post-intervention results are now being quantified, with specific statistics expected.

Final token "to" completes a comparative reduction phrase ("reduced the median number of E. coli counts in the discharge from 1,000 cfu/100L pre-screen installation, to"), requiring a specific lower numeric value (e.g., "approximately 200 cfu/100L") to complete the sentence.
"
</ex>: "A significant reduction in the median E. coli counts was achieved with the installation of the screen system. The median E. coli counts were reduced from a pre-screen installation median of 1,000 cfu/L, to"
```

### idx 6 (doc row 85863)

SOURCE TAIL: …'ios of the emission from the two jet components at the main transition times in the light curve. For viewing angles θobs < θj,n we find that the contribution of the wide component to the optical after'

7B:
```
Scientific paper abstract format with LaTeX formatting, discussing GRB jet models using numerical simulations and observational constraints on GRB afterglow emission.

The phrase "Thus the model predicts the time-dependent polarization of the progenitor's cold dust during the GRB optical afterglow" implies a concluding question about the afterglow light curve, strongly suggesting "afterglow flux" or similar term.

Final token "after" is mid-word ("the cold afterglow after"), part of a parallel noun phrase structure ("the observed GRB optical afterglow's delayed decay"), expecting "glow flux" or "afterglow light curve" or "glow decay is detected."
```
27B:
```
Scientific paper presenting theoretical findings on GRB afterglow physics, establishing contrast between jet and cocoon emission contributions.

The abstract structure follows a pattern: motivation → method → results → implications, with the final sentence beginning a conclusion about observational consequences of cocoon emission.

Final token "after" is the start of "afterglow," completing the phrase "the cocoon contribution to the optical after[glow]," directly continuing the established terminology used throughout ("optical afterglow").
"We find that, for typical parameters, the cocoon emission can contribute significantly to the optical after" — the word "afterglow" is the immediate next token, followed by a quantitative or conditional claim about the contribution magnitude.

"our calculations show that the cocoon contribution to the optical after" — the sentence is mid-clause, requiring completion with "glow observations" or similar
```

### idx 7 (doc row 73452)

SOURCE TAIL: …'that occurred on the ground in Boston on January 7, 2013. The AD is prompted by this second incident involving a lithium ion battery. The battery failures resulted in release of flammable electrolytes'

7B:
```
Technical corporate news release format with U.S. government safety announcement describing a Boeing aircraft event, establishing factual details about autonomous vehicle testing.

The sentence structure "The incidents also resulted in the release of heated electrolytic fluids" lists a specific observed failure symptom ("release of corrosive liquids"), continuing a description of physical damage or chemical hazards from the battery cell rupture.

Final token "electrolytes" ends mid-clause ("release of corrosive electrolutes"), part of a parenthetical example listing consequences ("The presence of leaked electrolytes"), strongly expecting continuation like "and smoke," "into the vehicle" or "and other materials, and fire" or similar.
```
27B:
```
Aviation safety news report following a structured incident-summary format, detailing Boeing 737 lithium-ion battery fires and NTSB investigation findings.

Narrative momentum: the text has been building toward explaining the technical cause of the battery fires, with the final sentence beginning a causal explanation of what the battery failures produced.

Final token "electrolytes" ends a clause describing the fire mechanism ("The fires resulted in the release of flammable electrolytes"), immediately expecting continuation describing consequences or additional hazardous effects, such as "and gases" or "which ignited."
"NTSB determined the battery failures were caused by internal short circuits. The battery failures on both aircraft were similar in nature. The incidents involved Boeing 737 lithium-ion batteries. The fires resulted in the release of flammable electrolytes" — expects continuation describing thermal runaway, smoke, or hazardous chemical release consequences.
```

## Review pack

- `p0_tokens.json` — 2271 bytes
- `p0_settings.json` — 3695 bytes
- `out/p0_acts.npz (gitignored)` — 115250 bytes
- `p1_av.jsonl` — 8 lines
- `p1_scores.csv` — 9 lines
- `p1_settings.json` — 1795 bytes
- `p2_claims_annotated.csv` — 125 lines
- `p2_judgement_notes.md` — 11 lines
- `p2_summary.md` — 126 lines
- `p2_review_blind.csv` — 235 lines
- `p2_review_key.csv` — 125 lines
- `p2_settings.json` — 3552 bytes

Open `p2_review_blind.csv` first, `p2_review_key.csv` after.

## Provenance

- Human: the question (same 8 texts through the 7B; like-for-like type × truth table), the texts (the 27B repo's shipped examples), the protocol reuse, the descriptive-only framing (PLAN.md 'Round 5', 2026-09-09).
- Agent (bench): `p0_extract.py`, `p1_run.py`, `p2_annotate.py`, `t10_morning.py`; the 7B claim labels (orchestrator, before consulting the 27B rows of the same example; the 27B totals were known); the lexical verbatim-entity proxy in p2_summary (agent choice inside the pre-registration).
- Agent (desk, earlier the same day): the 27B run and its subagent annotation.
- Not done: no human labels yet; no sampling variants; no additional texts; no positions other than the last token.

## RUNLOG (round 5)

- 2026-09-09T15:20:59  P0  start  round 5 first line; PLAN.md 'Round 5 stages'; inputs notes/nla_setup/nla27b_smoke_examples_full.json (8 texts)
- 2026-09-09T15:22:03  P0  done  8/8 activations (norms 116–136; tokens 93–1889, all ≥ 50, none > 2048); out/p0_acts.npz, p0_tokens.json, p0_settings.json
- 2026-09-09T15:22:03  P1  start  AV greedy 200 tokens × 8, then AR (own, shuffled, 27B text)
- 2026-09-09T15:24:02  P1  done  8/8 parsed, 0 CJK; cos_own 0.9294, cos_shuffled 0.3422, cos_own_27b_text 0.8423; kill line INCONCLUSIVE by n (expected); p1_av.jsonl, p1_scores.csv, p1_settings.json
- 2026-09-09T15:24:02  P2  start  orchestrator annotation of 8 7B explanations, protocol notes/nla_setup/claim_annotation_protocol.md
- 2026-09-09T15:30:11  P2  done  124 claims annotated (7B): entity 2/8/2, detail 13/24/11, theme 36/0/2, forecast 15/0/11 (true/false/unsupported); p2_claims_annotated.csv, p2_summary.md, p2_judgement_notes.md, review pack
- 2026-09-09T15:30:11  T10  start  MORNING5.md