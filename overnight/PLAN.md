# Nightshift — Round 1 plan for the NLA project

**Purpose.** Stand up the full NLA round-trip on the released Qwen2.5-7B-Instruct layer-20 pair
(target → verbalizer → reconstructor → cosine) on our own stimuli, then measure a **claim
usefulness score**: for each claim in a verbalizer explanation, how much does deleting it change
reconstruction? The hypothesis under test — not an assumption of the plan — is that this score
responds to *factual* corruption of a claim more than to equally sized superficial edits of the
same claim. Two further stages: whether the verbalizer obeys instruction text at inference time
(S5), and, if time remains, how well a describer that never sees the activation reconstructs it
(S4). Every stage reports numbers and a three-way pre-registered outcome per kill test; the
human decides what they mean.

**Vocabulary.** "Deletion improves reconstruction" is a statement about the reconstructor, not
about truth. A true but redundant claim can have positive Δ; a false claim can lower Δ through
correlated concepts. Write "usefulness to the reconstructor", never "true/false", in any output.

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
- **Round end:** write `overnight/MORNING1.md` (measurements, kill-test log, provenance:
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

## Stimuli (fixed; S0 builds them once, every later stage reads the file)

- Source: wikitext-2-raw-v1 **train** split, document level. Keep documents with ≥ 300 tokens
under the TARGET tokenizer. Shuffle with `seed=0`; take the first **200** documents.
- Raw text, **no chat template**, `add_special_tokens=False`, truncated to the first 512 tokens.
- One position per document: `pos ~ Uniform{16, …, min(len, 512) − 1}`, `numpy` RNG `seed=0`,
drawn in document order.
- A **second position per document** (`pos2`) drawn by the same rule from the same RNG stream,
redrawn until `|pos2 − pos| ≥ 8`; used by the same-document controls in S1 and S3.
- Save `overnight/stimuli.csv`: `doc_idx, pos, pos2, token_str, context_left_64, context_right_16`
(detokenized), and `overnight/out/acts_L20.npz` holding `h20[200, 3584]` fp32 at `pos`, plus
`h19`, `h21` at `pos` (S1 diagnostic) and `h20_pos2` (same-doc controls).

---

## Stages

### S0 — library + stimuli + 16-position smoke on wikitext
The round trip is already proven on one chat prompt (see Reference implementation); S0 proves it
on **our** stimuli and library code, and produces the activation cache every later stage uses.
- **Kill test K0:** verbalize the first 16 stimuli. `cjk_rate` = fraction of the 16 explanations
containing any CJK character (regex `[　-鿿가-힯]`). **threshold: cjk_rate > 0.25 →
MET** (injection not working on raw-text activations: the AV is describing the marker glyph).
Also log `parse_ok` rate.
- **Build:** `overnight/nla_lib.py` (vendored from `scripts/nla7b_roundtrip.py`, see above), then
`overnight/s0_smoke.py` — build the full 200-position stimulus set and `overnight/out/acts_L20.npz`
(layers 19/20/21 at the main position, layer 20 at the same-doc second position; TARGET only,
then free), then load AV, verbalize stimuli 0–15, free AV, load AR, score. Acceptance:
`overnight/stimuli.csv` has 200 rows, the npz has the four arrays, and `overnight/s0_smoke.csv`
has 16 rows (`doc_idx, pos, cos, n_tokens, parse_ok, cjk`).
- **Report:** `s0_summary.md` — load times, RSS after each load, seconds per explanation, the
16 cos values with their tokens, K0 line.

### S1 — baseline round trip on 200 positions
- **Kill test K1a:** mean cos over the 160 **evaluation** AV explanations (block 20).
**threshold: mean cos < 0.50 → MET** (pipeline is not reproducing the published fidelity on our
stimuli; note the published 0.752 FVE was on WildChat+FineWeb, so a modest gap is expected and
is not itself MET).
- **Kill test K1b (position specificity):** for each evaluation position i, cos(AR(z_i), h_j)
for a random other document j (seed 0) — the cross-document score — and cos(AR(z_i), h_pos2)
for the second position of the same document — the same-context score. **threshold: mean
cos_shuffled_samedoc ≥ mean cos_own − 0.05 → MET** (an explanation reconstructs a *different
position of the same context* about as well as its own; explanations are not
position-specific). Report the cross-document version alongside.
- **Positive control (no kill):** `cos_empty` = AR applied to the template with an empty
explanation, against each h. Report mean cos_own − mean cos_empty. This is the "whole
explanation deleted" reference every S2 delta is read against.
- **Build:** `overnight/s1_roundtrip.py`. Stimuli and `acts_L20.npz` come from S0. Load AV,
verbalize all 200 (greedy, 200 tokens; ~35 min at 10 s each — reuse the 16 from S0 only if the
prompt and decoding are byte-identical), free AV. Load AR, reconstruct every explanation, save predictions to
`overnight/out/recon_L20.npz` so later stages score against any activation without re-running.
Outputs: `overnight/explanations.jsonl` (`doc_idx, pos, raw_generation, explanation, parse_ok,
n_tokens, cjk`), `overnight/s1_recon.csv` (`doc_idx, pos, cos_own, cos_shuffled_doc,
cos_shuffled_samedoc, cos_L19, cos_L21, n_tokens, act_norm`).
  - `cos_shuffled_samedoc`: same document, a second position drawn with the same rule
  (its activation is already in `acts_L20.npz` from S0).
  - `cos_L19` / `cos_L21`: the AV explanation for block 20 scored against the block-19 and
  block-21 activations at the same position. **Diagnostic only** for the off-by-one question;
  do not switch layer whatever it shows — log the numbers under OPEN DECISIONS if L19 or L21
  beats L20.
- **Report:** `s1_summary.md` — mean / median / p10 / p90 of `cos_own`; the same for the two
shuffles and the two adjacent layers; Spearman(n_tokens, cos_own); mean cos binned by
`act_norm` tercile; fraction `parse_ok`; 5 verbatim explanations chosen by a seed (not
cherry-picked) with their context window. Both K1 lines.

### S2 — claim deletion: does the reconstructor distinguish edit types?
- **Claim splitter (fixed):** split the explanation on newlines, then on `(?<=[.!?])\s+`; strip;
drop pieces shorter than 3 words; drop leading list markers (`^\s*(\d+[.)]|[-*•])\s*`). Keep the
original order. Explanations with < 2 claims are excluded from S2/S3 and counted.
- **Per claim i of explanation z:** `Δcos_i = cos(AR(z \ c_i)) − cos(AR(z))`, where `z \ c_i` is
the remaining claims re-joined with a single space. Also `Δcos_all = cos_empty − cos(z)`
(delete everything; the positive control from S1) and `cos_alone_i = cos(AR(c_i))`.
- **Matched superficial edits of the same claim (controls):**
  - `randspan`: remove a random contiguous span of words from z with the same word count as
  `c_i`, not aligned to claim boundaries (3 draws, seeds `1000 + row`).
  - `shuffle_words`: shuffle the word order *inside* `c_i` only, keep everything else (1 draw).
  - `shuffle_order`: reorder the claims of z (1 draw per explanation).
- **Kill test K2 (comparative, not a magnitude threshold):** paired over evaluation claims,
`D = |Δcos_i| − mean_draws |Δcos_randspan_i|`. **MET if the cluster-bootstrap 95% CI of mean D
lies at or below 0** (deleting a whole claim is indistinguishable from deleting a random
equal-length span; claims are not units the reconstructor sees). **INCONCLUSIVE if the CI
straddles 0.** Also required: `|Δcos_all|` ≥ 5× median `|Δcos_i|` is *reported*, not a kill
— it says whether small per-claim effects are redundancy rather than insensitivity.
- **Build:** `overnight/s2_deletion.py`, AR only. Outputs `overnight/s2_claims.csv` (one row
per claim: `doc_idx, pos, split, claim_idx, n_claims, n_words, Δcos, Δcos_randspan_1..3,
Δcos_shuffle_words, cos_alone`) and `overnight/s2_expl.csv` (`doc_idx, pos, split, n_claims,
cos_z, cos_empty, Δcos_all, cos_shuffle_order, cos_best_single_deletion`). `split` ∈
{pilot, eval}.
- **Report:** `s2_summary.md` — n kept / excluded; `n_claims` histogram; distribution of `Δcos`
(mean, median, p10, p90, CI); **fraction of claims with Δcos > 0** overall and by claim index
(first / middle / last), with CI; the same distributions for each control; mean D with CI;
`Δcos_all` distribution; Spearman(`n_words`, `Δcos`). K2 line.

### S3 — corrupted claims: does the score respond to factual change more than to superficial change?
Design (per the reviewer): for each evaluation claim `c_i`, produce a **corrupted version `c_i*`**
that changes exactly one checkable fact to a contradictory value with matched wording and
length, and a **paraphrase `c_i~`** that preserves meaning. Then compare how the reconstructor
treats `z`, `z*` (c_i replaced by c_i*) and `z~` (c_i replaced by c_i~).
- **Editor:** plain `Qwen/Qwen2.5-7B-Instruct`, chat template, greedy, `max_new_tokens=120`.
Prompts (fixed, one claim per call, output between `<out></out>` tags):
  - CORRUPT: `Rewrite the sentence below changing exactly ONE checkable fact (a name, a number,
  a place, a category, or a polarity such as positive/negative) to a clearly contradictory value.
  Keep every other word, the length, and the style identical. Output only the rewritten
  sentence inside <out></out> tags.\n\nSentence: {claim}`
  - PARAPHRASE: `Rewrite the sentence below so that it says exactly the same thing with
  different wording. Do not add, remove or change any fact. Keep the length similar. Output
  only the rewritten sentence inside <out></out> tags.\n\nSentence: {claim}`
  - **Mechanical acceptance** of an edit: tags parsed; word count within ±30% of the original;
  at least one word changed; for CORRUPT, not identical to PARAPHRASE. Rejected edits are kept
  in the file with `edit_ok=False` and excluded from statistics; report the rejection rate.
  - **Deterministic corruption (second type, no LLM):** if `c_i` contains a number, replace
  the first number by a different one (`n → n+7`, or `n×3` if n<3); else if it contains a
  capitalised token that is not sentence-initial, swap it for a capitalised token drawn from
  another evaluation explanation (seed `3000 + row`); else `numeric_ok=False`. Column
  `Δcos_corrupt_det`.
  - **Off-topic swap (third type, weakest):** replace `c_i` by a claim from another document
  (seed `2000 + row`). Not "false by construction"; reported for continuity with S2 only.
- **Primary statistic (paired, per claim):**
  `A_i = Δcos_i(z*) − Δcos_i(z)` — does removing the corrupted claim from `z*` improve
  reconstruction *more* than removing the original claim from `z`? Positive A supports the
  hypothesis. Same for the paraphrase: `P_i = Δcos_i(z~) − Δcos_i(z)`, expected ≈ 0.
  **Secondary:** `cos(z) − cos(z*)` (does corruption hurt the whole explanation at all) and
  `cos(z) − cos(z~)`; AUROC of `Δcos` for corrupted vs original claim as a descriptive number.
- **Kill test K3:** cluster-bootstrap 95% CI of `mean A_i − mean P_i` on evaluation claims with
`edit_ok=True`. **MET if the CI lies at or below 0** (the score does not respond to a factual
contradiction more than to a meaning-preserving rewording — for *this* corruption type).
**INCONCLUSIVE if the CI straddles 0 or fewer than 100 accepted claims.** Report the same for
the deterministic corruption separately.
- **Build:** `overnight/s3_corrupt.py`. TARGET (as editor) + AR co-resident is allowed.
Outputs `overnight/s3_edits.jsonl` (`doc_idx, pos, claim_idx, claim, corrupt, paraphrase,
corrupt_det, offtopic, edit_ok, editor_raw_corrupt, editor_raw_paraphrase`),
`overnight/s3_scores.csv` (one row per claim × edit type: `cos_z, cos_z_edit, Δ_z, Δ_z_edit`),
`overnight/s3_summary.md`.
- **Report:** rejection rates; means and CIs of A, P, A − P, the secondary statistics, and the
AUROC; **10 fixed examples (evaluation claims at rows 0, 16, 32, …, 144 of the accepted list)
shown verbatim: original, corrupted, paraphrase, and the four Δ values** — the human checks
in the morning whether the editor actually produced contradictions. K3 line.

### S4 — blind-describer and raw-context baselines (OPTIONAL — runs last, only if the hard
stop is > 100 minutes away)
Interpretation is deliberately narrow: a strong blind score shows that reconstruction *can* be
achieved from the visible context (which the activation itself was computed from). It does
**not** show that the verbalizer ignores the activation. Report the gap; write nothing else.
- **Kill test K4:** paired over the 160 evaluation positions, `gap = cos_AV − cos_blind`.
**threshold: cluster-bootstrap 95% CI of mean gap entirely below 0.05 → MET; straddling 0.05 →
INCONCLUSIVE.**
- **Blind describer prompt (fixed; TARGET model, plain `Qwen/Qwen2.5-7B-Instruct`, chat template,
greedy, `max_new_tokens=200`):**
  ```
  You are a meticulous AI researcher conducting an important investigation into activation
  vectors from a language model. The model read the following text, and we are looking at its
  internal activation at the token marked with [[ ]].

  <text>{context_left_64}[[{token_str}]]{context_right_16}</text>

  Describe the semantic content that this activation most likely encodes. Produce an
  explanation enclosed within <explanation> tags, consisting of 2-3 text snippets describing
  that vector, in the same style a trained activation verbalizer would use.
  ```
  Note: the blind describer sees **right context** the target model could not have seen at that
  position; that makes the baseline stronger, not weaker, which is the intent (see
  `notes/nla_seed.md`, "tune the baseline to beat our own hypothesis"). Also run a
  **left-only** variant (drop `context_right_16`) on the **first 100 positions only** (time
  budget: ~10 s per generation) and report both.
- **Raw-context baseline (no describer at all):** feed `context_left_64 + token_str` verbatim
as the "explanation" to AR. Report `cos_rawctx`.
- **Build:** `overnight/s4_blind.py`. TARGET + AR co-resident is allowed (26 GB). Outputs:
`overnight/s4_blind.jsonl` (`doc_idx, pos, blind_explanation, blind_left_explanation`),
`overnight/s4_recon.csv` (`cos_AV, cos_blind, cos_blind_left, cos_rawctx, gap`).
- **Report:** `s4_summary.md` — means and medians of all four cos columns; mean gap with
bootstrap 95% CI; fraction of positions where blind ≥ AV; gap binned by `act_norm` tercile and
by `pos` tercile. K4 line.

### S5 — prompt steering of the describer
Question: if the instruction text around the injected vector changes, does the describer's
output change in the instructed way, and does it keep describing the same activation?
- **Positions:** the 40 **pilot** stimuli (0–39). Steering is exploratory and touches no
evaluation item. AV only (plus AR for scoring; AV+AR
co-residency is allowed).
- **Prompt variants (fixed wording).** Every variant keeps the line
`<concept>㈎</concept>` verbatim so the injection scan (id 149705, neighbours 29 / 522) still
passes; only the sentence marked `INSTRUCTION` changes. Template:
  ```
  You are a meticulous AI researcher conducting an important investigation into activation
  vectors from a language model. Your overall task is to describe the semantic content of that
  activation vector.

  We will pass the vector enclosed in <concept> tags into your context. You must then produce
  an explanation for the vector, enclosed within <explanation> tags. {INSTRUCTION}

  Here is the vector:

  <concept>㈎</concept>

  Please provide an explanation.
  ```
  | id | INSTRUCTION | mechanical check |
  |---|---|---|
  | V0 | `The explanation consists of 2-3 text snippets describing that vector.` (default) | — |
  | V1 opposite | `The explanation consists of 2-3 text snippets describing the OPPOSITE of the semantic content of that vector.` | none |
  | V2 emotion | `The explanation consists of 2-3 text snippets describing that vector, written in a furious, exasperated tone.` | none |
  | V3 one word | `The explanation consists of exactly ONE word that best describes that vector. Output nothing else inside the tags.` | word count == 1 |
  | V4 French | `The explanation consists of 2-3 text snippets describing that vector, written entirely in French.` | fraction of ASCII-letter tokens that are in a 200-word French stoplist ≥ 0.15 (hard-code the list) |
  | V5 question | `Answer this question about the vector, then give 1-2 text snippets: is the token this vector was taken from most likely a NOUN, VERB, or OTHER? Start the explanation with one of those three words in capitals.` | first word ∈ {NOUN, VERB, OTHER}; compare with the `token_str` POS from a fixed rule: alphabetic + not in a 50-word function-word list → "content word" (report agreement only, no gold POS) |
- **Kill test K5:** `follow_rate` = fraction of (variant, position) outputs for V3 and V4 that
pass their mechanical check (the two variants with an objective check). **threshold:
follow_rate < 0.25 → MET** (the describer ignores instruction text; it is not promptable at
inference time and every steering idea needs training).
- **Judge (agent-rubric, labelled as such).** For V1, V2, V5, the orchestrator reads each output
next to the V0 output for the same position and records, per item, in
`overnight/s5_judge.csv`: `followed (0/1)` = the instruction was visibly obeyed;
`same_referent (0/1)` = it is still recognisably about the same thing as V0 (for V1: the
*negation* of the same thing). This is an LLM-as-judge score produced by the agent under a fixed
rubric; say so in the summary. No other judgement or narrative.
- **Reconstruction:** score every variant output against the true activation: `cos_Vk`. Report
`cos_Vk − cos_V0` per variant. Of particular interest, reported flatly: V1 (opposite) — if
`cos_V1 ≈ cos_V0` the reconstructor is not reading negation; V3 (one word) — how much of the
score one word carries.
- **Build:** `overnight/s5_steer.py`. Outputs `overnight/s5_outputs.jsonl` (`doc_idx, pos,
variant, raw_generation, explanation, parse_ok, cjk, mech_pass`), `overnight/s5_recon.csv`,
`overnight/s5_judge.csv`.
- **Report:** `s5_summary.md` — per variant: mechanical pass rate, judge `followed` and
`same_referent` rates, mean `cos_Vk`, mean `cos_Vk − cos_V0`, parse_ok and cjk rates. Then a
**verbatim examples block for the human: positions 0, 7, 19, 33 (fixed) — the context window,
token, and all six variant outputs side by side.** K5 line.

### S6 — morning report
- `overnight/MORNING1.md`: every K line copied from `DISCONFIRMATION.md`; the headline tables
from every completed stage summary, including the S3 and S5 verbatim example blocks, the
contents of `FOLLOWUPS.md`; wall-clock per stage; the OPEN DECISIONS list; a provenance block
(scripts the agent wrote, choices the human pre-registered here, anything the agent had to pick
and why — e.g. a regex edge case). Commit. Stop the loop.

---

## Pre-registered thresholds, in one place
All CIs: cluster bootstrap by explanation, 1000 draws, seed 0. Outcome ∈ {MET, NOT MET,
INCONCLUSIVE}; INCONCLUSIVE whenever the CI straddles the threshold or n is under the minimum.
| K | stage | statistic (evaluation set unless stated) | MET if |
|---|---|---|---|
| K0 | S0 | cjk_rate over pilot 0–15 | > 0.25 |
| K1a | S1 | mean cos_own | < 0.50 |
| K1b | S1 | mean cos_shuffled_samedoc vs mean cos_own | ≥ cos_own − 0.05 |
| K2 | S2 | CI of mean(\|Δcos_claim\| − \|Δcos_randspan\|) | ≤ 0 |
| K3 | S3 | CI of mean(A − P), accepted claims ≥ 100 | ≤ 0 |
| K5 | S5 | follow_rate on V3+V4 mechanical checks (80 pilot items) | < 0.25 |
| K4 | S4 (optional) | CI of mean(cos_AV − cos_blind) | < 0.05 |

**Execution order:** S0 → S1 → S2 → S3 → S5 → S4 → S6. Priority is S0–S3; S4 is dropped
first under the hard stop.

## Left open on purpose (human decides after round 1)
- Chat-style stimuli (WildChat is half the training mix; none cached; not downloaded this round).
- LLM-judged claim splitting and human labelling of hallucinated claims against the context —
round 2, once S2/S3 show the AR is sensitive enough to be worth labelling for.
- Sampling temperature (greedy this round for reproducibility; the reference default is 0.7).
- Human labelling of natural (uncorrupted) claims against the context, annotators blinded to
  the reconstructor scores — day two, and only if S3 is NOT MET.
- Steering with the injected vector *removed* (random vector) as a control for S5, and steering
  variants that move the injection position — both deferred; S5 only edits the instruction sentence.
- The Celeste Qwen3.6-27B checkpoint Neel pointed at: infeasible on this machine (see
Environment). Revisit only with a rented GPU, after a gate here has passed.
