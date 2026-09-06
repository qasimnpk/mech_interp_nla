# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: C1 running (round 3 started 2026-09-06T19:47:49; hard stop 2026-09-07T00:47:49)
LAST UPDATED: 2026-09-06T19:55:02
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20
T5: SKIP (desk recommendation: superseded by the round-4 steering design; change to `T5: HUMAN-CONFIRMED` to run it)

## Stage status
# Round 3 — see PLAN.md "Round 3 stages". EXECUTION ORDER: T0 → C1 → C2 → T1 → T2 → T4 → T5 → T3 → T6 (T3 last, dropped first). Hard stop 5 h.
T0  artifact check + topics + entropy .. DONE (t0_check.md; no kill test)
C1  position vs content (AR only) ....... RUNNING
C2  matched one-fact activation pairs ... TODO
T1  AR as zero-shot probe ............... TODO
T2  forced-prefix yes/no on AV .......... TODO
T4  injected-vector perturbation ........ TODO
T5  steering specificity (OPTIONAL) ..... TODO
T3  AV residual steering (last) ......... TODO
T6  MORNING3.md ......................... TODO

## Blockers
(none)

## Open decisions (research calls left for the human)
(none)

## Notes
Rounds 1–2 complete; artifacts in this directory and out/.
