# Nightshift — Round 3 / 3b / 3c plan for the NLA project (round 1–2 artifacts are in this directory; never overwrite them)

**ROUND 3c (planned 2026-09-08 morning; runs after round 3b, merged) — THIS IS THE ROUND TO EXECUTE.
Stages are in "Round 3c stages" at the end of this file; execution order is in STATE.md. Rounds 1–3b are
complete and reused read-only. This round is a long queue: the orchestrator may run for many hours. Every
stage is pre-registered; a stage that fails its gate is reported and skipped, never rescued.**

**Human review of round 3b and the literature (2026-09-07, three advisors; verbatim in
`notes/advisor_round3_feedback.md`, `notes/response_to_reframing_2026-09-07.md`, `notes/round3c_plan_draft.md`).**
- Dingeto (arXiv 2607.20379, Jul/Aug 2026) already audits this exact released pair with claim flips (≈2% of specific
  claims grounded; paraphrase keeps 0.89 of the score). Our finding 2 is therefore a replication with a paired design.
  The NLA paper already applied a late-layer NLA to earlier activations ("more striking content, less coherent").
  A public model card (Solshine gemma-4-e2b NLA) reports teacher-forced discrimination "reproducible with an
  untrained model". Consequences: the likelihood readout needs a base-model control before it can be attributed to
  NLA training (U1); cross-layer work is only worth doing with an independently verified readout (X1); the pieces
  that are ours are the per-position decomposition (finding 3), the source-edit pairs (C2/C3), the AV's own
  likelihood as a readout with donor controls, promptability/steering (S5/T3) and injected-direction sensitivity (T4).
- Lead question for the write-up: *what task-relevant information survives a released NLA's
  verbalization–reconstruction pipeline, and can targeted access recover what its standard interface misses?*
- Two corrections carried into every stage below: (a) if the un-finetuned interpreter matches the AV, the signal is
  not an artifact; activation-dependent recovery may be real while NLA training adds little to this readout — report
  as such, never "artifact"; (b) compute estimates are not budgets: U0c benchmarks a small batch of every model call
  type and re-budgets before anything is scheduled.
- Progression the round tests: does the trained interpreter add value (U1) → what limits its score (X3) → does
  that limit matter for behaviour (RT, gated) → does the readout transfer across layers (X1) → what does the frozen
  AR reward (N3) → where in the target does the fact/phrasing displacement live (N4) → does reconstruction error
  warn of errors beyond uncertainty (M, gated pilot).
- The application does NOT depend on any stage here. The human's review budget for the round is ≤ 60 min.


**ROUND 3b (planned 2026-09-06 23:15; COMPLETE, merged 2d2d91e) — superseded by ROUND 3c below. Stages are in "Round 3b stages" at the end of this file; execution order is in STATE.md.
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

---

## Round 3c stages (2026-09-08; long queue; hard stop 9 h after the first round-3c RUNLOG line)

**Execution order: U0c → U1 → X3 → X1 → N3 → N4 → X1b → RT → M → T8.** Stage caps: 60 min (RT and M: 90 min).
A stage whose gate fails is reported in one line and skipped. Numbers only; all round-1–3b rules apply (pilot/eval
split, cluster bootstrap 1000 draws seed 0, three-way outcomes, settings files created in `main()`, raw outputs kept,
FOLLOWUPS not pivots, never overwrite an earlier round's files, never write outside `overnight/`).

**Reuse (read-only):** `stimuli.csv`, `explanations.jsonl`, `out/acts_L20.npz`, `t0_topics.csv`, `t0_entropy.csv`,
`s2_claims.csv`, `s3_scores.csv`, `s3_edits.jsonl`, `c1_expl.csv`, `c2_pairs.csv`, `out/c2_acts.npz`, `c3_cells.csv`,
`t2_scores.csv`, `t2a_scores.csv`, `t2c_pairs.csv`, scorers in `t2_prefix.py`, `t2a_audit.py`, `t2c_entity.py`,
`nla_lib.py`. `src/patching.py` may be read and copied, not edited.

**Shared readout definition (all likelihood stages):** default AV prompt with the activation injected exactly as
`nla_lib` (marker id 149705, rescale to norm 150, marker row replaced and asserted), assistant turn prefilled with a
prefix `p`; score of candidate `c` = summed log-prob of every token of `" " + c` (per-token mean also reported).
`h_0` = no injection (raw marker embedding). Prior-corrected score = `lp(c | h) − lp(c | h_0)` **computed with the
same interpreter's own no-injection run**. Prefixes: `p3 = "<explanation>\nThe document is about"` (topic, held-out in
T2a), `PREFILL_CC = "<explanation>\nThe passage concerns"` (topic, round 3), `p1 = "<explanation>\nThe {noun} mentioned
in the passage is"`, `p2 = "<explanation>\nThe passage mentions the {noun}"` (entity; nouns per template as in T2c).

### U0c — artifact check + micro-benchmark + re-budget (~15 min)
- Assert the reuse files exist with expected row counts (stimuli 200; t2a_scores 200; t2c_pairs 40; c2_pairs 40;
  s3_scores rows with `edit_ok`; acts_L20 h20 [200, 3584]; c2_acts 80 rows).
- **Benchmark before scheduling:** time 5 calls of each type actually used below — TARGET short forward, TARGET
  forward on a 512-token document with all hidden states, AV forward with prefill, AV generation (200 tokens), AR
  score, and a TARGET forward with a residual hook at block 20 — and write the measured s/item to `u0c_check.md`.
  Re-budget every stage from these numbers; if a stage's projected time exceeds its cap, cut its item count by the
  pre-declared rule in that stage (never change what is measured).
- No kill test.

### U1 — does NLA training improve targeted activation readout? (TARGET weights in the AV interface; ~30 min) — REQUIRED
Question: does the trained AV recover more source information than the original `Qwen/Qwen2.5-7B-Instruct` given the
same injected activation? "Baseline" = the un-finetuned instruct model, not random weights.
- **Matched interface (assert every item):** identical prompt token ids, marker position, injection rescale to 150,
  attention mask and position handling, candidate strings, likelihood aggregation, dtype (bf16) and scoring code. The
  only difference is the weights. Implement by constructing the `nla_lib.AV` object from the TARGET snapshot with the
  AV's `nla_meta` injection parameters; log that the role assert was bypassed. Never TARGET-as-AV and the real AV
  co-resident with the AR.
- **Conditions:** own activation, matched swapped activation (topic: the `(i+100) mod 200` foreign document; entity:
  the twin), no injection. Each model's prior correction uses its own no-injection scores.
- **Datasets:** (1) the 160 evaluation documents with `p3` (primary) and `PREFILL_CC` (secondary); (2) the 40 entity
  pairs with `p1` (primary) and `p2` (secondary). The AV-generated claim-prefix rows (T2b) are NOT used here.
- **Primary measurements:** paired topic-choice accuracy AV − baseline, raw and prior-corrected, bootstrap of the
  paired difference by document; entity-choice accuracy, both-correct rate and donor sensitivity per interpreter,
  paired differences by template. AUROC secondary. Also each interpreter's swap-following rate.
- **Text-only reference (reported, no kill):** the un-finetuned model reads the full prefix (tokens 0..pos) as plain
  text followed by `\nThe document is about`, scoring the same two titles; prior = the same prompt with the prefix
  removed. A match with the AV shows the task is solvable from text; it does not prove inversion.
- **Kill U1:** CI (by document) of the paired difference [AV − baseline] in **raw** `p3` choice accuracy **≤ 0 → MET**
  (NLA training does not improve this readout under the tested interface; not equivalence). Reported alongside: the
  same for prior-corrected accuracy, and for entity donor sensitivity.
- **Interpretation, pre-committed:** AV > baseline with donor sensitivity → training improves the readout; similar
  and both follow the donor → useful readout exists, training advantage not established; baseline > AV → training
  may impair this readout; neither follows the donor → priors/confounds may explain apparent performance.
- **Stop rule:** no prompt or injection-scale search for either model.
- Build `u1_base.py`. Outputs `u1_topic.csv`, `u1_entity.csv`, `u1_text.csv`, `u1_summary.md` (side-by-side table on
  identical items; 10 fixed rows). ≈2,500 TARGET-weight forwards.

### X3 — does the dominant local snippet suppress factual discrimination? (AR only; ~30 min) — MAIN EXPLANATORY EXTENSION
For activation h and condition c: `G_c = cos(AR(T_c), h) − cos(AR(F_c), h)`, T = explanation with the original claim,
F = the same with the corrupted claim (the accepted S3 corruption), differing only in the substitution.
- **Rows:** accepted S3 triples (corrupt and paraphrase both `edit_ok`, eval) whose claim is not the last claim
  (`claim_idx < n_claims − 1`) and whose changed word does not occur in any other claim of the explanation (string
  check; exclude repeats). Also run the paraphrase (P) in every condition so `A − P` is available.
- **Validity subset (reported, not a filter for the primary):** label each original claim supported / not supported
  against the full prefix (tokens 0..pos) and each corruption contradicting / not, with the TARGET as judge (fixed
  prompt, greedy; store raw judge outputs); report the primary statistic on all rows and on the judge-valid subset.
- **Conditions:** (1) full explanation; (2) local snippet removed (the last claim deleted, remaining claims joined by
  one space); (3) equal-length non-local removal: delete a random contiguous span of words equal to the snippet's
  word count from the other non-tested claims, never touching the tested claim (seed 1000 + row).
- **Feasibility gate (before scoring):** count rows with enough non-tested, non-snippet text for condition (3)
  (available words ≥ snippet words). Report the count. If < 100 rows, condition (3) is run on what is eligible and
  the interaction statistic is reported as INCONCLUSIVE with n; never substitute a shorter deletion.
- **Primary statistic:** `I = (G_2 − G_1) − (G_3 − G_1)`, mean with CI cluster by explanation.
- **Kill X3:** CI of mean I **≤ 0 → MET** (removing the snippet does not improve factual discrimination more than
  removing comparable other text). Report G_1, G_2, G_3, the three A − P margins, the three AUROC(Δ corrupt vs Δ
  paraphrase), and the mean absolute cos per condition (a large collapse limits interpretation).
- **Interpretation, pre-committed:** I > 0 with G_2 > G_1 → consistent with the snippet suppressing discrimination;
  G_2 ≈ G_3 > G_1 → general context/length effect; no change → snippet dominance does not explain the insensitivity;
  cos collapse under (2) → out-of-distribution caveat. This is a property of the frozen scorer, not of training.
- Build `x3_snippet.py`. Outputs `x3_scores.csv`, `x3_judge.jsonl`, `x3_summary.md`, 5 verbatim rows. ≈3,000 AR forwards.

### X1 — cross-layer readout with the fixed layer-20 AV (TARGET then AV forwards; ~30 min)
Question: how does independently verified recovery change when the layer-20 AV reads other layers? Exploratory
(same examples as T2c/T2a). The NLA paper reports cross-layer application is feasible but less coherent; this
measures verified readout, not fluency.
- **Layers (frozen):** blocks 16, 20, 24, 27 = `hidden_states[17, 21, 25, 28]`. Injection unchanged (norm 150; a scalar
  before rescaling changes nothing). No whitening, no learned map.
- TARGET forward on the 80 C2 contexts and the 200 stimuli, save the four layers to `out/x1_acts.npz`; assert the
  block-20 rows match `c2_acts.npz` / `acts_L20.npz` to 1e-3.
- Entity (`p1`, `h_a`, `h_b`, `h_0`) and topic (`p3`, own / foreign / none, eval 160) at each layer. Report **per layer,
  separately**: donor sensitivity (CI by template), both-correct, choice accuracy raw and prior-centred; topic raw and
  prior-corrected AUROC and accuracy, swap-following.
- **Kill X1:** entity donor-sensitivity CI **≤ 0 at every non-training layer (16, 24, 27) → MET** (no readable transfer).
  Reported: which layer maximises accuracy; whether donor sensitivity and accuracy move together. Pre-committed
  readings: accuracy better elsewhere → training layer is not the best extraction layer for this task; donor
  sensitivity up without accuracy → distribution shift changes the readout without making it useful; both down →
  a measurable transfer limit.
- Build `x1_layers.py`. Outputs `x1_entity.csv`, `x1_topic.csv`, `x1_summary.md`. ≈500 TARGET + ≈1,500 AV forwards.

### N3 — what does the frozen AR reward: correct specific / wrong specific / generic / omitted (AR only; ~15 min)
Tests the NLA paper's stated hypothesis that a thematically matched wrong specific reconstructs better than omitting
the specific. Rows: the accepted deterministic-swap triples (`corrupt_det`, n≈402, eval), where the swapped token
is a number or a capitalised name.
- Four versions of the claim inside the full explanation: original; wrong specific (the det swap); **generic**
  (number → `a number`, name → `a person` if the swap list marks it as a person name else `a place`; rule logged, no LLM);
  **omitted** (the claim deleted; from S2).
- Report cost of each relative to the original (cos drop), CIs by explanation, and the pairwise differences
  wrong − generic and wrong − omitted.
- **Kill N3:** CI of [cost(generic) − cost(wrong specific)] **≤ 0 → MET** (no evidence the frozen AR prefers a wrong
  specific over a generic). Reported: cost(omitted) − cost(wrong). This says what the frozen scorer rewards, not what
  training caused.
- Build `n3_generic.py`. Outputs `n3_scores.csv`, `n3_summary.md`, 5 verbatim rows. ≈1,200 AR forwards.

### N4 — fact-vs-phrasing displacement across all layers in the TARGET (TARGET only; ~10 min)
Descriptive. For the 40 C3 cells (contexts A, B, C, D) record `hidden_states[l]` at the final token for every l in
1..28; report per layer mean (1 − cos) for the entity edit (A vs B, C vs D) and the phrasing edit (A vs C, B vs D),
their ratio, and CI by template. Also for the 490 S3 claim texts (c, c*, c~ as raw text, last token) the R1 distances
per layer. No kill; a flat or rising curve is reported without a mechanism claim. Build `n4_layers.py`. Outputs
`n4_curve.csv`, `n4_summary.md`. ≈160 + ≈1,500 TARGET forwards.

### X1b — OPTIONAL: cross-layer full generations (AV; ~20 min) — dropped first among the optionals
40 pilot stimuli, greedy explanations from block-16 and block-27 activations (80 generations). Report parse_ok, CJK
rate, quoted-final-token accuracy, "expecting"-candidate hit rate on the target's top-1 next token (shuffled-pairing
floor at block 20: 0.029 [0.012, 0.056]; own 0.444), word overlap with the block-20 explanation, `cos(AR(desc), h_l)`
and `cos(AR(desc), h_20)`. No kill. Build `x1b_gen.py`. Outputs `x1b_outputs.jsonl`, `x1b_summary.md`, 4 fixed
examples (stimuli 0, 7, 19, 33).

### RT — does task-relevant information survive the NLA round trip? (GATED 8-pair pilot; TARGET + AV + AR; cap 90 min)
Question: can an activation reconstruct well while losing information the target needs for its answer?
- **Contexts (frozen; raw text, no chat template):** template
  `{N1} received the {O1}. {N2} received the {O2}.\nQuestion: Who received the {O1}?\nAnswer:` with twin
  `{N2} received the {O1}. {N1} received the {O2}.` (same question). Name pairs `(Anna, Tom)`, `(Sara, Ben)`; object
  pairs `(key, book)`, `(coin, letter)`, `(cup, hat)`, `(map, pen)` → 8 pairs = 16 contexts. All candidates are single
  tokens with a leading space (checked 2026-09-08). Correct answer for A is N1, for the twin N2.
- **Position:** the final prompt token (`:` after `Answer`); activation = `hidden_states[21]` there.
- **Behavioural measure:** `m = lp(" " + correct) − lp(" " + other)` at the next token.
- **Gates (frozen; pilot counts, not statistics):** G0 native competence: `m > 0` in ≥ 14/16 contexts. G1 self-patch:
  replacing the block-20 activation at that position with itself reproduces every next-token logit within 1e-2 (bf16)
  in 16/16. G2 natural donor patch: replacing it with the twin's activation moves `m` toward the twin's answer
  (Δm sign) in ≥ 12/16. **If any gate fails: write the numbers, stop RT, do not search layers or positions.**
- **Routes (only after the gates):** (1) native `m`; (2) default AV description of `h` (greedy, 200 tokens) → text-only
  QA: the TARGET reads `Description of the model's state:\n<desc>\n` + the question + `Answer:` with no injection →
  `m_text`; (3) forced-prefix AV scoring: prefill `<explanation>\nThe person who received the {O1} is` under `h`, `h_twin`,
  `h_0` → D as in T2c; (4) round trip: `ĥ = AR(desc) · ‖h‖ / ‖AR(desc)‖` patched at the position → `m_rt`.
  Controls for (4): matched perturbation `h + ε`, `‖ε‖ = ‖ĥ − h‖`, random direction, 3 seeds → `m_pert`; report
  `cos(ĥ, h)`. Preserve the recipient's other positions and cache; assert the patch touches one row.
- **Kill RT (only if the gates pass):** CI (paired over the 16 contexts) of [m_rt − m_pert] **≤ 0 → MET**
  (reconstruction preserves the answer no better than a displacement-matched perturbation). Reported: native vs
  round-trip preservation rate (sign of m), text-only QA accuracy, forced-prefix donor sensitivity and accuracy.
- **Interpretation, pre-committed:** high cos(ĥ,h), gates pass, m_rt impaired vs m_pert → concrete loss of
  task-relevant information in reconstruction; m_rt preserved → a boundary on "the AR discards specifics"; all NLA
  routes fail while native succeeds → interface limitation, not proof the activation lacks it; m_rt ≈ m_pert both
  failing → insufficient evidence of specifically semantic damage.
- Build `rt_roundtrip.py` (hook: copy the residual-patch pattern from `src/patching.py`; the TARGET must be loaded
  alone for patching, then AV, then AR; never all three). Outputs `rt_gates.csv`, `rt_routes.csv`, `rt_outputs.jsonl`,
  `rt_summary.md` with all 16 contexts verbatim.

### M — does reconstruction error warn of an incorrect answer beyond the target's own uncertainty? (GATED pilot; cap 90 min)
Exploratory; builds on the public "NLA Thought Anchors" post (same checkpoint, GSM8K-style) by testing incremental,
prospective value. Synthetic problems only (no downloads).
- **Problems (frozen generator, seed 0):** 200 items of the form `Compute {a} × {b}. Work step by step, then write
  "Answer:" followed by the number.` with a ∈ [100, 999], b ∈ [11, 99]. Greedy TARGET generation, ≤ 200 tokens, raw text.
  Correct iff the integer after the first `Answer:` equals a·b. **Gate GM: ≥ 20 incorrect and ≥ 20 correct; else stop.**
- **Position (predefined):** the `:` of the model's own first `Answer:` (the answer delimiter), extracted by re-running
  the prefix up to and including that token. Secondary, if time: the first newline of the generation (earlier boundary).
- **Sample:** all incorrect items (cap 40) and 40 correct items (seed 0). AV explanation from the prefix activation,
  AR cosine (primary NLA signal, frozen). Comparators at the same position: next-token entropy and top-1 margin of the
  TARGET; text-only: the TARGET reads the visible prefix and answers `Will the final answer be correct? Yes/No`
  (yes−no logit). Bootstrap by problem.
- **Kill M:** AUROC(−cos, incorrect vs correct) CI **≤ 0.60 → MET**. Reported: AUROC of entropy and margin; the
  incremental value of cos in a logistic model with entropy and margin (in-sample, labelled exploratory).
- Build `m_monitor.py`. Outputs `m_problems.csv`, `m_scores.csv`, `m_summary.md`, 5 verbatim cases.

### T8 — morning report
`overnight/MORNING3c.md`: kill lines; the U1 side-by-side table (AV vs baseline vs text on identical items); X3
condition table with n and the eligibility count; X1 per-layer table; N3 four-way table; N4 curve table; X1b, RT, M
if run (gates and numbers either way); verbatim examples; FOLLOWUPS; provenance (agent-built vs pre-registered);
wall-clock and measured per-item costs. Commit. Stop.

## Pre-registered thresholds (round 3c)
| K | stage | statistic | MET if |
|---|---|---|---|
| U1 | U1 | CI (by document) of paired [AV − baseline] raw p3 choice accuracy | ≤ 0 |
| X3 | X3 | CI (by explanation) of mean I = (G_2 − G_1) − (G_3 − G_1) | ≤ 0 |
| X1 | X1 | entity donor-sensitivity CI at blocks 16, 24, 27 | ≤ 0 at all three |
| N3 | N3 | CI (by explanation) of [cost(generic) − cost(wrong specific)] | ≤ 0 |
| RT | RT (after gates) | CI (paired, 16 contexts) of [m_rt − m_pert] | ≤ 0 |
| M | M (after gate) | AUROC(−cos) incorrect vs correct, CI by problem | ≤ 0.60 |
N4 and X1b are descriptive (no kill). Gates: X3 eligibility (≥ 100 rows), RT G0/G1/G2, M GM.

**Execution order (round 3c):** U0c → U1 → X3 → X1 → N3 → N4 → X1b → RT → M → T8. **Hard stop: 9 h after the first
round-3c RUNLOG line;** at the stop, the running stage is marked blocked (time) and T8 runs with what exists.
