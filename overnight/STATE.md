# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: R4 (MORNING2.md) RUNNING
LAST UPDATED: 2026-09-06 09:24
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20

## Stage status
# Round 2 — see PLAN.md "Round 2 stages". EXECUTION ORDER: R0 → R1 → R2 → R3 → R4. Hard stop 5.5 h after first round-2 RUNLOG line.
R0  artifact check ...................... DONE (r0_check.md: 0.8820 vs 0.8820, accepted)
R1  fact-blindness locus (target vs AR) . DONE (R1 MET; r1_summary.md)
R2  amplified corruption (AR only) ...... DONE (R2 MET; r2_summary.md)
R3  truncation curve (AR only) .......... DONE (k*_first=3, k*_last=1; r3_summary.md)
R4  MORNING2.md ......................... RUNNING

## Blockers
(none)

## Open decisions (research calls left for the human)
(none)

## Notes
Round 1 stages S0–S6 complete; artifacts in this directory and out/.
