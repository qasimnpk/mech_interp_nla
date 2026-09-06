# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: S1 (running; loop started 2026-09-06T02:18:09; hard stop 07:30 local)
LAST UPDATED: 2026-09-06T02:27:40
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20

## Stage status
# Round 1 — see PLAN.md "Stages".
# EXECUTION ORDER (fail-fast): S0 → S1 → S2 → S3 → S5 → S4 → S6. S4 is optional (last; dropped first under the 07:30 / 7 h hard stop). Pilot = stimuli 0–39, evaluation = 40–199. Kill tests first in every stage.
# Log every kill test to overnight/DISCONFIRMATION.md. A MET kill test is a result, not an abort.
S0  download, load, one round trip .... DONE (K0 NOT MET; cjk 1/16; cos 0.785–0.955 on 16)
S1  baseline round trip (200) ......... RUNNING
S2  claim deletion ..................... TODO
S3  corrupted vs paraphrased claims .... TODO
S5  prompt steering (pilot 40, 6 variants) TODO
S4  blind-describer + raw-context (OPTIONAL) TODO
S6  MORNING1.md ........................ TODO

## Blockers
(none)

## Open decisions (research calls left for the human)
(none)

## Notes
