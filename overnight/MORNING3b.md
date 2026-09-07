# MORNING3b — nightshift round 3b, NLA project

Generated 2026-09-07T00:42:46 at git ed7eb15. Numbers only; every kill-test outcome is the pre-registered three-way label. The human decides what they mean. Raw outputs: `overnight/t2c_pairs.csv`, `overnight/t2a_scores.csv`, `overnight/t2b_claims.csv`, `overnight/t2b_support_sheet.csv` (human fills `label_supported`), `overnight/c3_cells.csv`, `overnight/c3_descriptions.jsonl`, `out/c3_acts.npz`; per-stage settings in `overnight/<stage>_settings.json`; logs in `out/<stage>.log`. Round-1/2/3 files were read only.

## Kill-test log, round 3b (copied from DISCONFIRMATION.md)

- 2026-09-06T23:55:17  T2c  T2c  threshold=CI95 (cluster bootstrap by template) of mean [D(h_a) − D(h_b)] under p1 '<explanation>\nThe {noun} mentioned in the passage is', D = lp(' e_a') − lp(' e_b'), ≤ 0  observed=mean donor sensitivity=1.7379 [0.6272,3.2762] n=40 n_templates=10; frac>0=0.775; both-correct raw 0.225 prior-centred 0.150; choice accuracy raw 0.600 [0.525,0.688] centred 0.562 [0.487,0.650] (80 activations); paired AUROC D(h_a) vs D(h_b) 0.6516 [0.5666,0.7475] by template; prior D(h_0)>0 frac 0.625; p2 donor 1.8342 [0.7561,3.0039] both-correct raw 0.175  NOT MET  MET would mean the upstream entity is not readable from the final-token activation by forced prefix
- 2026-09-07T00:03:49  T2a  T2a  threshold=raw AUROC of held-out prefix p3 '<explanation>\nThe document is about' candidate continuation (' topic_true' vs ' topic_foreign'), own activation, eval, CI95 by document ≤ 0.60  observed=AUROC=0.7605 [0.7126,0.8059] n=160; per-token 0.7726 [0.7235,0.8196]; no-injection 0.4862 [0.4295,0.5500]; prior-corrected 0.9431 [0.9214,0.9643]; swap prefers foreign 0.7857 [0.7402,0.8300]; within-pair acc raw 0.781 [0.719,0.844] prior-corrected 0.944 [0.906,0.975] swap 0.800 [0.744,0.856]; pilot raw 0.8144 [0.7268,0.9031] n=40; round-3 PREFILL_CC on the same 160: raw 0.7516 [0.7017,0.7983] prior-corrected 0.9347 [0.9111,0.9580] (prior-corrected NOT pre-registered in round 3)  NOT MET  MET would mean the round-3 topic readout does not hold up on a held-out wording
- 2026-09-07T00:24:13  T2b  T2b  threshold=CI95 (cluster by explanation) of mean (d_own − d_pos2), d = lp_orig − lp_corrupt after the AV's own claim prefix, near donor = same document other position, all 691 single-word rows ≤ 0 (activation-dependence test, not a truth test)  observed=mean d_own−d_pos2=7.3473 [6.5589,8.1413] n=691 n_expl=159; d_own 12.9881 d_pos2 5.6408 d_foreign 2.8794 d_noinj 2.7256; frac d>0 own 0.973 pos2 0.792 foreign 0.645 noinj 0.712; d_own−d_foreign 10.1087 [9.2084,10.9556]; LLM (n=298) own−pos2 6.1652 [5.2560,7.1314]; det (n=393) 8.2436 [7.1885,9.3605]; in_ctx=True (n=192) 11.6013 [9.6341,14.0105], in_ctx=False (n=499) 5.7105 [5.1074,6.2641]  NOT MET  MET would mean the preference for the original word does not depend on which activation of the same document is injected: self-consistency, not readout
- 2026-09-07T00:42:16  C3  C3-score  threshold=CI95 (cluster by template) of mean [mean(M_fact(w1), M_fact(w2)) − mean(M_wording(a), M_wording(b))] ≤ 0  observed=mean diff=0.00782 [-0.00348,0.02407] n=40 n_templates=10 (with file M_fact(w1): 0.00782 [-0.00348,0.02407]); M_fact(w1) 0.01877 M_fact(w2) 0.01632 M_wording(a) 0.00965 M_wording(b) 0.00980; frac cells fact>wording 0.625; activation distance (1−cos): fact edit 0.03238 wording edit 0.02353 diff 0.00884 [-0.00948,0.03447]; dropped templates []  INCONCLUSIVE  MET would mean the reconstruction score discriminates a one-word phrasing change as well as a one-word fact change
- 2026-09-07T00:42:16  C3  C3-readout  threshold=CI95 (cluster by template) of mean [D(h_C) − D(h_D)] under p1 (the T2c entity readout at the rephrased contexts) ≤ 0  observed=mean donor sensitivity at w2=1.7723 [0.7183,3.2194] n=40 n_templates=10; at w1 (T2c contexts, re-scored) 1.7379 [0.6272,3.2762]; frac>0 w2 0.875; both-correct w2 0.200 w1 0.225; 2×2: entity main effect 1.7551 [0.6800,3.2433] wording main effect -0.0159 [-0.1922,0.1525] interaction -0.0172 [-0.1051,0.0686]  NOT MET  MET would mean the T2c entity preference does not survive a meaning-preserving phrasing change (only meaningful if T2c was NOT MET)

| K | stage | outcome | pre-registered kill? |
|---|---|---|---|
| T2c | T2c | NOT MET | yes |
| T2a | T2a | NOT MET | yes |
| T2b | T2b | NOT MET | yes |
| C3-score | C3 | INCONCLUSIVE | yes |
| C3-readout | C3 | NOT MET | yes |

## Stage status and wall-clock

```
## Stage status
# Round 3b — see PLAN.md "Round 3b stages". EXECUTION ORDER: U0 → T2c → T2a → T2b → C3 → T7 (C3 last, dropped first). Hard stop 2.5 h. Stage cap 45 min.
U0   artifact check + T3 closeout ............ DONE (18/18 checks; T3 closeout 420 items/35 stimuli, cap; u0_check.md)
T2c  entity readout on C2 pairs (PRIMARY) .... DONE — NOT MET (donor sens. 1.738 CI [0.627,3.276]; both-correct raw 0.225; t2c_summary.md)
T2a  topic-readout audit + held-out prefix ... DONE — NOT MET (p3 raw AUROC 0.7605 CI [0.7126,0.8059]; prior-corrected 0.9431; audit 9/9; t2a_summary.md)
T2b  claim-readout donor control ............. DONE — NOT MET (d_own−d_pos2 7.347 CI [6.559,8.141]; t2b_summary.md; support sheet awaiting human labels)
C3   phrasing control for C2 (factorial) ..... DONE — score INCONCLUSIVE (0.00782 CI [-0.00348,0.02407]); readout NOT MET (1.772 CI [0.718,3.219]); c3_summary.md
T7   MORNING3b.md ............................ DONE (MORNING3b.md; loop stops)
```

First round-3b RUNLOG line: 2026-09-06T23:49:14; hard stop = that + 2.5 h; stage cap 45 min; report generated 2026-09-07T00:42:46.

| stage | wall-clock (settings.json) |
|---|---|
| U0 | 2026-09-06T23:50:23 → 2026-09-06T23:50:23 |
| T2C | 2026-09-06T23:52:07 → 2026-09-06T23:55:17 |
| T2A | 2026-09-06T23:57:19 → 2026-09-07T00:03:49 |
| T2B | 2026-09-07T00:05:45 → 2026-09-07T00:24:13 |
| C3 | 2026-09-07T00:25:43 → 2026-09-07T00:42:16 |

RUNLOG (round 3b):

```
2026-09-06T23:49:14  U0  start  round 3b begins; artifact check + T3 closeout; hard stop = 2026-09-06T23:49:14 + 2.5 h = 2026-09-07T02:19:14
2026-09-06T23:50:35  U0  done  18/18 artifact checks OK (c2_pairs 40, t2_scores 200, t2_claims 691 single-word non-error = 298 LLM + 393 det, t0_topics 200, acts_L20 [200,3584] x2, c2_acts [40,2,3584]); T3 closeout: 420 items = 35 pilot stimuli x 12 cells, cut at the 5100 s cap, kill line MET as written; re-budget 44 min compute
2026-09-06T23:50:35  T2c  start  forced-prefix entity readout on the 40 C2 pairs, AV forward only; p1 kill, p2 confirmation
2026-09-06T23:55:31  T2c  done  40 pairs, 480 AV forwards (0.38 s), 0 errors; T2c NOT MET (mean D(h_a)−D(h_b) under p1 = 1.7379 CI [0.6272,3.2762], frac>0 0.775; both-correct raw 0.225, prior-centred 0.150; choice accuracy raw 0.600 [0.525,0.688]; AUROC 0.6516; p2 donor 1.8342 [0.7561,3.0039])
2026-09-06T23:55:31  T2a  start  audit of round-3 topic readout (no model) + held-out prefix p3 on 200 stimuli (own / foreign / no-injection), AV forward only
2026-09-07T00:04:12  T2a  done  audit 9/9 checks OK (prior-corrected AUROC not pre-registered in round 3; recomputed 0.9347 CI [0.9111,0.9580]); p3 held-out prefix: 999 AV forwards (0.38 s), 0 errors; T2a NOT MET (p3 raw AUROC eval 0.7605 CI [0.7126,0.8059]; no-inj 0.4862; prior-corrected 0.9431 [0.9214,0.9643]; swap 0.7857; acc raw 0.781 corr 0.944)
2026-09-07T00:04:12  T2b  start  activation-dependence control for the round-3 claim-word readout: 691 single-word rows x 2 words x 2 donors (h_pos2, h_foreign), AV forward only; support sheet for the human
2026-09-07T00:24:36  T2b  done  691 rows (298 LLM + 393 det), 2764 AV forwards (0.40 s), 0 errors, prefixes asserted against the file; T2b NOT MET (mean d_own−d_pos2 = 7.3473 CI [6.5589,8.1413], n_expl 159; d_own 12.99 d_pos2 5.64 d_foreign 2.88 d_noinj 2.73; frac d>0 own 0.973 pos2 0.792 foreign 0.645 noinj 0.712; in_ctx True n=192 11.60, False n=499 5.71); t2b_support_sheet.csv 30 rows, label_supported empty
2026-09-07T00:24:36  C3  start  phrasing control for C2, factorial: 40 cells x (C, D) new contexts; TARGET (160 fwd) -> AV (80 gens) -> AV+AR (640 AR scores + 320 AV readout forwards); all 10 primary wording pairs preserve token count (tokenizer dry-run)
2026-09-07T00:25:41  C3  crashfix  iteration 1 crashed before any model output (KeyError 'cos_ha_hb': build_pairs does not carry it; C2's main adds it later); now read from c2_pairs.csv; no statistic changed; rerun (out/c3_iter1_crash.log)
2026-09-07T00:42:46  C3  done  40 cells / 10 templates (all primary wording pairs), 160 TARGET fwd, 80 AV gens (parse_ok 80/80, 9.8 s), 160 AR scores, 320 AV readout fwd, 0 errors; C3-score INCONCLUSIVE (fact−wording 0.00782 CI [-0.00348,0.02407]; M_fact 0.0188/0.0163, M_wording 0.0097/0.0098; activation distance fact 0.0324 vs wording 0.0235); C3-readout NOT MET (D(h_C)−D(h_D) 1.7723 CI [0.7183,3.2194]; wording main effect −0.016 [−0.192,0.153]); one pre-model crash fix logged above
2026-09-07T00:42:46  T7  start  MORNING3b.md
```

Blockers:

## Blockers
(none)

## T2c — forced-prefix entity readout on the 40 C2 matched activation pairs (PRIMARY; AV forward only)

- pairs 40 (errors 0); templates 10; AV forwards 480 (0.38 s each); prompt 125 tokens, marker at 111
- prefixes: p1 = `<explanation>
The {noun} mentioned in the passage is`; p2 = `<explanation>
The passage mentions the {noun}`; nouns by template = ['city', 'ingredient', 'time', 'instrument', 'metal', 'city', 'illness', 'profession', 'animal', 'subject']
- candidate token counts (' ' + entity): a: {1: np.int64(40)}, b: {1: np.int64(40)}
- what each number is: *donor sensitivity* = activation dependence (prior cancels); *prior-centred* subtracts D(h_0), the no-injection prompt-only preference; nothing in any prefix or candidate was generated by the AV

## Kill T2c (p1, summed log-prob)

- mean [D(h_a) − D(h_b)]: 1.7379 [0.6272,3.2762] n=40 clusters=10 templates; threshold ≤ 0 → **NOT MET**

## All statistics, both prefixes, summed and per-token-normalised (CIs: cluster bootstrap by template; AUROC CI by template and by pair)

| prefix | norm | 1. donor sens. mean [CI] | frac>0 | 2. raw both-correct | raw D(h_a)>0 | raw D(h_b)<0 | 3. centred both-correct | centred a | centred b | 4. choice acc raw (80) | choice acc centred (80) | 5. AUROC D(h_a) vs D(h_b) [tpl CI] [pair CI] | mean D(h_a) | mean D(h_b) | mean D(h_0) | frac D(h_0)>0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| p1 | summed | 1.7379 [0.6272,3.2762] | 0.775 | 0.225 [0.050,0.425] | 0.625 | 0.575 | 0.150 [0.025,0.300] | 0.575 | 0.550 | 0.600 [0.525,0.688] | 0.562 [0.487,0.650] | 0.6516 [0.5666,0.7475] [0.5941,0.7347] | 1.281 | -0.457 | 0.524 | 0.625 |
| p1 | per-token | 1.7379 [0.6272,3.2762] | 0.775 | 0.225 [0.050,0.425] | 0.625 | 0.575 | 0.150 [0.025,0.300] | 0.575 | 0.550 | 0.600 [0.525,0.688] | 0.562 [0.487,0.650] | 0.6516 [0.5666,0.7475] [0.5941,0.7347] | 1.281 | -0.457 | 0.524 | 0.625 |
| p2 | summed | 1.8342 [0.7561,3.0039] | 0.775 | 0.175 [0.050,0.300] | 0.725 | 0.450 | 0.225 [0.050,0.425] | 0.675 | 0.550 | 0.588 [0.525,0.650] | 0.613 [0.525,0.713] | 0.6491 [0.5694,0.7285] [0.5984,0.7209] | 1.956 | 0.121 | 0.563 | 0.525 |
| p2 | per-token | 1.8342 [0.7561,3.0039] | 0.775 | 0.175 [0.050,0.300] | 0.725 | 0.450 | 0.225 [0.050,0.425] | 0.675 | 0.550 | 0.588 [0.525,0.650] | 0.613 [0.525,0.713] | 0.6491 [0.5694,0.7285] [0.5984,0.7209] | 1.956 | 0.121 | 0.563 | 0.525 |

## 6. Per-template table (p1 summed; own-entity mention rate from C2 descriptions)

| template | noun | n pairs | mean donor sens. p1 | frac>0 | both-correct raw p1 | both-correct centred p1 | mean donor sens. p2 | both-correct raw p2 | own-entity mention rate (C2) | mean C2 M | mean cos(h_a,h_b) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | city | 4 | 1.2227 | 1.00 | 0.25 | 0.00 | 2.0352 | 0.00 | 0.25 | 0.0109 | 0.9682 |
| 1 | ingredient | 4 | 1.8535 | 1.00 | 0.50 | 0.25 | 2.7891 | 0.50 | 0.12 | 0.0112 | 0.9630 |
| 2 | time | 4 | 0.5781 | 0.25 | 0.00 | 0.25 | 0.3613 | 0.00 | 0.25 | 0.0074 | 0.9889 |
| 3 | instrument | 4 | -0.0288 | 0.50 | 0.00 | 0.00 | -0.1369 | 0.00 | 0.00 | 0.0097 | 0.9770 |
| 4 | metal | 4 | 0.4042 | 0.50 | 0.00 | 0.00 | 0.9570 | 0.25 | 0.12 | 0.0143 | 0.9642 |
| 5 | city | 4 | 7.3590 | 1.00 | 0.75 | 0.75 | 5.5745 | 0.50 | 0.00 | 0.0155 | 0.9854 |
| 6 | illness | 4 | 1.1445 | 1.00 | 0.00 | 0.00 | 1.4336 | 0.25 | 0.00 | 0.0197 | 0.9790 |
| 7 | profession | 4 | 3.7290 | 0.75 | 0.75 | 0.25 | 4.7168 | 0.25 | 0.62 | 0.0837 | 0.8612 |
| 8 | animal | 4 | 0.2070 | 0.75 | 0.00 | 0.00 | -0.0059 | 0.00 | 0.00 | 0.0074 | 0.9876 |
| 9 | subject | 4 | 0.9102 | 1.00 | 0.00 | 0.00 | 0.6172 | 0.00 | 0.00 | 0.0079 | 0.9895 |

## Full 40-row table — p1 = `<explanation>
The {noun} mentioned in the passage is` (summed log-probs)

| pair | tpl | e_a | e_b | n_tok a/b | lp(a|h_a) | lp(b|h_a) | lp(a|h_b) | lp(b|h_b) | lp(a|h_0) | lp(b|h_0) | D(h_a) | D(h_b) | D(h_0) | donor | D(h_a)−D(h_0) | D(h_b)−D(h_0) | own-mention a/b (C2) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | Paris | Lyon | 1/1 | -6.68 | -17.86 | -8.72 | -17.44 | -15.68 | -19.82 | +11.17 | +8.72 | +4.14 | +2.45 | +7.03 | +4.58 | True/False |
| 1 | 0 | Rome | Milan | 1/1 | -8.13 | -11.38 | -7.50 | -10.50 | -14.51 | -17.47 | +3.25 | +3.00 | +2.95 | +0.25 | +0.30 | +0.05 | False/False |
| 2 | 0 | Madrid | Lisbon | 1/1 | -8.57 | -9.51 | -8.42 | -7.98 | -19.09 | -17.91 | +0.94 | -0.44 | -1.18 | +1.38 | +2.12 | +0.74 | True/False |
| 3 | 0 | Berlin | Munich | 1/1 | -6.38 | -10.57 | -7.06 | -10.44 | -14.39 | -15.86 | +4.19 | +3.38 | +1.47 | +0.81 | +2.72 | +1.91 | False/False |
| 4 | 1 | flour | sugar | 1/1 | -17.48 | -15.02 | -17.93 | -14.40 | -19.19 | -18.22 | -2.47 | -3.53 | -0.97 | +1.06 | -1.50 | -2.56 | False/False |
| 5 | 1 | rice | milk | 1/1 | -15.90 | -16.03 | -18.27 | -15.45 | -17.02 | -17.23 | +0.13 | -2.83 | +0.21 | +2.95 | -0.09 | -3.04 | False/False |
| 6 | 1 | butter | cream | 1/1 | -18.40 | -20.41 | -17.06 | -18.70 | -18.30 | -19.01 | +2.01 | +1.64 | +0.71 | +0.37 | +1.30 | +0.93 | False/False |
| 7 | 1 | water | wine | 1/1 | -15.57 | -16.79 | -15.44 | -13.62 | -15.12 | -15.48 | +1.22 | -1.81 | +0.36 | +3.03 | +0.86 | -2.17 | True/False |
| 8 | 2 | Monday | Friday | 1/1 | -13.87 | -14.56 | -13.55 | -14.24 | -18.79 | -17.40 | +0.69 | +0.69 | -1.39 | +0.00 | +2.08 | +2.08 | False/False |
| 9 | 2 | Tuesday | Thursday | 1/1 | -13.89 | -14.39 | -14.33 | -14.83 | -18.08 | -18.51 | +0.50 | +0.50 | +0.44 | +0.00 | +0.06 | +0.06 | True/False |
| 10 | 2 | March | April | 1/1 | -13.11 | -12.24 | -13.04 | -12.17 | -14.67 | -15.36 | -0.88 | -0.88 | +0.69 | +0.00 | -1.56 | -1.56 | True/False |
| 11 | 2 | noon | dusk | 1/1 | -14.33 | -19.41 | -15.39 | -18.15 | -16.22 | -20.81 | +5.08 | +2.77 | +4.59 | +2.31 | +0.49 | -1.82 | False/False |
| 12 | 3 | violin | guitar | 1/1 | -23.72 | -20.26 | -23.72 | -20.42 | -22.10 | -19.11 | -3.46 | -3.30 | -2.99 | -0.16 | -0.47 | -0.31 | False/False |
| 13 | 3 | flute | horn | 1/1 | -22.06 | -23.03 | -21.54 | -22.34 | -22.71 | -21.78 | +0.97 | +0.80 | -0.92 | +0.17 | +1.89 | +1.72 | False/False |
| 14 | 3 | piano | drums | 1/1 | -20.39 | -23.44 | -20.90 | -23.73 | -20.47 | -22.53 | +3.04 | +2.83 | +2.06 | +0.22 | +0.98 | +0.77 | False/False |
| 15 | 3 | trumpet | organ | 1/1 | -23.91 | -19.50 | -23.42 | -19.36 | -22.03 | -18.48 | -4.41 | -4.07 | -3.55 | -0.34 | -0.86 | -0.52 | False/False |
| 16 | 4 | gold | iron | 1/1 | -14.71 | -17.04 | -14.01 | -16.56 | -17.27 | -18.16 | +2.33 | +2.55 | +0.89 | -0.22 | +1.43 | +1.65 | True/False |
| 17 | 4 | silver | copper | 1/1 | -16.45 | -17.45 | -17.06 | -17.62 | -19.38 | -18.89 | +1.00 | +0.56 | -0.49 | +0.44 | +1.49 | +1.06 | False/False |
| 18 | 4 | platinum | bronze | 1/1 | -18.49 | -18.25 | -19.60 | -17.92 | -20.36 | -17.70 | -0.23 | -1.68 | -2.66 | +1.45 | +2.42 | +0.98 | False/False |
| 19 | 4 | steel | brass | 1/1 | -17.17 | -15.18 | -17.79 | -15.85 | -16.38 | -19.66 | -1.99 | -1.95 | +3.27 | -0.05 | -5.27 | -5.22 | False/False |
| 20 | 5 | London | Tokyo | 1/1 | -14.65 | -17.95 | -18.16 | -12.09 | -17.14 | -17.34 | +3.30 | -6.07 | +0.20 | +9.37 | +3.10 | -6.27 | False/False |
| 21 | 5 | Moscow | Cairo | 1/1 | -10.18 | -18.69 | -18.63 | -12.18 | -18.81 | -18.87 | +8.51 | -6.44 | +0.05 | +14.95 | +8.45 | -6.50 | False/False |
| 22 | 5 | Boston | Denver | 1/1 | -18.59 | -19.55 | -18.32 | -18.28 | -16.22 | -21.53 | +0.96 | -0.04 | +5.31 | +1.00 | -4.35 | -5.35 | False/False |
| 23 | 5 | Sydney | Dublin | 1/1 | -17.94 | -15.70 | -18.37 | -12.01 | -18.26 | -15.73 | -2.25 | -6.36 | -2.53 | +4.12 | +0.29 | -3.83 | False/False |
| 24 | 6 | asthma | diabetes | 1/1 | -17.15 | -15.09 | -16.93 | -14.11 | -18.35 | -16.69 | -2.06 | -2.81 | -1.67 | +0.75 | -0.40 | -1.15 | False/False |
| 25 | 6 | cancer | arthritis | 1/1 | -12.07 | -18.11 | -14.00 | -17.63 | -15.18 | -18.58 | +6.05 | +3.62 | +3.41 | +2.42 | +2.64 | +0.22 | False/False |
| 26 | 6 | malaria | pneumonia | 1/1 | -14.64 | -14.11 | -15.69 | -14.22 | -17.03 | -16.95 | -0.53 | -1.47 | -0.08 | +0.94 | -0.45 | -1.39 | False/False |
| 27 | 6 | measles | influenza | 1/1 | -15.71 | -15.02 | -16.16 | -15.00 | -17.00 | -17.22 | -0.69 | -1.16 | +0.22 | +0.47 | -0.91 | -1.38 | False/False |
| 28 | 7 | teacher | plumber | 1/1 | -14.61 | -21.03 | -17.68 | -16.91 | -19.01 | -17.75 | +6.42 | -0.77 | -1.26 | +7.19 | +7.68 | +0.49 | True/False |
| 29 | 7 | lawyer | farmer | 1/1 | -18.96 | -19.02 | -20.66 | -17.26 | -16.62 | -16.69 | +0.06 | -3.41 | +0.07 | +3.47 | -0.01 | -3.48 | True/True |
| 30 | 7 | nurse | baker | 1/1 | -20.09 | -20.04 | -20.52 | -20.91 | -19.64 | -20.95 | -0.05 | +0.39 | +1.31 | -0.44 | -1.36 | -0.92 | False/False |
| 31 | 7 | pilot | chef | 1/1 | -21.19 | -23.87 | -21.39 | -19.37 | -20.00 | -19.86 | +2.68 | -2.02 | -0.14 | +4.70 | +2.82 | -1.88 | True/True |
| 32 | 8 | tiger | dolphin | 1/1 | -20.85 | -20.50 | -21.00 | -20.23 | -18.67 | -19.61 | -0.35 | -0.77 | +0.94 | +0.41 | -1.29 | -1.70 | False/False |
| 33 | 8 | bear | eagle | 1/1 | -19.77 | -20.35 | -19.24 | -19.81 | -19.01 | -20.13 | +0.58 | +0.57 | +1.12 | +0.01 | -0.54 | -0.55 | False/False |
| 34 | 8 | lion | shark | 1/1 | -20.63 | -19.63 | -20.91 | -20.13 | -18.13 | -17.28 | -1.00 | -0.79 | -0.85 | -0.21 | -0.15 | +0.06 | False/False |
| 35 | 8 | wolf | hawk | 1/1 | -21.91 | -20.41 | -22.03 | -19.91 | -16.42 | -19.75 | -1.51 | -2.12 | +3.34 | +0.62 | -4.84 | -5.46 | False/False |
| 36 | 9 | river | castle | 1/1 | -20.35 | -20.01 | -21.33 | -19.67 | -16.43 | -19.18 | -0.34 | -1.66 | +2.75 | +1.31 | -3.09 | -4.41 | False/False |
| 37 | 9 | bridge | forest | 1/1 | -17.84 | -20.50 | -18.47 | -20.91 | -16.24 | -17.29 | +2.66 | +2.44 | +1.05 | +0.22 | +1.60 | +1.38 | False/False |
| 38 | 9 | garden | desert | 1/1 | -17.50 | -21.31 | -18.47 | -20.81 | -17.79 | -17.29 | +3.81 | +2.34 | -0.50 | +1.47 | +4.31 | +2.84 | False/False |
| 39 | 9 | mountain | village | 1/1 | -21.90 | -23.83 | -20.91 | -22.20 | -16.04 | -16.62 | +1.92 | +1.28 | +0.58 | +0.64 | +1.34 | +0.70 | False/False |

## T2a — audit of the round-3 topic readout + held-out wording p3

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

## T2b — activation-dependence control for the round-3 claim-word readout (NOT a truth test)

**ACTIVATION-DEPENDENCE TEST, NOT A TRUTH TEST.** The prefix and the "original" word are the AV's own greedy output; d_own and d_noinj are reused from t2_claims.csv.

git fa77ea33; settings in t2b_settings.json; rows in t2b_claims.csv; human labelling sheet t2b_support_sheet.csv (30 rows, label_supported empty)

- rows 691 (LLM corrupt 298, deterministic 393); errors 0; AV forwards 2764 (0.40 s each); prompt 125 tokens, marker at 111
- prefixes reconstructed from s3_edits.jsonl and asserted equal to the file's word_orig / word_corrupt / word_pos for all 691 rows
- in_ctx (word_orig in context_left_64 + token_str): 192/691; in_ctx_right (+ context_right_16): 192/691; corrupt word in left context: 24/691
- in_ctx by edit type: LLM 54/298, det 138/393

## Kill T2b

- mean (d_own − d_pos2), all rows, cluster by explanation: 7.3473 [6.5589,8.1413] n=691 n_expl=159; threshold ≤ 0 → **NOT MET**
- LLM corrupt: 6.1652 [5.2560,7.1314] → NOT MET; deterministic: 8.2436 [7.1885,9.3605] → NOT MET (splits, reported)
- far donor (reported, not a kill): mean (d_own − d_foreign) 10.1087 [9.2084,10.9556]

## Donor table (all rows)

| subset | n | n_expl | mean d_own | mean d_pos2 [CI] | mean d_foreign [CI] | mean d_noinj | d_own − d_pos2 [CI] | d_own − d_foreign [CI] | d_pos2 − d_noinj [CI] | d_foreign − d_noinj [CI] | frac d>0 own / pos2 / foreign / noinj | frac own>pos2 | frac own>foreign |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 691 | 159 | 12.988 | 5.641 [5.012,6.309] | 2.879 [2.330,3.420] | 2.726 | 7.347 [6.559,8.141] | 10.109 [9.208,10.956] | 2.915 [2.399,3.467] | 0.154 [-0.236,0.551] | 0.973 / 0.792 / 0.645 / 0.712 | 0.836 | 0.897 |
| LLM corrupt | 298 | 147 | 9.782 | 3.617 [2.755,4.426] | 1.075 [0.389,1.728] | 1.387 | 6.165 [5.256,7.131] | 8.707 [7.724,9.709] | 2.229 [1.479,3.009] | -0.313 [-0.788,0.197] | 0.973 / 0.725 / 0.540 / 0.638 | 0.832 | 0.909 |
| deterministic | 393 | 158 | 15.419 | 7.175 [6.312,8.052] | 4.248 [3.455,5.022] | 3.740 | 8.244 [7.188,9.361] | 11.171 [10.098,12.194] | 3.435 [2.759,4.170] | 0.507 [-0.032,1.051] | 0.972 / 0.842 / 0.725 / 0.768 | 0.840 | 0.888 |
| LLM last claim only | 82 | 82 | 11.553 | 1.839 [0.676,3.111] | -0.024 [-1.103,1.090] | 0.542 | 9.714 [7.857,11.690] | 11.577 [9.704,13.677] | 1.297 [0.149,2.539] | -0.566 [-1.561,0.502] | 0.976 / 0.683 / 0.463 / 0.598 | 0.890 | 0.927 |
| eval only | 691 | 159 | 12.988 | 5.641 [5.012,6.309] | 2.879 [2.330,3.420] | 2.726 | 7.347 [6.559,8.141] | 10.109 [9.208,10.956] | 2.915 [2.399,3.467] | 0.154 [-0.236,0.551] | 0.973 / 0.792 / 0.645 / 0.712 | 0.836 | 0.897 |
| eval LLM corrupt | 298 | 147 | 9.782 | 3.617 [2.755,4.426] | 1.075 [0.389,1.728] | 1.387 | 6.165 [5.256,7.131] | 8.707 [7.724,9.709] | 2.229 [1.479,3.009] | -0.313 [-0.788,0.197] | 0.973 / 0.725 / 0.540 / 0.638 | 0.832 | 0.909 |

## Donor table split by in_ctx (word_orig visible in context_left_64 + token_str)

| subset | n | n_expl | mean d_own | mean d_pos2 [CI] | mean d_foreign [CI] | mean d_noinj | d_own − d_pos2 [CI] | d_own − d_foreign [CI] | d_pos2 − d_noinj [CI] | d_foreign − d_noinj [CI] | frac d>0 own / pos2 / foreign / noinj | frac own>pos2 | frac own>foreign |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all, in_ctx=True | 192 | 112 | 18.227 | 6.625 [5.060,8.343] | 4.077 [2.984,5.342] | 3.139 | 11.601 [9.634,14.011] | 14.150 [12.534,15.976] | 3.486 [2.235,4.808] | 0.938 [0.159,1.908] | 0.990 / 0.766 / 0.672 / 0.693 | 0.802 | 0.911 |
| all, in_ctx=False | 499 | 155 | 10.972 | 5.262 [4.620,5.924] | 2.419 [1.873,2.971] | 2.566 | 5.710 [5.107,6.264] | 8.554 [7.888,9.336] | 2.696 [2.213,3.224] | -0.148 [-0.551,0.222] | 0.966 / 0.802 / 0.635 / 0.719 | 0.850 | 0.892 |
| LLM corrupt, in_ctx=True | 54 | 47 | 12.186 | 3.755 [1.059,6.705] | 0.467 [-1.085,2.093] | 0.408 | 8.431 [5.495,11.247] | 11.719 [9.404,13.963] | 3.347 [0.644,6.227] | 0.059 [-1.392,1.672] | 1.000 / 0.667 / 0.481 / 0.519 | 0.796 | 0.981 |
| LLM corrupt, in_ctx=False | 244 | 138 | 9.250 | 3.586 [2.816,4.407] | 1.209 [0.525,1.884] | 1.604 | 5.664 [4.817,6.590] | 8.041 [7.080,9.107] | 1.982 [1.294,2.601] | -0.395 [-0.885,0.117] | 0.967 / 0.738 / 0.553 / 0.664 | 0.840 | 0.893 |
| deterministic, in_ctx=True | 138 | 100 | 20.590 | 7.748 [6.118,9.474] | 5.489 [4.025,7.093] | 4.208 | 12.842 [10.402,15.436] | 15.101 [13.073,17.095] | 3.540 [2.344,4.745] | 1.281 [0.297,2.393] | 0.986 / 0.804 / 0.746 / 0.761 | 0.804 | 0.884 |
| deterministic, in_ctx=False | 255 | 137 | 12.620 | 6.865 [5.915,7.825] | 3.576 [2.733,4.504] | 3.487 | 5.755 [5.036,6.568] | 9.045 [8.033,10.070] | 3.378 [2.626,4.125] | 0.088 [-0.542,0.743] | 0.965 / 0.863 / 0.714 / 0.773 | 0.859 | 0.890 |
| LLM last claim only, in_ctx=True | 15 | 15 | 17.040 | 4.710 [1.267,8.496] | 3.304 [0.694,6.516] | 2.786 | 12.330 [7.813,17.050] | 13.736 [10.244,17.024] | 1.924 [-1.728,5.880] | 0.518 [-2.289,4.437] | 1.000 / 0.800 / 0.600 / 0.667 | 0.933 | 1.000 |
| LLM last claim only, in_ctx=False | 67 | 67 | 10.324 | 1.196 [0.039,2.348] | -0.769 [-1.844,0.314] | 0.039 | 9.128 [7.112,11.135] | 11.093 [8.956,13.236] | 1.157 [-0.006,2.342] | -0.808 [-1.818,0.164] | 0.970 / 0.657 / 0.433 / 0.582 | 0.881 | 0.910 |
| eval only, in_ctx=True | 192 | 112 | 18.227 | 6.625 [5.060,8.343] | 4.077 [2.984,5.342] | 3.139 | 11.601 [9.634,14.011] | 14.150 [12.534,15.976] | 3.486 [2.235,4.808] | 0.938 [0.159,1.908] | 0.990 / 0.766 / 0.672 / 0.693 | 0.802 | 0.911 |
| eval only, in_ctx=False | 499 | 155 | 10.972 | 5.262 [4.620,5.924] | 2.419 [1.873,2.971] | 2.566 | 5.710 [5.107,6.264] | 8.554 [7.888,9.336] | 2.696 [2.213,3.224] | -0.148 [-0.551,0.222] | 0.966 / 0.802 / 0.635 / 0.719 | 0.850 | 0.892 |
| eval LLM corrupt, in_ctx=True | 54 | 47 | 12.186 | 3.755 [1.059,6.705] | 0.467 [-1.085,2.093] | 0.408 | 8.431 [5.495,11.247] | 11.719 [9.404,13.963] | 3.347 [0.644,6.227] | 0.059 [-1.392,1.672] | 1.000 / 0.667 / 0.481 / 0.519 | 0.796 | 0.981 |
| eval LLM corrupt, in_ctx=False | 244 | 138 | 9.250 | 3.586 [2.816,4.407] | 1.209 [0.525,1.884] | 1.604 | 5.664 [4.817,6.590] | 8.041 [7.080,9.107] | 1.982 [1.294,2.601] | -0.395 [-0.885,0.117] | 0.967 / 0.738 / 0.553 / 0.664 | 0.840 | 0.893 |

## C3 — meaning-preserving phrasing control for C2, factorial (TARGET → AV → AV+AR)

This is a *phrasing control*, not a zero-information edit: (w1 → w2) is a one-word, meaning-preserving wording change in the same sentence as the entity.

- cells 40 (errors 0); templates used 10, dropped []; wording kinds {'primary': 40}
- wording pairs used: t0 primary: country→nation; t1 primary: calls→asks; t2 primary: moved→shifted; t3 primary: orchestra→ensemble; t4 primary: pure→solid; t5 primary: story→tale; t6 primary: was→got; t7 primary: worked→served; t8 primary: team's→club's; t9 primary: shows→depicts
- wording word distance to end (tokens): 12–20 (mean 16.8); entity distance 11–17 (mean 14.5); shared suffix C/D 10–16; wording diff tokens 1–1
- new AV descriptions: parse_ok 80/80, cjk 0/80, errors 0; 9.8 s/gen; AR forwards 160; AV readout forwards 320
- A/B re-derivation vs c2_acts max(1−cos) 2.22e-16; fresh AR re-score of C2 descriptions: max |M_fact(w1) − file M| 0.00000
- identical descriptions: C=D 0/40; A=C 0/40; B=D 0/40
- entity mentions in the new descriptions (C, D): own 13/80, other 4/80; w2 word mentioned 0/80, w1 word 15/80; C2 (A, B) own-mention was 11/80

## Kill C3-score

- mean [mean(M_fact) − mean(M_wording)]: 0.00782 [-0.00348,0.02407] n=40 clusters=10 → **INCONCLUSIVE** (with the file's M_fact(w1): 0.00782 [-0.00348,0.02407])

| margin | mean [CI by template] | frac > 0 |
|---|---|---|
| M_fact(w1) (C2 pairs, re-scored) | 0.01877 [0.00982,0.03382] | 1.000 |
| M_fact(w2) (new pairs) | 0.01632 [0.00731,0.03058] | 0.975 |
| M_wording(a) | 0.00965 [0.00582,0.01374] | 0.975 |
| M_wording(b) | 0.00980 [0.00543,0.01430] | 0.975 |
| fact − wording (per cell) | 0.00782 [-0.00348,0.02407] | 0.625 |

## Activation distance per edit type

| pair | mean cos | mean 1−cos | min cos | max cos |
|---|---|---|---|---|
| fact edit, w1: cos(h_A,h_B) | 0.9664 | 0.03359 | 0.8215 | 0.9988 |
| fact edit, w2: cos(h_C,h_D) | 0.9688 | 0.03117 | 0.8570 | 0.9993 |
| wording edit, a: cos(h_A,h_C) | 0.9758 | 0.02418 | 0.9142 | 0.9972 |
| wording edit, b: cos(h_B,h_D) | 0.9771 | 0.02289 | 0.9277 | 0.9977 |
| both edits: cos(h_A,h_D) | 0.9494 | 0.05063 | 0.8407 | 0.9946 |
| both edits: cos(h_B,h_C) | 0.9509 | 0.04910 | 0.8315 | 0.9903 |

- activation-distance difference (fact − wording, 1−cos): 0.00884 [-0.00948,0.03447]

## Kill C3-readout (p1 entity readout on all four activations)

- mean [D(h_C) − D(h_D)] (donor sensitivity at w2): 1.7723 [0.7183,3.2194] n=40 → **NOT MET**
- at w1 (T2c contexts re-scored here): 1.7379 [0.6272,3.2762]; max |D − T2c D| = 0.0000
- both-correct rate: w1 0.225, w2 0.200; frac donor>0: w1 0.775, w2 0.875

### 2×2 table of mean D(h) (rows: entity; columns: wording)

| | w1 | w2 |
|---|---|---|
| entity a | +1.2810 (A) | +1.3141 (C) |
| entity b | -0.4569 (B) | -0.4582 (D) |

- entity main effect mean[D(h_A)+D(h_C)]/2 − mean[D(h_B)+D(h_D)]/2: 1.7551 [0.6800,3.2433]
- wording main effect mean[D(h_A)+D(h_B)]/2 − mean[D(h_C)+D(h_D)]/2: -0.0159 [-0.1922,0.1525]
- interaction ½[(D_A − D_B) − (D_C − D_D)]: -0.0172 [-0.1051,0.0686]

## Per-template table

| template | wording | n | M_fact(w1) | M_fact(w2) | M_wording(a) | M_wording(b) | fact−wording | cos(hA,hB) | cos(hA,hC) | donor w1 | donor w2 | both-correct w2 | own-mention C/D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | country→nation (primary) | 4 | 0.0109 | 0.0095 | 0.0160 | 0.0183 | -0.0070 | 0.9682 | 0.9765 | 1.223 | 1.408 | 0.00 | 0.50 |
| 1 | calls→asks (primary) | 4 | 0.0112 | 0.0145 | 0.0075 | 0.0061 | 0.0060 | 0.9630 | 0.9777 | 1.854 | 1.840 | 0.50 | 0.25 |
| 2 | moved→shifted (primary) | 4 | 0.0074 | 0.0015 | 0.0052 | 0.0014 | 0.0011 | 0.9889 | 0.9861 | 0.578 | 0.312 | 0.00 | 0.25 |
| 3 | orchestra→ensemble (primary) | 4 | 0.0097 | 0.0090 | 0.0235 | 0.0190 | -0.0119 | 0.9770 | 0.9421 | -0.029 | -0.451 | 0.00 | 0.00 |
| 4 | pure→solid (primary) | 4 | 0.0143 | 0.0100 | 0.0048 | 0.0057 | 0.0069 | 0.9642 | 0.9829 | 0.404 | 0.638 | 0.25 | 0.00 |
| 5 | story→tale (primary) | 4 | 0.0155 | 0.0125 | 0.0032 | 0.0041 | 0.0104 | 0.9854 | 0.9970 | 7.359 | 7.077 | 0.50 | 0.00 |
| 6 | was→got (primary) | 4 | 0.0197 | 0.0165 | 0.0175 | 0.0172 | 0.0007 | 0.9790 | 0.9576 | 1.145 | 1.230 | 0.00 | 0.12 |
| 7 | worked→served (primary) | 4 | 0.0837 | 0.0780 | 0.0046 | 0.0042 | 0.0765 | 0.8612 | 0.9826 | 3.729 | 3.653 | 0.75 | 0.50 |
| 8 | team's→club's (primary) | 4 | 0.0074 | 0.0047 | 0.0123 | 0.0200 | -0.0101 | 0.9876 | 0.9602 | 0.207 | 0.772 | 0.00 | 0.00 |
| 9 | shows→depicts (primary) | 4 | 0.0079 | 0.0070 | 0.0018 | 0.0020 | 0.0055 | 0.9895 | 0.9956 | 0.910 | 1.242 | 0.00 | 0.00 |

## Three verbatim cells

### pair 0 (template 0): Paris / Lyon; country → nation; M_fact(w1)=0.0021 M_fact(w2)=0.0127 M_wording(a)=0.0156 M_wording(b)=0.0143
- context_a: The capital of the country is Paris. Tourists arrive at the main station and walk to the
- d_a (mentions own=True, other=False): Formal mathematical/structural description pattern with a numbered sequence ("A train from Moscow to Paris with a probability"), implying a scenario about a tourist arriving at a metro station.

The phrase "A person leaves the train station with a random time to the Eiffel Tower and goes to the metro center" strongly implies a destination or attraction description, suggesting the sentence structure continues describing the route or destination's location.

Final token "the" is an article mid-noun phrase ("from the hotel to the"), directly continuing "a person goes from the metro to the," requiring a noun like "central station" or "hotel, or the clock tower" or "station, with a probability distribution."
- context_b: The capital of the country is Lyon. Tourists arrive at the main station and walk to the
- d_b (mentions own=False, other=False): Formal mathematical/urban description format with a translated phrase ("A random walk in the city"), implying a puzzle or event context about a metro station.

The sentence structure "A person leaves from a random station in the center of the city and goes to the metro station, then decides whether to go to the" suggests a paired noun phrase describing destination or attraction location about the city's main square.

Final token "the" is an article mid-noun phrase ("from the hotel to the"), continuing the parallel structure "a random walk to the metro station and to the," strongly expecting a noun like "main square" or "hotel entrance" or "bus stop, with a certain probability."
- context_c: The capital of the nation is Paris. Tourists arrive at the main station and walk to the
- d_c (mentions own=True, other=False): Formal mathematical/linguistic description format with a travel context suggesting a numbered sequence or interactive scenario about a metro station in Paris.

The phrase "A person leaves from a random station in Paris and walks to the Eiffel Tower, then decides to go to the metro" implies a sentence structure describing a destination and journey, likely implying a clock or schedule event about the museum's location.

Final token "the" is an incomplete noun phrase mid-sentence ("from the train to the museum and goes to the"), directly requiring a noun like "central museum" or "clock tower" or "entrance hall," continuing the parallel structure describing attendees' destination or attraction.
- context_d: The capital of the nation is Lyon. Tourists arrive at the main station and walk to the
- d_d (mentions own=False, other=False): Formal descriptive/mathematical context with a travel/urban setting, suggesting a puzzle or interactive app format with numbered directions.

The phrase "A person starts from the train station in the city center and walks to the metro station, then decides to go to the tourist attraction" implies a sentence structure describing two destinations or a destination's characteristics, likely a noun phrase about the city's main square or museum.

Final token "the" is an article mid-phrase ("from the train station to the"), part of a parallel structure ("people walk from the clock to the destination and to the"), expecting a noun like "central square" or "entrance hall" or "bus schedule."

### pair 18 (template 4): platinum / bronze; pure → solid; M_fact(w1)=0.0067 M_fact(w2)=0.0039 M_wording(a)=0.0002 M_wording(b)=0.0041
- context_a: The ring was made of pure platinum. The jeweller placed it carefully in a small box on the
- d_a (mentions own=False, other=False): Narrative context: a British English-language story with a quirky wildlife photograph, implying a dialogue or scene about a gemstone jeweler's display.

The phrase "The trembling detective held the diamond and other specimens on a white cloth on the" suggests a descriptive clause about a shop's display or tray, continuing a scene-setting phrase about a mysterious gift being handed to a client.

Final token "the" is an article mid-phrase ("on the shelf on the"), part of an incomplete noun phrase describing a receipt or tray location ("A specimen with a diamond and other items was placed on the shelf on the"), expecting a noun like "floor" or "client's desk" or "box."
- context_b: The ring was made of pure bronze. The jeweller placed it carefully in a small box on the
- d_b (mentions own=False, other=False): Narrative context: a short story or descriptive prose about a cat, with a mysterious gemstone being shown to a customer.

The phrase "The little bird flew the specimen of the precious stone onto the counter of the cabinet on the" suggests a dialogue setup or scene description, implying a shopkeeper's display or inventory tray, continuing a list of items.

Final token "the" is an incomplete noun phrase mid-sentence ("placed on the shelf on the... on the"), part of a quoted description clause ("A trembling spider with a letter and some papers he placed on the shelf on the"), strongly expecting "floor" or "customer's desk" or "box, waiting."
- context_c: The ring was made of solid platinum. The jeweller placed it carefully in a small box on the
- d_c (mentions own=False, other=False): Narrative context: a short story or descriptive prose about a diamond ring, implying a British English scene with a detective or jewelry seller.

The sentence structure "The little bird held the specimen on a white cloth on the counter, he placed the mysterious object on the" suggests a dialogue or display scenario, with a specific phrase about a receipt or box being shown to a customer.

Final token "the" is an article mid-phrase ("on the shelf on the"), part of an incomplete noun phrase describing a location ("A small box with the specimen and other items was placed on the desk on the"), expecting a noun like "floor" or "customer's desk" or "bottom of the box."
- context_d: The ring was made of solid bronze. The jeweller placed it carefully in a small box on the
- d_d (mentions own=False, other=False): Narrative momentum: a descriptive English-language story about a gemstone seller, implying a quirky or dramatic scene with a cat figure.

The phrase "The detective picked up the specimen from the microscope and placed it on a white cloth on the counter of the shop" suggests a dialogue or inventory scene setup, with "a note and a box of remedies" implying a customer's receipt or display.

Final token "the" is an incomplete noun phrase mid-sentence ("on the desk on the"), part of a quoted description clause ("He placed a specimen and some items on the desk on the"), expecting a noun like "floor" or "customer's desk" or "bottom of his box."

### pair 36 (template 9): river / castle; shows → depicts; M_fact(w1)=0.0147 M_fact(w2)=0.0104 M_wording(a)=0.0023 M_wording(b)=0.0049
- context_a: The painting shows a river under a clear sky. Visitors to the gallery often stop in front of it and
- d_a (mentions own=False, other=False): European language description with literary/educational tone, suggesting a museum exhibit or art piece about a tree, implying an observation or contemplative experience.

The sentence structure "Some visitors often stop before this fountain and many people stand still and" strongly implies a common reaction or activity pattern, likely continuing with "take time to observe" or "are fascinated by the artwork," establishing the scene.

Final token "and" is a conjunction mid-clause ("visitors often stop by the fountain and many people stop and"), part of an incomplete clause describing observer behavior, immediately expecting a verb like "enjoy the silence" or "write notes," or "often linger for a long time."
- context_b: The painting shows a castle under a clear sky. Visitors to the gallery often stop in front of it and
- d_b (mentions own=False, other=False): European museum exhibition text with formal descriptive tone, suggesting a literary or art book context about a sculpture.

The sentence structure "Some visitors often stop in front of this painting and many people stand still and" implies an observed behavior pattern or invitation, likely continuing with a clause describing visitors' reactions or interest in the artwork, completing the introductory setup about the sculpture's appealing qualities.

Final token "and" is a conjunction mid-clause ("visitors often stop by and many visitors stop to look at the exhibition and"), strongly expecting a verb phrase like "take notes" or "are fascinated by its" or "often spend time discussing," continuing the observational description of visitor behavior.
- context_c: The painting depicts a river under a clear sky. Visitors to the gallery often stop in front of it and
- d_c (mentions own=False, other=False): Formal literary description with a bilingual context, suggesting an exhibition or art piece about trees, inviting readers to observe a particular sculpture.

The sentence structure "Some visitors often stop before this fountain and many people stand quietly and" implies an observed behavior pattern or anecdote, strongly implying a clause describing what visitors do or feel about the artwork's peaceful atmosphere or beauty.

Final token "and" is a conjunction mid-clause ("visitors often stop by and many visitors stop by the exhibition and"), part of an incomplete clause structure ("People often visit these sculptures and many people often stop and"), expecting a verb like "take notes" or "are fascinated by the scene," or "linger."
- context_d: The painting depicts a castle under a clear sky. Visitors to the gallery often stop in front of it and
- d_d (mentions own=False, other=False): Bulgarian language text with literary/artistic context, suggesting a museum or exhibition description format about a sculpture.

The sentence structure "Some visitors often stop in front of this painting and many people stand still and" implies an expected continuation describing viewer behavior or reaction, likely a common activity or observation about the artwork's beauty or mystery, continuing the introductory clause.

Final token "and" is a conjunction mid-clause ("visitors often stop by and many visitors stop to observe the paintings and"), strongly expecting a verb phrase like "take notes" or "are fascinated by its details" or "often discuss," completing the observation clause about people's reactions to the artwork.

## T3 closeout (from U0; report only, not rerun)

## T3 closeout (report only; not rerun, not extended)

- pre-registered design: pilot stimuli 0–39 (n=40) × 2 directions × 2 layers × 3 α = 480 items; stage cap 5100 s
- completed before the cap: 420 items = 35 pilot stimuli (0–34) × 12 cells; items per stimulus min 12 max 12; errors 0; 12.3 s/item; wall 2026-09-06T22:03:11 → 2026-09-06T23:29:47
- stopping rule as pre-registered (PLAN round 3): stage cap (T0 re-budget: 'T3 111 min > cap, run stimulus-outer and cut at cap'); settings `stopped_at_stimulus` = 35; round-3 PLAN execution order put T3 last ('dropped first under the hard stop')
- outcome rule as written in t3_settings.json: eligible = french cells with parse_ok >= 0.5; MET if all eligible CI hi < 0.25; NOT MET if any eligible CI lo >= 0.25; else INCONCLUSIVE; INCONCLUSIVE if no eligible cell
- kill T3 as written in t3_settings.json: outcome MET; eligible cells ['french_L8_a1']
- kill line as written in DISCONFIRMATION.md:

```
2026-09-06T23:29:47  T3  T3  threshold=French pass rate < 0.25 at every (ℓ, α) with parse_ok ≥ 0.5 (pilot, french direction, CI by stimulus)  observed=L8 α=1: pass 0.057 [0.000,0.143] parse_ok 1.00 n=35; L8 α=2: pass 0.400 [0.229,0.571] parse_ok 0.00 n=35; L8 α=4: pass 0.000 [0.000,0.000] parse_ok 0.00 n=35; L14 α=1: pass 0.114 [0.029,0.229] parse_ok 0.00 n=35; L14 α=2: pass 0.171 [0.057,0.314] parse_ok 0.00 n=35; L14 α=4: pass 0.514 [0.343,0.686] parse_ok 0.00 n=35; eligible cells 1/6  MET  MET would mean the AV is not steerable by residual addition either, at doses that keep it fluent
```

- RUNLOG lines for T3:

```
2026-09-06T22:03:04  T3  start  AV residual steering, pilot 0-39: french/terse directions at blocks 8,14 x α 1,2,4 = 12 cells x 40 = 480 generations (budget 111 min > 85-min cap; stimulus-outer, cut at cap)
2026-09-06T23:30:16  T3  done  420 items (35 of 40 pilot stimuli x 12 cells; generation cut at the 85-min stage cap before stimulus 35), 0 errors, 12.3 s/item; T3 MET (eligible french cells with parse_ok>=0.5: 1/6 = L8 α=1, pass 0.057 CI [0.000,0.143]; α>=2 destroys the <explanation> format at both layers, French pass up to 0.514 at L14 α=4 with parse_ok 0)
```

## Write-up phrasings requested by the human in the round-3 review (PLAN.md round-3b block; verbatim, for the desk)

- "substantially more sensitive to wording and relevance than to the tested factual corruptions" (not "reads wording, not facts")
- "local-snippet dominance persists across positions" (moving it cut its cost by ~21%, so not "content, not position")
- "the tested instructions did not produce the requested changes" (not "ignores instruction text")
- T4 "replicates injected-concept sensitivity", not the outside-J-space result (no J-space complement was built)
- report rotation angles as angles (18° ≈ 31% of the norm for equal-norm vectors, not "small")
- the blind/raw-context scores 0.429/0.473 sit well above the empty baseline 0.347
- three things kept apart in every readout number: self-consistency (the AV prefers a word it generated itself), activation dependence (the preference changes when the activation changes), factual recovery (the preference follows an independently known source fact). T2-claims / T2b = self-consistency + activation dependence; T2c = factual recovery; C3 = a phrasing control, not a zero-information edit
- the prior-corrected topic AUROC (0.935 in round 3) was not pre-registered → exploratory; T2a reports the held-out wording and within-pair accuracy with CIs alongside

## FOLLOWUPS.md (queued for the human, not acted on)

- S3 statistic A_i = Δ_i(z*) − Δ_i(z) equals cos(z) − cos(z*) by construction (z* minus c_i* is the same text as z minus c_i), so the primary and the first secondary statistic coincide; both are reported as pre-registered.
- Stage scripts create their Settings file at module import; importing one stage from another (S3 imports S2's splitter) or re-running with --summary overwrites the finished stage's settings JSON. Move Settings creation under main() next round.

## OPEN DECISIONS (from STATE.md)

## Open decisions (research calls left for the human)
(none)

## Provenance

**Pre-registered by the human (PLAN.md round 3b, 2026-09-06 23:15):** the stage list and execution order (U0 → T2c → T2a → T2b → C3 → T7), the shared readout definition (summed log-prob of every token of ' ' + candidate after the prefilled assistant turn; h_0 = no injection), the T2c nouns and both prefixes p1/p2, the T2c candidates (the pair's own entities), the held-out prefix p3, the T2b donors (h_pos2 near, h_foreign far) and the rule that own / no-injection log-probs are reused from t2_claims.csv, the in_ctx source-support proxy and the 30-row support sheet, the C3 wording pairs (primary and fallback) and the drop rule, the C3 margins and 2×2 decomposition, every kill statistic and threshold in the round-3b threshold table, the three-outcome rule, the cluster-bootstrap rule (by template for the C2-derived stages, by document / explanation otherwise; 1000 draws, seed 0), the pilot/eval split, the 45-min stage cap and the 2.5 h hard stop.

**Written by the agent:** `u0_check.py`, `t2c_entity.py`, `t2a_audit.py`, `t2b_donor.py`, `c3_phrasing.py`, `t7_morning.py`, this file. `nla_lib.py`, `t2_prefix.py` (the `Prefix` class), `c2_matched.py` (`TEMPLATES`, `build_pairs`, `mentions`), `t1_arprobe.py` (`auroc`, `boot_auroc`, `detok`, `load_triples`) and all round-1/2/3 files were reused unchanged.

**Choices the agent had to make (none changes a pre-registered statistic; each is logged in the stage's settings.json):**
- T2c: the paired AUROC (statistic 5) is given with two bootstrap CIs, by template and by pair, because the plan says 'cluster by template' for 1–4 and 'over the 40 pairs' for 5. Within-pair choice accuracy (statistic 4) is the fraction of the 80 activations whose argmax candidate is the entity in that context, i.e. D(h_a) > 0 for side a and D(h_b) < 0 for side b. MIN pairs for a non-INCONCLUSIVE outcome = 30 (as C2). All 80 candidate strings are single tokens, so the per-token rows equal the summed rows.
- T2a: the audit checks are source-string matches in t2_prefix.py plus arithmetic identities in t2_scores.csv; the 'pre-registered?' check reads the round-3 T2 stage text in PLAN.md for the words 'prior-corrected'. The swap statistic is also reported prior-corrected (same no-injection prior subtracted). Within-pair accuracy CIs are a bootstrap over stimuli (one row per document).
- T2b: the kill is computed over all 691 rows pooled (the stage text says 'every non-error row'), with the LLM / deterministic / last-claim splits reported in the same line. in_ctx strips leading/trailing non-alphanumerics from word_orig before the whole-word match. The support sheet is sampled with pandas `sample(random_state=0)` from evaluation LLM-corrupt rows and sorted by row.
- C3: the wording replacement is the first whole-word occurrence of w1 in the whole template (all ten primaries sit in the first sentence). A and B activations are C2's cached ones (re-derived and compared, deviation logged); A and B descriptions are C2's. M_fact(w1) is re-scored fresh by the AR and also recomputed from the c2_pairs.csv cos columns (asserted equal to the file's M; both versions of the kill statistic are reported). The 'activation-distance difference' uses 1 − cos averaged over the two fact pairs minus the two wording pairs. The verbatim cells are pairs 0, 18, 36.
- Settings files are created inside `main()`; stage scripts import round-3 modules whose Settings creation is inside `main()` (checked in U0), so no earlier settings file is rewritten.

