# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: ROUND 3 NOT STARTED (rounds 1–2 complete and merged; human reviewed 2026-09-06 evening)
LAST UPDATED: 2026-09-06 19:30
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20
T5: NOT CONFIRMED (human must change this line to `T5: HUMAN-CONFIRMED` before launch for T5 to run)

## Stage status
# Round 3 — see PLAN.md "Round 3 stages". EXECUTION ORDER: T0 → T1 → T2 → T4 → T3 → T5 → T6. Hard stop 5 h.
T0  artifact check + topics + entropy .. TODO
T1  AR as zero-shot probe ............... TODO
T2  forced-prefix yes/no on AV .......... TODO
T4  injected-vector perturbation ........ TODO
T3  AV residual steering ................ TODO
T5  steering specificity (OPTIONAL) ..... TODO
T6  MORNING3.md ......................... TODO

## Blockers
(none)

## Open decisions (research calls left for the human)
(none)

## Notes
Rounds 1–2 complete; artifacts in this directory and out/.
