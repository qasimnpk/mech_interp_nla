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
