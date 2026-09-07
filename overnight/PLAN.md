# Nightshift — Round 3 / 3b plan for the NLA project (round 1–2 artifacts are in this directory; never overwrite them)

**ROUND 3b (planned 2026-09-06 23:15, runs after round 3 has written MORNING3.md) — THIS IS THE ROUND TO
EXECUTE. Stages are in "Round 3b stages" at the end of this file; execution order is in STATE.md.
Round-3 stages above are complete (T3 cut at its cap) and are reused read-only.**

**Human review of round 3 with the third advisor (2026-09-06 ~23:00; verbatim in
`notes/advisor_round3_feedback.md`).** Round 3 results: C1 NOT MET (snippet keeps 79% of its deletion
cost when moved to the front), C2 NOT MET (four-way margin M = 0.019, 40/40 pairs > 0), T1 INCONCLUSIVE
(AR topic probe AUROC 0.61; RepE 0.74–0.81), T2 NOT MET (candidate-continuation topic AUROC 0.75,
no-injection 0.49, foreign-swap 0.77; yes/no format 0.55 MET), T2-claims lp(original) − lp(corrupt)
9.78 injected vs 1.39 no injection, T4 NOT MET (sports words in 100% of descriptions at an 18° rotation
of the injected vector; random direction 17.5%). The human and advisor:
- **Prioritise validating the forced-prefix readout over any new steering experiment.** The emerging
  result is a comparison of two interfaces to one NLA: reconstruction scoring largely misses the tested
  factual edits; targeted AV likelihoods may recover the information. Round 4 (distributed edits) stays
  deferred.
- **Three things to keep apart in every readout number:** *self-consistency* (the AV prefers a word it
  generated itself), *activation dependence* (the preference changes when the activation changes),
  *factual recovery* (the preference follows an independently known source fact). The T2-claims 97.3%
  number is self-consistency by construction (prefix and "original" word are the AV's own greedy output;
  "original" ≠ "true"). T2b tests activation dependence only; **T2c is the factual-recovery test and the
  primary stage of this round**; C3 is a meaning-preserving phrasing control, not a zero-information edit.
- **Audit before headline:** the prior-corrected AUROC 0.935 was not pre-registered (round-3 T2 asked
  only for the no-injection AUROC) → exploratory. T2a confirms on a held-out prefix wording frozen below,
  reports within-pair choice accuracy with CIs, and compares AR-probe / RepE / prefix readout on the same
  160 items and labels.
- **Wording corrections for the write-up (bench: use these phrasings in MORNING3b):** "substantially more
  sensitive to wording and relevance than to the tested factual corruptions" (not "reads wording, not
  facts"); "local-snippet dominance persists across positions" (moving it cut its cost by ~21%, so not
  "content, not position"); "the tested instructions did not produce the requested changes" (not "ignores
  instruction text"); T4 "replicates injected-concept sensitivity", not the outside-J-space result (no
  J-space complement was built); report rotation angles as angles (18° ≈ 31% of the norm for equal-norm
  vectors, not "small"); the blind/raw-context scores 0.429/0.473 sit well above the empty baseline 0.347.
- **Finish plan:** T2c → T2a → T2b → C3; cut T3 at its cap and report the completed sample and stopping
  rule; no new steering task; three central figures (reconstruction specificity, local-snippet ablation,
  targeted readout with donor controls).

**Merge note for the desk (not the bench):** merge round 3 with
`git merge --no-commit --no-ff nightshift/round3 && git checkout HEAD -- CLAUDE.md overnight/PLAN.md overnight/STATE.md`
so main's plan and stage list win; copy `overnight/out/*.npz` (acts_L20, recon_L20, c2_acts, t1_repe,
t3_dirs, t4_dirs) before removing the worktree.


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

**Third-advisor input (2026-09-06 late):** stay with NLAs; first make the existing result
unassailable (position-vs-content control C1; matched semantic discrimination C2), then readout
pilots (T1/T2/T4), then one frozen steering experiment with baselines (round 4 proposal). Working
title suggested: "What does an NLA reconstruction score measure? Testing semantic readout and
causal control beyond local-token reconstruction." The human intends to write up after round 3
before refining further.

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

### C1 — position vs content: does the last snippet dominate because of what it says or where it sits? (AR only, ~10 min)
Round 1–2 found the final "expecting X" snippet carries 88% of the lift. Two explanations: local
content matters, or the AR weights the end of its input. Disentangle:
- For each evaluation explanation with ≥ 3 claims: `z_rot` = the last claim moved to the FRONT, all
other claims in original order (same claims, one position change). Also `z_rev` = claims reversed.
- Score `cos(z_rot)`, `cos(z_rev)`; deletion cost of the local snippet in `z` (from S2) vs in `z_rot`
(recompute: delete it from `z_rot`); deletion cost of the claim that is now last in `z_rot`.
- **Kill C1:** paired CI of [local-snippet deletion cost in `z_rot` − in `z`] **≤ −0.05 → MET**
(the snippet loses most of its weight when moved: dominance is positional, not content).
Report the raw numbers whatever the outcome; both readings are useful.
- **Build:** `c1_position.py`. Outputs `c1_expl.csv`, `c1_summary.md`.

### C2 — matched semantic discrimination: two activations that differ in one fact (TARGET + AV + AR, ~40 min)
The round-1 corruption test edited the *text*; the activation was fixed. This edits the
*activation*: two contexts identical except one earlier fact, same final token and suffix.
- **Stimuli (agent-written from fixed templates, 40 pairs, seed 0):** e.g.
`The capital of the country is {Paris|Lyon}. Tourists arrive at the main station and walk to the`
— 10 templates × 4 entity pairs, the differing entity 8–20 tokens before the end, the final 6+
tokens identical. Record `h_a`, `h_b` at the shared final token (block 20). Assert the two contexts
tokenize to the same length.
- Verbalize both (80 generations, greedy). Record whether each description mentions its own entity,
the other entity, or neither.
- **Four-way matching:** `M = [cos(h_a,AR(d_a)) − cos(h_a,AR(d_b))] + [cos(h_b,AR(d_b)) − cos(h_b,AR(d_a))]`
per pair. Also the cross-text control: `cos(h_a, AR(d_a with entity swapped to b's))` — the round-1
style text edit — so text-edit and activation-edit sensitivity sit side by side.
- **Kill C2:** CI of mean M (cluster by template) **≤ 0 → MET** (the score cannot tell which of two
one-fact-different activations a description belongs to). Report the fraction of pairs with M > 0,
and `|cos(h_a,h_b)|` (how different the activations are at all).
- **Build:** `c2_matched.py`. Outputs `c2_pairs.csv`, `c2_descriptions.jsonl`, `c2_summary.md` with
5 verbatim pairs (both descriptions, both contexts).

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
| C1 | C1 | CI of [snippet deletion cost in z_rot − in z] | ≤ −0.05 |
| C2 | C2 | CI of mean four-way margin M, cluster by template | ≤ 0 |
| T1 | T1 | AUROC cos(h,AR(true topic)) vs foreign, eval, CI by document | ≤ 0.60 |
| T2 | T2 | AUROC yes−no for true vs foreign topic, eval | ≤ 0.60 |
| T3 | T3 | French pass rate at every (ℓ, α) with parse_ok ≥ 0.5, pilot | < 0.25 |
| T4 | T4 | sports mention rate at both β, pilot | < 0.25 |
| T5 | T5 (optional) | CI of (expect-edit − paraphrase-edit) log-prob effect | ≤ 0 |

**Execution order:** T0 → C1 → C2 → T1 → T2 → T4 → T5 → T3 → T6. C1/C2 are the mandatory controls on the existing result (third advisor); T3 is last and is dropped first under the hard stop. **Hard stop: 5 h after the first
round-3 RUNLOG line. Timing estimates in stage titles are hypotheses; T0 logs measured per-item costs and the orchestrator re-budgets from them.** All round-1/2 rules apply (pilot/eval split, cluster bootstrap by document,
three outcomes, settings files created inside `main()`, raw outputs kept, FOLLOWUPS not pivots,
never overwrite round-1/2 files).

---

## Round 3b stages (2026-09-07; ~1 h compute; hard stop 2.5 h after the first round-3b RUNLOG line)

**Purpose.** Establish whether the forced-prefix likelihood readout (round-3 T2) recovers *source facts*
from the activation, as opposed to reproducing the AV's own output or reflecting broad topic
compatibility; give C2 a phrasing control; audit the T2 topic result on a held-out wording. Everything
runs on cached round-1/3 artifacts plus 80 new C3 contexts. Numbers only; all round-1/2/3 rules apply
(pilot/eval split, cluster bootstrap 1000 draws seed 0, three-way outcomes, settings files created in
`main()`, raw outputs kept, FOLLOWUPS not pivots, never overwrite an earlier round's files).

**Round-3 artifacts to reuse (read-only):** `c2_pairs.csv`, `c2_descriptions.jsonl`, `out/c2_acts.npz`,
`t2_scores.csv`, `t2_claims.csv`, `t2_prefix.py` (the `Prefix` class: injection, prefill, `cont_logprob`;
import-safe only if its Settings creation is inside `main()`, otherwise copy the class), `t0_topics.csv`,
`stimuli.csv`, `out/acts_L20.npz` (`h20`, `h20_pos2`), `c2_matched.py` (`TEMPLATES`, `build_pairs`).

**Shared readout definition (used by T2c, T2a, T2b, C3).** With activation `h` injected exactly as
`nla_lib` does (marker row replaced, asserted) and the assistant turn prefilled with `p`, the score of a
candidate string `c` is the **summed log-prob of every token of `" " + c`** (leading space; record the
token count; also report the per-token mean). `h_0` = no injection (raw marker embedding, asserted), the
prompt-only prior. Nothing generated by the AV appears in any prefix of T2c, T2a or C3.

### U0 — artifact check + T3 closeout (~5 min)
- Assert the round-3 files above exist and have the expected row counts (c2_pairs 40, t2_scores 200,
  t2_claims 691 non-error rows, t0_topics 200, acts_L20 h20/h20_pos2 [200, 3584], c2_acts 80 rows).
- **T3 closeout, report only:** from `t3_summary.md` / `t3_outputs.jsonl`, the number of pilot stimuli
  and items completed before the 5100 s cap, the stopping rule as pre-registered, and the kill line
  as written. Do NOT rerun or extend T3.
- No kill test. Write `u0_check.md`.

### T2c — forced-prefix entity readout on the C2 matched activation pairs (AV forward only, ~10 min) — PRIMARY
Question: is the upstream entity (11–17 tokens before the extraction point, never in the suffix) readable
from the final-token activation by likelihood, given that the default descriptions name it in only 11/80?
- **Prefixes (frozen; one noun per C2 template, index = template_id):**
  nouns = `["city", "ingredient", "time", "instrument", "metal", "city", "illness", "profession", "animal", "subject"]`.
  Primary `p1` = `<explanation>\nThe {noun} mentioned in the passage is`; held-out paraphrase
  `p2` = `<explanation>\nThe passage mentions the {noun}`. Same `<explanation>\n` prefill convention as
  round-3 T2. Both prefixes are run on every item; `p1` is the kill statistic, `p2` is the confirmation.
- **Candidates:** the pair's own entities `e_a`, `e_b` from `c2_pairs.csv`, scored as `" " + e` in full.
  Assert both candidates' token counts are recorded; report the count distribution.
- **Activations:** `h_a`, `h_b` from `out/c2_acts.npz`; `h_0` no injection.
- **Score:** `D(h) = lp(e_a | p, h) − lp(e_b | p, h)`. Per pair report `D(h_a)`, `D(h_b)`, `D(h_0)`.
- **Statistics (cluster bootstrap by template, 10 clusters):**
  1. *Donor sensitivity:* mean `[D(h_a) − D(h_b)]`, CI, fraction of pairs > 0. (The prior cancels here.)
  2. *Correct discrimination, raw:* fraction of pairs with `D(h_a) > 0` AND `D(h_b) < 0`; also each side.
  3. *Correct discrimination, prior-centred:* same with `D(h) − D(h_0)`.
  4. *Within-pair choice accuracy* for each activation: `argmax_c lp(c | p, h)` equals the entity in
     that context (raw and prior-centred), pooled over 80 activations, CI by template.
  5. Paired AUROC of `D(h_a)` vs `D(h_b)` over the 40 pairs.
  6. Per-template table: mean donor sensitivity, both-correct rate, own-entity mention rate from C2.
  7. Everything in 1–5 again with `p2`, and per-token-normalised.
- **Kill T2c:** CI of mean `[D(h_a) − D(h_b)]` under `p1` **≤ 0 → MET** (the entity is not readable
  from the final-token activation by forced prefix). INCONCLUSIVE if the CI straddles 0.
- **Build:** `t2c_entity.py`. Outputs `t2c_pairs.csv` (one row per pair with every lp and D), `t2c_summary.md`
  (all statistics, the full 40-row table, both prefixes). ~500 AV forwards.

### T2a — audit of the round-3 topic readout + held-out wording confirmation (AV forward only, ~10 min)
- **Audit from `t2_scores.csv` and `t2_prefix.py` (no model):** assert that the prior-corrected statistic
  used the identical prefix (`PREFILL_CC`) and candidate strings (`" " + topic`) for injected and
  no-injection runs; state in the summary that the prior-corrected AUROC was **not pre-registered** in
  round-3 PLAN (exploratory); confirm that the `(i+100) mod 200` pairing makes every title both a true and a
  foreign candidate; report **within-pair choice accuracy** with CI (by document) for raw
  (`cc_true > cc_foreign`, own activation), prior-corrected, and swap; recompute the prior-corrected AUROC
  with its CI (it was reported without one in DISCONFIRMATION.md).
- **Held-out wording (frozen now, never seen by any model):** `p3` = `<explanation>\nThe document is about`.
  Score `" " + topic_true` vs `" " + topic_foreign` on all 200 stimuli under own activation, foreign
  activation (`(i+100) mod 200`), and no injection. Evaluation set n=160 is the headline; pilot reported.
- **Same-items comparison table:** on the 160 evaluation stimuli with the same true/foreign labels: AR
  probe (T1 `t1_scores.csv`), RepE centred and direction (T1), T2 `PREFILL_CC` raw and prior-corrected,
  `p3` raw and prior-corrected. Assert the row sets are identical.
- **Kill T2a:** raw AUROC of `p3` candidate continuation (own activation, eval, CI by document) **≤ 0.60
  → MET** (the round-3 topic readout does not hold up on a held-out wording). Report prior-corrected
  AUROC with CI, within-pair accuracy with CI, swap AUROC, alongside.
- **Build:** `t2a_audit.py`. Outputs `t2a_scores.csv`, `t2a_summary.md`. ~1000 AV forwards.

### T2b — activation-dependence control for the round-3 claim-word readout (AV forward only, ~20 min)
Label in every output: **activation-dependence test, not a truth test.** The prefix and the "original" word
are the AV's own greedy output.
- **Rows:** every non-error row of `t2_claims.csv` (298 LLM single-word + 393 deterministic). Prefix and
  both candidate words exactly as round-3 T2 (`PREFILL_CLAIM + prefix words`; `word_orig`, `word_corrupt`).
  Reuse `lp_*` own and no-injection from the file; do not recompute them.
- **Donors:** (i) `h_pos2` = same document, other position (`acts_L20.npz["h20_pos2"]`) — the near donor,
  the kill statistic; (ii) `h_foreign` = `h20` of stimulus `(i+100) mod 200` — the far donor.
- **Scores:** `d = lp_orig − lp_corrupt` under own (`d_own`, from file), `d_pos2`, `d_foreign`, `d_noinj`
  (from file). Paired `d_own − d_pos2`, `d_own − d_foreign`; fraction `d > 0` under each; split LLM /
  deterministic / last-claim-only as in `t2_summary.md`; CIs cluster by explanation.
- **Source-support proxy (mechanical, reported):** `in_ctx` = `word_orig` occurs (case-insensitive whole
  word) in `context_left_64 + token_str` of the stimulus (what the activation could have seen); also with
  `context_right_16` added. Report every statistic split by `in_ctx`.
- **Human labelling sheet (bench builds, human fills in the morning):** `t2b_support_sheet.csv`, 30 rows
  sampled with seed 0 from evaluation LLM-corrupt rows: `row, stim_idx, claim, word_orig, word_corrupt,
  context_left_64, token_str, context_right_16, d_own, d_pos2, d_foreign, d_noinj, label_supported`
  (last column empty). The bench does NOT fill the label.
- **Kill T2b:** CI of mean `(d_own − d_pos2)` **≤ 0 → MET** (the preference for the original word does
  not depend on which activation of the same document is injected: self-consistency, not readout).
  Report `d_own − d_foreign` alongside, not as a kill.
- **Build:** `t2b_donor.py`. Outputs `t2b_claims.csv`, `t2b_support_sheet.csv`, `t2b_summary.md`.
  ~2800 AV forwards at ~0.4 s.

### C3 — meaning-preserving phrasing control for C2, factorial (TARGET + AV + AR, ~25 min)
C2 has no null: a description generated from `h_a` fits `h_a` better than one generated from any other
activation. This adds a one-word, meaning-preserving wording change in the same sentence as the entity
and asks (i) whether the score's margin for the fact edit exceeds its margin for the phrasing edit and
(ii) whether the T2c entity readout survives the phrasing change. Call it a *phrasing control*, not a
zero-information edit.
- **Wording pairs (frozen; index = template_id; `(w1 → w2)` replaces the first occurrence in the
  template's first sentence; `w1` is the existing C2 text):** primary
  `[("country","nation"), ("calls","asks"), ("moved","shifted"), ("orchestra","ensemble"), ("pure","solid"),
  ("story","tale"), ("was","got"), ("worked","served"), ("team's","club's"), ("shows","depicts")]`;
  fallback if the primary changes the token count under the TARGET tokenizer:
  `[("Tourists","Visitors"), ("Stir","Mix"), ("printed","typed"), ("plays","performs"), ("carefully","gently"),
  ("during","in"), ("explained","described"), ("leaves","exits"), ("wave","raise"), ("painting","picture")]`.
  (Desk check 2026-09-06 23:20 with the Qwen2.5 tokenizer: all ten primaries preserve token count for all
  entities; wording-word distance to the end 12–20 tokens vs entity 11–17. "clear→cloudless" was dropped
  for changing the count. All 80 C2 entities are single tokens with a leading space.)
  Assert equal token count for all four contexts of a cell and the same shared suffix rule as C2; if both
  primary and fallback fail for a template, drop that template, log it, and report on the rest (never
  invent a third pair). Record the wording word's distance to the end next to the entity's.
- **Cells:** for each of the 40 C2 pairs, contexts A = (a, w1), B = (b, w1) (existing, activations and
  descriptions reused from C2), C = (a, w2), D = (b, w2) (new: 80 TARGET forwards, 80 AV generations,
  greedy 200 tokens). Record `h_C`, `h_D` at the final token as C2 did; save to `out/c3_acts.npz`.
- **Reconstruction margins (AR):** score all four descriptions against all four activations (16 per cell).
  `M_fact(w1)` = C2's M (recomputed from the same numbers, assert equal); `M_fact(w2)` on C, D;
  `M_wording(a)` = `[cos(h_A,d_A) − cos(h_A,d_C)] + [cos(h_C,d_C) − cos(h_C,d_A)]`; `M_wording(b)` on B, D.
  Report `cos(h_A,h_B)`, `cos(h_A,h_C)`, `cos(h_B,h_D)` (activation distance per edit type), entity
  mention rates in the new descriptions, and identical-description count.
- **Readout under the phrasing change (AV forward, `p1` from T2c):** `D(h)` for all four activations;
  donor sensitivity at w2: `D(h_C) − D(h_D)`; 2×2 decomposition: entity main effect
  `mean[D(h_A) + D(h_C)] − mean[D(h_B) + D(h_D)]` vs wording main effect
  `mean[D(h_A) + D(h_B)] − mean[D(h_C) + D(h_D)]`; both-correct rate at w2.
- **Kill C3 (score):** CI (cluster by template) of mean `[mean(M_fact(w1), M_fact(w2)) − mean(M_wording(a),
  M_wording(b))]` **≤ 0 → MET** (the reconstruction score discriminates a one-word phrasing change as well
  as a one-word fact change). Report the activation-distance difference next to it, since a larger
  activation change trivially gives a larger M.
- **Kill C3 (readout):** CI of mean `[D(h_C) − D(h_D)]` **≤ 0 → MET** (the T2c entity preference does not
  survive a phrasing change). Only meaningful if T2c was NOT MET; report regardless.
- **Build:** `c3_phrasing.py` reusing `c2_matched.py` and the T2c scorer. Outputs `c3_cells.csv`,
  `c3_descriptions.jsonl`, `c3_summary.md` with 3 verbatim cells (all four contexts and descriptions).
  Memory: TARGET alone, then AV+AR co-resident (AR for the margins, AV for the readout; never TARGET+AV).

### T7 — morning report
`overnight/MORNING3b.md`: kill lines, the T2c table (40 rows), the T2a same-items comparison table, the T2b
donor table split by `in_ctx`, the C3 2×2 table, verbatim examples, the T3 closeout paragraph, FOLLOWUPS,
provenance (what the bench built vs what was pre-registered here), wall-clock. Use the write-up phrasings
listed in the round-3b review block at the top of this file. Commit. Stop the loop.

## Pre-registered thresholds (round 3b)
| K | stage | statistic | MET if |
|---|---|---|---|
| T2c | T2c | CI (by template) of mean [D(h_a) − D(h_b)] under p1 | ≤ 0 |
| T2a | T2a | raw AUROC of held-out prefix p3, own activation, eval, CI by document | ≤ 0.60 |
| T2b | T2b | CI (by explanation) of mean (d_own − d_pos2) | ≤ 0 |
| C3-score | C3 | CI (by template) of mean [M_fact − M_wording] | ≤ 0 |
| C3-readout | C3 | CI (by template) of mean [D(h_C) − D(h_D)] under p1 | ≤ 0 |

**Execution order (round 3b):** U0 → T2c → T2a → T2b → C3 → T7. T2c is primary and runs first after the
check; C3 is last and is dropped first under the hard stop. **Hard stop: 2.5 h after the first round-3b
RUNLOG line.** Stage cap 45 min. Timing estimates are hypotheses; U0 may re-budget from round-3 measured
costs (AV forward 0.3–0.4 s, AV generation 10 s, AR score 0.36 s, TARGET short forward 0.11 s).
