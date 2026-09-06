# MORNING2 — nightshift round 2, NLA project

Generated 2026-09-06T09:24:33 at git 276ad66. Numbers only; every kill-test outcome is the pre-registered three-way label. The human decides what they mean. Round 2 reused the round-1 artifacts (no new verbalizer generation). Raw outputs: `overnight/r*_*.csv`, `out/*.npz` (regenerated in R0), per-stage settings in `overnight/r*_settings.json`, logs in `out/r*.log`.

## Kill-test log, round 2 (copied from DISCONFIRMATION.md)

- 2026-09-06T09:17:55  R1  R1  threshold=CI95 of mean(d_corr_T − d_para_T), last-token, n>=300, ≤ 0  observed=mean d_corr_T=0.03952 [0.03112,0.04722]; mean d_para_T=0.13357 [0.12455,0.14228]; mean S_T=-0.09405 CI95=[-0.10376,-0.08445] n=490 n_expl=160  MET  MET would mean the target's own layer-20 representation of the claim text is no more sensitive to the factual change than to rewording (blindness upstream of the AR)
- 2026-09-06T09:21:11  R2  R2  threshold=CI95 of mean[(cos z − cos z**) − (cos z − cos z~~)] ≤ 0  observed=mean cos z − cos z**=0.00754 [0.00473,0.01082]; mean cos z − cos z~~=0.01407 [0.01149,0.01667]; paired diff=-0.00653 CI95=[-0.00992,-0.00260] n_expl=160  MET  MET would mean corrupting every claim of an explanation is indistinguishable from paraphrasing every claim

| K | stage | outcome |
|---|---|---|
| R1 | R1 | MET |
| R2 | R2 | MET |

Round-1 kill lines these stages build on (for reference):

- 2026-09-06T02:59:26  S1  K1a  threshold=mean cos_own<0.5 (eval n>=160)  observed=mean cos_own=0.8820 CI95=[0.8753,0.8886] n=160  NOT MET  pipeline fidelity on wikitext stimuli vs published 0.752 FVE on WildChat+FineWeb
- 2026-09-06T03:14:37  S2  K2  threshold=CI95 of mean(|Δcos_claim| − mean|Δcos_randspan|) ≤ 0  observed=mean D=0.00578 CI95=[0.00224,0.00964] n_claims=538 n_expl=160; mean|Δcos_all|=0.5349 vs 5×median|Δcos_i|=0.0821 (>=: True)  NOT MET  MET would mean deleting a whole claim is indistinguishable from deleting a random equal-length span
- 2026-09-06T04:26:37  S3  K3  threshold=CI95 of mean(A−P) ≤ 0; INCONCLUSIVE if straddles or accepted<100  observed=mean A=0.00313 [0.00159,0.00478]; mean P=0.00494 [0.00354,0.00665]; mean A−P=-0.00181 CI95=[-0.00279,-0.00080] n_accepted=490 n_expl=160  MET  MET would mean the score does not respond to an LLM factual contradiction more than to a meaning-preserving rewording
- 2026-09-06T04:26:37  S3  K3-det  threshold=same as K3 for deterministic corruption (reported separately, not a pre-registered kill)  observed=mean A_det=0.00376 [0.00231,0.00538]; mean A_det−P=-0.00137 CI95=[-0.00241,-0.00034] n=402  MET  deterministic number/name swap instead of LLM corruption

## Stage status and wall-clock

```
## Stage status
# Round 2 — see PLAN.md "Round 2 stages". EXECUTION ORDER: R0 → R1 → R2 → R3 → R4. Hard stop 5.5 h after first round-2 RUNLOG line.
R0  artifact check ...................... DONE (r0_check.md: 0.8820 vs 0.8820, accepted)
R1  fact-blindness locus (target vs AR) . DONE (R1 MET; r1_summary.md)
R2  amplified corruption (AR only) ...... DONE (R2 MET; r2_summary.md)
R3  truncation curve (AR only) .......... DONE (k*_first=3, k*_last=1; r3_summary.md)
R4  MORNING2.md ......................... RUNNING
```

First round-2 RUNLOG line: 2026-09-06T09:03:21; report generated 2026-09-06T09:24:33.

| stage | wall-clock (settings.json) |
|---|---|
| R0 | 2026-09-06T09:03:27 → 2026-09-06T09:08:25 |
| R1 | 2026-09-06T09:09:15 → 2026-09-06T09:17:55 |
| R2 | 2026-09-06T09:18:16 → 2026-09-06T09:21:11 |
| R3 | 2026-09-06T09:21:29 → 2026-09-06T09:24:16 |

RUNLOG (round 2):

```
2026-09-06T09:03:21  R0  start  round 2 begins; artifact check + regenerate out/acts_L20.npz and out/recon_L20.npz; hard stop = 2026-09-06T09:03:21 + 5.5 h
2026-09-06T09:08:40  R0  done  counts OK (200/200/671/538/490); acts_L20.npz + recon_L20.npz regenerated; eval mean cos_own 0.8820 vs round-1 0.8820 (diff +0.00003, per-row max |diff| 0.00000); ACCEPTED; 226 s acts, 0.28 s/AR score
2026-09-06T09:08:40  R1  start  fact-blindness locus: 490 S3 triples through TARGET (last token + mean) and AR; TARGET then AR sequentially
2026-09-06T09:09:04  R1  crashfix  iteration 1 crashed before any model load (TypeError sorting text set: pandas NaN for missing corrupt_det); texts_of now keeps only str entries; no statistic changed; rerun
2026-09-06T09:18:09  R1  done  490 triples (402 with det), 1860 texts x TARGET + AR; R1 MET (mean S_T=-0.09405 CI [-0.10376,-0.08445]); S_AR=-0.04945 CI [-0.05569,-0.04328]; mean-pooled S_T=-0.00121; one pre-model crash fix logged above
2026-09-06T09:18:09  R2  start  amplified corruption, AR only (every accepted claim replaced)
2026-09-06T09:21:25  R2  done  160 eval explanations (all >=2 accepted claims), 635 AR forwards; R2 MET (paired diff=-0.00653 CI [-0.00992,-0.00260]); D_corrupt 0.00754, D_para 0.01407, frac corrupt>para 0.2125; det (n=155) diff -0.00506 CI [-0.00855,-0.00137]
2026-09-06T09:21:25  R3  start  truncation curve, AR only (first k / last k claims), descriptive
2026-09-06T09:24:32  R3  done  160 eval explanations, 916 AR forwards; median first-k lift >0.9 at k=3, last-k at k=1; Spearman(words, cos_alone)=0.7024; no kill test
2026-09-06T09:24:32  R4  start  MORNING2.md
```

Blockers:

## Blockers
(none)

## R0 — artifact check + cache regeneration

## Artifact counts (expected / found)

- stimuli: expected 200, found 200
- explanations: expected 200, found 200
- claims: expected 671, found 671
- s3_edits: expected 538, found 538
- s3_edit_ok: expected 490, found 490

## Acceptance: mean cos_own on evaluation set (stimuli 40-199)

- round-1 value (S1, s1_recon.csv): 0.8820
- regenerated value: 0.8820 CI95 [0.8753, 0.8886] n=160
- difference: +0.00003; tolerance +-0.002; within tolerance: True
- round-1 eval mean recomputed from s1_recon.csv: 0.8820

## Per-row agreement with round 1 (all 200 stimuli)

- |cos_own − cos_own_round1|: max 0.00000, mean 0.00000, n>0.001: 0
- |act_norm − act_norm_round1|: max 0.0000, mean 0.0000
- |cos_empty − cos_empty_round1|: max 0.00000
- AR errors: 0

## R1 — fact-blindness locus: target layer-20 representation vs reconstructor (490 accepted S3 triples)

- triples: 490; with corrupt_det: 402; explanations: 160; distinct texts scored: 1860
- claim length (TARGET tokens): mean 40.7, min 4, max 67

## 2x2 table: mean d = 1 − cos (cluster-bootstrap CI95 by explanation)

| side | d_corr (c vs c*) | d_para (c vs c~) | S = d_corr − d_para | outcome(CI≤0) | ratio of means d_corr/d_para | median item ratio | frac d_corr > d_para |
|---|---|---|---|---|---|---|---|
| TARGET last token | 0.03952 [0.03112, 0.04722] (n=490) | 0.13357 [0.12455, 0.14228] (n=490) | -0.09405 [-0.10376, -0.08445] (n=490) | MET | 0.2959 | 0.0873 | 0.0816 [0.0573, 0.1065] (n=490) |
| TARGET mean over tokens | 0.00013 [0.00012, 0.00015] (n=490) | 0.00134 [0.00128, 0.00140] (n=490) | -0.00121 [-0.00127, -0.00115] (n=490) | MET | 0.0979 | 0.0662 | 0.0061 [0.0000, 0.0142] (n=490) |
| AR (value head) | 0.02167 [0.01793, 0.02554] (n=490) | 0.07113 [0.06517, 0.07745] (n=490) | -0.04945 [-0.05569, -0.04328] (n=490) | MET | 0.3047 | 0.1834 | 0.1286 [0.0990, 0.1585] (n=490) |

## Deterministic corruption (corrupt_det; number/name swap) where present

| side | d_det (c vs c_det) | S_det = d_det − d_para | ratio of means d_det/d_para |
|---|---|---|---|
| TARGET last token | 0.01914 [0.01523, 0.02330] (n=402) | -0.11349 [-0.12281, -0.10393] (n=402) | 0.1443 |
| TARGET mean over tokens | 0.00027 [0.00025, 0.00030] (n=402) | -0.00111 [-0.00118, -0.00104] (n=402) | 0.1967 |
| AR (value head) | 0.02096 [0.01795, 0.02467] (n=402) | -0.04915 [-0.05655, -0.04227] (n=402) | 0.2990 |

## Cross-side agreement (Spearman, per triple)

- rho(d_corr_T_last, d_corr_AR) = 0.4643 (p=1.43e-27)
- rho(d_para_T_last, d_para_AR) = 0.1061 (p=0.0188)
- rho(S_T_last, S_AR) = -0.0098 (p=0.828)

## Distributions (evaluation triples)

| quantity | mean | median | p10 | p90 |
|---|---|---|---|---|
| d_corr_T_last | 0.03952 | 0.00945 | 0.00161 | 0.09101 |
| d_para_T_last | 0.13357 | 0.10949 | 0.04898 | 0.25252 |
| d_det_T_last | 0.01914 | 0.00873 | 0.00149 | 0.03581 |
| d_corr_T_mean | 0.00013 | 0.00008 | 0.00002 | 0.00028 |
| d_para_T_mean | 0.00134 | 0.00121 | 0.00051 | 0.00231 |
| d_det_T_mean | 0.00027 | 0.00021 | 0.00003 | 0.00062 |
| d_corr_AR | 0.02167 | 0.00791 | 0.00158 | 0.05189 |
| d_para_AR | 0.07113 | 0.04749 | 0.00817 | 0.17274 |
| d_det_AR | 0.02096 | 0.00883 | 0.00101 | 0.05336 |

## 10 fixed S3 example rows (verbatim) with their four d values

### accepted #0 (row 133, stim 40, claim 0/4)
- original:   Wikipedia-style chemistry article structure with numbered sections listing properties of europium, presenting factual data about the element's atomic and physical characteristics.
- corrupted:  Wikipedia-style chemistry article structure with numbered sections listing properties of lead, presenting factual data about the element's atomic and physical characteristics.
- paraphrase: Europium's properties detailed in a numbered sections Wikipedia-style chemistry article, encompassing factual data on its atomic and physical attributes.
- corrupt_det: nan
- d_corr_T=0.00726  d_para_T=0.06526  d_corr_AR=0.02456  d_para_AR=0.04535  (mean-pooled: d_corr_T_mean=0.00009 d_para_T_mean=0.00163; det: d_det_T=nan d_det_AR=nan)

### accepted #16 (row 150, stim 44, claim 0/3)
- original:   Narrative momentum: a comic book description listing character traits and dialogue, with a specific scene detailing a gangster's actions.
- corrupted:  Narrative momentum: a comic book description listing character traits and dialogue, with a specific scene detailing a puppy's actions.
- paraphrase: A comic book description focusing on character traits and dialogue, including a particular scene that outlines a gangster's activities.
- corrupt_det: nan
- d_corr_T=0.02371  d_para_T=0.07726  d_corr_AR=0.02672  d_para_AR=0.14714  (mean-pooled: d_corr_T_mean=0.00008 d_para_T_mean=0.00139; det: d_det_T=nan d_det_AR=nan)

### accepted #32 (row 167, stim 49, claim 0/3)
- original:   Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of TV show details about a fictional detective series.
- corrupted:  Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of video game details about a fictional detective series.
- paraphrase: A wiki article structured with metadata fields preceding the film description, setting a standard for TV show details on a fictional detective series.
- corrupt_det: Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of The show details about a fictional detective series.
- d_corr_T=0.00910  d_para_T=0.07346  d_corr_AR=0.01621  d_para_AR=0.04372  (mean-pooled: d_corr_T_mean=0.00006 d_para_T_mean=0.00120; det: d_det_T=0.17420 d_det_AR=0.05173)

### accepted #48 (row 184, stim 54, claim 1/3)
- original:   The sentence "Another biographer was John Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- corrupted:  The sentence "Another biographer was Jack Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- paraphrase: The sentence "John Carter was another biographer" introduces a named source or figure, probably a secondary account or personal detail about the soldier's life, indicating a particular person or event linked to his fame or death.
- corrupt_det: The sentence "Initially biographer was John Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- d_corr_T=0.00296  d_para_T=0.04357  d_corr_AR=0.01964  d_para_AR=0.10252  (mean-pooled: d_corr_T_mean=0.00008 d_para_T_mean=0.00072; det: d_det_T=0.01866 d_det_AR=0.04621)

### accepted #64 (row 201, stim 59, claim 0/3)
- original:   American military article format with numbered statistics detailing a Florida county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- corrupted:  American military article format with numbered statistics detailing a Antarctica county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- paraphrase: American military-style article, featuring numbered statistics about a Florida county's infrastructure, presented in organized bullet points and complete with citations.
- corrupt_det: American military article format with numbered statistics detailing a However county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- d_corr_T=0.00603  d_para_T=0.06098  d_corr_AR=0.02003  d_para_AR=0.18822  (mean-pooled: d_corr_T_mean=0.00011 d_para_T_mean=0.00092; det: d_det_T=0.03583 d_det_AR=0.04227)

### accepted #80 (row 218, stim 64, claim 0/3)
- original:   British historical biography article detailing parliamentary politics of Charles I, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- corrupted:  British historical biography article detailing parliamentary politics of Charles II, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- paraphrase: Article on British historical biography focusing on Charles I's parliamentary politics, systematically outlining parliamentary opposition and constitutional crisis through numbered sections and a chronological narrative.
- corrupt_det: British historical biography article detailing parliamentary politics of War I, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- d_corr_T=0.00322  d_para_T=0.02767  d_corr_AR=0.00218  d_para_AR=0.02889  (mean-pooled: d_corr_T_mean=0.00004 d_para_T_mean=0.00073; det: d_det_T=0.01745 d_det_AR=0.01828)

### accepted #96 (row 239, stim 69, claim 3/4)
- original:   " closes a third item in a parallel list ("While the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Slavic dialects' variant counts."
- corrupted:  " closes a third item in a parallel list ("While the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Sino-Tibetan languages' variant counts."
- paraphrase: closes a third entry in an analogous list ("While the latter encompasses the Turkish language with its complete written form and the Greek language with abbreviated characters..."), anticipating either "The written form of the last language is..." or "The variants of Slavic dialects count."
- corrupt_det: " closes a third item in a parallel list ("Black the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Slavic dialects' variant counts."
- d_corr_T=0.01493  d_para_T=0.13111  d_corr_AR=0.00890  d_para_AR=0.09778  (mean-pooled: d_corr_T_mean=0.00021 d_para_T_mean=0.00164; det: d_det_T=0.00562 d_det_AR=0.01392)

### accepted #112 (row 258, stim 74, claim 0/3)
- original:   British music article format with Wikipedia-style entry structure detailing an album by Scottish rock band Feeder, listing discography and chart performance.
- corrupted:  British music article format with Wikipedia-style entry structure detailing an album by English rock band Feeder, listing discography and chart performance.
- paraphrase: An article in the style of a British music Wikipedia entry, providing details on an album by the Scottish rock band Feeder, including discography and chart performance.
- corrupt_det: British music article format with Wikipedia-style entry structure detailing an album by Imagine rock band Feeder, listing discography and chart performance.
- d_corr_T=0.00087  d_para_T=0.12190  d_corr_AR=0.00148  d_para_AR=0.01523  (mean-pooled: d_corr_T_mean=0.00002 d_para_T_mean=0.00150; det: d_det_T=0.00608 d_det_AR=0.00327)

### accepted #128 (row 275, stim 79, claim 2/3)
- original:   Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as Darren Aronofsky, also known as"), strongly expecting "DA" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- corrupted:  Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as Darren Aronofsky, also known as"), strongly expecting "Bob" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- paraphrase: The concluding token "as" signals an unfinished noun phrase ("also known as"), which is part of a name attribution clause ("known as Darren Aronofsky, also known as"), with a strong anticipation for "DA," "Arno," "Aronofsky," or "DAF" to finalize the nickname or abbreviated identity.
- corrupt_det: Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as AI Aronofsky, also known as"), strongly expecting "DA" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- d_corr_T=0.01687  d_para_T=0.24649  d_corr_AR=0.00266  d_para_AR=0.01845  (mean-pooled: d_corr_T_mean=0.00025 d_para_T_mean=0.00387; det: d_det_T=0.01495 d_det_AR=0.09317)

### accepted #144 (row 292, stim 85, claim 1/3)
- original:   The sentence structure "While some songs were originally intended for the compilation album, several artists chose not to include certain tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- corrupted:  The sentence structure "While some songs were originally intended for the compilation album, several artists chose to include all tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- paraphrase: The sentence structure "Although some songs were planned for the compilation album, various artists decided against including particular tracks in the ultimate tracklist" outlines a pattern of detailing exclusions, suggesting the definitive answer regarding the initial album's contents.
- corrupt_det: The sentence structure "Dutch some songs were originally intended for the compilation album, several artists chose not to include certain tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- d_corr_T=0.00314  d_para_T=0.05588  d_corr_AR=0.03337  d_para_AR=0.04824  (mean-pooled: d_corr_T_mean=0.00023 d_para_T_mean=0.00054; det: d_det_T=0.00505 d_det_AR=0.04891)

## R2 — amplified corruption (every accepted claim replaced), AR only

- evaluation explanations with claims (S2): 160; included (>= 2 accepted claims): 160; excluded: 0; errors: 0
- explanations with >= 2 corrupt_det claims: 155
- per included explanation: n_claims mean 3.36; n_accepted mean 3.06; fraction of claims replaced 0.911; n_det mean 2.78

## Headline (paired per explanation; cluster bootstrap CI95)

| statistic | mean | CI95 lo | CI95 hi | n_expl |
|---|---|---|---|---|
| cos(z) − cos(z**)  [all accepted claims corrupted] | 0.00754 | 0.00473 | 0.01082 | 160 |
| cos(z) − cos(z~~)  [all accepted claims paraphrased] | 0.01407 | 0.01149 | 0.01667 | 160 |
| (cos z − cos z**) − (cos z − cos z~~) | -0.00653 | -0.00992 | -0.00260 | 160 |
| cos(z) − cos(z*det)  [all det-corruptible claims swapped] | 0.00922 | 0.00662 | 0.01214 | 155 |
| (cos z − cos z*det) − (cos z − cos z~~)  [same explanations] | -0.00506 | -0.00855 | -0.00137 | 155 |
| cos(z_joined) − cos(z**) | 0.00665 | 0.00425 | 0.00984 | 160 |
| cos(z_joined) − cos(z~~) | 0.01318 | 0.01085 | 0.01562 | 160 |
| cos(z) − cos(empty)  [scale reference] | 0.53490 | 0.52118 | 0.54772 | 160 |

- fraction of explanations where corruption hurts more than paraphrase (D_corrupt > D_para): 0.2125 CI95 [0.1562, 0.2750] n=160
- same for deterministic corruption: 0.3161 CI95 [0.2452, 0.3873] n=155
- for comparison, S3 single-claim: cos(z) − cos(z*) 0.00313, cos(z) − cos(z~) 0.00494, A − P −0.00181 (s3_summary.md)

## Distributions (included explanations)

| quantity | mean | median | p10 | p90 | n |
|---|---|---|---|---|---|
| cos_z | 0.88203 | 0.89176 | 0.81632 | 0.92884 | 160 |
| cos_z_joined | 0.88114 | 0.89249 | 0.81607 | 0.92919 | 160 |
| cos_z_corrupt_all | 0.87449 | 0.88626 | 0.81227 | 0.92472 | 160 |
| cos_z_para_all | 0.86796 | 0.87853 | 0.80494 | 0.92192 | 160 |
| cos_z_det_all | 0.87288 | 0.88355 | 0.80513 | 0.92321 | 155 |
| cos_empty | 0.34713 | 0.34829 | 0.24351 | 0.44351 | 160 |
| D_corrupt | 0.00754 | 0.00322 | -0.00259 | 0.01527 | 160 |
| D_para | 0.01407 | 0.00946 | 0.00166 | 0.03204 | 160 |
| D_det | 0.00922 | 0.00316 | -0.00222 | 0.03024 | 155 |
| D_corrupt_minus_para | -0.00653 | -0.00691 | -0.02656 | 0.00763 | 160 |

## By number of replaced claims

| n_accepted | n_expl | mean D_corrupt | mean D_para | mean diff |
|---|---|---|---|---|
| 2 | 24 | 0.00367 | 0.00804 | -0.00436 |
| 3 | 111 | 0.00638 | 0.01310 | -0.00673 |
| 4 | 17 | 0.01705 | 0.01480 | 0.00225 |
| 5 | 7 | 0.00928 | 0.03905 | -0.02977 |
| 6 | 1 | 0.05571 | 0.07938 | -0.02367 |

## R3 — truncation curve (first k / last k claims), AR only, descriptive

- explanations: 160; claims: 538; n_claims histogram: 3:123, 4:23, 5:9, 6:3, 7:2
- cos_z mean 0.8820; cos_empty mean 0.3471; errors 0

## Mean cos and lift vs k (explanations with n_claims >= k; cluster-bootstrap CI95 by explanation)

| k | n_expl | first-k mean cos | first-k mean lift | first-k median lift | last-k mean cos | last-k mean lift | last-k median lift |
|---|---|---|---|---|---|---|---|
| 1 | 160 | 0.4673 [0.4528, 0.4814] | 0.2270 [0.2080, 0.2460] | 0.2251 | 0.8217 [0.8060, 0.8349] | 0.8837 [0.8574, 0.9044] | 0.9253 |
| 2 | 160 | 0.7115 [0.6917, 0.7320] | 0.6766 [0.6395, 0.7143] | 0.7240 | 0.8635 [0.8551, 0.8724] | 0.9640 [0.9533, 0.9730] | 0.9791 |
| 3 | 160 | 0.8533 [0.8384, 0.8669] | 0.9427 [0.9206, 0.9624] | 0.9982 | 0.8768 [0.8689, 0.8847] | 0.9885 [0.9809, 0.9949] | 0.9985 |
| 4 | 37 | 0.8657 [0.8465, 0.8830] | 0.9728 [0.9443, 0.9910] | 0.9979 | 0.8702 [0.8536, 0.8855] | 0.9853 [0.9715, 0.9950] | 0.9975 |
| 5 | 14 | 0.8534 [0.8211, 0.8827] | 0.9539 [0.8894, 1.0009] | 0.9993 | 0.8598 [0.8349, 0.8830] | 0.9742 [0.9402, 0.9988] | 0.9983 |
| 6 | 5 | 0.8281 [0.7818, 0.8711] | 0.9072 [0.8285, 0.9858] | 0.9412 | 0.8365 [0.7892, 0.8795] | 0.9277 [0.8495, 0.9973] | 0.9949 |
| 7 | 2 | 0.8391 [0.7969, 0.8813] | 0.9252 [0.8553, 0.9950] | 0.9252 | 0.8391 [0.7969, 0.8813] | 0.9252 [0.8553, 0.9950] | 0.9252 |

- k at which the median first-k lift first exceeds 0.9: 3; last-k: 1
- all claims joined (k = n) minus cos_z: -0.00089 [-0.00188, -0.00005] n=160

## Per-explanation smallest k with lift > 0.9

| direction | n_expl | never reached | k*=1 | k*=2 | k*=3 | k*>=4 | mean k*/n |
|---|---|---|---|---|---|---|---|
| first | 160 | 2 | 0 | 33 | 102 | 23 | 0.897 |
| last | 160 | 1 | 103 | 44 | 10 | 2 | 0.430 |

## First k vs last k, paired within explanation (same k)

| k | n_expl | mean cos(first k) − cos(last k) | CI95 |
|---|---|---|---|
| 1 | 160 | -0.35444 | [-0.37379, -0.33391] |
| 2 | 160 | -0.15206 | [-0.17204, -0.13159] |
| 3 | 37 | -0.10149 | [-0.14181, -0.06278] |
| 4 | 14 | -0.01194 | [-0.02873, 0.00135] |
| 5 | 5 | -0.01802 | [-0.03935, 0.00231] |
| 6 | 2 | -0.02108 | [-0.02667, -0.01550] |

## Single claims alone (S2 cos_alone)

- cos_alone: mean 0.6603, median 0.6924, p10 0.4171, p90 0.8705 (n=538)
- lift_alone: mean 0.5808, median 0.6418
- Spearman(claim word count, cos_alone): rho=0.7024 p=3.45e-81 (n=538)
- Spearman(claim word count, lift_alone): rho=0.7339 p=4.2e-92
- Spearman(relative claim position, cos_alone): rho=0.7638 p=5.5e-104

| claim position | n | mean cos_alone | mean n_words |
|---|---|---|---|
| first | 160 | 0.4673 | 20.3 |
| middle | 218 | 0.6835 | 30.5 |
| last | 160 | 0.8217 | 39.4 |

## FOLLOWUPS.md (queued for the human, not acted on)

- S3 statistic A_i = Δ_i(z*) − Δ_i(z) equals cos(z) − cos(z*) by construction (z* minus c_i* is the same text as z minus c_i), so the primary and the first secondary statistic coincide; both are reported as pre-registered.
- Stage scripts create their Settings file at module import; importing one stage from another (S3 imports S2's splitter) or re-running with --summary overwrites the finished stage's settings JSON. Move Settings creation under main() next round.

## OPEN DECISIONS (from STATE.md)

## Open decisions (research calls left for the human)
(none)

## Provenance

**Pre-registered by the human (PLAN.md round 2):** the three questions and their stages, the R0 acceptance rule (0.8820 ± 0.002), the inputs (490 accepted S3 triples plus corrupt_det where present; S2 claim lists), the target-side encoding (raw claim text, no chat template, hidden_states[21], last token and mean over tokens), the AR-side encoding, d = 1 − cos, the R1 and R2 kill statistics and thresholds (CI ≤ 0 → MET; R1 n ≥ 300), the R3 quantities (first k / last k, lift over floor, k at median lift > 0.9, Spearman(word count, cos_alone)), the cluster bootstrap (by explanation, 1000 draws, seed 0), the INCONCLUSIVE rule, and the 5.5 h hard stop.

**Written by the agent:** `r0_check.py`, `r1_locus.py`, `r2_amplify.py`, `r3_truncate.py`, `r4_morning.py`, this file. `nla_lib.py` and all round-1 files were reused unchanged.

**Choices the agent had to make (none changes a pre-registered statistic):**
- R0: activations rebuilt from `doc_idx`, `pos`, `pos2` in `stimuli.csv` (no re-shuffle of the corpus); the tokenisation was asserted against `seq_len` and `token_str` for every stimulus; `stimuli.csv` and `explanations.jsonl` were not rewritten. Per-row agreement with `s1_recon.csv` is reported beside the mean.
- R1: TARGET then AR ran sequentially in one process (TARGET freed first) rather than co-resident; the 1860 distinct texts were scored once each. `corrupt_det` included where `numeric_ok` and non-null (402 of 490). The ratio d_corr/d_para is reported both as ratio of means and as the median per-item ratio. The same CI ≤ 0 rule is applied to the mean-pooled and AR sides as descriptive outcome labels; only the last-token target side is the pre-registered kill. The 10 example rows are the S3 fixed examples, read from `s3_summary.md`.
- R2: 'accepted' = S3 `edit_ok`; z*det built on explanations with ≥ 2 det-corruptible claims (155 of 160). cos(z) is the S1 reconstruction of the original explanation text; cos(z_joined) − cos(edited) is reported alongside as in S3. No minimum-n rule was pre-registered for R2 and none was applied.
- R3: per-k statistics are over explanations with n_claims ≥ k; k* = the first k at which the median lift over those explanations exceeds 0.9 (also per-explanation smallest k). `cos_alone` is taken from `s2_claims.csv` as pre-registered (S2 run), while its lift uses the regenerated cos_empty; the first-vs-last paired statistic excludes k = n (identical text).
- Crash fix (RUNLOG): R1 iteration 1 died before any model load (pandas NaN for missing `corrupt_det` in the text set); the text filter now keeps only strings. No statistic touched; log kept as `out/r1_iter1_crash.log`.
- Settings files are created inside `main()` (round-1 FOLLOWUP applied); importing a stage module no longer writes anything.

