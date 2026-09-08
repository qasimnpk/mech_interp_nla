# RUNLOG — nightshift, NLA project
# One line per stage transition:
# <ISO timestamp>  <stage>  start|done|blocked  <detail>
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
2026-09-06T05:40:31  S6  done  MORNING1.md written; round 1 ended; loop stops
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
2026-09-06T09:24:42  R4  done  MORNING2.md written; round 2 ended (started 09:03:21, well inside the 5.5 h stop); loop stops
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
2026-09-06T23:30:16  T6  done  MORNING3.md written; round 3 ended (started 19:47:49, hard stop 00:47:49 not reached); loop stops
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
2026-09-07T00:42:46  T7  done  MORNING3b.md written; round 3b ended (started 23:49:14, hard stop 02:19:14 not reached); loop stops
2026-09-08T00:38:40  U0c  start  round 3c begins (single long session, not /loop); artifact check + micro-benchmark of every call type + re-budget; hard stop = 2026-09-08T00:38:40 + 9 h = 2026-09-08T09:38:40
2026-09-08T00:42:22  U0c  crashfix  iteration 1 crashed in the 512-token benchmark loop before any output (RuntimeError: docs.index(tensor) boolean ambiguity); loop now iterates indices; no measurement changed; rerun (out/u0c_iter1_crash.log)
2026-09-08T00:44:56  U0c  done  27/27 artifact checks OK; measured s/call (5 each, first call includes warm-up): TARGET short fwd 0.42 (min 0.12), TARGET 512-doc all-hidden 1.12, TARGET hook@20 0.10 (self-patch max|Δlogit| 0), AV prefill fwd 0.60 (min 0.38), AV gen-200 9.8, AR score 0.48 (min 0.28); re-budget: every stage under its cap, total projected 199 min; one pre-output crash fix logged above
2026-09-08T00:44:56  U1  start  base-model control: TARGET weights in the AV interface (TargetAsAV), p3/PREFILL_CC topic on 200 stimuli (own/swap/no-inj), p1/p2 entity on 40 pairs, text-only reference; AV scores from t2a/t2/t2c files
2026-09-08T01:06:14  U1  done  2478 baseline forwards (TARGET weights in the AV interface; role assert bypassed by construction), 0 errors; U1 NOT MET (paired [AV − baseline] raw p3 acc 0.312 CI [0.244,0.388]; AV 0.781, baseline 0.469, text-only 0.988; prior-corrected AV 0.944 base 0.494; entity p1 donor AV 1.738 base -0.011); wall 00:44:50→01:05:51
2026-09-08T01:06:14  X3  start  snippet vs factual discrimination: AR scoring (T/F/P x 3 conditions on eligible S3 triples) then TARGET judge
2026-09-08T01:21:46  X3  done  211 eligible rows (147 last-claim + 132 repeated-word excluded), 1337 AR forwards (0.22 s), 422 judge generations (0.94 s), 0 errors; X3-gate FAIL (valid condition-3 rows 74 < 100); X3 INCONCLUSIVE (mean I=-0.00057 CI [-0.00401,0.00206] n=74; G1 0.00115 G2 0.00217 G3 0.00275); judge-valid subset n=1 (contradict=yes for 1/211); wall 01:06→01:18
2026-09-08T01:21:46  X1  start  cross-layer readout: TARGET (80 C2 contexts + 200 docs at blocks 16/20/24/27) then AV (p1 entity 40 pairs, p3 topic eval 160, at each layer)
