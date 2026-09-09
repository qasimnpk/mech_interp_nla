# STATE — nightshift, NLA project
# Read this first every turn. Update after every stage transition.

CURRENT STAGE: ROUND 5 COMPLETE (T10 done; MORNING5.md written). Review from the desk: DISCONFIRMATION.md (P1 line), MORNING5.md, then p2_review_blind.csv before p2_review_key.csv.
LAST UPDATED: 2026-09-09T15:30:19 (bench, round 5 complete)
MODEL=Qwen/Qwen2.5-7B-Instruct  AV=kitft/nla-qwen2.5-7b-L20-av  AR=kitft/nla-qwen2.5-7b-L20-ar  LAYER=block 20

## Stage status

# Round 5 — see PLAN.md "Round 5 stages" (binding). EXECUTION ORDER: P0 → P1 → P2 → T10. First RUNLOG line 2026-09-09T15:20:59; hard stop 2026-09-09T+3h; T10 reserve = last 20 min.
P0   artifact check + last-token activations of the 8 texts (TARGET) ..... DONE (8/8; tokens 93–1889)
P1   7B greedy verbalization + AR scoring (own / shuffled / 27B text) ..... DONE (8/8; cos_own 0.929 / shuffled 0.342; INCONCLUSIVE by n)
P2   claim annotation of the 8 7B explanations (protocol verbatim) ....... DONE (124 claims; entity 2/8/2, detail 13/24/11, theme 36/0/2, forecast 15/0/11)
T10  MORNING5.md (reserved: last 20 min) ................................ DONE
Round-5 open decisions: (none; descriptive round, n = 8 by design → P1 kill line INCONCLUSIVE by n is the expected outcome)
# Round 4 — see PLAN.md "Round 4 stages". EXECUTION ORDER: V0 → B1 → A1 → K1 → D1 → T9. Stage caps: V0 30, B1 150, A1 210, K1 45, D1 60 min (orchestrator judgement time counts). T9 owns the last 30 min before the hard stop.
V0   artifact check + benchmark + pipeline verification + re-budget ..... DONE (v0_check.md; all checks OK; 5.0 min)
B1   controlled paired contexts, meanings A/B (human; PRIMARY CONTROLLED)  DONE — INCONCLUSIVE by n (eligible eval carriers 0/48: omission 64/64); 12.4 min
A1   natural AV claims, paraphrase-averaged preference (human; PRIMARY) .. DONE — A1 INCONCLUSIVE by n (in-primary eval slots 4/30), A1-nat INCONCLUSIVE by n (4/15); 27.0 min
K1   K-way alternative ranking on deterministic-swap claims (AR only) .... DONE — NOT MET (in-prefix top-1 0.308, top1−0.125 CI [0.096,0.265]; positive control 0.449); 12.8 min
D1   claim-direction ablation via the AR as encoder (greedy AV; one γ) ... DONE at cap — NOT MET (random − own persist_word 0.209 [0.111,0.311], n=91 non-last; 111/140 rows, 29 incomplete); 60.2 min
T9   MORNING4.md (reserved: last 30 min) ................................ DONE (834 lines, 5 kill lines)

## Blockers
D1: stage cap (60 min) reached at 111/140 rows; 29 rows (round-robin tail of each stratum) not generated — partial results reported under the pre-registered rules (n=91 non-last ≥ 60).
(note: the loop slept from 03:09 to 09:31 — fallback wakeup fired late — leaving 116 min for D1 + T9)

## Open decisions (research calls left for the human)
(none — the round-4 cut rules are pre-declared in PLAN.md V0; apply them in order and record which applied)

## Notes
V0 re-budget (0.14 min per judgement task, uniform measured rate; v0_check.md): CUT RULES APPLIED — A1(a) paraphrases 2+2→1+1 (light1, aggr1); A1(b) negation candidate dropped; A1(c) contexts 60→40 (dev 10, eval 30 by selection order) — A1 still projects 256 min > 210 cap after all three cuts, so A1 runs to its cap and reports partial results by n; B1(a) fillings 5→4 (drop f4; 32 pairs / 64 contexts; eval 24 pairs / 48 contexts; the B1 minimum of 32 eligible eval carriers is therefore reachable only if ≥ 32 of the 48 eval contexts are eligible); B1(b) not applied (paraphrases stay 2+2); K1 no cut; D1 no cut (140 rows). B1 position check: min t = 55, no second filler.
Rounds 1–3c complete and merged into main; artifacts in this directory and out/ (acts_L20.npz is required by K1 and D1; present).
Round 4 helpers go in overnight/r4_lib.py; nla_lib.py is read-only. Each stage persists <stage>_progress.json (cumulative minutes, phase, failure count); AWAITING_AGENT_TASKS / MISSING exits are normal transitions; saved generations are never regenerated; every unit is checkpointed as it completes.
Round 4: all editor / judge tasks are done by the orchestrator (Claude) via the agent-judgement protocol in PLAN.md; the TARGET is never used as an LLM. Labels are PROVISIONAL; every analysis script must accept --labels for the human's relabelling. Review sheets: open <stage>_review_blind.csv first, <stage>_review_key.csv after.
