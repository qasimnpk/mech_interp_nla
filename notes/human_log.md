# Human log — hours, decisions, and what I verified by hand

Neel's rule: ~16 h (max 20) of *human* work counts — thinking, reading, analysing, writing.
Waiting on runs does not. Keep Toggl as the primary record; this file is the narrative that
goes with the screenshot, and the "what I verified and how" ledger the write-up must contain.

## Hours (human only)
| date | hours | what |
|---|---|---|
| 2026-09-06 | _fill_ | Direction choice, checkpoint feasibility review, round-1 plan review with outside reviewer feedback, loop launch |
| 2026-09-06 | _fill_ | Morning read of MORNING1 (agent summary), round-2 launch |

## Verified by hand (one line each: what, how, result)
<!-- e.g. 2026-09-07  mean cos on eval set  `python -c` over s1_recon.csv rows 40-199  0.xx, matches s1_summary -->
- 2026-09-06 08:50 (AGENT, desk session, not human): re-derived S1 eval mean cos_own = 0.882 (n=160) and S3 mean A = 0.00313, P = 0.00494, A−P = −0.00181 (n=490) from s1_recon.csv / s3_scores.csv with a fresh pandas script; matches MORNING1. Human re-derivation still owed.
- 2026-09-06 09:55 (AGENT, desk): verified R0 regenerated caches reproduce 0.8820 (diff +0.00003, per-row max 0.0). Re-derived from s2_claims.csv / s3_scores.csv: deletion cost by claim position first −0.010 / middle −0.017 / last −0.125; corruption vs paraphrase cost by position first 0.0012/0.0035, middle 0.0033/0.0057, last 0.0048/0.0055. Human re-derivation still owed.
- (human) ...

## Round 1 loop — launched 2026-09-06
Worktree `../mech_interp_nla-nightshift`, branch `nightshift/round1` at merge `99f8f95` (plan `b01221e`). Prompt used:

```
/loop Read overnight/STATE.md, then overnight/PLAN.md in full, then overnight/DISCONFIRMATION.md, overnight/RUNLOG.md and overnight/FOLLOWUPS.md. Execute the next TODO stage in the EXECUTION ORDER in STATE.md (S0 → S1 → S2 → S3 → S5 → S4 → S6), exactly as pre-registered in PLAN.md: kill tests first, numbers only, no verdicts, no analysis narrative, three-way outcomes (MET / NOT MET / INCONCLUSIVE). Pilot set is stimuli 0–39, evaluation set is 40–199; never edit a script after seeing evaluation outputs except to fix a crash, and log any such fix in RUNLOG. Every stage script is its own process under `uv run python`, writes its <stage>_settings.json, and saves all raw outputs including failures. Update STATE.md and RUNLOG.md at every stage transition, append every kill-test line to DISCONFIRMATION.md the moment it is computed, and `git add overnight/ && git commit` after each stage. Never push. Never write outside overnight/. Any idea beyond the plan goes as one line into FOLLOWUPS.md and is not acted on. If a stage hits its 90-minute cap or 5 failed iterations, log the blocker in STATE.md and move to the next stage that does not depend on it. Hard stop at 7 hours after the first RUNLOG line or 07:30 local time, whichever is earlier: mark the running stage blocked (time) and run S6. When S6 has written overnight/MORNING1.md and committed, stop the loop.
```

## Round 2 loop — launched 2026-09-06 ~09:10
Worktree recreated on `nightshift/round2` at merge `893a21d` (plan `d5e64d7` + R0 cache-regeneration fix). Round-1 `out/*.npz` caches were lost when the desk agent force-removed the round-1 worktree; R0 regenerates them and must reproduce 0.8820 ± 0.002.
Prompt: as round 1 (in this file above) with execution order R0 → R1 → R2 → R3 → R4, R0 acceptance on the regenerated caches, settings files created in main(), hard stop 5.5 h.

Round 2 finished 09:24 (22 min). R1 MET, R2 MET, R3 descriptive. Merged into main as e25793b.

## Round 3 and 3b — 2026-09-06 19:47 → 2026-09-07 00:43 (desk record; human review owed)
Round 3 (`nightshift/round3`, merged 0f9f122): C1 NOT MET, C2 NOT MET, T1 INCONCLUSIVE, T2 NOT MET (yes/no MET), T4 NOT MET, T3 MET at the 85-min cap (35/40), T5 skipped. Round 3b (`nightshift/round3b`, merged 2d2d91e; plan fe12e3b after the third advisor's feedback): T2c NOT MET, T2a NOT MET, T2b NOT MET, C3-score INCONCLUSIVE, C3-readout NOT MET. Crash fixes logged in RUNLOG (round 1 S3 line 12, round 2 R1 line 24, round 3b C3 line 58), all pre-output, no statistic changed.
- 2026-09-07 01:20 (AGENT, desk): re-derived T2c donor 1.738 / frac 0.775 / both-correct 0.225 (t2c_pairs.csv); T2a p3 accuracy raw 0.781 / corrected 0.944 (t2a_scores.csv, eval); T2b d_own − d_pos2 = 7.347 (t2b_claims.csv); C3 fact − wording 0.00782, readout 1.772 (c3_cells.csv). Human re-derivation still owed — one-liners in human-plan.md §2.
