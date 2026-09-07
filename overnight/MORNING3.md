# MORNING3 — nightshift round 3, NLA project

Generated 2026-09-06T23:30:16 at git 7eaf62b. Numbers only; every kill-test outcome is the pre-registered three-way label. The human decides what they mean. Raw outputs: `overnight/c*_*.csv`, `overnight/t*_*.csv|.jsonl`, `out/*.npz`, per-stage settings in `overnight/<stage>_settings.json`, logs in `out/<stage>.log`. Round-1/2 files were read only.

## Kill-test log, round 3 (copied from DISCONFIRMATION.md)

- 2026-09-06T19:59:18  C1  C1  threshold=paired CI95 of [snippet deletion cost in z_rot − in z] ≤ −0.05  observed=mean diff=-0.02642 CI95=[-0.03215,-0.02126] n=160; cost in z (S2)=0.1253; cost in z_rot=0.0989; n_expl=160  NOT MET  MET would mean the final snippet loses most of its weight when moved to the front: dominance is positional, not content
- 2026-09-06T19:59:18  C1  C1-joined  threshold=same statistic with cost in z computed from the space-joined z (secondary, not a pre-registered kill)  observed=mean diff=-0.02553 CI95=[-0.03130,-0.02032] n=160; cost in z_joined=0.1244; n_expl=160  NOT MET  joined-text baseline removes the newline/space formatting difference between z and z_rot
- 2026-09-06T20:15:53  C2  C2  threshold=CI95 of mean four-way margin M (cluster by template) ≤ 0  observed=mean M=0.01877 CI95=[0.00982,0.03382] n=40 n_templates=10; frac M>0=1.000; mean cos(h_a,h_b)=0.9664; mean cos own=0.8894 cross=0.8800  NOT MET  MET would mean the score cannot tell which of two one-fact-different activations a description belongs to
- 2026-09-06T20:26:52  T1  T1  threshold=AUROC cos(h,AR(true topic)) vs cos(h,AR(foreign topic)), eval, CI95 by document ≤ 0.60  observed=AUROC=0.6125 CI95=[0.5887,0.6400] n=160; frac s_topic>0=0.787; mean cos true=0.3911 foreign=0.3579  INCONCLUSIVE  MET would mean text-specified topic probing through the AR fails for these wordings, this template and these positions
- 2026-09-06T20:26:55  T1  T1-claims  threshold=matched-claim contrast (reported, not a pre-registered kill): CI95 of mean[cos(h,AR(c)) − cos(h,AR(c*))] − mean[cos(h,AR(c)) − cos(h,AR(c~))]  observed=true−corrupt=0.01454 [0.01118,0.01841]; true−para=0.03575 [0.03068,0.04117]; para−corrupt=-0.02121 [-0.02672,-0.01570] n=490 n_expl=160; frac true>corrupt=0.727 true>para=0.780  MET  ≤0 would mean the claim-alone probe prefers the true claim over its one-fact corruption no more than over a paraphrase
- 2026-09-06T21:01:26  T2  T2  threshold=AUROC of candidate-continuation log-prob (' {topic_true}' vs ' {topic_foreign}' after '<explanation>\nThe passage concerns'), eval, CI95 by document ≤ 0.60  observed=AUROC=0.7516 CI95=[0.7017,0.7983] n=160; per-token 0.7479 [0.6961,0.7950]; no-injection 0.4880 [0.4315,0.5508]; prior-corrected 0.9347; swap prefers foreign 0.7749; topic-absent subset (n=154) 0.7482 [0.6993,0.7964]  NOT MET  MET would mean the prefilled-continuation readout cannot tell the document's own topic from a foreign one
- 2026-09-06T21:01:26  T2  T2-yesno  threshold=AUROC of yes−no logit for the true vs foreign topic question, eval, CI95 by document ≤ 0.60 (threshold-table wording; reported alongside)  observed=AUROC=0.5502 CI95=[0.5227,0.5777] n=160; no-injection 0.4969; mean yes−no under no injection: true-q +2.630 foreign-q +2.648 conf +2.438 torn +3.562  MET  a general preference for Yes or for the commoner noun is not evidence; compare with the no-injection AUROC
- 2026-09-06T21:01:26  T2  T2-claims  threshold=single-word claim corruptions (reported, not a pre-registered kill): CI95 of mean[(lp_orig − lp_corrupt) injected − same with no injection]  observed=LLM corrupt n=298 n_expl=147: injected 9.7822 [8.9749,10.5217], no-inj 1.3875, diff 8.3947 [7.4664,9.3455], frac orig>corrupt inj 0.973 noinj 0.638; det n=393: diff 11.6787 [10.6376,12.7097]  NOT MET  ≤0 would mean the injected activation does not raise the original word over its corruption beyond the prompt-only prior
- 2026-09-06T22:02:42  T4  T4  threshold=sports mention rate < 0.25 at both positive β (pilot, CI by stimulus)  observed=β=0.25: 1.000 [1.000,1.000] n=40 (above); β=0.5: 1.000 [1.000,1.000] n=40 (above); baseline unperturbed 0.125; random β=0.5 0.175  NOT MET  MET would mean a large injected concept direction does not surface in the description (readout not direction-additive)
- 2026-09-06T23:29:47  T3  T3  threshold=French pass rate < 0.25 at every (ℓ, α) with parse_ok ≥ 0.5 (pilot, french direction, CI by stimulus)  observed=L8 α=1: pass 0.057 [0.000,0.143] parse_ok 1.00 n=35; L8 α=2: pass 0.400 [0.229,0.571] parse_ok 0.00 n=35; L8 α=4: pass 0.000 [0.000,0.000] parse_ok 0.00 n=35; L14 α=1: pass 0.114 [0.029,0.229] parse_ok 0.00 n=35; L14 α=2: pass 0.171 [0.057,0.314] parse_ok 0.00 n=35; L14 α=4: pass 0.514 [0.343,0.686] parse_ok 0.00 n=35; eligible cells 1/6  MET  MET would mean the AV is not steerable by residual addition either, at doses that keep it fluent

| K | stage | outcome | pre-registered kill? |
|---|---|---|---|
| C1 | C1 | NOT MET | yes |
| C1-joined | C1 | NOT MET | no (reported alongside) |
| C2 | C2 | NOT MET | yes |
| T1 | T1 | INCONCLUSIVE | yes |
| T1-claims | T1 | MET | no (reported alongside) |
| T2 | T2 | NOT MET | yes |
| T2-yesno | T2 | MET | no (reported alongside) |
| T2-claims | T2 | NOT MET | no (reported alongside) |
| T4 | T4 | NOT MET | yes |
| T3 | T3 | MET | yes |

## Stage status and wall-clock

```
## Stage status
# Round 3 — see PLAN.md "Round 3 stages". EXECUTION ORDER: T0 → C1 → C2 → T1 → T2 → T4 → T5 → T3 → T6 (T3 last, dropped first). Hard stop 5 h.
T0  artifact check + topics + entropy .. DONE (t0_check.md; no kill test)
C1  position vs content (AR only) ....... DONE (NOT MET; c1_summary.md)
C2  matched one-fact activation pairs ... DONE (NOT MET; c2_summary.md)
T1  AR as zero-shot probe ............... DONE (INCONCLUSIVE; t1_summary.md)
T2  forced-prefix yes/no on AV .......... DONE (NOT MET; yes/no MET; t2_summary.md)
T4  injected-vector perturbation ........ DONE (NOT MET; t4_summary.md)
T5  steering specificity (OPTIONAL) ..... SKIPPED (STATE says T5: SKIP, not HUMAN-CONFIRMED)
T3  AV residual steering (last) ......... DONE (MET; 35/40 pilot stimuli, cut at stage cap; t3_summary.md)
T6  MORNING3.md ......................... RUNNING
```

First round-3 RUNLOG line: 2026-09-06T19:47:49; hard stop = that + 5 h; report generated 2026-09-06T23:30:16.

| stage | wall-clock (settings.json) |
|---|---|
| T0 | 2026-09-06T19:49:34 → 2026-09-06T19:54:24 |
| C1 | 2026-09-06T19:56:22 → 2026-09-06T19:59:18 |
| C2 | 2026-09-06T20:01:47 → 2026-09-06T20:15:54 |
| T1 | 2026-09-06T20:17:34 → 2026-09-06T20:26:55 |
| T2 | 2026-09-06T20:27:21 → 2026-09-06T21:01:26 |
| T4 | 2026-09-06T21:01:55 → 2026-09-06T22:02:42 |
| T3 | 2026-09-06T22:03:11 → 2026-09-06T23:29:47 |

RUNLOG (round 3):

```
2026-09-06T19:47:49  T0  start  round 3 begins; artifact check + topics + entropy sidecar; hard stop = 2026-09-06T19:47:49 + 5 h = 2026-09-07T00:47:49
2026-09-06T19:55:02  T0  done  counts OK (200/200/671/538/490), both npz caches present; t0_topics.csv 200 rows (199 unique, 0 doc collisions, topic_true in default explanation 6/200); t0_entropy.csv 200 rows 0 errors (eval mean entropy 1.411 nats, top1_prob 0.647); measured costs: AV 10.6 s/expl, AV fwd 0.28 s, AR 0.36 s/score (0.07 s short), TARGET 1.15 s/doc, 0.11 s/short; re-budget total 244 min (T3 111 min > 90-min cap, run stimulus-outer and cut at cap)
2026-09-06T19:55:02  C1  start  position vs content, AR only (160 eval explanations, ≥3 claims)
2026-09-06T20:00:05  C1  done  160 eval explanations (all >=3 claims), 800 AR forwards; C1 NOT MET (paired diff=-0.02642 CI [-0.03215,-0.02126]; snippet cost in z 0.1253, in z_rot 0.0989, in z_rev 0.1320; ratio 0.789); secondary joined baseline NOT MET
2026-09-06T20:00:05  C2  start  matched one-fact activation pairs: TARGET (80 contexts) -> AV (80 generations) -> AR
2026-09-06T20:17:28  C2  done  40 pairs / 10 templates, 80 AV generations (parse_ok 80/80, 9.9 s/gen), 200 AR forwards; C2 NOT MET (mean M=0.01877 CI [0.00982,0.03382], frac M>0 40/40, cos(h_a,h_b) 0.9664); own-entity mention 11/80, other 3/80
2026-09-06T20:17:28  T1  start  AR as zero-shot text probe: TARGET RepE (3200 short forwards) then AR (topic/probe/490 claims x3)
2026-09-06T20:27:13  T1  done  200 stimuli, 3200 RepE TARGET forwards + 2065 AR forwards; T1 INCONCLUSIVE (AUROC 0.6125 CI [0.5887,0.6400] straddles 0.60; RepE centred 0.7405 [0.6825,0.7972]); claims-alone: true−corrupt 0.01454 < true−para 0.03575 (para−corrupt −0.02121 CI [−0.02672,−0.01570], MET as reported-only line); Spearman(s_conf,−entropy) +0.355 [+0.203,+0.479]
2026-09-06T20:27:13  T2  start  forced-prefix readout, AV forward only (200 stimuli x yes/no + candidate continuation incl. swap and no-injection; single-word claim pairs)
2026-09-06T21:01:47  T2  done  200 stimuli + 691 single-word claim pairs, 5164 AV forwards, 0 errors; T2 NOT MET (candidate-continuation AUROC 0.7516 CI [0.7017,0.7983]; no-injection 0.4880; prior-corrected 0.9347; swap prefers foreign 0.7749); T2-yesno MET (0.5502 CI [0.5227,0.5777]); claims: injected lp_orig−lp_corrupt 9.78 vs no-inj 1.39, frac 0.973
2026-09-06T21:01:47  T4  start  injected-vector perturbation, pilot 0-39: TARGET directions (sports, french) then AV+AR co-resident, 9 cells x 40 = 360 generations (budget ~70 min, cap 85 min)
2026-09-06T22:03:04  T4  done  360 items (40 pilot x 9 cells), 0 errors, 10.0 s/item; T4 NOT MET (sports mention 1.000 at β=+0.25 and +0.5, baseline 0.125, random 0.175; french pass 0.725/0.950 at +0.25/+0.5); collateral: seq-sim to V0 0.44/0.31, cos(AR,h) −0.019/−0.144 vs V0
2026-09-06T22:03:04  T5  skipped  STATE.md carries 'T5: SKIP' (desk recommendation: superseded by the round-4 steering design), not 'T5: HUMAN-CONFIRMED'; no gate G5 run
2026-09-06T22:03:04  T3  start  AV residual steering, pilot 0-39: french/terse directions at blocks 8,14 x α 1,2,4 = 12 cells x 40 = 480 generations (budget 111 min > 85-min cap; stimulus-outer, cut at cap)
2026-09-06T23:30:16  T3  done  420 items (35 of 40 pilot stimuli x 12 cells; generation cut at the 85-min stage cap before stimulus 35), 0 errors, 12.3 s/item; T3 MET (eligible french cells with parse_ok>=0.5: 1/6 = L8 α=1, pass 0.057 CI [0.000,0.143]; α>=2 destroys the <explanation> format at both layers, French pass up to 0.514 at L14 α=4 with parse_ok 0)
2026-09-06T23:30:16  T6  start  MORNING3.md
```

Blockers:

## Blockers
(none)

## Topic readout AUROC table (evaluation stimuli 40–199, paired, bootstrap by document)

| readout | AUROC [CI95] | control |
|---|---|---|
| T1 AR probe cos(h, AR('This text is about {topic}.')) | 0.612 [0.589,0.640] | topic-absent subset 0.613 [0.588,0.641] |
| T1 RepE class means (TARGET L20, centred) | 0.741 [0.682,0.797] | uncentred 0.577 [0.559,0.602]; diff-direction s vs −s 0.813 [0.740,0.878] |
| T2 candidate continuation, summed log-prob | 0.752 [0.702,0.798] | no-injection 0.488 [0.432,0.551]; prior-corrected 0.935 [0.911,0.958]; swap prefers foreign 0.775 [0.729,0.820]; topic-absent subset 0.748 [0.699,0.796] |
| T2 candidate continuation, per-token | 0.748 [0.696,0.795] | no-injection 0.508 [0.450,0.564] |
| T2 yes/no logit difference | 0.550 [0.523,0.578] | no-injection 0.497 [0.430,0.565]; prior-corrected 0.561 [0.532,0.589]; swap prefers foreign 0.560 [0.533,0.591] |

## T0 — artifact check, topics, entropy sidecar, measured costs

## Artifact counts (expected / found)

- stimuli: expected 200, found 200
- explanations: expected 200, found 200
- claims: expected 671, found 671
- s3_edits: expected 538, found 538
- s3_edit_ok: expected 490, found 490
- out/acts_L20.npz: {'h20': [200, 3584], 'h19': [200, 3584], 'h21': [200, 3584], 'h20_pos2': [200, 3584], 'stim_idx': [200], 'doc_idx': [200], 'pos': [200], 'pos2': [200]}
- out/recon_L20.npz: {'pred': [200, 3584], 'pred_empty': [3584], 'stim_idx': [200]}

## Topics (t0_topics.csv)

- headings found: 200/200; unique topic_true: 199
- foreign pairing (i+100) mod 200: document collisions 0 (asserted)
- topic_true appears (case-insensitive) in the default explanation: all 6/200; eval 6/160
- topic_true word count: mean 3.97, max 21

## Entropy at pos (t0_entropy.csv; TARGET logits at pos, nats)

- rows OK: 200/200; errors: 0
- entropy all: mean 1.417 median 1.182 min 0.000 max 5.231
- entropy eval: mean 1.411 median 1.182
- top1_prob eval: mean 0.647 median 0.667
- top-1 matches actual next token: all 110/200; eval 86/160

| token_type | n (eval) | mean entropy | median entropy | mean top1_prob |
|---|---|---|---|---|
| punctuation | 24 | 1.728 | 1.645 | 0.589 |
| word_initial | 108 | 1.461 | 1.182 | 0.638 |
| word_piece | 28 | 0.947 | 0.774 | 0.733 |

## Re-budget from measured costs (item counts from PLAN.md stage specs)

| stage | items | est. compute (min) | + model loads (min) | PLAN estimate |
|---|---|---|---|---|
| C1 | 640 ar | 3.8 | 4.4 | ~10 |
| C2 | 80 target_short, 80 av_gen, 360 ar | 16.4 | 18.1 | ~40 |
| T1 | 1876 ar, 6400 target_short | 22.8 | 23.9 | ~10 |
| T2 | 3380 av_fwd | 16.0 | 16.5 | ~15 |
| T4 | 128 target_short, 360 av_gen, 720 ar | 67.9 | 69.7 | ~30 |
| T3 | 608 av_gen, 480 ar | 109.9 | 111.1 | ~45 |
| total | | | 244 | |

## C1 — position vs content (snippet moved to the front / order reversed), AR only, 160 eval explanations

- explanations: 160 (errors 0); AR forwards 800; 0.22 s/score
- snippet (last claim) is a 'Final token' claim in 141/160 explanations

## Kill C1

- paired diff [cost_snippet_in_z_rot − cost_snippet_in_z (S2)]: -0.02642 CI95=[-0.03215,-0.02126] n=160  threshold ≤ -0.05 → **NOT MET**
- secondary (joined baseline) [cost_snippet_in_z_rot − cost_snippet_in_z_joined]: -0.02553 CI95=[-0.03130,-0.02032] n=160 → NOT MET

## Reconstruction of the rearranged texts

| text | mean cos | CI95 |
|---|---|---|
| z (original, S2) | 0.8820 | [0.8753,0.8886] |
| z_joined (space-joined, S3) | 0.8811 | [0.8742,0.8881] |
| z_rot (snippet first) | 0.8556 | [0.8461,0.8648] |
| z_rev (reversed) | 0.8533 | [0.8446,0.8621] |
| z_rot − snippet (= rest) | 0.7567 | [0.7389,0.7734] |
| z_rot − new last claim | 0.8404 | [0.8323,0.8489] |
| z_rev − snippet | 0.7213 | [0.7016,0.7401] |

## Deletion costs (cos(text) − cos(text minus claim))

| quantity | mean | CI95 | median | frac > 0 |
|---|---|---|---|---|
| snippet in z (S2, −Δcos) | 0.1253 | [0.1087,0.1416] | 0.0882 | 0.988 |
| snippet in z_joined | 0.1244 | [0.1079,0.1410] | 0.0873 | 0.988 |
| snippet in z_rot (moved to front) | 0.0989 | [0.0835,0.1149] | 0.0611 | 0.925 |
| snippet in z_rev (first position) | 0.1320 | [0.1141,0.1495] | 0.0921 | 0.956 |
| claim[-2] in z (S2) | 0.0183 | [0.0158,0.0208] | 0.0145 | 0.956 |
| claim[-2] when last in z_rot | 0.0152 | [0.0092,0.0207] | 0.0176 | 0.838 |

## Paired differences

| difference | mean | CI95 | frac < 0 |
|---|---|---|---|
| snippet cost: z_rot − z (kill statistic) | -0.02642 | [-0.03215,-0.02126] | 0.944 |
| snippet cost: z_rot − z_joined | -0.02553 | [-0.03130,-0.02032] | 0.944 |
| snippet cost: z_rev − z | 0.00665 | [-0.00421,0.01917] | 0.519 |
| claim[-2] cost: when last (z_rot) − in z | -0.00310 | [-0.00882,0.00191] | 0.463 |

Ratio of mean snippet cost in z_rot to mean snippet cost in z (S2): 0.789; to z_joined: 0.795

## C2 — matched one-fact activation pairs (40 pairs, 10 templates), TARGET → AV → AR

- pairs: 40 (errors 0); templates 10; tokens per context 18–22; entity distance to end 11–17 tokens; shared suffix 10–16 tokens
- AV: parse_ok 80/80, cjk 0/80, errors 0; 9.9 s/gen
- identical descriptions within a pair: 0/40

## Kill C2

- mean M (four-way margin): 0.01877 CI95=[0.00982,0.03382] n=40, clusters=10 templates; threshold ≤ 0 → **NOT MET**
- fraction of pairs with M > 0: 1.000 (40/40)
- M_a = cos(h_a,d_a) − cos(h_a,d_b): 0.00926 CI95=[0.00364,0.01558] n=40; M_b = cos(h_b,d_b) − cos(h_b,d_a): 0.00951 CI95=[0.00243,0.01882] n=40

## Activation geometry

- cos(h_a, h_b): mean 0.9664 min 0.8215 max 0.9988; norms mean 111.5
- cos(AR(d_a), AR(d_b)): mean 0.9755

## Reconstruction scores

| quantity | mean | min | max |
|---|---|---|---|
| cos(h_a, AR(d_a)) own | 0.8883 | 0.7889 | 0.9490 |
| cos(h_b, AR(d_b)) own | 0.8904 | 0.7908 | 0.9487 |
| cos(h_a, AR(d_b)) cross | 0.8791 | 0.7742 | 0.9466 |
| cos(h_b, AR(d_a)) cross | 0.8809 | 0.7846 | 0.9350 |

## Text-edit control (entity swapped inside the description, same activation) vs activation edit

- swap available (entity string present in description): 12/80 descriptions
- cos(h, AR(d)) − cos(h, AR(d with entity swapped)): 0.00476 CI95=[-0.00006,0.00804] n=12
- per-side activation-edit margin cos(h_x,AR(d_x)) − cos(h_x,AR(d_y)) on all 80 sides: 0.00939 CI95=[0.00491,0.01691] n=80

## Entity mentions in the descriptions (80 descriptions)

- mentions own entity: 11/80; mentions other entity: 3/80; mentions neither: 66/80; both: 0/80

| template | own-mention rate | mean M | frac M>0 | mean cos(h_a,h_b) |
|---|---|---|---|---|
| 0 | 0.25 | 0.0109 | 1.00 | 0.9682 |
| 1 | 0.12 | 0.0112 | 1.00 | 0.9630 |
| 2 | 0.25 | 0.0074 | 1.00 | 0.9889 |
| 3 | 0.00 | 0.0097 | 1.00 | 0.9770 |
| 4 | 0.12 | 0.0143 | 1.00 | 0.9642 |
| 5 | 0.00 | 0.0155 | 1.00 | 0.9854 |
| 6 | 0.00 | 0.0197 | 1.00 | 0.9790 |
| 7 | 0.62 | 0.0837 | 1.00 | 0.8612 |
| 8 | 0.00 | 0.0074 | 1.00 | 0.9876 |
| 9 | 0.00 | 0.0079 | 1.00 | 0.9895 |

### pair 0 (template 0): Paris / Lyon; cos(h_a,h_b)=0.9643; M=0.0021
- context_a: The capital of the country is Paris. Tourists arrive at the main station and walk to the
- context_b: The capital of the country is Lyon. Tourists arrive at the main station and walk to the
- d_a (mentions own=True, other=False; cos own 0.8598, cross 0.8494): Formal mathematical/structural description pattern with a numbered sequence ("A train from Moscow to Paris with a probability"), implying a scenario about a tourist arriving at a metro station.

The phrase "A person leaves the train station with a random time to the Eiffel Tower and goes to the metro center" strongly implies a destination or attraction description, suggesting the sentence structure continues describing the route or destination's location.

Final token "the" is an article mid-noun phrase ("from the hotel to the"), directly continuing "a person goes from the metro to the," requiring a noun like "central station" or "hotel, or the clock tower" or "station, with a probability distribution."
- d_b (mentions own=False, other=False; cos own 0.8777, cross 0.8860): Formal mathematical/urban description format with a translated phrase ("A random walk in the city"), implying a puzzle or event context about a metro station.

The sentence structure "A person leaves from a random station in the center of the city and goes to the metro station, then decides whether to go to the" suggests a paired noun phrase describing destination or attraction location about the city's main square.

Final token "the" is an article mid-noun phrase ("from the hotel to the"), continuing the parallel structure "a random walk to the metro station and to the," strongly expecting a noun like "main square" or "hotel entrance" or "bus stop, with a certain probability."

## T1 — the reconstructor as a zero-shot text probe, with RepE baseline and matched-claim contrast

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

## T2 — forced-prefix readout from the verbalizer (AV forward only)

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

## T4 — perturbing the injected vector with TARGET concept directions (pilot 0–39)

- items 360 (errors 0); 10.0 s/item; stopped at stimulus None (None = all 40 done)
- direction geometry: ||d_sports|| 25.7, ||d_french|| 40.4, cos(d_sports, d_french) 0.007; cos(d, mean h20): sports 0.012, french -0.018
- prior art: LessWrong 'Models are blind outside the J-space. NLAs aren't.' (Llama-3.3-70B, L53 NLA, diff-of-means concept vectors injected norm-matched; NLA named the concept 100 %, n=16, 0 false positives). T4 is a replication/control on this 7B pair.

## Kill T4

β=0.25: sports mention 1.000 [1.000,1.000] (above); β=0.5: sports mention 1.000 [1.000,1.000] (above) → **NOT MET**
- baseline (unperturbed round-1 explanations, pilot): sports mention 0.125, french pass 0.000, topic preserved 0.025, mean words 99.7

## Grid (mean over pilot stimuli; CI by stimulus where shown)

| direction | β | n | cos(h,h') | angle° | sports mention [CI] | french pass | french frac | topic preserved | parse_ok | cjk | words | seq-sim V0 | Jaccard V0 | cos(AR,h) | cos(AR,h') | cos(AR,h) − cos V0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sports | -0.5 | 40 | 0.948 | 18.5 | 0.075 [0.000,0.175] | 0.000 | 0.076 | 0.050 | 1.000 | 0.000 | 98.8 | 0.461 | 0.395 | 0.8832 | 0.8453 | -0.0102 |
| sports | -0.25 | 40 | 0.981 | 11.3 | 0.100 [0.025,0.200] | 0.000 | 0.077 | 0.025 | 1.000 | 0.000 | 99.5 | 0.531 | 0.453 | 0.8882 | 0.8740 | -0.0052 |
| sports | +0.25 | 40 | 0.949 | 18.4 | 1.000 [1.000,1.000] | 0.025 | 0.074 | 0.025 | 1.000 | 0.025 | 100.0 | 0.444 | 0.366 | 0.8742 | 0.8411 | -0.0192 |
| sports | +0.5 | 40 | 0.710 | 44.8 | 1.000 [1.000,1.000] | 0.000 | 0.084 | 0.000 | 1.000 | 0.000 | 99.2 | 0.313 | 0.238 | 0.7497 | 0.6366 | -0.1437 |
| french | -0.5 | 40 | 0.949 | 18.4 | 0.200 [0.100,0.325] | 0.000 | 0.076 | 0.025 | 1.000 | 0.025 | 100.9 | 0.490 | 0.433 | 0.8886 | 0.8458 | -0.0047 |
| french | -0.25 | 40 | 0.981 | 11.3 | 0.175 [0.075,0.300] | 0.000 | 0.072 | 0.000 | 1.000 | 0.000 | 99.4 | 0.535 | 0.473 | 0.8906 | 0.8745 | -0.0028 |
| french | +0.25 | 40 | 0.948 | 18.5 | 0.150 [0.050,0.275] | 0.725 | 0.179 | 0.000 | 1.000 | 0.000 | 94.1 | 0.377 | 0.310 | 0.8207 | 0.8224 | -0.0727 |
| french | +0.5 | 40 | 0.704 | 45.3 | 0.150 [0.050,0.275] | 0.950 | 0.226 | 0.000 | 1.000 | 0.050 | 92.2 | 0.260 | 0.218 | 0.7653 | 0.6616 | -0.1280 |
| random | +0.5 | 40 | 0.707 | 45.0 | 0.175 [0.075,0.300] | 0.050 | 0.079 | 0.000 | 1.000 | 0.000 | 99.3 | 0.340 | 0.299 | 0.8435 | 0.6044 | -0.0499 |

## Sports keywords hit (positive β), counts over items

- β=0.25: sports:36, player:15, football:13, team:9, season:5, cricket:5, baseball:5, basketball:4, game:4, sport:4, athlete:4, rugby:3, score:3, athletic:3, soccer:3, tennis:3, matches:3, match:3, games:2, players:2, medal:2, olympic:2, tournament:2, touchdown:1, stadium:1, playoffs:1, hockey:1, scored:1, goal:1, captain:1, championship:1
- β=0.5: sports:38, player:36, score:17, team:16, football:15, goal:15, game:14, basketball:14, match:14, scored:12, hockey:8, soccer:7, goals:7, rugby:6, cricket:4, championship:4, sport:4, athlete:3, tennis:3, olympics:3, medal:3, tournament:3, touchdown:2, penalty:2, league:2, teams:1, season:1, matches:1, arena:1, stadium:1, athletic:1, boxing:1, games:1, olympic:1, sprinter:1, wickets:1, sprint:1
- random β=0.5: player:4, baseball:3, score:2, athlete:2, football:2, goals:1, athletic:1, basketball:1, sports:1, game:1, games:1, medal:1, olympic:1, cricket:1

### stim 0 — topic Tropical Storm Brenda (1960)

**unperturbed (round 1):**
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods and storm intensity details.

The final sentence "The fourth storm surge moved inland along the Florida Panhandle, with a second landfall occurring near Cape Hatteras" mirrors earlier landfall descriptions, completing a list of four landfall locations and likely a final one.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event sequence listing multiple landfall points ("The system also made a second landfall..."), expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
```
**sports β=+0.5** (cos(h,h')=0.726, sports=True, french_frac=0.10, cos(AR,h)=0.613, seq-sim=0.25):
```
Sports statistics article format with NFL game log structure, detailing player performance metrics for the USA team during a record-breaking heat wave.

The final sentence "His third game of the night saw the Heat registering a second touchdown and a late comeback win, before finishing with a touchdown" lists two final touchdown events, completing a sequence of US soccer's final scoring moments including a beach touchdown.

Final token "touchdown" ends an incomplete clause ("a second touchdown tallied a beach touchdown and a re-touching"), strongly expecting "in the Bahamas" or "at the Dallas Mavericks" or "with a score of 89-88" — a specific ending location or score detail.
```
**french β=+0.5** (cos(h,h')=0.695, sports=False, french_frac=0.28, cos(AR,h)=0.754, seq-sim=0.17):
```
French meteorological report format with numbered stages describing Atlantic storm tracks, detailing successive landfalls along the French coast.

The sentence structure "La troisième phase de la traversée a ensuite quitté la Manche par la côte sud, avant une seconde arrivée... La troisième traversée a également touché la côte française" mirrors a list of landfall dates, completing a fourth.

Final token "landfallLa" is mid-phrase ("une nouvelle arrivée se produisait et une nouvelle landfall touchait"), expecting "à Saint-Malo" or "en Normandie le 15 octobre" to close the final landfall.
```

## T5 — steering specificity (OPTIONAL)

Skipped: STATE.md carries `T5: SKIP`, not `T5: HUMAN-CONFIRMED`. Gate G5 was not run.

## T3 — residual-stream steering of the verbalizer (pilot 0–39; last stage, cut at the stage cap)

- items 420 (errors 0); 12.3 s/item; stopped at stimulus 35 (None = all 40 done); prompt 125 tokens, marker at 111
- directions: french_L8 ||d||=17.5, mean||h||=50.1, french_L14 ||d||=20.7, mean||h||=65.2, terse_L8 ||d||=38.1, mean||h||=53.4, terse_L14 ||d||=49.2, mean||h||=69.0
- baseline (round-1 explanations, pilot): french pass 0.000, mean words 99.7, topic preserved 0.025

## Kill T3

- eligible french cells (parse_ok ≥ 0.5): 1; outcome → **MET**

## Grid

| direction | ℓ | α | n | parse_ok | French pass [CI] | French frac | words | cjk | topic preserved | seq-sim V0 | Jaccard V0 | mean cos(AR,h) | mean Δcos vs V0 | median Δcos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| french | 8 | 1 | 35 | 1.000 | 0.057 [0.000,0.143] | 0.083 | 90.0 | 0.029 | 0.057 | 0.391 | 0.364 | 0.8840 | -0.0094 | -0.0072 |
| french | 8 | 2 | 35 | 0.000 | 0.400 [0.229,0.571] | 0.243 | 59.1 | 0.000 | 0.000 | 0.028 | 0.024 | 0.2830 | -0.6103 | -0.6167 |
| french | 8 | 4 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 1.0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.1389 | -0.7544 | -0.7699 |
| french | 14 | 1 | 35 | 0.000 | 0.114 [0.029,0.229] | 0.094 | 101.9 | 0.000 | 0.000 | 0.240 | 0.250 | 0.7751 | -0.1183 | -0.0702 |
| french | 14 | 2 | 35 | 0.000 | 0.171 [0.057,0.314] | 0.056 | 149.8 | 0.257 | 0.000 | 0.070 | 0.059 | 0.2955 | -0.5979 | -0.5977 |
| french | 14 | 4 | 35 | 0.000 | 0.514 [0.343,0.686] | 0.514 | 22.6 | 0.971 | 0.000 | 0.000 | 0.000 | 0.1979 | -0.6955 | -0.7079 |
| terse | 8 | 1 | 35 | 1.000 | 0.000 [0.000,0.000] | 0.067 | 114.0 | 0.000 | 0.029 | 0.230 | 0.281 | 0.8536 | -0.0398 | -0.0276 |
| terse | 8 | 2 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 101.5 | 0.000 | 0.000 | 0.002 | 0.002 | 0.2404 | -0.6530 | -0.6601 |
| terse | 8 | 4 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 200.0 | 0.000 | 0.000 | 0.000 | 0.011 | 0.2162 | -0.6772 | -0.6800 |
| terse | 14 | 1 | 35 | 0.000 | 0.029 [0.000,0.086] | 0.008 | 113.1 | 0.000 | 0.000 | 0.024 | 0.021 | 0.2626 | -0.6308 | -0.6421 |
| terse | 14 | 2 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 141.8 | 0.000 | 0.000 | 0.031 | 0.015 | 0.2445 | -0.6489 | -0.6513 |
| terse | 14 | 4 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 200.0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.2269 | -0.6664 | -0.6734 |

### stim 0 — topic Tropical Storm Brenda (1960)

**V0 (round 1):**
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods and storm intensity details.

The final sentence "The fourth storm surge moved inland along the Florida Panhandle, with a second landfall occurring near Cape Hatteras" mirrors earlier landfall descriptions, completing a list of four landfall locations and likely a final one.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event sequence listing multiple landfall points ("The system also made a second landfall..."), expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
```
**steered ('french', 8, 1.0)** (parse_ok=True, french_frac=0.05, words=90, cos(AR,h)=0.896):
```
Meteorological report structure with numbered storm tracks detailing Hurricane Sandy's path, presenting sequential storm data with precise numerical details and storm surge measurements.

The sentence ending "The storm then made a second inland landfall and a second tropical landfall" continues listing storm events, completing the final landfall sequence with a third landfall location and its timing.

Final token "landfall" ends an incomplete clause ("made a second touchdown"), expecting continuation describing the third landfall's location or outcome, likely "in the Gulf of Mexico near Cape Hatteras" or "on the eastern coast."
```

## FOLLOWUPS.md (queued for the human, not acted on)

- S3 statistic A_i = Δ_i(z*) − Δ_i(z) equals cos(z) − cos(z*) by construction (z* minus c_i* is the same text as z minus c_i), so the primary and the first secondary statistic coincide; both are reported as pre-registered.
- Stage scripts create their Settings file at module import; importing one stage from another (S3 imports S2's splitter) or re-running with --summary overwrites the finished stage's settings JSON. Move Settings creation under main() next round.

## OPEN DECISIONS (from STATE.md)

## Open decisions (research calls left for the human)
(none)

## Provenance

**Pre-registered by the human (PLAN.md round 3):** the stage list and execution order (T0 → C1 → C2 → T1 → T2 → T4 → T5 → T3 → T6), the T5 gate line, the pilot/eval split, every kill statistic and threshold in the round-3 threshold table, the three-outcome rule, the cluster-bootstrap rule (by explanation, by document, by template as each stage says; 1000 draws, seed 0), the probe sentences and questions (T1, T2 verbatim), the prefill strings, the C2 template design constraints (10 × 4, entity 8–20 tokens from the end, ≥ 6 shared final tokens, equal length), the direction recipes (difference of means; T3 layers 8/14 and α 1/2/4; T4 β grid and random direction), the collateral measures, the stage cap and the 5 h hard stop.

**Written by the agent:** `t0_check.py`, `c1_position.py`, `c2_matched.py`, `t1_arprobe.py`, `t2_prefix.py`, `t3_avsteer.py`, `t4_inject.py`, `t34_sentences.py` (the fixed sentence lists), `t6_morning.py`, this file. `nla_lib.py` and all round-1/2 files were reused unchanged.

**Choices the agent had to make (none changes a pre-registered statistic; each is logged in the stage's settings.json):**
- T0: `topic_true` is the raw wikitext heading; a detokeniser (`' ( 1960 )'` → `'(1960)'`, `' @-@ '` → `'-'`, space before punctuation removed) is applied only when the topic is inserted into a probe sentence or matched against text; the raw string is kept in every CSV. The per-doc TARGET timing in T0 was taken without an MPS sync and is annotated; the wall-clock number (1.15 s/doc) was used for the re-budget.
- C1: the snippet is the last S2 claim; its deletion cost in z is the pre-registered S2 value (−Δcos); a space-joined baseline is reported as a secondary line because z_rot is space-joined while z has newlines.
- C2: entity pairs are template-specific (the plan's '10 templates × 4 pairs'); six pairs were replaced before any model ran so that both contexts tokenise to the same length. The cross-text swap control is only defined where the entity string occurs in the description (12/80). Bootstrap clusters = the 10 templates.
- T1: the RepE 'agent-written sentences' are 16 fixed templates filled with the topic (200 topics × 16). The RepE AUROC is defined in parallel to the AR probe (positives cos(h, μ_true − μ̄), negatives cos(h, μ_foreign − μ̄), μ̄ = grand mean of the 200 topic means); the uncentred and difference-direction versions are reported too. cos is invariant to the plan's normalisation u(d). The matched-claim contrast is logged as a non-kill line.
- T2: the kill statistic follows the stage text (candidate-continuation log-prob); the threshold table's 'yes−no' wording is logged as a second line. Prefill and candidate are tokenised separately and concatenated. 'Single-word corruption' = equal word count and exactly one differing whitespace token (298 of 490 LLM corruptions, 393 of 402 deterministic). A prior-corrected AUROC (log-prob minus its no-injection value) is reported as a secondary number.
- T4: the random direction is drawn per stimulus (seed 1000 + stim_idx). Sports mention = whole-word match against a fixed keyword list (in settings). The three-way rule uses per-β bootstrap CIs (below / above / straddles). The LessWrong prior-art post named in the plan was fetched and is summarised in the T4 summary.
- T3: 'mean‖h_ℓ‖' = mean last-token norm over the 64 direction sentences at block ℓ. Steering is applied at the final prompt position in the prefill pass and at every decode position; the injected marker row and earlier prompt positions are untouched. Cells with parse_ok < 0.5 are ineligible for the kill; the outcome uses per-cell CIs. The loop is stimulus-outer and stops at 85 min so every cell has the same n.
- Settings files are created inside `main()`; `FRENCH` (S5 stoplist) is vendored into `t34_sentences.py` rather than imported from `s5_steer.py`, which would rewrite S5's settings file.

