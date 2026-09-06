# Nightshift — Round 3 plan for the NLA project (round 1–2 artifacts are in this directory; never overwrite them)

**Human review of rounds 1–2 (2026-09-06 evening), recorded before round 3 was planned.**
The human read the round-1/2 morning reports, the desk summary (`notes/findings_so_far.md`) and
the gap analysis against an external advisor (`notes/progress_vs_advisor.md`), and:
- **Accepted** the findings as stated: pipeline reproduces (cos 0.882, position-specific); the
  reconstructor scores wording and relevance, not facts (one-fact corruption 0.003 < paraphrase
  0.005, all-claims corruption 0.0075 < 0.014, off-topic swap AUROC 0.955); the final "expecting X"
  snippet carries 88% of the lift; the verbalizer does not follow instruction text (0/200).
- **Redirected** two framings: (a) do not write "failed to reproduce" the NLA paper's deletion
  result — we did not run their natural true/false test; ours refines it (`notes/nla_paper_card.md`);
  (b) do not say steered outputs were "identical" — they differ like a sampling seed would
  (similarity 0.57 vs 0.17 across stimuli), content/format/length unchanged.
- **Rejected** for now: migrating to the 27B checkpoint (hardware; revisit only as a late
  robustness replication).
- **Accepted for round 3** (this plan): four inference-only ways to make the existing AV/AR pair
  answer questions about an activation without retraining — AR as a zero-shot text probe (T1),
  forced-prefix yes/no readout from the AV (T2), residual-stream steering of the AV itself (T3),
  and perturbing the injected vector with a target-model concept direction (T4). The human wants
  these because they are the inference-time route to "is concept X in this activation / is the
  model confident / in conflict" questions, which the fixed template cannot ask.
- **Desk-proposed, human has NOT yet confirmed:** T5, a steering-specificity test on the target
  using the round-1 corrupted/paraphrased claims. It runs last and only if STATE.md carries the
  line `T5: HUMAN-CONFIRMED`; otherwise skip it and say so.
- **Deferred to a round-4 proposal** (`notes/round4_distributed_edit_proposal.md`, under
  review): the distributed / coordinated-edit direction from a second advisor.

**Purpose (round 3, overnight 2026-09-06→07, ~4 h).** Given that the verbalizer ignores prompt
text, can the *existing* checkpoints still be made to answer targeted questions about an
activation? Four routes, each with a built-in ground truth (the document's own topic; the target's
next-token entropy), each on cached round-1 activations. Numbers only.

**Round-1/2 artifacts to reuse (read-only):** `stimuli.csv` (topic = the wikitext document's
first ` = Title = ` heading; R0 extracts it), `explanations.jsonl`, `out/acts_L20.npz`,
`out/recon_L20.npz`, `s3_edits.jsonl`, `s3_scores.csv`, `nla_lib.py`, `s5_steer.py` (variant
prompt construction), `src/patching.py` (block hooks; read-only).

**You are:** an autonomous orchestrator running under `/loop` inside a git worktree.
Branch `nightshift/round3`. Your working directory is this worktree.

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
- **Round end:** write `overnight/MORNING3.md` (measurements, kill-test log, provenance:
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

## Round 3 stages

### T0 — artifact check + topic and entropy sidecar (~10 min)
- Assert counts as in round 2 R0 (200 / 200 / 671 / 538 / 490) and that both npz caches exist
(if not, regenerate exactly as round-2 R0 did, with the same ±0.002 acceptance).
- **Topics:** for each stimulus, `topic_true` = the first ` = X = ` heading of its wikitext
document (strip ` = `), `topic_foreign` = the topic of the stimulus at `(stim_idx + 100) mod 200`
(disjoint documents by construction). Write `t0_topics.csv`.
- **Entropy:** one TARGET pass per document (batch 1, raw text) recording next-token entropy
(nats) and top-1 probability at `pos` for all 200 stimuli → `t0_entropy.csv`. Also record the
target's top-1 next token string.
- No kill test. Write `t0_check.md`.

### T1 — the reconstructor as a zero-shot text probe (AR only, ~10 min)
Idea: the AR maps English to activation space; cos(h, AR(sentence)) is a probe for any sentence.
- **Probe sentences (fixed):**
  - topic: `This text is about {topic}.` for `topic_true` and `topic_foreign`.
  - confidence: `The model is highly confident about the next token.` vs
  `The model is uncertain about the next token.`
  - conflict (exploratory): `The model is torn between two continuations.` vs
  `The model has one clear continuation in mind.`
  - two neutral fillers as a floor: `This is a sentence.`, `Text.`
- **Matched nearby contrast (the hard level, reuses round-1 edits):** for each of the 490 accepted
S3 triples, score the claim ALONE: `cos(h, u(c))`, `cos(h, u(c*))`, `cos(h, u(c~))` with
`u(d) = AR(d)/‖AR(d)‖`. Report the paired difference true−corrupted (does the probe prefer the
true claim over its one-fact corruption?) and true−paraphrase (wording null), with CIs, and the
fraction of triples where true > corrupted. This is the distinction the whole-explanation score
missed (0.003); a claim-alone probe is not diluted by the final snippet.
- **Standard-probe baseline (RepE / difference-of-means):** for the topic test, build a direction
in the TARGET at block 20 from 16 agent-written sentences about `topic_true` minus 16 about
`topic_foreign` (fixed seed, per stimulus pair; last-token activations), and score
`cos(h, d̂_true−foreign)`. Report its AUROC next to the AR-probe AUROC. The AR probe is only
interesting if it is competitive with a probe built from the same English.
- **Scores:** `s_topic = cos(h, AR(true)) − cos(h, AR(foreign))`; `s_conf = cos(h, AR(confident))
− cos(h, AR(uncertain))`; likewise `s_conflict`. AUROC of `cos(h, AR(true))` vs
`cos(h, AR(foreign))` over the 160 evaluation stimuli (paired). Spearman(`s_conf`, −entropy) and
Spearman(`s_conflict`, entropy). Endpoint is **prediction of next-token entropy**, not
introspective confidence. Report the Spearmans within token-type bins (punctuation / word-piece /
word-initial, from `token_str`) as well as pooled, since punctuation positions have low entropy.
- **Kill test T1:** topic AUROC (evaluation) with 95% bootstrap CI (by document) **≤ 0.60 → MET**
(text-specified topic probing fails for these wordings, this template and these positions;
the confidence/conflict probes are then reported but not interpreted). A NOT MET on the distant
topic alone largely repeats the round-1 relevance result; the matched-claim contrast is the
number that matters.
- **Build:** `t1_arprobe.py`. Outputs `t1_scores.csv` (per stimulus, all cosines), `t1_summary.md`
with AUROC + CI, the two Spearmans with CIs, mean cos for fillers, and 10 fixed rows (eval rows
0,16,…,144) showing topic_true / topic_foreign / both cosines / entropy.

### T2 — forced-prefix yes/no readout from the verbalizer (AV forward only, ~15 min)
Idea: prompt text is ignored, but a prefilled assistant turn must be continued.
- **Construction:** default AV prompt with injection exactly as `nla_lib`, then prefill the
assistant turn with `<explanation>\nQuestion: {q} Answer:` and read the next-token logits.
Score = `logit(" Yes") − logit(" No")` (assert both are single tokens; else log token ids used).
- **Second format, closer to training (candidate continuation):** prefill
`<explanation>\nThe passage concerns` and compare the summed log-prob of the continuation
` {topic_true}` vs ` {topic_foreign}` (tokenize both; report token counts; length-normalise and
also report unnormalised). Same for the 490 S3 claim pairs where the corruption changes a single
word: prefill the claim up to the changed word and compare the original vs corrupted word's
log-prob. **Swap control:** the same prefix with the foreign activation injected must prefer the
foreign topic — report both directions.
- **Questions (fixed, yes/no format):** `Is this activation from a text about {topic}?` for true and foreign
topic; `Is the model confident about the next token?`; `Is the model torn between two
continuations?`; and a **no-injection control**: the same prompts with the marker embedding left
as the raw `㈎` embedding (asserted), to measure prompt-only bias.
- **Subset that matters:** split stimuli by whether `topic_true` (case-insensitive) appears in the
default explanation from `explanations.jsonl`. Report every T2 statistic on the subset where it
does NOT appear — that is where a readout beats "default description + text-only QA".
- **Kill test T2:** AUROC of the candidate-continuation score for true vs foreign topic over
evaluation stimuli **≤ 0.60 → MET** (the yes/no format is reported alongside; a general
preference for "Yes" or for the commoner noun is not evidence — report the no-injection AUROC
and the mean yes−no under no injection). Also report the no-injection AUROC (should be ≈0.5) and
Spearman(confidence score, −entropy).
- **Build:** `t2_prefix.py`. Outputs `t2_scores.csv`, `t2_summary.md` (AUROCs with CIs, no-injection
AUROC, Spearmans, mean yes-minus-no per question, 10 fixed rows).

### T3 — residual-stream steering of the verbalizer itself (AV + AR, ~45 min, pilot set 0–39)
Idea: bypass the ignored prompt by adding a direction inside the AV during generation.
- **Directions (difference of means inside the AV, computed once):** run the AV (no injection,
plain text) on 32 French vs 32 English sentences (fixed list hard-coded from the S5 French
stoplist sentences; agent writes 32 simple parallel pairs, e.g. `The weather is cold today.` /
`Il fait froid aujourd'hui.`) and take mean residual difference at block ℓ over the last token;
ℓ ∈ {8, 14}. Second direction: `terse` — 32 one-word answers vs 32 long sentences.
- **Steering:** add `α · d/‖d‖ · mean‖h_ℓ‖` at block ℓ output at every generated position,
α ∈ {1, 2, 4}. Greedy, 200 tokens, injection unchanged and asserted.
- **Measures:** French mechanical pass rate (S5 rule), word count (terse), parse_ok, cjk,
`cos(AR(output), h)` vs the S5 V0 cos for the same stimulus, **and separately** topic-preservation
rate (does `topic_true` survive) and word-sequence similarity to V0 — a cos of 0.88 can survive
while the topical claims change, so reconstruction alone is not evidence of preserved content.
The directions are built from French vs English *text*, not from instructions, to avoid encoding
the instruction words.
- **Kill test T3:** French pass rate **< 0.25 at every (ℓ, α) with parse_ok ≥ 0.5 → MET** (the AV
is not steerable by residual addition either, at doses that keep it fluent). INCONCLUSIVE if no
cell reaches parse_ok ≥ 0.5.
- **Build:** `t3_avsteer.py`. Outputs `t3_outputs.jsonl`, `t3_summary.md` (grid table: pass rate,
parse_ok, mean cos, mean Δcos vs V0; 4 fixed verbatim examples at stimuli 0, 7, 19, 33 for the
best cell).

### T4 — perturbing the injected vector with a target-model concept direction (AV + AR, ~30 min, pilot set)
Idea: the mirror of T3 — which directions can the AV read?
- **Directions (difference of means in the TARGET at block 20, last token):** `sports` (32
sentences about sports vs 32 matched neutral sentences, agent-written, fixed), `french` (the 32
French/English pairs from T3, run through the TARGET). Norm-preserving mix:
`h' = ‖h‖ · normalize((1−β) ĥ + β d̂)`, β ∈ {−0.5, −0.25, +0.25, +0.5}, plus a norm-matched **random direction** at β = 0.5.
Record the **actual** geometry per item: `cos(h, h')` and the angle, since the AV renormalises to
norm 150 and β is not a comparable dose across items.
- **Measures:** keyword mention rate in the explanation (sports list / French-language detection),
`cos(AR(desc'), h)` and `cos(AR(desc'), h')`, parse_ok, and **collateral**: does `topic_true`
still appear in the description (topic-preservation rate), word-sequence similarity to the
unperturbed explanation.
- **Prior art (UNVERIFIED, from a critique): a LessWrong post "NLAs read thoughts beyond the
J-space" reportedly shows NLAs recover injected concepts; if so T4 is a control/replication, not a
finding. Fetch and read before writing.**
- **Kill test T4:** mention rate for `sports` **< 0.25 at both positive β → MET** (a large injected concept
direction does not surface in the description; the AV's readout is not direction-additive).
- **Build:** `t4_inject.py`. Outputs `t4_outputs.jsonl`, `t4_summary.md`, 4 fixed examples.

### T5 — steering-specificity test on the target (OPTIONAL; runs only if STATE.md says `T5: HUMAN-CONFIRMED`)
- **Gate G5 (donor patch):** for 40 pilot stimuli, replace h at `pos` with h_pos2 (same document)
at block 20 and measure the KL between original and patched next-token distributions; **if median
KL < 0.05 nats → site not steerable, skip the rest and report.**
- **Edits:** from `s3_edits.jsonl`, three edit types of the LAST claim only (the one that carries
the score): corrupt, paraphrase, and a desk-supplied `expect` edit that changes the quoted
expected continuation (agent builds it by replacing the quoted string after "expecting" with the
target's actual top-1 next token vs a random other token; log the rule).
- **Vector:** `u(d) = AR(d)/‖AR(d)‖`, `v = ‖h‖ (u(d*) − u(d))`, `h' = h + α v`, α ∈ {0.5, 1, 2}.
- **Measures:** change in log-prob of the edited-in expected token and of the original top-1; KL
to original; the same for paraphrase-derived v (null) and norm-matched random v.
- **Kill test T5:** paired (expect-edit effect − paraphrase-edit effect) on the edited-in token's
log-prob, CI ≤ 0 → MET.
- **Build:** `t5_specificity.py`. Outputs `t5_scores.csv`, `t5_summary.md`.

### T6 — morning report
`overnight/MORNING3.md`: kill lines, the T1/T2 AUROC table, T3/T4 grids, T5 if run, verbatim
examples, FOLLOWUPS, provenance, wall-clock. Commit. Stop the loop.

## Pre-registered thresholds (round 3)
| K | stage | statistic | MET if |
|---|---|---|---|
| T1 | T1 | AUROC cos(h,AR(true topic)) vs foreign, eval, CI by document | ≤ 0.60 |
| T2 | T2 | AUROC yes−no for true vs foreign topic, eval | ≤ 0.60 |
| T3 | T3 | French pass rate at every (ℓ, α) with parse_ok ≥ 0.5, pilot | < 0.25 |
| T4 | T4 | sports mention rate at both β, pilot | < 0.25 |
| T5 | T5 (optional) | CI of (expect-edit − paraphrase-edit) log-prob effect | ≤ 0 |

**Execution order:** T0 → T1 → T2 → T4 → T5 → T3 → T6. T3 is last and is the first stage dropped under the hard stop. **Hard stop: 5 h after the first
round-3 RUNLOG line. Timing estimates in stage titles are hypotheses; T0 logs measured per-item costs and the orchestrator re-budgets from them.** All round-1/2 rules apply (pilot/eval split, cluster bootstrap by document,
three outcomes, settings files created inside `main()`, raw outputs kept, FOLLOWUPS not pivots,
never overwrite round-1/2 files).
