# S1 summary — baseline round trip (200 positions; headline numbers on evaluation set 40–199)

git 7a23504c; settings in s1_settings.json

## Timings

- av_load_s: 5.08
- rss_after_av_G: 3.54
- av_sec_per_explanation: 9.98
- av_n_generated: 184
- rss_after_av_free_G: 0.52
- ar_load_s: 3.62
- ar_sec_per_score: 0.28

## Evaluation set (n=160)

| column | distribution |
|---|---|
| cos_own | mean 0.8820 | median 0.8918 | p10 0.8163 | p90 0.9288 | n 160 |
| cos_shuffled_samedoc | mean 0.3664 | median 0.3598 | p10 0.2370 | p90 0.4974 | n 160 |
| cos_shuffled_doc | mean 0.3198 | median 0.3166 | p10 0.1957 | p90 0.4295 | n 160 |
| cos_L19 | mean 0.8345 | median 0.8454 | p10 0.7665 | p90 0.8845 | n 160 |
| cos_L21 | mean 0.8359 | median 0.8467 | p10 0.7657 | p90 0.8882 | n 160 |
| cos_empty | mean 0.3471 | median 0.3483 | p10 0.2435 | p90 0.4435 | n 160 |

- mean cos_own − mean cos_empty (positive control, whole explanation deleted): 0.5349
- mean cos_own CI95 (cluster bootstrap): [0.8753, 0.8886]
- paired cos_own − cos_shuffled_samedoc: 0.5156 CI95 [0.4987, 0.5331]
- paired cos_own − cos_shuffled_doc: 0.5622 CI95 [0.5455, 0.5779]
- fraction cos_L19 > cos_own: 0.000; fraction cos_L21 > cos_own: 0.006
- parse_ok fraction: 1.000; cjk fraction: 0.006; AV/AR errors: 0
- Spearman(n_tokens, cos_own): rho=-0.1912 p=0.0155

| act_norm tercile | act_norm range | mean cos_own | n |
|---|---|---|---|
| low | 80.0–109.4 | 0.8733 | 54 |
| mid | 109.5–117.8 | 0.8766 | 53 |
| high | 117.9–140.2 | 0.8963 | 53 |

## Pilot set (n=40, for reference)

| column | distribution |
|---|---|
| cos_own | mean 0.8934 | median 0.9010 | p10 0.8500 | p90 0.9392 | n 40 |
| cos_shuffled_samedoc | mean 0.3692 | median 0.3561 | p10 0.2388 | p90 0.5076 | n 40 |
| cos_shuffled_doc | mean 0.3062 | median 0.3092 | p10 0.2150 | p90 0.4015 | n 40 |
| cos_L19 | mean 0.8444 | median 0.8516 | p10 0.7842 | p90 0.8926 | n 40 |
| cos_L21 | mean 0.8391 | median 0.8424 | p10 0.7716 | p90 0.8956 | n 40 |
| cos_empty | mean 0.3310 | median 0.3478 | p10 0.1808 | p90 0.4555 | n 40 |

## Kill tests

- 2026-09-06T02:59:26  S1  K1a  threshold=mean cos_own<0.5 (eval n>=160)  observed=mean cos_own=0.8820 CI95=[0.8753,0.8886] n=160  NOT MET  pipeline fidelity on wikitext stimuli vs published 0.752 FVE on WildChat+FineWeb
- 2026-09-06T02:59:26  S1  K1b  threshold=mean cos_shuffled_samedoc >= mean cos_own-0.05  observed=mean cos_own=0.8820 mean cos_shuffled_samedoc=0.3664 paired diff=0.5156 CI95=[0.4987,0.5331] n=160; cross-doc: mean cos_shuffled_doc=0.3198 diff=0.5622 CI95=[0.5455,0.5779]  NOT MET  position specificity: MET would mean explanations reconstruct another position of the same context about as well as their own

## 5 evaluation explanations chosen by seed 0 (verbatim)

### stim 82 (doc 207, pos 224) token=' in' cos_own=0.809 cos_samedoc=0.323 parse_ok=True

context: " parents and leave the nest after a fortnight . There may be two broods in southern parts of the range but only one further north . Migrating birds and wintering birds often form large flocks , often in the company of Redwings . \n The fieldfare is 25 cm ( 10" [[" in"]] " ) long , with a grey crown , neck and rump , a plain brown"

```
Wikipedia article format with structured biological description of a plant species, listing characteristics and measurements with parenthetical details.

The measurement value "Height: 15 cm (6 in" is mid-sentence with a numeric comparison ("length: 15 cm (6 in"), suggesting a second unit or closing parenthesis completing the size description of the bird's dimensions.

Final token "in" ends an incomplete unit expression ("6 in"), part of a parenthetical measurement specification ("length: 15 cm (6 in"), immediately expecting " )" or " ) in diameter" or " a)" to close the size comparison, likely continuing the bird's physical description.
```

### stim 89 (doc 272, pos 377) token=' typical' cos_own=0.892 cos_samedoc=0.436 parse_ok=True

context: ".@ 4 \u2013 0 @.@ 8 in ) long and about 0 @.@ 15 cm ( 0 @.@ 06 in ) wide . New growth occurs in summer , and flowering ranges from November to April with a peak in February , but can be irregular in timing . Flowers arise from" [[" typical"]] " Banksia \" flower spikes \" , and the inflorescences are made"

```
Australian botanical/field guide format with structured species description, detailing a rare New Zealand orchid species with botanical characteristics and habitat.

The sentence "The flower is tubular shaped, emerging from a bulb-like spike typical" introduces a descriptive clause mid-sentence listing flower features, likely referencing the orchid's characteristic corolla structure or inflorescence form from the genus.

Final token "typical" ends an incomplete noun phrase ("from typical"), part of a botanical description clause ("Flowers feature from typical"), immediately expecting a noun like "orchidoid sepals" or "rounded orchid flowers" or "Bulbous orchid flower structures" continuing the taxonomic description.
```

### stim 120 (doc 393, pos 186) token=' promised' cos_own=0.879 cos_samedoc=0.317 parse_ok=True

context: " . The episode also earned 3 other Emmy nominations as well as WGA : Episodic Drama and DGA \u2013 Drama Series nominations . \n Frank Underwood ( Kevin Spacey ) is an ambitious Democratic congressman and the House Majority Whip . Underwood helped ensure the election of President Garrett Walker ( Michel Gill ) , who" [[" promised"]] " to appoint Underwood as Secretary of State . However , before Walker is sworn in"

```
Political news article format with quoted tweet structure detailing a celebrity's Senate testimony, establishing narrative context around Republican congressman Roy Moore's sexual assault allegations.

The sentence "The character is a Democrat congressman named Todd Young who is running for Senate and vowed" contains a specific historical reference ("Obama's promise to support him"), implying a backstory about Biden's political deal or campaign promise.

Final token "promised" ends mid-clause ("who promised"), part of a parenthetical list of reasons for Trump's character ("Biden, who Obama promised"), expecting continuation like "to deliver jobs" or "him the cabinet position" or "the Republican's support before breaking his word."
```

### stim 140 (doc 315, pos 28) token='5' cos_own=0.891 cos_samedoc=0.407 parse_ok=True

context: " = The Litigators = \n \n The Litigators is a 2011 legal thriller novel by John Grisham , his 2" [["5"]] "th fiction novel overall . The Litigators is about a two @-@ partner"

```
Wiki article format with descriptive prose about a novel, establishing a book title and author context.

The phrase "The fifth novel of Stephen King , his 25" strongly implies a numbered list or record of his works, with "25th novel" suggesting a milestone or ranking number for his career.

Final token "25" is mid-number in "his 25," part of an attribution claim ("his 25th novel, his 25"), immediately expecting "th novel" or "th work" or "th novel in his series," completing the numerical claim about his record-breaking or numbered literary achievement.
```

### stim 172 (doc 448, pos 150) token='9' cos_own=0.924 cos_samedoc=0.334 parse_ok=True

context: " operations . Three prototypes were ordered with the company designation of B @-@ 48 and the informal name of \" Firecrest \" , but only two of them actually flew . The development of the aircraft was prolonged by significant design changes and slow deliveries of components , but the determination by the Ministry of Supply in 1" [["9"]] "46 that the airframe did not meet the requirements for a strike fighter doomed"

```
British military history reference article with technical specifications of a World War II British aircraft, describing design and production details.

The sentence structure "The aircraft was withdrawn from production in December 1942 but work continued on the Avro Lincoln's development programme. In 19" implies a date event or decision, completing a historical clause about wartime urgency or cancellation timing.

Final token "19" is mid-number in "in 19," part of a date specification clause ("Decision was made in December 19"), strongly expecting "43" or "44" to complete the year, likely followed by "43, the Ministry delayed the test."
```

