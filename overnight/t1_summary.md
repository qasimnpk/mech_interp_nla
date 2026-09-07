# T1 summary — the reconstructor as a zero-shot text probe (AR only; RepE baseline in the TARGET)

git c980a7ce; settings in t1_settings.json; per-stimulus rows in t1_scores.csv; claim rows in t1_claims.csv; RepE activations in out/t1_repe.npz

- stimuli 200 (eval 160); AR forwards 2065 (0.115 s each); RepE 3200 TARGET forwards (0.097 s each)

## Kill T1 — topic AUROC (evaluation, paired, bootstrap by document)

- AR probe `This text is about {topic}.`: AUROC 0.6125 [0.5887,0.6400] n=160 → **INCONCLUSIVE**
- all 200 stimuli: 0.6131 [0.5908,0.6352] n=200
- paired difference s_topic = cos(true) − cos(foreign): 0.03316 [0.02613,0.04007] n=160; fraction > 0: 0.787
- subset where topic_true is NOT in the default explanation (n=154): 0.6128 [0.5877,0.6411] n=154
- mean cos(h, AR(true)) 0.3911; cos(h, AR(foreign)) 0.3579; cos(AR(true), AR(foreign)) 0.8063

## RepE / difference-of-means baseline (TARGET block 20, 16 templates per topic)

| probe | AUROC (eval) | CI95 |
|---|---|---|
| AR probe (kill statistic) | 0.6125 | [0.5887,0.6400] |
| RepE class means, centred by grand mean | 0.7405 | [0.6825,0.7972] |
| RepE class means, uncentred | 0.5772 | [0.5595,0.6018] |
| RepE difference direction s vs −s | 0.8128 | [0.7402,0.8782] |

- RepE s = cos(h, mu_true − mu_foreign): 0.05432 [0.03952,0.06805] n=160; fraction > 0: 0.769
- cos(mu_true, mu_foreign) mean 0.9003 (how similar the two class means are before centring)
- Spearman(s_topic AR, s_repe) over eval: +0.2188

## Matched nearby contrast — 490 accepted S3 triples scored alone (cluster bootstrap by explanation)

| difference | mean | CI95 | frac > 0 |
|---|---|---|---|
| cos(h,AR(c)) − cos(h,AR(c*)) true − corrupt | 0.01454 | [0.01118,0.01841] | 0.727 |
| cos(h,AR(c)) − cos(h,AR(c~)) true − paraphrase | 0.03575 | [0.03068,0.04117] | 0.780 |
| paraphrase − corrupt | -0.02121 | [-0.02672,-0.01570] | 0.337 |
| true − corrupt_det (n=402) | 0.00993 | [0.00726,0.01287] | 0.657 |
| last claims only (n=147): true − corrupt | 0.00982 | [0.00666,0.01367] | 0.769 |
| last claims only: true − paraphrase | 0.02793 | [0.02124,0.03552] | 0.857 |

- mean cos alone: claim 0.6625, corrupt 0.6479, paraphrase 0.6267; errors 0

## Confidence / conflict probes vs next-token entropy (evaluation; Spearman, bootstrap by stimulus)

| statistic | pooled | punctuation | word_initial | word_piece |
|---|---|---|---|---|
| conf_vs_negentropy | +0.3554 [+0.2030,+0.4787] n=160 | +0.6983 [+0.3590,+0.8811] n=24 | +0.2227 [+0.0359,+0.4103] n=108 | +0.3733 [+0.0329,+0.6269] n=28 |
| conflict_vs_entropy | +0.1225 [-0.0387,+0.2829] n=160 | +0.6339 [+0.3014,+0.8160] n=24 | -0.0866 [-0.2748,+0.1027] n=108 | +0.2233 [-0.1773,+0.5704] n=28 |
| conf_vs_top1prob | +0.3205 [+0.1634,+0.4526] n=160 | +0.7183 [+0.3743,+0.8914] n=24 | +0.1943 [+0.0007,+0.3765] n=108 | +0.3618 [+0.0024,+0.6314] n=28 |
| cos_confident_vs_negentropy | +0.1485 [-0.0025,+0.2955] n=160 | +0.3278 [-0.0940,+0.6712] n=24 | +0.1068 [-0.0826,+0.3052] n=108 | +0.0837 [-0.3326,+0.4775] n=28 |
| cos_uncertain_vs_entropy | -0.1059 [-0.2548,+0.0404] n=160 | -0.2687 [-0.6341,+0.1554] n=24 | -0.0607 [-0.2639,+0.1289] n=108 | -0.0350 [-0.4193,+0.3764] n=28 |
| cos_own_expl_vs_negentropy | -0.0891 [-0.2619,+0.0968] n=160 | -0.4339 [-0.7277,+0.0154] n=24 | -0.0718 [-0.2663,+0.1374] n=108 | +0.0367 [-0.3615,+0.4173] n=28 |

| sentence | mean cos (eval) | sd |
|---|---|---|
| confident: The model is highly confident about the next token. | 0.2615 | 0.0836 |
| uncertain: The model is uncertain about the next token. | 0.2719 | 0.0836 |
| torn: The model is torn between two continuations. | 0.2234 | 0.0788 |
| clear: The model has one clear continuation in mind. | 0.2754 | 0.0829 |
| filler1: This is a sentence. | 0.3281 | 0.0768 |
| filler2: Text. | 0.3466 | 0.0831 |
| topic_true sentence | 0.3911 | 0.0854 |
| topic_foreign sentence | 0.3579 | 0.0872 |
| (S1) own full explanation | 0.8820 | 0.0439 |
| (S1) empty explanation | 0.3471 | 0.0813 |

- mean s_conf -0.01042 (sd 0.00859); mean s_conflict -0.05192 (sd 0.01588)

## Ten fixed rows (eval rows 0,16,…,144)

| stim | topic_true | topic_foreign | cos true | cos foreign | repe s | entropy | s_conf |
|---|---|---|---|---|---|---|---|
| 40 | Europium | The Litigators | 0.3798 | 0.2976 | +0.1025 | 1.453 | -0.0060 |
| 56 | Andrew Johnston (singer) | President Evil | 0.5191 | 0.4967 | +0.0059 | 0.005 | +0.0033 |
| 72 | No result, Pts | Blackburn Firecrest | 0.3820 | 0.4004 | -0.1111 | 4.831 | -0.0115 |
| 88 | Draining and development of the Everglades | Battle of Binh Gia | 0.5112 | 0.5474 | +0.3087 | 4.085 | -0.0186 |
| 104 | Martin Keamy | Pokiri | 0.3888 | 0.3818 | -0.0015 | 1.563 | -0.0078 |
| 120 | Chapter 1 (House of Cards) | Battle of Hubbardton | 0.2289 | 0.2612 | +0.1097 | 1.482 | -0.0011 |
| 136 | Hurricane Omar (2008) | Saint Leonard Catholic Church (Madison, Nebraska) | 0.5330 | 0.4517 | +0.0135 | 0.107 | -0.0103 |
| 152 | Ulysses (poem) | 766th Independent Infantry Regiment (North Korea) | 0.3318 | 0.3198 | -0.0600 | 0.268 | -0.0048 |
| 168 | Stop!! Hibari-kun! | Texas A & M Singing Cadets | 0.3303 | 0.3362 | -0.0426 | 3.283 | -0.0110 |
| 184 | Florida State Road 878 | Central Area Command (RAAF) | 0.2624 | 0.2451 | +0.0275 | 1.834 | -0.0074 |

