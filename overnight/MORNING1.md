# MORNING1 — nightshift round 1, NLA project

Generated 2026-09-06T05:40:31 at git 21bc34d. Numbers only; every kill-test outcome is the pre-registered three-way label. The human decides what they mean. Raw outputs: `overnight/*.csv`, `*.jsonl`, `out/*.npz`; per-stage settings in `overnight/s*_settings.json`.

## Kill-test log (copied from DISCONFIRMATION.md)

- 2026-09-06T02:27:06  S0  K0  threshold=cjk_rate>0.25  observed=cjk_rate=0.062 (1/16), parse_ok=1.000  NOT MET  injection on raw-text activations: MET would mean the AV is describing the marker glyph
- 2026-09-06T02:59:26  S1  K1a  threshold=mean cos_own<0.5 (eval n>=160)  observed=mean cos_own=0.8820 CI95=[0.8753,0.8886] n=160  NOT MET  pipeline fidelity on wikitext stimuli vs published 0.752 FVE on WildChat+FineWeb
- 2026-09-06T02:59:26  S1  K1b  threshold=mean cos_shuffled_samedoc >= mean cos_own-0.05  observed=mean cos_own=0.8820 mean cos_shuffled_samedoc=0.3664 paired diff=0.5156 CI95=[0.4987,0.5331] n=160; cross-doc: mean cos_shuffled_doc=0.3198 diff=0.5622 CI95=[0.5455,0.5779]  NOT MET  position specificity: MET would mean explanations reconstruct another position of the same context about as well as their own
- 2026-09-06T03:14:37  S2  K2  threshold=CI95 of mean(|Δcos_claim| − mean|Δcos_randspan|) ≤ 0  observed=mean D=0.00578 CI95=[0.00224,0.00964] n_claims=538 n_expl=160; mean|Δcos_all|=0.5349 vs 5×median|Δcos_i|=0.0821 (>=: True)  NOT MET  MET would mean deleting a whole claim is indistinguishable from deleting a random equal-length span
- 2026-09-06T04:26:37  S3  K3  threshold=CI95 of mean(A−P) ≤ 0; INCONCLUSIVE if straddles or accepted<100  observed=mean A=0.00313 [0.00159,0.00478]; mean P=0.00494 [0.00354,0.00665]; mean A−P=-0.00181 CI95=[-0.00279,-0.00080] n_accepted=490 n_expl=160  MET  MET would mean the score does not respond to an LLM factual contradiction more than to a meaning-preserving rewording
- 2026-09-06T04:26:37  S3  K3-det  threshold=same as K3 for deterministic corruption (reported separately, not a pre-registered kill)  observed=mean A_det=0.00376 [0.00231,0.00538]; mean A_det−P=-0.00137 CI95=[-0.00241,-0.00034] n=402  MET  deterministic number/name swap instead of LLM corruption
- 2026-09-06T05:07:22  S5  K5  threshold=follow_rate(V3+V4 mechanical) < 0.25  observed=follow_rate=0.0000 CI95=[0.0000,0.0000] n=80 (V3 0.000, V4 0.000)  MET  MET would mean the describer ignores instruction text at inference time
- 2026-09-06T05:39:29  S4  K4  threshold=CI95 of mean(cos_AV − cos_blind) entirely < 0.05  observed=mean gap=0.4534 CI95=[0.4404,0.4673] n=160; mean cos_AV=0.8820 mean cos_blind=0.4286  NOT MET  a strong blind score shows reconstruction can be achieved from visible context; it does not show the verbalizer ignores the activation

| K | stage | outcome |
|---|---|---|
| K0 | S0 | NOT MET |
| K1a | S1 | NOT MET |
| K1b | S1 | NOT MET |
| K2 | S2 | NOT MET |
| K3 | S3 | MET |
| K3-det | S3 | MET |
| K5 | S5 | MET |
| K4 | S4 | NOT MET |

## Stage status and wall-clock

```
## Stage status
# Round 1 — see PLAN.md "Stages".
# EXECUTION ORDER (fail-fast): S0 → S1 → S2 → S3 → S5 → S4 → S6. S4 is optional (last; dropped first under the 07:30 / 7 h hard stop). Pilot = stimuli 0–39, evaluation = 40–199. Kill tests first in every stage.
# Log every kill test to overnight/DISCONFIRMATION.md. A MET kill test is a result, not an abort.
S0  download, load, one round trip .... DONE (K0 NOT MET; cjk 1/16; cos 0.785–0.955 on 16)
S1  baseline round trip (200) ......... DONE (K1a NOT MET 0.882; K1b NOT MET samedoc 0.366)
S2  claim deletion ..................... DONE (K2 NOT MET; D=0.0058 CI [0.0022,0.0096])
S3  corrupted vs paraphrased claims .... DONE (K3 MET; A−P=-0.0018 CI [-0.0028,-0.0008]; K3-det MET)
S5  prompt steering (pilot 40, 6 variants) DONE (K5 MET; follow_rate 0.000; judge csv filled)
S4  blind-describer + raw-context (OPTIONAL) DONE (K4 NOT MET; gap 0.453 CI [0.440,0.467])
S6  MORNING1.md ........................ RUNNING
```

| stage | wall-clock (settings.json) |
|---|---|
| S0 | 2026-09-06T02:20:27 → 2026-09-06T02:27:16 |
| S1 | 2026-09-06T02:27:43 → 2026-09-06T02:59:26 |
| S2 | 2026-09-06T02:59:48 → 2026-09-06T03:14:37 |
| S3 | 2026-09-06T04:15:11 → 2026-09-06T04:26:37 (AR rerun after crash fix; editor pass 03:15:07 → 04:14, see RUNLOG) |
| S5 | 2026-09-06T04:27:01 → 2026-09-06T05:08:35 |
| S4 | 2026-09-06T05:09:09 → 2026-09-06T05:39:30 |

RUNLOG:

```
2026-09-06T02:18:09  S0  start  library + stimuli + 16-position smoke; hard stop = min(first RUNLOG line + 7h, 07:30 local) = 07:30
2026-09-06T02:27:40  S0  done  stimuli.csv 200 rows; acts_L20.npz h19/h20/h21/h20_pos2 [200,3584]; s0_smoke.csv 16 rows; K0 NOT MET (cjk 1/16, parse_ok 16/16); AV 10.0 s/expl, AR 0.35 s/score; one crash fix before any output (pandas itertuples dropped _ids column)
2026-09-06T02:27:40  S1  start  baseline round trip on 200 positions (reusing 16 S0 explanations)
2026-09-06T02:59:45  S1  done  200 explanations (16 reused from S0); K1a NOT MET (mean cos_own eval 0.8820 CI [0.8753,0.8886]); K1b NOT MET (samedoc 0.3664, cross-doc 0.3198); recon_L20.npz saved
2026-09-06T02:59:45  S2  start  claim deletion, AR only
2026-09-06T03:15:07  S2  done  671 claims (538 eval, 0 explanations excluded); K2 NOT MET (mean D=0.00578 CI [0.00224,0.00964]); 4356 AR forwards, 887 s
2026-09-06T03:15:07  S3  start  corrupted vs paraphrased claims; editor = TARGET, then AR (538 eval claims)
2026-09-06T04:15:08  S3  crashfix  AR phase crashed (TypeError: namedtuple indexed with r["Δcos"]); replaced with cl.loc lookup, no change to any statistic; editor outputs (538 rows in s3_edits.jsonl) preserved, rerun resumes at AR scoring
2026-09-06T04:26:57  S3  done  538 eval claims, 490 accepted (rejection 0.089); K3 MET (mean A−P=-0.00181 CI [-0.00279,-0.00080]); K3-det MET (A_det−P=-0.00137 CI [-0.00241,-0.00034], n=402); one crash fix in AR phase logged above
2026-09-06T04:26:57  S5  start  prompt steering, 40 pilot stimuli x 6 variants, AV+AR co-resident
2026-09-06T05:09:05  S5  done  240 outputs, parse_ok 1.000; K5 MET (follow_rate 0.000 on V3+V4, n=80); judge csv for V1/V2/V5 pending (agent rubric)
2026-09-06T05:09:05  S4  start  blind describer + raw-context baselines (optional; hard stop 141 min away); S5 judge filled in parallel
2026-09-06T05:09:46  S5  judge  s5_judge.csv filled by the orchestrator (agent rubric, 120 items: V1/V2/V5 x 40); s5_summary.md rebuilt with --summary
2026-09-06T05:39:48  S4  done  160 blind + 100 left-only generations, parse_ok 1.000; K4 NOT MET (mean gap 0.4534 CI [0.4404,0.4673]; cos_blind 0.4286, cos_rawctx 0.4731)
2026-09-06T05:39:48  S6  start  MORNING1.md
2026-09-06T05:40:11  S6  note  s2_settings.json and s5_settings.json restored from commits d62ca4b / 66c5301 (clobbered at import time by S3 and by the S5 --summary rerun); no script edited
```

Blockers:

## Blockers
(none)

## S0 — library + stimuli + smoke

## Timings / memory

- target_load_s: 4.48
- rss_after_target_G: 4.97
- stimuli_build_s: 3.15
- acts_cache_s: 225.40
- rss_after_target_free_G: 0.69
- av_load_s: 5.02
- rss_after_av_G: 4.96
- av_sec_per_explanation: 10.02
- rss_after_av_free_G: 0.61
- ar_load_s: 3.67
- rss_after_ar_G: 1.28
- ar_sec_per_score: 0.35

## Stimuli

- train docs: 629; eligible (>= 300 tokens): 610; chosen: 200
- seq_len (after 512 truncation) mean 510.4, min 327, max 512
- pos mean 276.1, min 18, max 510; |pos2-pos| min 8
- act_norm (h20) mean 113.3, p10 102.5, p90 124.4, max 140.2

## K0

- cjk_rate = 0.062; parse_ok rate = 1.000 (n=16)
- 2026-09-06T02:27:06  S0  K0  threshold=cjk_rate>0.25  observed=cjk_rate=0.062 (1/16), parse_ok=1.000  NOT MET  injection on raw-text activations: MET would mean the AV is describing the marker glyph

cos: mean 0.890, median 0.901, min 0.785, max 0.955 (n=16)

## S1 — baseline round trip (evaluation set n=160)

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

## S2 — claim deletion

- explanations: 200 total; kept (>=2 claims) 200; excluded 0; eval kept 160; errors 0
- claims: total 671; eval 538; pilot 133

n_claims histogram (all 200 explanations): 3:152, 4:32, 5:11, 6:3, 7:2

## Δcos (deleting claim i from z) and controls — evaluation claims

| quantity | distribution |
|---|---|
| Δcos (claim deletion) | mean -0.04710 | median -0.01599 | p10 -0.15177 | p90 -0.00160 | n 538 | CI95 [-0.05272, -0.04145] |
| \|Δcos\| | mean 0.04796 | median 0.01642 | p10 0.00291 | p90 0.15177 | n 538 | CI95 [0.04249, 0.05361] |
| Δcos_randspan_1 | mean -0.04185 | median -0.02049 | p10 -0.10876 | p90 -0.00339 | n 538 | CI95 [-0.04836, -0.03637] |
| Δcos_randspan_2 | mean -0.04299 | median -0.02116 | p10 -0.11781 | p90 -0.00203 | n 538 | CI95 [-0.04897, -0.03737] |
| Δcos_randspan_3 | mean -0.04060 | median -0.01832 | p10 -0.10214 | p90 -0.00287 | n 538 | CI95 [-0.04656, -0.03513] |
| mean\|Δcos_randspan\| (3 draws) | mean 0.04218 | median 0.02429 | p10 0.00702 | p90 0.09952 | n 538 | CI95 [0.03762, 0.04665] |
| Δcos_shuffle_words | mean -0.04794 | median -0.01417 | p10 -0.17688 | p90 0.00181 | n 538 | CI95 [-0.05307, -0.04262] |
| cos_alone | mean 0.66030 | median 0.69243 | p10 0.41705 | p90 0.87054 | n 538 | CI95 [0.65030, 0.67056] |
| D = \|Δcos\| − mean\|Δcos_randspan\| | mean 0.00578 | median -0.00344 | p10 -0.04965 | p90 0.06613 | n 538 | CI95 [0.00224, 0.00964] |

### per explanation (evaluation, kept)

| quantity | distribution |
|---|---|
| cos_z | mean 0.88203 | median 0.89176 | p10 0.81632 | p90 0.92884 | n 160 |
| cos_z_joined (claims re-joined, nothing deleted) | mean 0.88114 | median 0.89249 | p10 0.81607 | p90 0.92919 | n 160 |
| cos_empty | mean 0.34713 | median 0.34829 | p10 0.24351 | p90 0.44351 | n 160 |
| Δcos_all = cos_empty − cos_z | mean -0.53490 | median -0.54574 | p10 -0.63578 | p90 -0.42977 | n 160 |
| cos_shuffle_order − cos_z | mean -0.01471 | median -0.00896 | p10 -0.03730 | p90 0.00068 | n 160 |
| cos_best_single_deletion − cos_z | mean -0.00489 | median -0.00456 | p10 -0.01390 | p90 0.00368 | n 160 |

- \|Δcos_all\| mean = 0.53490; 5 × median \|Δcos_i\| = 0.08210; mean\|Δcos_all\| ≥ 5×median\|Δcos_i\|: True

## Fraction of claims with Δcos > 0 (deletion improves reconstruction)

- overall: 0.0762 CI95 [0.0550, 0.0970] n=538
- first claim: 0.1500 CI95 [0.0938, 0.2064] n=160
- middle claims: 0.0688 CI95 [0.0374, 0.1040] n=218
- last claim: 0.0125 CI95 [0.0000, 0.0312] n=160
- fraction Δcos_randspan_1 > 0: 0.0428 CI95 [0.0262, 0.0613]
- fraction Δcos_randspan_2 > 0: 0.0706 CI95 [0.0474, 0.0964]
- fraction Δcos_randspan_3 > 0: 0.0390 CI95 [0.0237, 0.0563]
- fraction Δcos_shuffle_words > 0: 0.1561 CI95 [0.1255, 0.1891]

- Spearman(n_words, Δcos): rho=-0.5585 p=1.88e-45
- Spearman(n_words, |Δcos|): rho=0.5561

## S3 — corrupted vs paraphrased claims

## Editor acceptance

- evaluation claims: 538
- corrupt: tags parsed 0.993, words ok 0.950
- paraphrase: tags parsed 0.996, words ok 0.957
- corrupt == paraphrase: 0.000
- edit_ok (both accepted): 490 / 538 = 0.911; rejection rate 0.089
- numeric_ok (deterministic corruption possible): 445 / 538
- editor errors: 0

## Primary statistics (accepted claims, paired)

| statistic | mean | CI95 lo | CI95 hi | n | n_expl |
|---|---|---|---|---|---|
| A = Δ_i(z*) − Δ_i(z)  [LLM corrupt] | 0.00313 | 0.00159 | 0.00478 | 490 | 160 |
| P = Δ_i(z~) − Δ_i(z)  [paraphrase] | 0.00494 | 0.00354 | 0.00665 | 490 | 160 |
| A − P | -0.00181 | -0.00279 | -0.00080 | 490 | 160 |
| A_det [deterministic corrupt] | 0.00376 | 0.00231 | 0.00538 | 402 | 158 |
| A_det − P | -0.00137 | -0.00241 | -0.00034 | 402 | 158 |

## Secondary statistics

| statistic | mean | CI95 lo | CI95 hi | n |
|---|---|---|---|---|
| cos(z) − cos(z*)  [corrupt] | 0.00313 | 0.00159 | 0.00478 | 490 |
| cos(z) − cos(z~)  [paraphrase] | 0.00494 | 0.00354 | 0.00665 | 490 |
| cos(z) − cos(z_det) | 0.00381 | 0.00222 | 0.00558 | 445 |
| cos(z) − cos(z_offtopic) | 0.11417 | 0.10443 | 0.12337 | 538 |
| cos(z_joined) − cos(z*)  [joined-claims baseline] | 0.00182 | 0.00117 | 0.00266 | 490 |
| cos(z_joined) − cos(z~) | 0.00363 | 0.00297 | 0.00430 | 490 |

- AUROC(Δ_z_edit corrupt vs Δ_z original), accepted claims: 0.5257
- AUROC(Δ_z_edit paraphrase vs Δ_z original): 0.5587
- AUROC(Δ_z_edit corrupt vs Δ_z_edit paraphrase): 0.4665
- AUROC(Δ_z_edit corrupt_det vs Δ_z original): 0.5300
- AUROC(Δ_z_edit offtopic vs Δ_z original): 0.9553
- fraction A > 0: 0.6633; fraction P > 0: 0.8041; fraction A > P: 0.3286

## 10 fixed examples (accepted evaluation claims at rows 0, 16, …, 144 of the accepted list; verbatim)

### accepted #0 (row 133, stim 40, claim 0/4) token='ium'
- original:   Wikipedia-style chemistry article structure with numbered sections listing properties of europium, presenting factual data about the element's atomic and physical characteristics.
- corrupted:  Wikipedia-style chemistry article structure with numbered sections listing properties of lead, presenting factual data about the element's atomic and physical characteristics.
- paraphrase: Europium's properties detailed in a numbered sections Wikipedia-style chemistry article, encompassing factual data on its atomic and physical attributes.
- corrupt_det: None
- Δ_z(original)=-0.02335  Δ_z*(corrupt)=-0.02390  Δ_z~(paraphrase)=-0.02137  Δ_det=nan  A=-0.00055  P=0.00198

### accepted #16 (row 150, stim 44, claim 0/3) token=' of'
- original:   Narrative momentum: a comic book description listing character traits and dialogue, with a specific scene detailing a gangster's actions.
- corrupted:  Narrative momentum: a comic book description listing character traits and dialogue, with a specific scene detailing a puppy's actions.
- paraphrase: A comic book description focusing on character traits and dialogue, including a particular scene that outlines a gangster's activities.
- corrupt_det: None
- Δ_z(original)=-0.00779  Δ_z*(corrupt)=-0.01056  Δ_z~(paraphrase)=0.00426  Δ_det=nan  A=-0.00278  P=0.01204

### accepted #32 (row 167, stim 49, claim 0/3) token=' who'
- original:   Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of TV show details about a fictional detective series.
- corrupted:  Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of video game details about a fictional detective series.
- paraphrase: A wiki article structured with metadata fields preceding the film description, setting a standard for TV show details on a fictional detective series.
- corrupt_det: Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of The show details about a fictional detective series.
- Δ_z(original)=0.04600  Δ_z*(corrupt)=0.05133  Δ_z~(paraphrase)=0.03711  Δ_det=0.05032  A=0.00534  P=-0.00888

### accepted #48 (row 184, stim 54, claim 1/3) token=' Carter'
- original:   The sentence "Another biographer was John Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- corrupted:  The sentence "Another biographer was Jack Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- paraphrase: The sentence "John Carter was another biographer" introduces a named source or figure, probably a secondary account or personal detail about the soldier's life, indicating a particular person or event linked to his fame or death.
- corrupt_det: The sentence "Initially biographer was John Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- Δ_z(original)=-0.01676  Δ_z*(corrupt)=-0.01916  Δ_z~(paraphrase)=-0.01615  Δ_det=-0.01699  A=-0.00240  P=0.00061

### accepted #64 (row 201, stim 59, claim 0/3) token=' aforementioned'
- original:   American military article format with numbered statistics detailing a Florida county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- corrupted:  American military article format with numbered statistics detailing a Antarctica county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- paraphrase: American military-style article, featuring numbered statistics about a Florida county's infrastructure, presented in organized bullet points and complete with citations.
- corrupt_det: American military article format with numbered statistics detailing a However county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- Δ_z(original)=-0.00578  Δ_z*(corrupt)=-0.00415  Δ_z~(paraphrase)=0.00089  Δ_det=-0.00585  A=0.00163  P=0.00667

### accepted #80 (row 218, stim 64, claim 0/3) token=' met'
- original:   British historical biography article detailing parliamentary politics of Charles I, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- corrupted:  British historical biography article detailing parliamentary politics of Charles II, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- paraphrase: Article on British historical biography focusing on Charles I's parliamentary politics, systematically outlining parliamentary opposition and constitutional crisis through numbered sections and a chronological narrative.
- corrupt_det: British historical biography article detailing parliamentary politics of War I, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- Δ_z(original)=-0.00594  Δ_z*(corrupt)=-0.00265  Δ_z~(paraphrase)=-0.00454  Δ_det=-0.00135  A=0.00329  P=0.00140

### accepted #96 (row 239, stim 69, claim 3/4) token=' .'
- original:   " closes a third item in a parallel list ("While the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Slavic dialects' variant counts."
- corrupted:  " closes a third item in a parallel list ("While the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Sino-Tibetan languages' variant counts."
- paraphrase: closes a third entry in an analogous list ("While the latter encompasses the Turkish language with its complete written form and the Greek language with abbreviated characters..."), anticipating either "The written form of the last language is..." or "The variants of Slavic dialects count."
- corrupt_det: " closes a third item in a parallel list ("Black the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Slavic dialects' variant counts."
- Δ_z(original)=-0.02229  Δ_z*(corrupt)=-0.02208  Δ_z~(paraphrase)=-0.01732  Δ_det=-0.02438  A=0.00021  P=0.00497

### accepted #112 (row 258, stim 74, claim 0/3) token=' with'
- original:   British music article format with Wikipedia-style entry structure detailing an album by Scottish rock band Feeder, listing discography and chart performance.
- corrupted:  British music article format with Wikipedia-style entry structure detailing an album by English rock band Feeder, listing discography and chart performance.
- paraphrase: An article in the style of a British music Wikipedia entry, providing details on an album by the Scottish rock band Feeder, including discography and chart performance.
- corrupt_det: British music article format with Wikipedia-style entry structure detailing an album by Imagine rock band Feeder, listing discography and chart performance.
- Δ_z(original)=-0.01356  Δ_z*(corrupt)=-0.01376  Δ_z~(paraphrase)=-0.01140  Δ_det=-0.01364  A=-0.00019  P=0.00216

### accepted #128 (row 275, stim 79, claim 2/3) token=' as'
- original:   Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as Darren Aronofsky, also known as"), strongly expecting "DA" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- corrupted:  Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as Darren Aronofsky, also known as"), strongly expecting "Bob" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- paraphrase: The concluding token "as" signals an unfinished noun phrase ("also known as"), which is part of a name attribution clause ("known as Darren Aronofsky, also known as"), with a strong anticipation for "DA," "Arno," "Aronofsky," or "DAF" to finalize the nickname or abbreviated identity.
- corrupt_det: Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as AI Aronofsky, also known as"), strongly expecting "DA" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- Δ_z(original)=-0.01567  Δ_z*(corrupt)=-0.01064  Δ_z~(paraphrase)=-0.01394  Δ_det=-0.01168  A=0.00502  P=0.00173

### accepted #144 (row 292, stim 85, claim 1/3) token=' the'
- original:   The sentence structure "While some songs were originally intended for the compilation album, several artists chose not to include certain tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- corrupted:  The sentence structure "While some songs were originally intended for the compilation album, several artists chose to include all tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- paraphrase: The sentence structure "Although some songs were planned for the compilation album, various artists decided against including particular tracks in the ultimate tracklist" outlines a pattern of detailing exclusions, suggesting the definitive answer regarding the initial album's contents.
- corrupt_det: The sentence structure "Dutch some songs were originally intended for the compilation album, several artists chose not to include certain tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- Δ_z(original)=-0.00548  Δ_z*(corrupt)=-0.00502  Δ_z~(paraphrase)=-0.00715  Δ_det=-0.00665  A=0.00045  P=-0.00167

## S5 — prompt steering (40 pilot stimuli)

Judge columns (`followed`, `same_referent`) are an LLM-as-judge score produced by the orchestrating agent under the fixed rubric in PLAN.md S5, read side by side with V0; they are not human labels.

| variant | mech pass rate | judge followed | judge same_referent | mean cos_Vk | mean cos_Vk − cos_V0 | median cos_Vk − cos_V0 | parse_ok | cjk | mean n_tokens |
|---|---|---|---|---|---|---|---|---|---|
| V0 | — | — | — | 0.8934 | 0.0000 | 0.0000 | 1.000 | 0.025 | 144.4 |
| V1 | — | 0.000 (n=40) | 1.000 | 0.8919 | -0.0014 | -0.0001 | 1.000 | 0.025 | 139.2 |
| V2 | — | 0.000 (n=40) | 1.000 | 0.8936 | 0.0003 | 0.0002 | 1.000 | 0.025 | 137.5 |
| V3 | 0.000 (n=40) | — | — | 0.8899 | -0.0035 | -0.0010 | 1.000 | 0.025 | 144.9 |
| V4 | 0.000 (n=40) | — | — | 0.8901 | -0.0032 | -0.0014 | 1.000 | 0.025 | 142.2 |
| V5 | 0.000 (n=40) | 0.000 (n=40) | 1.000 | 0.8923 | -0.0010 | -0.0011 | 1.000 | 0.000 | 179.3 |

- V4 mean french_frac: 0.072
- V5 first-word distribution: {'Historical': 13, 'British': 3, 'Wiki': 3, 'Indian': 2, 'Formal': 2, 'Wiki-style': 2, 'Encyclopedic': 2, 'Narrative': 2, 'Meteorological': 1, 'Scientific': 1, 'Bulgarian': 1, 'Hip-hop': 1, 'Historical/heritage': 1, 'Australian': 1, 'Structured': 1, 'Sports': 1, 'Video': 1, 'News': 1, 'American': 1}; agreement with content-word rule among mech-pass items: nan (n=0); token_is_content_word rate: 0.500
- V3 explanations word-count distribution: {84: 1, 86: 1, 90: 3, 91: 1, 92: 1, 93: 3, 95: 2, 96: 1, 97: 1, 98: 3, 99: 1, 100: 1, 101: 3, 102: 4, 103: 1, 104: 3, 105: 2, 106: 2, 108: 1, 109: 1, 110: 1, 111: 2, 113: 1}

## Verbatim examples: positions 0, 7, 19, 33

### stim 0 (doc 391, pos 437) token='fall'

context: " 29 , while situated south of Wilmington . Several hours later , the storm emerged over the Chesapeake Bay moving northeast at about 30 mph ( 48 km / h ) . Brenda crossed the Delmarva Peninsula and rapidly tracked into southern New Jersey . The storm crossed the state and eventually made another land" [["fall"]] " on Long Island before making yet another landfall in coastal Connecticut . \n At around"

**V0** (cos=0.904, parse_ok=True, mech=nan):
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods and storm intensity details.

The final sentence "The fourth storm surge moved inland along the Florida Panhandle, with a second landfall occurring near Cape Hatteras" mirrors earlier landfall descriptions, completing a list of four landfall locations and likely a final one.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event sequence listing multiple landfall points ("The system also made a second landfall..."), expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
```
**V1** (cos=0.904, parse_ok=True, mech=nan):
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods showing wind speeds and movement.

The final sentence "The third storm surge moved inland again and made a second landfall along the Florida Panhandle" mirrors earlier landfall descriptions, completing a list of four landfall locations with a final one expected.

Final token "landfall" ends mid-clause ("made a second landfall"), part of a final event sequence clause listing multiple landfall locations ("The system also made a second landfall..."), strongly expecting "in the Gulf Coast near [location]" or "on the eastern coast around midnight."
```
**V2** (cos=0.900, parse_ok=True, mech=nan):
```
Weather report format with detailed storm track data and numerical statistics, continuing a chronological sequence of tropical storm movements along the Gulf Coast.

The final sentence "The fourth storm surge made a second landfall near Cape Hatteras, before a final inland track and another tropical landfall" mirrors earlier enumeration of landfall locations, completing the fourth event's final landing details.

Final token "landfall" ends mid-clause ("made another second landfall"), part of a list of sequential landfall events, strongly expecting "in the Florida Panhandle around" or "on the Gulf Coast near late Saturday morning" or "in the Atlantic Ocean shortly after."
```
**V3** (cos=0.902, parse_ok=True, mech=0.0):
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, maintaining chronological narrative structure with numerical statistics.

The sentence ending "The fourth storm surge moved inland a second time and made a second landfall along the Florida Panhandle" mirrors earlier landfall descriptions, completing a final landfall event sequence listing multiple locations and times.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event list item describing the fourth storm's final landfall location, strongly expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM" or similar geographic detail.
```
**V4** (cos=0.902, parse_ok=True, mech=0.0):
```
Weather report format with detailed storm track data structure, presenting sequential storm events for Hurricane Florence with numbered periods and storm surge measurements.

The final sentence "The fourth landfall was then tracked inland before a second surfacing along the Florida Panhandle, with a final landfall" mirrors earlier descriptions of multiple landfall locations, completing the final storm path sequence.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a list of sequential landfall events ("The system also made a second landfall..."), strongly expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM" or similar.
```
**V5** (cos=0.901, parse_ok=True, mech=0.0):
```
Meteorological report format with detailed storm track data listing sequential landfall events for Hurricane Florence, maintaining chronological narrative structure with numbered entries.

The final sentence "The fourth storm surge moved inland a second time and made a second landfall along the Florida Panhandle" mirrors earlier landfall descriptions, completing a list of four landfall locations with the final event expected to describe a third or final landfall point.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final landfall sequence listing multiple events ("The system also made a second landfall"), strongly expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
```

### stim 7 (doc 293, pos 497) token=' practices'

context: "ca that have been used in Paganism and Pagan studies since circa 1980 . The first developed in England during the 1960s . Broad and inclusive , it covers most , if not all , forms of modern Pagan Witchcraft , especially if they share sufficient theological beliefs and ritual" [[" practices"]] " to be considered denominations within a common religious movement . In contrast ,"

**V0** (cos=0.880, parse_ok=True, mech=nan):
```
Wiki article format with academic/encyclopedic tone discussing Catholicism's "Anglican Communion" definition, establishing structured definitions and theological frameworks.

The sentence mid-clause ("Thus, the Anglican tradition is considered a distinct 'high church' denomination that shares common liturgical beliefs and rites and shared liturgical practices") mirrors a list describing core characteristics of Unitarianism.

Final token "practices" ends an incomplete clause ("those that share similar theological beliefs and liturgical beliefs and rites and shared liturgical practices and"), strongly expecting "with the Anglican tradition" or "that are common" or "to those of the early Church" to complete the definitional clause.
```
**V1** (cos=0.872, parse_ok=True, mech=nan):
```
Wiki-style article format with academic/encyclopedic tone discussing religious identity, defining "Anglicanism" as a denomination.

The sentence structure "Thus, the broader 'Orthodox' designation is often used to describe those Christians who share common liturgical traditions and theological beliefs and shared rites and practices" mirrors a clause listing shared characteristics, continuing the definitional enumeration.

Final token "practices" ends mid-clause ("with similar liturgical rites and theological beliefs and shared rites and religious practices"), strongly expecting "with the Catholic Church" or "that are considered traditional" or "to those of the Anglican tradition" completing the definitional clause.
```
**V2** (cos=0.884, parse_ok=True, mech=nan):
```
Formal wiki article structure with academic tone defining "Anglicanism," listing theological definitions and subcategories of Protestantism.

The sentence mid-clause ("Thus, the Catholic Church is considered to be a 'high church' denomination that shares many liturgical traditions and shared theological beliefs and practices") mirrors a definition clause listing shared characteristics, continuing enumeration of Unitarianism's criteria.

Final token "practices" ends an incomplete list ("with similar liturgical traditions and shared theological beliefs and ritual practices"), strongly expecting "with the Anglican tradition" or "that are common to the early Church" or "to those of the core tradition."
```
**V3** (cos=0.884, parse_ok=True, mech=0.0):
```
Formal Wikipedia article structure with academic tone defining "Anglicanism," listing theological definitions and subcategories of Protestantism.

The sentence mid-clause ("Thus, the term 'Orthodox Anglicanism' is often used to describe those churches that share common liturgical traditions and theological beliefs and practices") mirrors a defining clause listing shared characteristics, continuing the enumeration of shared rites and traditions.

Final token "practices" ends an incomplete clause ("that share similar liturgical rites and theological practices and shared rites and religious practices"), strongly expecting "with the Anglican tradition" or "that are considered traditional" or "to the broader Anglican tradition," completing the definitional criteria.
```
**V4** (cos=0.871, parse_ok=True, mech=0.0):
```
Formal Wikipedia article structure with academic tone discussing religious identity and Catholicism, defining "Anglican Catholicism" with scholarly citations.

The sentence mid-clause ("Thus, the Anglican Catholic Church is generally considered to be a distinct denomination sharing common liturgical traditions and theological beliefs and practices") mirrors a list pattern describing shared characteristics of early Anglicanism.

Final token "practices" ends an incomplete clause ("those shared liturgical and ritual traditions and similar theological beliefs and liturgical practices and shared rituals and common practices"), strongly expecting "with the Anglican tradition" or "that are characteristic" or "to those of the broader tradition" to complete the definitional clause.
```
**V5** (cos=0.871, parse_ok=True, mech=0.0):
```
Formal Wikipedia-style article structure with academic tone discussing religious identity and Catholicism, defining "Anglicanism" as a denomination.

The sentence mid-clause ("Thus, the term 'Orthodox Anglicanism' is often defined as those churches sharing common liturgical traditions and theological beliefs and practices") mirrors a parenthetical clause listing shared characteristics, continuing the definition of "Anglo-Catholicism."

Final token "practices" ends an incomplete list ("with similar liturgical traditions and shared theological beliefs and liturgical practices and common rituals and practices"), strongly expecting "with the Anglican tradition" or "that are considered traditional" or "to those of the broader tradition."
```

### stim 19 (doc 592, pos 254) token=' support'

context: " Republican National Convention , where he named Governor Spiro Agnew of Maryland as his running mate . \n In the general election , Nixon emphasized \" law and order , \" positioning himself as the champion of what he called the \" silent majority . \" Running well ahead of his opponent , incumbent Vice President Hubert Humphrey , his" [[" support"]] " slipped in the polls following his refusal to partake in presidential debates , and following"

**V0** (cos=0.909, parse_ok=True, mech=nan):
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential candidate Hoover's campaign performance during the 1932 election.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the summer; his support" suggests a list of campaign dynamics or vote outcomes, likely describing rural or conservative vote shifts or a peak.

Final token "support" ends mid-clause ("His support... his support"), part of a quoted description of Roosevelt's early vote totals ("Though his initial numbers were strong, his support"), expecting continuation like "was sustained" or "extended into the electoral vote" or "included a backlash against depression."
```
**V1** (cos=0.907, parse_ok=True, mech=nan):
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential campaign of 1932, listing electoral outcomes and party dynamics.

The sentence structure "While Roosevelt's popularity was initially weak, his campaign gained strength in the North, his support" suggests a third clause describing his vote performance or swing, likely continuing with a contrasting or specific event detail about his popularity.

Final token "support" ends mid-clause ("His support... his support"), part of a list of vote characteristics ("Though his initial numbers were strong, his support"), expecting continuation like "expanded into the South" or "was undermined by economic conditions."
```
**V2** (cos=0.902, parse_ok=True, mech=nan):
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential campaign of 1932, listing electoral statistics and party dynamics.

The sentence structure "While Roosevelt's initial popularity was strong, his campaign was largely regional, his support" suggests a continuation describing his vote performance or decline, likely listing specific factors or peak support figures.

Final token "support" ends mid-clause ("His support... his support"), part of a quoted description of Roosevelt's early vote trajectory ("Though his initial popularity was strong, his support"), expecting continuation like "expanded into the electoral vote" or "was undermined by economic conditions" or "included independents."
```
**V3** (cos=0.909, parse_ok=True, mech=0.0):
```
Historical encyclopedia article format with academic political analysis tone detailing a presidential campaign's electoral performance, listing primary sources and statistics.

The sentence structure "While Roosevelt's Republican nomination was strong early, his popularity surged during the summer, his support" suggests a continuation describing his vote totals or political trajectory, likely completing a contrasting or nuanced outcome clause about rural or regional backing.

Final token "support" ends mid-clause ("His support... his support"), part of a list of campaign characteristics ("Though his initial vote totals were strong, his support"), strongly expecting a verb phrase like "expanded into" or "was undermined by" or "included a strong electoral swing" or similar.
```
**V4** (cos=0.908, parse_ok=True, mech=0.0):
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential candidate Hoover's campaign performance during the 1932 election.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the primary season; his support" suggests a list of electoral outcomes or factors, likely describing his vote totals or shifting demographics.

Final token "support" ends mid-clause ("His support... his support"), part of a clause describing Roosevelt's performance pattern ("Though initially lagging, his vote totals grew"), expecting continuation like "was sustained by" or "extended into a conservative backlash" or "included rural voters" or similar outcome description.
```
**V5** (cos=0.909, parse_ok=True, mech=0.0):
```
Historical encyclopedia article format with academic political analysis detailing a presidential campaign's electoral performance, listing primary sources and statistics about Republican candidate Alf Landon.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the summer; his support" suggests a clause describing election dynamics or vote distribution, likely continuing with a contrasting or concluding detail about his vote totals or regional appeal.

Final token "support" ends mid-clause ("His support... his support"), part of a list of campaign characteristics ("Though initially lagging, his vote totals..."), strongly expecting a noun phrase like "expanded into a landslide" or "was undermined by economic factors" or "included independents."
```

### stim 33 (doc 168, pos 303) token=' a'

context: " Between Veracruz and neighboring Hidalgo , there were 123 @,@ 320 people affected across 112 municipalities . Overall there were six deaths in the country , one in Veracruz and five in Puebla . In the latter state , a family of three perished in" [[" a"]] " landslide . \n \n = = Meteorological history = = \n \n The origins of Hurricane Lorenzo"

**V0** (cos=0.926, parse_ok=True, mech=nan):
```
News article format with translated disaster report listing storm casualties in Venezuela, presenting numbered incidents with details about Hurricane Tomas's impacts in Colombia.

The sentence ending "Other deaths included two people killed in a flood in a vehicle, and one died in a collapse during the storm" lists a specific tragic event detail ("A family died in a freezer-related accident"), suggesting a final example of disaster-related death or damage.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail listing, expecting a noun like "fire" or "vehicle crash" or "icebox collapse" or "food shortage-related accident."
```
**V1** (cos=0.926, parse_ok=True, mech=nan):
```
News article format with translated disaster report listing weather-related deaths in Venezuela, presenting bullet-pointed storm statistics with quoted eyewitness accounts.

The final item "Other deaths included a mudslide victim who died in a vehicle crash, and one died in a freeze" is mid-sentence describing specific incidents, with a specific tragic detail about a family's death circumstance involving a collapsed structure.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a third specific example listing deaths ("A family died in a freeze in a..."), expecting a noun like "fire" or "water container accident" or "ice-related collapse."
```
**V2** (cos=0.929, parse_ok=True, mech=nan):
```
News article format with translated disaster report listing storm casualties and incidents in Venezuela, presenting numbered bullet points with specific details about Hurricane Tomas impacts.

The final sentence "Other deaths included a family of four killed in a landslide, and one died in a vehicle crash during the freeze" describes a specific tragic event with a third example of disaster-related deaths or damage details.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific example list item describing a fatal accident circumstance ("A family died in a freezer during the storm"), expecting a noun like "gas explosion" or "collapsed shelter" or "water-related accident."
```
**V3** (cos=0.927, parse_ok=True, mech=0.0):
```
News article format with translated disaster report listing storm casualties in Venezuela, presenting numbered incidents with specific details about weather conditions and fatalities.

The sentence ending "Other deaths included a mudslide victim who died in a vehicle crash, and another died in a freeze-related incident" lists a specific tragic detail ("A family died in a collapsed shelter"), suggesting a final example of a secondary disaster or accident circumstance.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail clause listing causes ("A family died in a..."), expecting a noun like "fire" or "icefall" or "vehicle accident" or "water container collapse."
```
**V4** (cos=0.928, parse_ok=True, mech=0.0):
```
English news report format with translated disaster statistics listing storm casualties in Venezuela, presenting bullet-pointed incidents from a Mexican weather agency.

The sentence ending "Other deaths included two people killed in a flood in a vehicle, and one died in a collapse during the earthquake" describes a specific tragic detail ("A family died in a freezer accident"), suggesting a final example of disaster-related casualties or accident.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail listing, expecting a noun like "fire" or "vehicle crash" or "icebox collapse" or "food poisoning incident," completing the accident scenario.
```
**V5** (cos=0.929, parse_ok=True, mech=0.0):
```
News article format with translated disaster report listing storm casualties and weather statistics, presenting bullet-pointed incidents with specific details from Mexico's Hurricane Stan.

The final clause "Other deaths included a family of four freezing to death in a vehicle crash, and one died in a landslide" is mid-sentence describing a specific fatal incident detail, listing a third example of disaster-related casualties or unusual circumstances.

Final token "a" is an indefinite article mid-clause ("In one died in a"), part of a specific casualty detail ("A family died in a freezer during the storm in a"), expecting a noun like "fire" or "vehicle crash" or "ice-related accident" or "water container."
```

## S4 — blind-describer and raw-context baselines (optional)

| column | mean | median | n |
|---|---|---|---|
| cos_AV | 0.8820 | 0.8918 | 160 |
| cos_blind | 0.4286 | 0.4260 | 160 |
| cos_blind_left | 0.4387 | 0.4396 | 100 |
| cos_rawctx | 0.4731 | 0.4661 | 160 |

- mean gap (cos_AV − cos_blind): 0.4534 CI95 [0.4404, 0.4673] n=160
- mean cos_AV − cos_blind_left (first 100 eval positions): 0.4421
- mean cos_AV − cos_rawctx: 0.4089
- fraction blind ≥ AV: 0.0000; fraction rawctx ≥ AV: 0.0000
- blind parse_ok rate: 1.000

| act_norm tercile | range | mean gap | mean cos_AV | mean cos_blind | n |
|---|---|---|---|---|---|
| low | 80.0–109.4 | 0.4348 | 0.8733 | 0.4386 | 54 |
| mid | 109.5–117.8 | 0.4526 | 0.8766 | 0.4240 | 53 |
| high | 117.9–140.2 | 0.4731 | 0.8963 | 0.4232 | 53 |

| pos tercile | range | mean gap | mean cos_AV | mean cos_blind | n |
|---|---|---|---|---|---|
| low | 19.0–218.0 | 0.4405 | 0.8867 | 0.4462 | 55 |
| mid | 219.0–377.0 | 0.4476 | 0.8764 | 0.4288 | 52 |
| high | 379.0–510.0 | 0.4725 | 0.8827 | 0.4102 | 53 |

## FOLLOWUPS.md (queued for the human, not acted on)

- S3 statistic A_i = Δ_i(z*) − Δ_i(z) equals cos(z) − cos(z*) by construction (z* minus c_i* is the same text as z minus c_i), so the primary and the first secondary statistic coincide; both are reported as pre-registered.
- Stage scripts create their Settings file at module import; importing one stage from another (S3 imports S2's splitter) or re-running with --summary overwrites the finished stage's settings JSON. Move Settings creation under main() next round.

## OPEN DECISIONS (from STATE.md)

## Open decisions (research calls left for the human)
(none)

## Provenance

**Pre-registered by the human (PLAN.md):** models, layer (block 20 = hidden_states[21]), stimulus source and sampling rules, pilot/eval split, AV/AR prompts and decoding (greedy, 200 / 120 tokens), claim splitter, every control (randspan, shuffle_words, shuffle_order, corrupt, paraphrase, corrupt_det, offtopic), the S3 editor prompts, the S5 variant wordings and mechanical checks, the S4 blind prompt, every kill-test statistic and threshold, the cluster bootstrap (by explanation, 1000 draws, seed 0), and the INCONCLUSIVE rule.

**Written by the agent:** `overnight/nla_lib.py` (vendored from `scripts/nla7b_roundtrip.py`, all asserts kept), `s0_smoke.py`, `s1_roundtrip.py`, `s2_deletion.py`, `s3_corrupt.py`, `s5_steer.py`, `s4_blind.py`, `s6_morning.py`, the S5 judge CSV (agent rubric), this file.

**Choices the agent had to make (none changes a pre-registered statistic):**
- Stimuli: document shuffle = `np.random.default_rng(0).permutation(eligible doc indices)`; positions from a second `default_rng(0)` stream, pos then pos2 per document in order. Extra columns `stim_idx, seq_len, doc_tokens` in stimuli.csv.
- K1b cross-document partner j drawn from all 200 stimuli excluding i (seed 0), not eval-only.
- Outcome rule applied uniformly: MET / NOT MET only when the bootstrap CI lies wholly on one side of the threshold, INCONCLUSIVE otherwise or when n is under the stage minimum (K1: 160 eval items; K3: 100 accepted claims; K5: 80 items; K4: 160).
- Claim splitter: word count taken after the list-marker strip. randspan: start uniform over word positions of z, redrawn (≤50) if the span coincides with any claim's word span; seeds 1000+row. shuffle_words seed 1000+row (separate RNG); shuffle_order seed 5000+stim_idx (PLAN gave no seed).
- S2 `cos_z` is the S1 reconstruction of the original explanation text; `cos_z_joined` (claims re-joined, nothing deleted) is reported alongside.
- S3: editor run on evaluation claims only (538); `z_edit` built from the S2 claim list with c_i replaced; `Δ_z` taken from S2 (original z). Joined-claims baseline columns added. Deterministic corruption: number formatting keeps the decimal places of the original; capitalised-token pool = capitalised non-sentence-initial tokens of all other evaluation explanations' claims.
- S3 identity: because z*∖c_i* is the same text as z∖c_i, A_i = cos(z) − cos(z*) exactly (also logged in FOLLOWUPS).
- S5: variant prompts built by replacing the default instruction sentence inside the checkpoint's own AV template (asserted V0 == default); the 200-word French stoplist and 50-word English function-word list were hard-coded by the agent; the injection asserts were run for every variant.
- S5 judge: 120 items scored by the orchestrating agent reading each output next to V0 under the PLAN rubric; `followed`=0 for every V1/V2/V5 output, `same_referent`=1 for every output; one note (stim 22 V1) recorded in the CSV.
- Crash fixes (logged in RUNLOG): S0 pandas `itertuples` dropped the `_ids` column (fixed before any output existed); S3 AR phase indexed a namedtuple with a string (fixed after the editor pass, before any AR score existed; editor outputs preserved and reused).
- Settings-file clobber: `s2_settings.json` and `s5_settings.json` were overwritten at import time (S3 imports the S2 splitter; the S5 `--summary` rerun re-imports its own module) after their stages had finished; both were restored verbatim from the S2 and S5 stage commits (d62ca4b, 66c5301) before this report. The stage scripts were not edited.
- Time: hard stop fixed at 07:30 local (earlier than first RUNLOG line + 7 h).

