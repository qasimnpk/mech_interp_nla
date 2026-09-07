# T2a summary — audit of the round-3 topic readout + held-out wording p3 (AV forward only)

git 103a3c38; settings in t2a_settings.json; rows in t2a_scores.csv (200 stimuli; p3 own / foreign-swap / no-injection log-probs)

- AV forwards 999 (0.38 s each); errors 0; prompt 125 tokens, marker at 111
- p3 = `'<explanation>\nThe document is about'` (frozen in PLAN 2026-09-06 23:15; first run here); round-3 prefix = `'<explanation>\nThe passage concerns'`; candidates ' ' + detok(topic) in both
- token counts (' ' + topic): true mean 5.81, foreign mean 5.64

## Audit of the round-3 statistic (no model)

- [x] t2_prefix.py: no-injection candidate scored with PREFILL_CC and ' ' + topic (source)
- [x] t2_prefix.py: injected candidates scored with PREFILL_CC and ' ' + topic (source)
- [x] t2_prefix.py: cc_true_corr = cc_true − cc_true_noinj (source)
- [x] t2_scores.csv: cc_*_corr == cc_* − cc_*_noinj (max |dev| 1.42e-14)
- [x] foreign_stim_idx == (i+100) mod 200 for all 200 stimuli (t2_scores and t0_topics)
- [x] pairing is an involution (foreign of foreign = self): every title is exactly once a true and once a foreign candidate
- [x] multiset of true topics == multiset of foreign topics (200 rows)
- [x] evaluation rows whose foreign partner is also an evaluation row: 120/160 (pairs (i, i+100) with 40<=i<100 both in eval; 100<=i<140 partners 0-39 are pilot)
- [x] round-3 PLAN T2 stage text asks for a prior-corrected AUROC: False (it asks for the no-injection AUROC and mean yes−no under no injection) → prior-corrected AUROC 0.9347 is EXPLORATORY, not pre-registered

- **The prior-corrected AUROC (0.9347 in DISCONFIRMATION.md, reported there without a CI) was not pre-registered in the round-3 PLAN; it is exploratory.** Recomputed on the same 160 items with CI by document: 0.9347 [0.9111,0.9580]; raw 0.7516 [0.7017,0.7983]; no-injection 0.4880 [0.4315,0.5508]; swap prefers foreign 0.7749 [0.7295,0.8202]; swap prior-corrected 0.9361 [0.9131,0.9581]
- within-pair choice accuracy (own activation, eval, CI by document): raw 0.775 [0.706,0.838]; prior-corrected 0.950 [0.912,0.981]; swap (foreign activation prefers foreign topic) 0.787 [0.725,0.844]; swap prior-corrected 0.950 [0.919,0.981]; no injection 0.481 [0.406,0.562]

## Kill T2a — held-out prefix p3 (evaluation n=160, own activation, paired bootstrap by document)

- raw AUROC ' topic_true' vs ' topic_foreign': 0.7605 [0.7126,0.8059] → **NOT MET**
- per-token normalised: 0.7726 [0.7235,0.8196]
- no injection (prior only): 0.4862 [0.4295,0.5500]; per-token 0.5070 [0.4467,0.5613]
- prior-corrected (lp − lp_noinj): 0.9431 [0.9214,0.9643]
- swap control (foreign activation; AUROC that it prefers the foreign topic): 0.7857 [0.7402,0.8300]; prior-corrected 0.9428 [0.9207,0.9632]
- within-pair choice accuracy: raw 0.781 [0.719,0.844]; prior-corrected 0.944 [0.906,0.975]; swap 0.800 [0.744,0.856]; no injection 0.475 [0.400,0.556]
- pilot (n=40): raw 0.8144 [0.7268,0.9031]; prior-corrected 0.9506 [0.9056,0.9863]; swap 0.7150 [0.6125,0.8088]
- topic-absent subset (topic_true not in default explanation; n=154): raw 0.7569 [0.7088,0.8048]; prior-corrected 0.9397 [0.9154,0.9614]; no-injection 0.4736 [0.4139,0.5380]
- per-item agreement of raw choice between the two prefixes: 0.981; Spearman of the raw margins +0.991; of the prior-corrected margins +0.976

## Same-items comparison (160 evaluation stimuli, identical true/foreign labels; AUROC paired bootstrap by document; accuracy = fraction of items where the true topic wins)

| readout | AUROC [CI95] | within-pair accuracy [CI95] |
|---|---|---|
| AR probe `This text is about {topic}.` (T1) | 0.6125 [0.5887,0.6400] | 0.787 [0.719,0.850] |
| RepE class means, centred (T1) | 0.7405 [0.6825,0.7972] | 0.775 [0.706,0.844] |
| RepE difference direction s vs −s (T1) | 0.8128 [0.7402,0.8782] | 0.769 [0.700,0.838] |
| T2 `The passage concerns` raw (round 3) | 0.7516 [0.7017,0.7983] | 0.775 [0.706,0.838] |
| T2 `The passage concerns` prior-corrected (round 3; exploratory) | 0.9347 [0.9111,0.9580] | 0.950 [0.912,0.981] |
| T2 `The passage concerns` no injection (round 3) | 0.4880 [0.4315,0.5508] | 0.481 [0.406,0.562] |
| T2 `The passage concerns` swap, prefers foreign (round 3) | 0.7749 [0.7295,0.8202] | 0.787 [0.725,0.844] |
| p3 `The document is about` raw (held-out, this stage) | 0.7605 [0.7126,0.8059] | 0.781 [0.719,0.844] |
| p3 `The document is about` prior-corrected | 0.9431 [0.9214,0.9643] | 0.944 [0.906,0.975] |
| p3 `The document is about` no injection | 0.4862 [0.4295,0.5500] | 0.475 [0.400,0.556] |
| p3 `The document is about` swap, prefers foreign | 0.7857 [0.7402,0.8300] | 0.800 [0.744,0.856] |

## Ten fixed rows (eval rows 0,16,…,144)

| stim | topic_true | topic_foreign | p3 true | p3 foreign | p3 true noinj | p3 foreign noinj | p3 true swap | p3 foreign swap | T2 cc true | T2 cc foreign |
|---|---|---|---|---|---|---|---|---|---|---|
| 40 | Europium | The Litigators | -5.66 | -44.42 | -20.73 | -31.45 | -29.15 | -32.82 | -14.66 | -46.14 |
| 56 | Andrew Johnston (singer) | President Evil | -41.39 | -26.98 | -38.61 | -23.39 | -47.83 | -28.13 | -44.81 | -27.65 |
| 72 | No result, Pts | Blackburn Firecrest | -60.51 | -43.40 | -51.13 | -36.98 | -66.47 | -32.66 | -60.15 | -44.38 |
| 88 | Draining and development of the Everglades | Battle of Binh Gia | -38.27 | -41.40 | -52.70 | -32.76 | -51.16 | -33.85 | -41.00 | -44.39 |
| 104 | Martin Keamy | Pokiri | -34.24 | -36.41 | -39.48 | -28.05 | -43.85 | -32.35 | -35.86 | -37.78 |
| 120 | Chapter 1 (House of Cards) | Battle of Hubbardton | -34.92 | -45.69 | -33.62 | -26.22 | -46.89 | -25.64 | -36.56 | -45.46 |
| 136 | Hurricane Omar (2008) | Saint Leonard Catholic Church (Madison, Nebraska) | -28.96 | -65.87 | -29.03 | -57.92 | -49.49 | -62.13 | -32.29 | -70.31 |
| 152 | Ulysses (poem) | 766th Independent Infantry Regiment (North Korea) | -23.01 | -85.68 | -24.03 | -49.55 | -54.55 | -47.27 | -26.28 | -91.43 |
| 168 | Stop!! Hibari-kun! | Texas A & M Singing Cadets | -62.77 | -77.27 | -65.18 | -61.33 | -81.62 | -33.47 | -64.34 | -79.25 |
| 184 | Florida State Road 878 | Central Area Command (RAAF) | -34.60 | -56.16 | -38.80 | -51.55 | -55.47 | -34.87 | -36.88 | -58.79 |

