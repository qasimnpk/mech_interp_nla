# Human log — hours, decisions, and what I verified by hand

Neel's rule: ~16 h (max 20) of *human* work counts — thinking, reading, analysing, writing.
Waiting on runs does not. Keep Toggl as the primary record; this file is the narrative that
goes with the screenshot, and the "what I verified and how" ledger the write-up must contain.

## Hours (human only)
| date | hours | what |
|---|---|---|
| 2026-09-06 | _fill_ | Direction choice, checkpoint feasibility review, round-1 plan review with outside reviewer feedback, loop launch |

## Verified by hand (one line each: what, how, result)
<!-- e.g. 2026-09-07  mean cos on eval set  `python -c` over s1_recon.csv rows 40-199  0.xx, matches s1_summary -->

## Round 1 loop — launched 2026-09-06
Worktree `../mech_interp_nla-nightshift`, branch `nightshift/round1` at merge `99f8f95` (plan `b01221e`). Prompt used:

```
/loop Read overnight/STATE.md, then overnight/PLAN.md in full, then overnight/DISCONFIRMATION.md, overnight/RUNLOG.md and overnight/FOLLOWUPS.md. Execute the next TODO stage in the EXECUTION ORDER in STATE.md (S0 → S1 → S2 → S3 → S5 → S4 → S6), exactly as pre-registered in PLAN.md: kill tests first, numbers only, no verdicts, no analysis narrative, three-way outcomes (MET / NOT MET / INCONCLUSIVE). Pilot set is stimuli 0–39, evaluation set is 40–199; never edit a script after seeing evaluation outputs except to fix a crash, and log any such fix in RUNLOG. Every stage script is its own process under `uv run python`, writes its <stage>_settings.json, and saves all raw outputs including failures. Update STATE.md and RUNLOG.md at every stage transition, append every kill-test line to DISCONFIRMATION.md the moment it is computed, and `git add overnight/ && git commit` after each stage. Never push. Never write outside overnight/. Any idea beyond the plan goes as one line into FOLLOWUPS.md and is not acted on. If a stage hits its 90-minute cap or 5 failed iterations, log the blocker in STATE.md and move to the next stage that does not depend on it. Hard stop at 7 hours after the first RUNLOG line or 07:30 local time, whichever is earlier: mark the running stage blocked (time) and run S6. When S6 has written overnight/MORNING1.md and committed, stop the loop.
```
