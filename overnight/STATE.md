# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: ROUND 4 — V0 (not started). Hard stop: 10 h after the first round-4 RUNLOG line (T9 reserved: the last 30 min).
LAST UPDATED: 2026-09-09 (desk, before the round; revised after advisor review)
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20

## Stage status
# Round 4 — see PLAN.md "Round 4 stages". EXECUTION ORDER: V0 → B1 → A1 → K1 → D1 → T9. Stage caps: V0 30, B1 150, A1 210, K1 45, D1 60 min (orchestrator judgement time counts). T9 owns the last 30 min before the hard stop.
V0   artifact check + benchmark + pipeline verification + re-budget ..... TODO
B1   controlled paired contexts, meanings A/B (human; PRIMARY CONTROLLED)  TODO
A1   natural AV claims, paraphrase-averaged preference (human; PRIMARY) .. TODO
K1   K-way alternative ranking on deterministic-swap claims (AR only) .... TODO
D1   claim-direction ablation via the AR as encoder (greedy AV; one γ) ... TODO
T9   MORNING4.md (reserved: last 30 min) ................................ TODO

## Blockers
(none)

## Open decisions (research calls left for the human)
(none — the round-4 cut rules are pre-declared in PLAN.md V0; apply them in order and record which applied)

## Notes
Rounds 1–3c complete and merged into main; artifacts in this directory and out/ (acts_L20.npz is required by K1 and D1; present).
Round 4: all editor / judge tasks are done by the orchestrator (Claude) via the agent-judgement protocol in PLAN.md; the TARGET is never used as an LLM. Labels are PROVISIONAL; every analysis script must accept --labels for the human's relabelling. Review sheets: open <stage>_review_blind.csv first, <stage>_review_key.csv after.
