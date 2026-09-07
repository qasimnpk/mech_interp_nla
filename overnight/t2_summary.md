# T2 summary — forced-prefix readout from the verbalizer (AV forward only)

git 96e2eede; settings in t2_settings.json; rows in t2_scores.csv (per stimulus) and t2_claims.csv

- AV forwards 5164 (0.32 s each on topics, 0.40 s on claims); errors 0 stimuli, 0 claim rows
- ' Yes' ids [7414], ' No' ids [2308], single-token: True; prompt 125 tokens, marker at 111
- eval n=160; topic-absent subset (topic_true not in default explanation) n=154

## Kill T2 — candidate continuation (evaluation, paired AUROC, bootstrap by document)

- summed log-prob ' {topic_true}' vs ' {topic_foreign}', own activation: 0.7516 [0.7017,0.7983] → **NOT MET**
- per-token normalised: 0.7479 [0.6961,0.7950]
- no injection (prior only): 0.4880 [0.4315,0.5508]; per-token 0.5076 [0.4504,0.5635]; frac true>foreign 0.481
- prior-corrected (lp − lp_noinj): 0.9347 [0.9111,0.9580]
- swap control (foreign activation injected; AUROC that it prefers the foreign topic): 0.7749 [0.7295,0.8202]; per-token 0.7344 [0.6883,0.7860]; frac 0.787
- fraction cc_true > cc_foreign (own activation): 0.775
- topic token counts: true mean 5.81, foreign mean 5.64

## Yes/no format (evaluation)

- AUROC yes−no true-q vs foreign-q, injected: 0.5502 [0.5227,0.5777] → MET (threshold-table wording); no injection 0.4969 [0.4300,0.5647]; prior-corrected 0.5610 [0.5321,0.5892]; swap prefers foreign 0.5603 [0.5333,0.5906]; frac true>foreign 0.637

| question | mean yes−no injected | mean yes−no no injection |
|---|---|---|
| true | +2.280 | +2.630 |
| foreign | +2.041 | +2.648 |
| conf | +2.883 | +2.438 |
| torn | +2.568 | +3.562 |

## Same statistics on the topic-absent subset

- cc AUROC 0.7482 [0.6993,0.7964]; per-token 0.7484 [0.6949,0.7994]; no-inj 0.4749 [0.4148,0.5373]; prior-corrected 0.9317 [0.9051,0.9546]; swap prefers foreign 0.7881 [0.7389,0.8332]
- yes/no AUROC 0.5471 [0.5203,0.5763]; no-inj 0.4960 [0.4342,0.5651]; prior-corrected 0.5587 [0.5310,0.5879]
- Spearman(yn_conf, −entropy) +0.0092 [-0.1410,+0.1639] n=154; Spearman(yn_torn, entropy) -0.1616 [-0.3086,-0.0072] n=154

## Confidence / conflict questions vs next-token entropy (evaluation)

| statistic | pooled | punctuation | word_initial | word_piece |
|---|---|---|---|---|
| Spearman(yes−no conf, −entropy) | +0.0402 [-0.1131,+0.1835] n=160 | +0.2889 [-0.0478,+0.5788] n=24 | -0.0551 [-0.2556,+0.1525] n=108 | +0.0967 [-0.2735,+0.4575] n=28 |
| Spearman(yes−no torn, entropy) | -0.1841 [-0.3235,-0.0363] n=160 | -0.6146 [-0.7991,-0.2846] n=24 | -0.0368 [-0.2247,+0.1519] n=108 | -0.1109 [-0.5351,+0.3102] n=28 |

## Single-word claim corruptions (claim prefix prefilled; log-prob of original vs corrupted word)

- S3 pairs: corrupt 490 (single-word 298); corrupt_det 402 (single-word 393)

| edit | n | n_expl | mean lp_orig − lp_corrupt injected | CI95 | no injection | diff (inj − noinj) | CI95 | frac orig>corrupt inj / noinj |
|---|---|---|---|---|---|---|---|---|
| LLM corrupt | 298 | 147 | 9.7822 | [8.9749,10.5217] | 1.3875 | 8.3947 | [7.4664,9.3455] | 0.973 / 0.638 |
| deterministic | 393 | 158 | 15.4190 | [14.4406,16.5458] | 3.7403 | 11.6787 | [10.6376,12.7097] | 0.972 / 0.768 |
| LLM corrupt, last claims only | 82 | 82 | 11.5530 | | 0.5417 | 11.0113 | [9.3673,13.0329] | 0.976 / 0.598 |

## Ten fixed rows (eval rows 0,16,…,144)

| stim | topic_true | topic_foreign | cc true | cc foreign | cc true noinj | cc foreign noinj | yn true | yn foreign | yn conf | entropy |
|---|---|---|---|---|---|---|---|---|---|---|
| 40 | Europium | The Litigators | -14.66 | -46.14 | -21.75 | -34.18 | +4.00 | +3.00 | +4.06 | 1.453 |
| 56 | Andrew Johnston (singer) | President Evil | -44.81 | -27.65 | -40.01 | -24.68 | +2.81 | +1.69 | +2.00 | 0.005 |
| 72 | No result, Pts | Blackburn Firecrest | -60.15 | -44.38 | -50.48 | -37.90 | +1.09 | +2.34 | +3.06 | 4.831 |
| 88 | Draining and development of the Everglades | Battle of Binh Gia | -41.00 | -44.39 | -54.40 | -33.95 | +0.56 | +0.75 | +2.75 | 4.085 |
| 104 | Martin Keamy | Pokiri | -35.86 | -37.78 | -40.37 | -30.25 | +2.06 | +2.00 | +3.12 | 1.563 |
| 120 | Chapter 1 (House of Cards) | Battle of Hubbardton | -36.56 | -45.46 | -35.62 | -26.66 | +1.81 | +2.38 | +4.00 | 1.482 |
| 136 | Hurricane Omar (2008) | Saint Leonard Catholic Church (Madison, Nebraska) | -32.29 | -70.31 | -29.50 | -59.97 | +2.06 | +2.12 | +2.06 | 0.107 |
| 152 | Ulysses (poem) | 766th Independent Infantry Regiment (North Korea) | -26.28 | -91.43 | -26.11 | -51.10 | +2.50 | +1.50 | +2.62 | 0.268 |
| 168 | Stop!! Hibari-kun! | Texas A & M Singing Cadets | -64.34 | -79.25 | -67.15 | -63.79 | +0.00 | +1.50 | +2.12 | 3.283 |
| 184 | Florida State Road 878 | Central Area Command (RAAF) | -36.88 | -58.79 | -42.07 | -51.95 | +1.47 | +1.69 | +2.06 | 1.834 |

