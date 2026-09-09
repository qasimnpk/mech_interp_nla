# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: ROUND 4 — V0 (not started). Hard stop: 10 h after the first round-4 RUNLOG line.
LAST UPDATED: 2026-09-09 (desk, before the round)
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20

## Stage status
# Round 4 — see PLAN.md "Round 4 stages". EXECUTION ORDER: V0 → B1 → K1 → A1 → D1 → T9. Stage caps: V0 30, B1 150, K1 45, A1 210, D1 75 min (orchestrator judgement time counts).
V0   artifact check + benchmark + pipeline verification + re-budget ..... TODO
B1   controlled paired contexts (human; PRIMARY CONTROLLED) ............. TODO
K1   K-way alternative ranking on deterministic-swap claims (AR only) ... TODO
A1   natural AV claims, paraphrase-averaged preference (human; PRIMARY) . TODO
D1   claim-direction ablation via the AR as encoder (greedy AV) ......... TODO
T9   MORNING4.md ....................................................... TODO

## Blockers
(none)

## Open decisions (research calls left for the human)
(none — the round-4 cut rules are pre-declared in PLAN.md V0; apply them in order and record which applied)

## Notes
Rounds 1–3c complete and merged into main; artifacts in this directory and out/ (copy the .npz caches into the new worktree's out/ before V0: acts_L20.npz is required by K1 and D1).
Round 4: all editor / judge / translator tasks are done by the orchestrator (Claude) via the agent-judgement protocol in PLAN.md; the TARGET is never used as an LLM. Labels are PROVISIONAL; every analysis script must accept --labels for the human's relabelling.
