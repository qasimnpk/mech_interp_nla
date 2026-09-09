# P2 summary — claim type × truth, 7B (round 5) vs 27B (pod smoke, notes/nla_setup), same 8 texts, last token, greedy 200 tokens

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
