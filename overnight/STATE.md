# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: M (round 3c running; started 2026-09-08T00:38:40 local; hard stop 2026-09-08T09:38:40)
LAST UPDATED: 2026-09-08T02:14:11
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20

## Stage status
# Round 3c — see PLAN.md "Round 3c stages". EXECUTION ORDER: U0c → U1 → X3 → X1 → N3 → N4 → X1b → RT → M → T8. Hard stop 9 h. Stage cap 60 min (RT, M: 90 min).
U0c  artifact check + micro-benchmark + re-budget ..... DONE (27/27 checks; all stages under cap; u0c_check.md)
U1   base-model control for the likelihood readout .... DONE — NOT MET (AV−base raw p3 acc +0.312 [0.244,0.388]; u1_summary.md)
X3   snippet vs factual discrimination (AR only) ...... DONE — gate FAIL (74 < 100 cond-3 rows); INCONCLUSIVE (I=-0.00057 [-0.00401,0.00206] n=74)
X1   cross-layer verified readout ..................... DONE — NOT MET (donor CI > 0 at L16/L24/L27; L24 highest; x1_summary.md)
N3   correct / wrong / generic / omitted (AR only) .... DONE — INCONCLUSIVE (generic−wrong -0.00029 [-0.00087,0.00025]; omitted−wrong +0.048)
N4   fact-vs-phrasing displacement across layers ...... DONE — descriptive (n4_curve.csv; C3 entity/phrasing ratio peaks at block 24)
X1b  cross-layer full generations (OPTIONAL) .......... DONE — descriptive (x1b_summary.md)
RT   round-trip relational pilot (GATED G0/G1/G2) ..... BLOCKED — gate G2 FAIL (11/16 < 12); G0 16/16, G1 16/16; routes not run
M    error-monitoring pilot (GATED GM) ................ RUNNING
T8   MORNING3c.md ..................................... TODO

## Blockers
(none)

## Open decisions (research calls left for the human)
(none)

## Notes
Rounds 1–3b complete; artifacts in this directory and out/ (npz caches copied from the previous worktrees).
