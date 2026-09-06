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
