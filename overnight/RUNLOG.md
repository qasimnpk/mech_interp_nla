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
