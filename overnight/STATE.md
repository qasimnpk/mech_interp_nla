# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: X3 (round 3c running; started 2026-09-08T00:38:40 local; hard stop 2026-09-08T09:38:40)
LAST UPDATED: 2026-09-08T01:06:14
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20

## Stage status
# Round 3c — see PLAN.md "Round 3c stages". EXECUTION ORDER: U0c → U1 → X3 → X1 → N3 → N4 → X1b → RT → M → T8. Hard stop 9 h. Stage cap 60 min (RT, M: 90 min).
U0c  artifact check + micro-benchmark + re-budget ..... DONE (27/27 checks; all stages under cap; u0c_check.md)
U1   base-model control for the likelihood readout .... DONE — NOT MET (AV−base raw p3 acc +0.312 [0.244,0.388]; u1_summary.md)
X3   snippet vs factual discrimination (AR only) ...... RUNNING
X1   cross-layer verified readout ..................... TODO
N3   correct / wrong / generic / omitted (AR only) .... TODO
N4   fact-vs-phrasing displacement across layers ...... TODO
X1b  cross-layer full generations (OPTIONAL) .......... TODO
RT   round-trip relational pilot (GATED G0/G1/G2) ..... TODO
M    error-monitoring pilot (GATED GM) ................ TODO
T8   MORNING3c.md ..................................... TODO

## Blockers
(none)

## Open decisions (research calls left for the human)
(none)

## Notes
Rounds 1–3b complete; artifacts in this directory and out/ (npz caches copied from the previous worktrees).
