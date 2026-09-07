# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: T6 running (round 3 started 2026-09-06T19:47:49; hard stop 2026-09-07T00:47:49)
LAST UPDATED: 2026-09-06T23:30:16
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20
T5: SKIP (desk recommendation: superseded by the round-4 steering design; change to `T5: HUMAN-CONFIRMED` to run it)

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

## Blockers
(none)

## Open decisions (research calls left for the human)
(none)

## Notes
Rounds 1–2 complete; artifacts in this directory and out/.
Round 3: T3 generation stopped at the 85-min stage cap after 35 of 40 pilot stimuli (every cell has n=35); no pre-registered minimum n for T3, outcome reported as computed. T5 skipped (STATE line was `T5: SKIP`).
