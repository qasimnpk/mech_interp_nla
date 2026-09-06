# Nightshift — Round 1 plan for the NLA project

**Purpose.** *(TODO, human — written on `main` before the worktree is spawned.)* One paragraph:
what the bench must stand up while the human sleeps, and what the morning decision is.

**You are:** an autonomous orchestrator running under `/loop` inside a git worktree.
Branch `nightshift/round1`. Your working directory is this worktree.

---

## Rules of engagement

- **State of record:** `overnight/STATE.md`. Read it first every turn. Update it whenever
you finish or block a stage.
- **Log:** append one line to `overnight/RUNLOG.md` per stage transition
(`<ISO timestamp>  <stage>  start|done|blocked  <detail>`).
- **Kill tests:** every stage lists its pre-registered kill tests. Run them **first**. Append one
line per kill test to `overnight/DISCONFIRMATION.md` the moment it is computed. A MET kill test
is a result, not an abort — report it flatly, never soften, re-run or skip because of it.
- **One stage at a time, in the EXECUTION ORDER in STATE.md.** Before starting a stage, check
whether its artifact already exists and passes its acceptance check — if so, mark it done and
move on.
- **Stage cap:** ~90 min wall-clock or 5 failed iterations. Then write the blocker to
STATE.md and skip to the next stage that does not depend on the blocked one.
- **Commit after every stage:** `git add overnight/ && git commit`. Never `git push`.
- **Never guess past a research decision.** If a choice would change what the experiment
*means* (which layer, which metric, whether to drop data), log it under
OPEN DECISIONS in STATE.md and take the most conservative option, or skip.
- **Numbers only.** Do NOT decide a gate passed or failed. Do NOT write an analysis
narrative. Report measurements.
- **Scope ceiling:** only the positions, layers, models, prompts and thresholds listed below.
No per-head work, no extra sweeps, no verdicts.
  - Do NOT touch anything outside `overnight/`. You MAY *read* `src/`, `pyproject.toml`,
  `notes/` and the notebooks.
  - Do NOT modify or execute the notebooks. Do NOT delete data. Do NOT overwrite a previous
  round's artifacts.
- **Files:** code in `overnight/*.py`; small outputs (`.csv`, `.txt`, `.md`) commit
normally; large caches (`.npz`, `.pt`, `.safetensors`) go in `overnight/out/` and are
gitignored by extension — keep them, the morning review needs them.
- **Round end:** write `overnight/MORNING<n>.md` (measurements, kill-test log, provenance:
what the agent built vs what the human pre-registered), commit, stop the loop.

---

## Environment

- **Load** via `src.model_utils.load_model(repo_id=...)`. Use its `build_prompt` /
`cache_residual` / `get_blocks` / `free` helpers. The MPS `.to()` workaround lives in
`src.model_utils`; import it before touching `torch`. `uv run python …` from this directory.
- **Make the model swappable.** Every script takes `repo_id` as a CLI arg.
- Do NOT download a model that is not already in the HF cache unless the plan below names it.
- `transformers` 5.x overwrites `output_hidden_states[-1]` with the post-final-norm
`last_hidden_state`; cache residuals via forward hooks on the decoder blocks instead
(see `src/model_utils.cache_residual`).
- *(TODO, human)* target model, NLA verbalizer / reconstructor repo ids, layer, memory budget.

---

## Stages

*(TODO, human — every research choice fixed here before the loop starts: model, positions,
layers, stimulus filters, prompt wordings, metrics, and a numeric kill-test threshold per
stage. Template per stage:)*

### S1 — <name>
- **Kill test K1a:** threshold = … ; observed how = … ; MET means … .
- **Build:** `overnight/<script>.py` — inputs, outputs, acceptance check.
- **Report:** which numbers go in `overnight/<stage>_summary.md`.
