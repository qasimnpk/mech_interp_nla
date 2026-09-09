# K1 summary — K-way alternative ranking on deterministic-swap claims (AR only)

git 846a34ea; settings in k1_settings.json; progress in k1_progress.json

## Kill test

- 2026-09-09T03:08:52  K1  K1  threshold=CI95 (cluster by explanation) of (top-1 rate − 0.125) on non-last in_full_prefix rows (n=107) ≤ 0 → MET; > 0 → NOT MET; straddles or < 80 rows completed → INCONCLUSIVE  observed=nonlast_in_prefix: n=107 top1−0.125 0.1834 [0.0962,0.2650] n=107 k=89 (top1 0.308) MRR 0.487 gap 0.00125 [0.00058,0.00202] n=107 k=89 frac gap>0 0.654; nonlast_not_in_prefix: n=159 top1−0.125 0.1266 [0.0613,0.1895] n=159 k=115 (top1 0.252) MRR 0.443 gap 0.00044 [0.00000,0.00086] n=159 k=115 frac gap>0 0.535; positive_control_last: n=127 top1−0.125 0.3238 [0.2372,0.4104] n=127 k=127 (top1 0.449) MRR 0.587 gap 0.01080 [0.00729,0.01461] n=127 k=127 frac gap>0 0.732; rows completed 393/393 (errors 0); original cache reused True  NOT MET  preference for the AV's original word among 8 one-word variants; not a truth label; in_full_prefix is a string proxy

## Counts

- rows 393 (non-last in-prefix 107, non-last not-in-prefix 159, last 127); completed 393; errors 0; pool_short 6; dup_sentence 0
- slot type: non-last entity 235, non-last detail 31
- original cos cache: reused s2 cos_z = True (max |dev| on 20 rows 1.11e-16)

## Per stratum (cluster by explanation)

| stratum | n | n_expl | top1 | top1−0.125 CI | MRR | mean gap | gap CI | frac gap>0 | mean gap_max | mean spread |
|---|---|---|---|---|---|---|---|---|---|---|
| nonlast_in_prefix | 107 | 89 | 0.308 | [0.0962,0.2650] | 0.487 | 0.00125 | [0.00058,0.00202] | 0.654 | -0.00051 | 0.00465 |
| nonlast_not_in_prefix | 159 | 115 | 0.252 | [0.0613,0.1895] | 0.443 | 0.00044 | [0.00000,0.00086] | 0.535 | -0.00114 | 0.00370 |
| positive_control_last | 127 | 127 | 0.449 | [0.2372,0.4104] | 0.587 | 0.01080 | [0.00729,0.01461] | 0.732 | 0.00398 | 0.02203 |

## 2×2 (non-last rows): in_full_prefix × slot type

| in_full_prefix \ slot type | entity | detail |
|---|---|---|
| True | n=99 top1 0.293 [0.213,0.379] gap 0.00094 [0.00039,0.00159] | n=8 top1 0.500 [0.125,0.875] gap 0.00508 [0.00034,0.01046] |
| False | n=136 top1 0.272 [0.197,0.346] gap 0.00048 [-0.00001,0.00096] | n=23 top1 0.130 [0.000,0.273] gap 0.00021 [-0.00006,0.00048] |

Distributions for the four cells (gap):

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gap / in_full_prefix=True × entity | 99 | 0.00094 | 0.00316 | 0.00001 | -0.00441 | -0.00213 | -0.00144 | -0.00023 | 0.00035 | 0.00144 | 0.00258 | 0.00467 | 0.02233 |
| gap / in_full_prefix=True × detail | 8 | 0.00508 | 0.00816 | 0.00007 | -0.00055 | -0.00032 | -0.00008 | 0.00022 | 0.00054 | 0.00680 | 0.01753 | 0.01852 | 0.01952 |
| gap / in_full_prefix=False × entity | 136 | 0.00048 | 0.00315 | 0.00001 | -0.01273 | -0.00245 | -0.00167 | -0.00070 | 0.00006 | 0.00129 | 0.00247 | 0.00574 | 0.01554 |
| gap / in_full_prefix=False × detail | 23 | 0.00021 | 0.00068 | 0.00000 | -0.00090 | -0.00063 | -0.00047 | -0.00019 | 0.00013 | 0.00048 | 0.00077 | 0.00118 | 0.00230 |

## Distributions

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gap / nonlast_in_prefix | 107 | 0.00125 | 0.00385 | 0.00001 | -0.00441 | -0.00198 | -0.00117 | -0.00022 | 0.00035 | 0.00154 | 0.00316 | 0.00656 | 0.02233 |
| gap_max / nonlast_in_prefix | 107 | -0.00051 | 0.00283 | 0.00001 | -0.00614 | -0.00445 | -0.00349 | -0.00164 | -0.00052 | 0.00021 | 0.00131 | 0.00270 | 0.01278 |
| spread / nonlast_in_prefix | 107 | 0.00465 | 0.00651 | 0.00004 | 0.00035 | 0.00085 | 0.00116 | 0.00178 | 0.00289 | 0.00459 | 0.00779 | 0.01325 | 0.04568 |
| rank / nonlast_in_prefix | 107 | 3.59813 | 2.42961 | 5.90302 | 1.00000 | 1.00000 | 1.00000 | 1.00000 | 3.00000 | 5.00000 | 7.40000 | 8.00000 | 8.00000 |
| cos_orig / nonlast_in_prefix | 107 | 0.88784 | 0.03866 | 0.00149 | 0.79396 | 0.81427 | 0.81897 | 0.86883 | 0.89719 | 0.91203 | 0.93047 | 0.94130 | 0.96257 |
| cos_alts_mean / nonlast_in_prefix | 107 | 0.88659 | 0.03935 | 0.00155 | 0.79422 | 0.80759 | 0.81806 | 0.86849 | 0.89652 | 0.91103 | 0.92872 | 0.93896 | 0.96244 |
| gap / nonlast_not_in_prefix | 159 | 0.00044 | 0.00292 | 0.00001 | -0.01273 | -0.00227 | -0.00154 | -0.00051 | 0.00007 | 0.00109 | 0.00229 | 0.00424 | 0.01554 |
| gap_max / nonlast_not_in_prefix | 159 | -0.00114 | 0.00277 | 0.00001 | -0.01592 | -0.00507 | -0.00357 | -0.00211 | -0.00074 | 0.00002 | 0.00076 | 0.00236 | 0.00673 |
| spread / nonlast_not_in_prefix | 159 | 0.00370 | 0.00398 | 0.00002 | 0.00049 | 0.00082 | 0.00093 | 0.00144 | 0.00262 | 0.00409 | 0.00720 | 0.01087 | 0.02911 |
| rank / nonlast_not_in_prefix | 159 | 3.99371 | 2.57912 | 6.65186 | 1.00000 | 1.00000 | 1.00000 | 1.50000 | 3.00000 | 6.00000 | 8.00000 | 8.00000 | 8.00000 |
| cos_orig / nonlast_not_in_prefix | 159 | 0.87962 | 0.04880 | 0.00238 | 0.67928 | 0.79650 | 0.81542 | 0.86406 | 0.89018 | 0.90791 | 0.92649 | 0.93439 | 0.96257 |
| cos_alts_mean / nonlast_not_in_prefix | 159 | 0.87919 | 0.04894 | 0.00239 | 0.67960 | 0.78964 | 0.81386 | 0.86434 | 0.89096 | 0.90810 | 0.92622 | 0.93350 | 0.96266 |
| gap / positive_control_last | 127 | 0.01080 | 0.02153 | 0.00046 | -0.00926 | -0.00272 | -0.00132 | -0.00012 | 0.00129 | 0.00904 | 0.04226 | 0.05345 | 0.14347 |
| gap_max / positive_control_last | 127 | 0.00398 | 0.01269 | 0.00016 | -0.01449 | -0.00493 | -0.00375 | -0.00156 | -0.00026 | 0.00245 | 0.01878 | 0.02628 | 0.07451 |
| spread / positive_control_last | 127 | 0.02203 | 0.03622 | 0.00131 | 0.00038 | 0.00073 | 0.00135 | 0.00270 | 0.00486 | 0.02106 | 0.07258 | 0.08566 | 0.22340 |
| rank / positive_control_last | 127 | 3.15748 | 2.46701 | 6.08611 | 1.00000 | 1.00000 | 1.00000 | 1.00000 | 2.00000 | 5.00000 | 7.00000 | 8.00000 | 8.00000 |
| cos_orig / positive_control_last | 127 | 0.88213 | 0.04498 | 0.00202 | 0.67928 | 0.79955 | 0.81615 | 0.86501 | 0.89184 | 0.90721 | 0.92692 | 0.93790 | 0.96257 |
| cos_alts_mean / positive_control_last | 127 | 0.87133 | 0.04703 | 0.00221 | 0.64475 | 0.79347 | 0.81004 | 0.84956 | 0.88479 | 0.90384 | 0.91476 | 0.92536 | 0.94168 |

## Rank histogram of the original among 8 (per stratum)

- nonlast_in_prefix: rank 1: 33, rank 2: 10, rank 3: 18, rank 4: 8, rank 5: 12, rank 6: 7, rank 7: 8, rank 8: 11
- nonlast_not_in_prefix: rank 1: 40, rank 2: 23, rank 3: 17, rank 4: 11, rank 5: 15, rank 6: 17, rank 7: 11, rank 8: 25
- positive_control_last: rank 1: 57, rank 2: 10, rank 3: 12, rank 4: 10, rank 5: 10, rank 6: 8, rank 7: 10, rank 8: 10

## 5 fixed verbatim examples (seed 0; non-last in-prefix rows)

### row 481 (stim 142, claim 0/3, entity, word_orig 'Jewish')

- prefix tail (last 400 chars): "syt , grew up in Warsaw , survived the Warsaw Ghetto , the Majdanek concentration camp , and two slave labor camps . Her first husband died in the war . She considered the day of her liberation as the most horrible day of her life , as she realized that she was alone , her parents and siblings gone . Norman 's father , Zacharias Finkelstein , active in Hashomer Hatzair , was a survivor of both the"
- claim: 'Historical/academic book description format with numbered testimonies listing Jewish Holocaust survivors, detailing biographical credentials and testimonies about the Holocaust.'
- cos orig 0.89367; alternatives: Canadian 0.89482, UK 0.89480, Che 0.89507, Over 0.89508, C60 0.89534, Global 0.89524, Mike 0.89667
- rank 8, gap -0.00162

### row 411 (stim 120, claim 1/3, entity, word_orig '"The')

- prefix tail (last 400 chars): ' series developer Beau Willimon and directed by executive producer David Fincher . The episode also earned 3 other Emmy nominations as well as WGA : Episodic Drama and DGA – Drama Series nominations . \n Frank Underwood ( Kevin Spacey ) is an ambitious Democratic congressman and the House Majority Whip . Underwood helped ensure the election of President Garrett Walker ( Michel Gill ) , who promised'
- claim: 'The sentence "The character is a Democrat congressman named Todd Young who is running for Senate and vowed" contains a specific historical reference ("Obama\'s promise to support him"), implying a backstory about Biden\'s political deal or campaign promise.'
- cos orig 0.87933; alternatives: Italian 0.87777, Muslim 0.87723, Darren 0.87925, Reviewers 0.88009, Lower 0.87880, EMI 0.87755, Known 0.87725
- rank 2, gap 0.00105

### row 277 (stim 80, claim 1/3, entity, word_orig '"The')

- prefix tail (last 400 chars): 'sed France into administrative departments in order to rebalance the uneven distribution of French wealth , which had been subject to feudalism under the monarchical Ancien Régime . \n \n = = Rebellion in Southern France = = \n \n In July 1793 Captain Napoleon Bonaparte , an artillery officer , was placed under the command of Jean @-@ Baptiste Carteaux to deal with rebels from Marseille situated in Av'
- claim: 'The sentence "The Pope also sent troops from Rome to support the Carbonari in the village of Av" appears to be listing a specific location or event, likely a place name or military campaign detail about the rebellion\'s advance.'
- cos orig 0.94213; alternatives: Singapore 0.94268, First 0.94408, Aggi 0.94216, Beirut 0.94232, Nip 0.94182, UK 0.94275, Having 0.94214
- rank 7, gap -0.00043

### row 307 (stim 89, claim 0/3, entity, word_orig 'New')

- prefix tail (last 400 chars): 'to floriculture , it is rarely cultivated . \n \n = = Description = = \n \n Banksia violacea grows as a shrub up to 1 @.@ 5 m ( 5 ft ) tall , with narrow leaves 1 – 2 cm ( 0 @.@ 4 – 0 @.@ 8 in ) long and about 0 @.@ 15 cm ( 0 @.@ 06 in ) wide . New growth occurs in summer , and flowering ranges from November to April with a peak in February , but can be irregular in timing . Flowers arise from typical'
- claim: 'Australian botanical/field guide format with structured species description, detailing a rare New Zealand orchid species with botanical characteristics and habitat.'
- cos orig 0.89168; alternatives: Korea 0.88993, Nip 0.89197, He 0.89184, Haji 0.89195, Los 0.89171, David 0.89168, Additionally 0.89185
- rank 6, gap 0.00012

### row 565 (stim 167, claim 1/3, entity, word_orig '"The')

- prefix tail (last 400 chars): 'outh and southwest through wetlands and passes through two small lakes , Tumtum and Mica . It has sections of rapids and whitewater , and flows over cataracts below Tumtum Lake . Its flow drops by 5 metres ( 16 ft ) per kilometre in certain sections . After travelling for 94 kilometres ( 58 mi ) and entering the Shuswap Highland , it enters the northern end of Adams Lake . \n Adams Lake is roughly '
- claim: 'The sentence structure "The Long Lake is a long narrow lake north of the town, with a length of" continues a distance/dimension fact about the Lake of Two Hills, likely providing another geographic measurement or feature detail about the lake.'
- cos orig 0.91094; alternatives: Royal 0.91065, Background 0.90857, Known 0.90952, 1930s 0.91104, Song 0.91112, Bal 0.91146, Unlike 0.91122
- rank 5, gap 0.00043


- review sheets: k1_review_blind.csv (20 rows, seed 0) — open first; k1_review_key.csv after
