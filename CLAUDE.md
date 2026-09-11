# CLAUDE.md — mech_interp_nla

Mechanistic-interpretability project for a MATS (Neel Nanda stream) application, on
**natural language autoencoders (NLAs)** — verbalizer/reconstructor pairs that turn an activation
vector into an English description and back. Run on open-weight Qwen models on an M-series
MacBook (MPS, 48 GB).

> **TODO (human):** replace this paragraph with the one-paragraph statement of the primary
> experiment once it is chosen. Seed material from the previous project is in
> `notes/nla_seed.md`. Nothing below assumes a particular design.

## Read first
- **`/Users/mbp_qasim/repos/mech_interp/notes/neel_drive/mats12_admissions_procedure_faq.md` — Neel's own admissions doc (kept outside this repo since 2026-09-11). The application
  is graded against it; `notes/README.md` has line pointers.** The rules that govern everything here:
  - Deadline: **Fri Sept 11, 11:59pm PT** (late-app window; Sept 4 was struck through). Extensions form linked in the doc.
  - The **application-form questions are the primary filter** — he reads those first, not every write-up.
  - **Write in your own voice.** LLM-written prose is held to a "significantly higher bar." Agent drafts
    here are scaffolding for the human to rewrite, never text to submit.
  - **"Sanity-check your agent" is the most important advice in the doc.** Read raw data; re-derive
    headline numbers with a fresh one-liner; design controls yourself; **document in the write-up what
    you verified and how.** "An agent did a project and a human forwarded it" is rejected.
  - Time: ~16 h (max 20) of *human* work — thinking, reading relevant papers, analysing, writing count;
    waiting on runs and form answers don't. +2 h for the exec summary. Track it (Toggl screenshot).
  - Exec summary: 1–3 pages, ≤600 words, graphs; then the write-up. Structure by finding, not chronology.
- `notes/nla_seed.md` — what the previous project (tool/knowledge conflict) already knew about NLAs:
  the Transformer Circuits "misreported tool calls" audit card, the "NLA information gain" fallback
  design (blind-describer baseline), and the released Qwen2.5-7B layer-20 checkpoint pointer.
- **TODO (human):** project brief and literature survey for the NLA project go here once written.

## The experiment lives in a separate worktree
`/Users/mbp_qasim/repos/mech_interp_nla-nightshift` — branch `nightshift/round1` — runs an
autonomous `/loop` overnight from `overnight/PLAN.md`. Its `overnight/STATE.md` is the state of
record; `overnight/DISCONFIRMATION.md` is the kill-test log; results land in
`overnight/MORNING<n>.md`. **From this checkout, read those files; never edit them.** Merge the
branch into `main` when a round is reviewed.

## Reference corpus — look things up, do not bulk-load
- **`notes/README.md` is the index of everything in `notes/`** — start there.
- `notes/neel_how_interp_researchers_help_agi_go_well.md` — the Pragmatic Vision's companion
  piece: which problem classes GDM's team thinks matter. Contents block at the top.
- `/Users/mbp_qasim/repos/mech_interp/notes/context_600k_index.md` → **use this to navigate** `/Users/mbp_qasim/repos/mech_interp/notes/context_600k.md` (outside this repo since 2026-09-11; Neel's 600k-token
  context file: research-process posts, Steinhardt, paper-writing advice, glossary, annotated paper
  list, Ferrando primer, Sharkey open problems, TransformerLens/NNsight/ARENA source). The file is
  2.2 MB — read by line range (`Read` with `offset`/`limit`) or `grep -n`. Regenerate the index
  with `python3 scripts/mkindex_context600k.py`.
- `notes/neel_pragmatic_vision_interpretability.md` — "A Pragmatic Vision for Interpretability"
  (Nanda et al., Dec 2025), full text, contents block with line numbers at the top. The framing the
  application is scored against: North Star → proxy task → cheapest method first.
- `notes/mats_paper_index.md` — synthesized index of all 48 papers on Neel's MATS scholar list,
  each read in full: taste tag (CURRENT/COOLED vs his stated interests), baselines/controls
  (flagged WEAK), open threads. ~45k tokens; written to be read whole when doing ideation or
  positioning, otherwise grep it.
- To archive another Alignment Forum / LessWrong post: `scripts/af_post_to_md.py`.

## Code
- `src/model_utils.py` is the **only** model loader; it carries the MPS `.to()` workaround —
  import it before touching `torch`. `src/patching.py` — residual patch sweeps, direct logit
  attribution. `src/viz.py` — display only. See `README.md`, `SETUP.md`, `notes/environment.md`.
- `uv` project; `uv run python …`. `scripts/smoke_test.py` is the correctness gate.
- Models in the shared HF cache: `Qwen/Qwen2.5-7B-Instruct` (has a released NLA at layer 20),
  `Qwen/Qwen3-4B-Instruct-2507` (harness smoke-test model). NLA checkpoints (downloaded and
  round-trip verified 2026-09-06, see `notes/nla_setup/README.md`): `kitft/nla-qwen2.5-7b-L20-av`
  (15.2 GB bf16, full 28-layer fine-tune) and `kitft/nla-qwen2.5-7b-L20-ar` (10.9 GB, 21-layer
  truncated backbone + `value_head.safetensors`); working reference `scripts/nla7b_roundtrip.py`,
  peak footprint 17 GB, ~10 s per explanation on MPS. `ceselder/qwen3.6-27b-nla-rl` does not fit
  this machine (54 GB + 35 GB bf16); partial blobs in the cache are dead weight.

## Working conventions
- Research choices (model, positions, layers, tiers, thresholds, prompt wordings, stimulus
  filters) are pre-registered in writing before an experiment runs; agents execute them and
  report **numbers only — no verdicts**. Kill tests run first; a MET kill test is a result.
- Every number in the brief must trace to a verified primary source; hedge or omit otherwise.
- The write-up declares provenance: what an agent built, what the human decided and reviewed.
- Don't rent a GPU until a gate has passed and MPS is the demonstrated bottleneck.

## Roles: this checkout vs the nightshift worktree
**This checkout (`mech_interp_nla`, `main`) is the desk.** Ideation, discussion, literature work,
planning the next round, analysis, and the write-up happen here. It is the source of truth.

**The worktree (`../mech_interp_nla-nightshift`) is the bench.** It exists only to run the
autonomous `/loop` from `overnight/PLAN.md`. Nobody ideates there; its own CLAUDE.md tells any
session to stay numbers-only and inside `overnight/`. While a round is running, do not edit
anything in it and do not merge it.

**The cycle, each round:**
1. Loop finishes → `overnight/MORNING<n>.md` written, everything committed on its branch.
2. Review from here, reading the worktree's files by path (`DISCONFIRMATION.md` first).
3. Merge the round into main: `git merge nightshift/<branch>`. Artifacts now live in main's
   history under `overnight/`. (`.npz` caches are gitignored — copy any you need first.)
4. Plan the next round **here**: edit `overnight/PLAN.md` on main, commit.
5. Fresh worktree from main for the next round:
   `git worktree remove ../mech_interp_nla-nightshift && git worktree add ../mech_interp_nla-nightshift -b nightshift/round<n+1>`.
   PLAN edits flow in; nothing is edited in two places.

If asked to plan or discuss while a round is mid-run, draft in `notes/` (e.g.
`notes/round<n+1>_plan.md`) and apply it at step 4.
