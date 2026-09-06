# CLAUDE.md — mech_interp_nla-nightshift (git worktree, branch `nightshift/round1`)

You are in the **nightshift worktree**: an isolated checkout of `mech_interp_nla` where an
autonomous `/loop` runs the overnight experiment program. The main checkout is
`/Users/mbp_qasim/repos/mech_interp_nla` — do not edit files there from here.

## State of record — read these first, in this order
1. `overnight/STATE.md` — current stage, model, blockers, open decisions.
2. `overnight/PLAN.md` — the full program with pre-registered kill tests. Every research
   choice is fixed there; do not change a listed position, layer, tier, threshold, regex or
   prompt wording. If PLAN.md still says TODO in its Stages section, the round has not been
   planned: stop and say so.
3. `overnight/DISCONFIRMATION.md` — kill-test log. A MET kill test is a result, not an abort.
4. `overnight/RUNLOG.md` — one line per stage transition.

## Hard rules (from PLAN.md; repeated here because they matter)
- One stage at a time, in the EXECUTION ORDER in STATE.md. Kill tests run first in every stage.
- Numbers only. No gate verdicts, no analysis narrative. Report measurements.
- Commit after each stage: `git add overnight/ && git commit`. Never `git push`.
- Nothing outside `overnight/` is written. `src/`, notebooks, `notes/` are read-only here.
- Never overwrite a previous round's artifacts. Large caches (`.npz`, `.pt`) go in `overnight/out/`.
- 90-min stage cap, then log the blocker and move to the next independent stage.

## Reference material (read-only; look up, do not bulk-load)
- `notes/README.md` — index of everything in `notes/`.
- `notes/nla_seed.md` — what is already known about NLAs from the previous project.
- `notes/context_600k_index.md` → line-numbered outline of `notes/context_600k.md`
  (Neel Nanda's research-process posts, glossary, paper list, tooling). Read by line range.
- `notes/neel_pragmatic_vision_interpretability.md` and
  `notes/neel_how_interp_researchers_help_agi_go_well.md` — contents block at the top of each.
- `notes/mats_paper_index.md` — index of past MATS-scholar papers.
- `src/model_utils.py` is the only model loader.

## Environment
`uv run python …` from this directory (own `.venv`). MPS. The `.to()` workaround lives in
`src/model_utils`; import it before touching `torch`. Models are in the shared HF cache.

## Role: this worktree is the bench, not the desk
This directory exists to **execute** a pre-registered experiment program, nothing else.
Ideation, discussion, literature work, planning the next round, analysis and the write-up all
happen in the main checkout, `/Users/mbp_qasim/repos/mech_interp_nla` (its CLAUDE.md describes
the full cycle). If the human starts a design discussion here, say so and point them to main —
this session's rules (numbers only, `overnight/` only, fixed pre-registrations) are deliberately
the wrong ones for thinking.

When a round ends: the loop writes `overnight/MORNING<n>.md`, commits, and stops. Main then
reviews, merges this branch, plans the next round on main, and spawns a fresh worktree. Do not
edit `PLAN.md` here after a round has ended; the next PLAN comes from main.
