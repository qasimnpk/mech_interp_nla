# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: T2a (round 3b started 2026-09-06T23:49:14; hard stop 2026-09-07T02:19:14; stage cap 45 min)
LAST UPDATED: 2026-09-06 23:55
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20

## Stage status
# Round 3b — see PLAN.md "Round 3b stages". EXECUTION ORDER: U0 → T2c → T2a → T2b → C3 → T7 (C3 last, dropped first). Hard stop 2.5 h. Stage cap 45 min.
U0   artifact check + T3 closeout ............ DONE (18/18 checks; T3 closeout 420 items/35 stimuli, cap; u0_check.md)
T2c  entity readout on C2 pairs (PRIMARY) .... DONE — NOT MET (donor sens. 1.738 CI [0.627,3.276]; both-correct raw 0.225; t2c_summary.md)
T2a  topic-readout audit + held-out prefix ... RUNNING
T2b  claim-readout donor control ............. TODO
C3   phrasing control for C2 (factorial) ..... TODO
T7   MORNING3b.md ............................ TODO

## Blockers
(none)

## Open decisions (research calls left for the human)
(none)

## Notes
Rounds 1–3 complete; artifacts in this directory and out/ (round-3 out/*.npz copied from the round-3 worktree before removal).
