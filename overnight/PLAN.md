# Nightshift — Round 2 plan for the NLA project (round 1 artifacts are in this directory; never overwrite them)

**Purpose (round 2, 2026-09-06 daytime, ~6 h).** Round 1 found the reconstructor (AR) is
nearly blind to factual corruption of a claim: corrupting one fact moves cos by ~0.003, a
paraphrase by ~0.005 (K3 MET). Round 2 asks three cheap questions on the round-1 artifacts,
with no new verbalizer generation: **(R1) where is the fact-blindness — in the AR, or already
in the target model's own layer-20 representation of the claim text?** **(R2) does the
blindness survive amplification — corrupt every claim of an explanation, not one?** **(R3) how
much of the reconstruction does the first k claims carry (truncation curve)?** Numbers only.

**Round-1 artifacts to reuse (read-only):** `stimuli.csv`, `explanations.jsonl`,
`s2_claims.csv`, `s3_edits.jsonl` (490 accepted claim triples: original / corrupt / paraphrase,
plus corrupt_det), `s3_scores.csv`, `out/acts_L20.npz`, `out/recon_L20.npz`, `nla_lib.py`.
The `out/*.npz` caches were lost with the round-1 worktree; **R0 regenerates them** (see R0).

**You are:** an autonomous orchestrator running under `/loop` inside a git worktree.
Branch `nightshift/round2`. Your working directory is this worktree.

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
- **Three outcomes per kill test:** `MET`, `NOT MET`, or `INCONCLUSIVE`. INCONCLUSIVE is
mandatory when the stage ran on fewer evaluation items than its pre-registered minimum, when
the bootstrap CI straddles the threshold, or when the stage was blocked. Never force a binary.
- **Pilot / evaluation split (fixed):** stimuli `0–39` are the **pilot** set — use them for
smoke tests, debugging, prompt-format checks and S5. Stimuli `40–199` (n=160) are the
**evaluation** set: every headline number is computed on them, and no script may be edited after
first seeing evaluation-set outputs except to fix a crash (log such fixes in RUNLOG).
- **Uncertainty:** every headline statistic gets a 95% CI from a **cluster bootstrap by source
example** (resample explanations, not claims; 1000 draws, seed 0). Claims from one explanation
are not independent.
- **Settings file:** every stage writes `overnight/<stage>_settings.json` — git commit hash,
model repo ids and snapshot hashes, prompts verbatim, seeds, `max_new_tokens`, dtype, device,
wall-clock start/end.
- **Raw outputs always saved**, including failures (parse failures, CJK outputs, crashes with
traceback) — never filtered out of the files, only flagged in a column.
- **No autonomous threshold changes, new hypotheses, extra variants, or pivots.** Any idea
that occurs to you goes as one line into `overnight/FOLLOWUPS.md` for the human. Nothing else.
- **Hard stop:** the loop stops at **7 hours after its first RUNLOG line, or 07:30 local time,
whichever is earlier**. At the stop, whatever stage is running is marked `blocked (time)` and
S6 (MORNING1.md) runs with what exists.
- **Scope ceiling:** only the positions, layers, models, prompts and thresholds listed below.
No per-head work, no extra sweeps, no verdicts.
  - Do NOT touch anything outside `overnight/`. You MAY *read* `src/`, `scripts/`,
  `pyproject.toml`, `notes/` and the notebooks.
  - Do NOT modify or execute the notebooks. Do NOT delete data. Do NOT overwrite a previous
  round's artifacts.
- **Files:** code in `overnight/*.py`; small outputs (`.csv`, `.txt`, `.md`, `.jsonl`) commit
normally; large caches (`.npz`, `.pt`, `.safetensors`) go in `overnight/out/` and are
gitignored by extension — keep them, the morning review needs them.
- **Round end:** write `overnight/MORNING2.md` (measurements, kill-test log, provenance:
what the agent built vs what the human pre-registered), commit, stop the loop.

---

## Environment

- **Load** via `src.model_utils.load_model(repo_id=...)`. The MPS `.to()` workaround lives in
`src.model_utils`; import it before touching `torch`. `uv run python …` from this directory.
`src.model_utils.free(model)` between models; if RSS does not drop, the next stage runs in a
fresh process (every stage script is its own process anyway — never load two 7B models in one
process unless the memory table below allows it).
- **Activations:** `model(ids, output_hidden_states=True).hidden_states[21]` is the output of
block 20 (verified in `scripts/nla7b_roundtrip.py` against the released example transcript).
`transformers` 5.x only clobbers `hidden_states[-1]` (index 28), so index 21 is safe. Run one
document at a time (batch 1, no padding) and keep the full `[seq, d]` slice for the positions you
need.
- **No downloads.** Every weight is already in the HF cache: TARGET, AV (28 GB on disk incl. an
older snapshot), AR (20 GB, incl. `value_head.safetensors`). `snapshot_download(repo_id)` returns
the cached path without network. Do NOT download anything, and do NOT touch
`ceselder/qwen3.6-27b-nla-rl` (cancelled: 54 GB + 35 GB bf16 does not fit; partial blobs remain
in the cache, ignore them).
- **Datasets:** `EleutherAI/wikitext_document_level`, config `wikitext-2-raw-v1`, is in the
cache. `load_dataset("EleutherAI/wikitext_document_level", "wikitext-2-raw-v1")`. Nothing else.

### Models and memory (48 GB unified; bf16)

| role | repo id | size | notes |
|---|---|---|---|
| TARGET | `Qwen/Qwen2.5-7B-Instruct` | 15.2 GB | 28 blocks, d=3584. Activations taken from **block index 20** (0-indexed; the 21st block's output; `hidden_states[21]`). |
| AV | `kitft/nla-qwen2.5-7b-L20-av` | 15.2 GB | full fine-tune of TARGET, `Qwen2ForCausalLM`, 28 layers. `nla_meta.yaml`: injection char `㈎` id 149705, neighbours 29 / 522, `injection_scale` 150. |
| AR | `kitft/nla-qwen2.5-7b-L20-ar` | 10.9 GB | 21-layer truncated `Qwen2ForCausalLM` + `value_head.safetensors` (Linear 3584→3584, no bias). Final norm → Identity, `lm_head` stripped. Extract at **last token**. `mse_scale` 59.87. |

Allowed co-residency: TARGET+AR, AV+AR. Never TARGET+AV. Never all three.

### Reference implementation — already working on this machine
**`scripts/nla7b_roundtrip.py` (read-only) ran the full round trip on 2026-09-06**: TARGET →
`hidden_states[21]` → AV verbalize → AR reconstruct, 67 s wall for 4 positions with the three
models loaded one at a time, peak footprint 17 GB, cos 0.87–0.91 matching the released example
transcript to ±0.01 (`notes/nla_setup/README.md`, raw numbers in
`notes/nla_setup/nla7b_roundtrip_out.json`). **AV decode is ~10 s per ~140-token explanation
on MPS** — budget with that number. Copy its `av_prompt_ids`, `verbalize` and
`reconstruct_and_score` logic into `overnight/nla_lib.py` (keep every `assert`: tokenizer drift,
marker neighbours, `critic_suffix_ids` tail, AR layer count) and reuse it from every stage script.
Do not re-implement from the README; do not clone anything. The recipe, for reference:

- **AV prompt:** `nla_meta.yaml → prompt_templates.av` formatted with `injection_char`, placed as
the single user turn, `tok.apply_chat_template([...], tokenize=False, add_generation_prompt=True)`,
then `tok(text, add_special_tokens=False)`. Locate the injection position by scanning for token
id 149705 and asserting neighbours 29 and 522 (`>` and `<`). Build `inputs_embeds` from
`model.get_input_embeddings()`, then overwrite that row with `v * 150 / ||v||₂` (norm in fp32).
Generate with `inputs_embeds=` (no `input_ids`). Qwen2.5 has no BOS and `embed_scale` 1.0.
- **AV decoding:** greedy (`do_sample=False`), `max_new_tokens=200`. Explanation = text inside
`<explanation>…</explanation>`; if the tags are absent, use the whole generation and set
`parse_ok=False`.
- **AR scoring:** `template.format(explanation=z)` with `Summary of the following text:
<text>{explanation}</text> <summary>`, `add_special_tokens=True`, forward the backbone, take
`last_hidden_state[0, -1]`, apply `value_head`. Report **cos** between prediction and the true
activation, and `mse = 2(1 − cos)` (identical information; cos is the headline).
- **Sanity:** `nla-inference` README says clean positions land around cos 0.9 and the pair's
in-distribution FVE is 0.752. Early positions (< ~10 tokens) and rare high-norm positions decode
badly; that is expected, not a bug.

---

## Round 2 stages

### R0 — artifact check + cache regeneration (~15 min)
- Assert every reused file above exists and row counts match round 1 (200 stimuli, 671 claims,
538 S3 edit rows with 490 `edit_ok`).
- Regenerate `out/acts_L20.npz` exactly as round-1 S0 did (`s0_smoke.py` stimulus/activation
code; same docs, `pos`, `pos2` from `stimuli.csv`; TARGET `hidden_states[21]`, batch 1, raw text)
and `out/recon_L20.npz` (AR on every `explanations.jsonl` text). **Acceptance:** mean cos_own on
the evaluation set recomputed from the regenerated caches equals the round-1 value 0.8820 to
±0.002 — write both numbers to `r0_check.md`. If not, STOP with the blocker. No kill test.

### R1 — fact-blindness locus: target representation vs reconstructor
- **Inputs:** the 490 accepted S3 triples (c, c*, c~) plus `corrupt_det` where present.
- **Target side:** run each claim text through TARGET (raw text, no chat template,
`add_special_tokens=False`), take `hidden_states[21]` at the **last token** and also the
**mean over tokens**. `d_corr_T = 1 − cos(h(c), h(c*))`, `d_para_T = 1 − cos(h(c), h(c~))`.
- **AR side:** `d_corr_AR = 1 − cos(AR(c), AR(c*))`, `d_para_AR = 1 − cos(AR(c), AR(c~))`
(AR on the single claim, template as usual).
- **Kill test R1:** paired `S_T = d_corr_T − d_para_T` (last-token). **MET if the cluster-bootstrap
95% CI (by explanation) of mean S_T ≤ 0** (the target's own representation of the claim text
is no more sensitive to the factual change than to rewording — blindness is upstream of the
AR). Report `S_AR` the same way, and the ratio `d_corr/d_para` for both, plus mean-pooled
variants. INCONCLUSIVE if the CI straddles 0.
- **Build:** `r1_locus.py`, TARGET + AR co-resident. Outputs `r1_scores.csv` (one row per
triple: all d's), `r1_summary.md` with a 2×2 table (target / AR × corrupt / paraphrase) and
the 10 fixed S3 example rows with their four d values.

### R2 — amplified corruption (AR only)
- For each evaluation explanation with ≥ 2 accepted claims: `z**` = every accepted claim
replaced by its corruption (unaccepted claims kept original), `z~~` = every accepted claim
replaced by its paraphrase, `z*det` likewise with `corrupt_det` where present.
- Report `cos(z) − cos(z**)`, `cos(z) − cos(z~~)`, paired difference with CI, fraction of
explanations where corruption hurts more than paraphrase.
- **Kill test R2:** CI of mean[(cos(z) − cos(z**)) − (cos(z) − cos(z~~))] ≤ 0 → MET (even
corrupting every claim is indistinguishable from paraphrasing every claim).
- **Build:** `r2_amplify.py`. Outputs `r2_expl.csv`, `r2_summary.md`.

### R3 — truncation curve (AR only)
- For each evaluation explanation with n claims, score the first k claims for k = 1..n, and
the last k claims, and (from S2) each single claim alone. Report mean cos vs k, lift over floor
`(cos_k − cos_empty)/(cos_z − cos_empty)`, the k at which median lift first exceeds 0.9, and
Spearman(claim word count, cos_alone). No kill test; descriptive.
- **Build:** `r3_truncate.py`. Outputs `r3_curve.csv`, `r3_summary.md`.

### R4 — morning report
- `overnight/MORNING2.md`: kill lines, the R1 2×2 table, R2 and R3 headline tables, wall-clock,
FOLLOWUPS, provenance. Commit. Stop the loop.

## Pre-registered thresholds (round 2)
| K | stage | statistic (evaluation set) | MET if |
|---|---|---|---|
| R1 | R1 | CI of mean(d_corr_T − d_para_T), last-token, n ≥ 300 | ≤ 0 |
| R2 | R2 | CI of mean[(cos z − cos z**) − (cos z − cos z~~)] | ≤ 0 |

**Execution order:** R0 → R1 → R2 → R3 → R4. **Hard stop: 5.5 h after the first round-2 RUNLOG
line.** Round-1 rules (pilot/eval split, cluster bootstrap, three outcomes, settings files
created inside `main()` not at import, raw outputs kept, FOLLOWUPS instead of pivots) all apply.
