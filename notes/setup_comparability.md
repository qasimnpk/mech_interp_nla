# Setup comparability: our experiments vs the NLA paper's (desk, 2026-09-08 ~17:00 EDT)

**Purpose.** Answer "how faithful are our setups to the paper's experiments, in spirit and in detail", row by row, so
every difference that could change a conclusion becomes one stated sentence in the methods paragraph. Sources: the
paper-setups reconstruction `notes/NLA_paper_experiment_setup.md` (agent, 2026-09-08; IDs E0–E7, C1–C7, M1–M4, S1–S6 are
its IDs); our pre-registrations in `overnight/PLAN.md` (rounds 3–3c on
main; round 1 at `git show b01221e:overnight/PLAN.md`, round 2 at `d5e64d7`); our `overnight/*_settings.json`.
Numbers marked **DESK** were computed today from committed CSVs and are unverified by the human; everything else is copied
from `notes/evidence_table.md` or the setup doc. Nothing here has been re-run on a model.

**One-paragraph verdict.** Mechanics are identical to the released pair's own convention (hook, injection, AR template,
score); that part is not "comparable", it is the same code path, verified against the authors' example transcript. The
experiments are faithful **in spirit** to three paper items — E4.2 (AR as claim verifier), E2 (meaning-preserving
transforms), E6.1 (off-layer application) — and differ from them **in detail** in ways that are all in our favour for the
question we ask but forbid number-level comparison: our claim unit is a whole bullet, not an atomic proposition; our edits
are substitutions and paraphrases of the same sentence, not LLM rewrites that remove one proposition; our labels are
synthetic (one fact changed) rather than judged truth; our corpus is wikitext-2 with raw spacing, not UltraFineWeb or
Common Pile; our score is cosine on the direction-only scorer, theirs FVE. The paper's evaluations we did not run and
should not imply we ran: the five prediction tasks (E1), groundedness by judge (E3.3), the claim taxonomy and recurrence
(E4.1, E4.3), eval awareness (E5), auditing (E6.0/E6.2), AO training (E7).

## 1. Shared mechanics (paper S1–S3 vs `overnight/nla_lib.py` and `*_settings.json`)

| item | paper / released-pair convention | ours | same? |
|---|---|---|---|
| hook | output of block 20 = `hidden_states[21]`, pre-norm residual | `hidden_states[21]`; verified against `examples/qwen7b_layer20_step4200.txt` to ±0.01 cos (`notes/nla_setup/README.md`) | **same** |
| injection | replace marker `㈎` (id 149705, neighbours 29/522) embedding with `v·150/‖v‖` | identical; asserted every call (`nla_lib`) | **same** |
| AV prompt | paper prompt with "2-3 text snippets", Qwen chat template, 125 tokens, marker at 111 | identical (`s0_settings.json`: `av_prompt_len_tokens 125`, `av_marker_pos 111`) | **same** |
| AV decoding | training T=1, 150-token cap; eval temperature not stated; authors' example greedy; Dingeto greedy | greedy, `max_new_tokens 200` | same as the authors' example; **differs from training-time sampling** (say "greedy" once) |
| AR | 21 blocks, norm→Identity, `value_head` 3584×3584 no bias; template `Summary of the following text: <text>{z}</text> <summary>`, last token | identical; suffix ids asserted | **same** |
| score | `mse_nrm = 2(1 − cos)` on √d-normalised vectors; `fve_nrm = 1 − mse_nrm/0.7335` (training-set Var) | cosine; mse reported as identical information; **FVE never reported** | same information; **we do not report FVE**. Conversion below is approximate because 0.7335 is the training-distribution variance, not wikitext's |
| normalisation | unit-L2 at use time | same | **same** |
| activation norms (M1 sanity) | raw block-20 norms "mostly 100–170"; α=150 ≈ Q0.75 heuristic | eval quantiles Q25/Q50/Q75/max = 107 / 113 / 120 / 140 (**DESK**, `s1_recon.csv act_norm`) | slightly lower than the training band; irrelevant to the AV (rescaled to 150) but a mild sign that wikitext sits off the training text distribution |
| corpus | SFT/RL: UltraFineWeb raw web text + WildChat chats, docs truncated at 4096; E4 texts: Common Pile ("pretraining-like") | wikitext-2-raw train, docs ≥300 tokens truncated to **512**, no chat template; wikitext-raw has spaces before punctuation and ` @-@ ` joins | **differs**: Wikipedia with tokenisation-unfriendly spacing; shorter prefixes. State it. Reconstruction 0.882 says the pair copes |
| position rule | training sampled positions **≥ 50** only (positions < 50 never seen) | `pos ~ U{16, …, min(len,512)−1}`; **17/160 eval positions are < 50** (**DESK**) | **differs**. Check done today (**DESK**): cos_own 0.886 (n=17, pos<50) vs 0.882 (n=143); A−P on pos≥50 only −0.00240 [−0.00329, −0.00146], n=437 — the headline is unchanged. State "17 evaluation positions fall below the pair's training minimum; excluding them does not change the paired result" |
| sampling of positions per text | E4: last 10 tokens of each text; training: 5 random positions per doc | 1 position per document (+1 same-doc control position) | differs; ours is one random position, theirs a run of adjacent ones |
| uncertainty | error bars with unstated semantics; N mostly `[U]` | cluster bootstrap by document, 1000 draws, seed 0; n stated everywhere | ours is stricter; say so plainly, not as a criticism |

## 2. Experiment by experiment

Legend: **spirit** = same scientific question and contrast; **detail** = same unit, edit, label, metric. "Consequence" is the
sentence the methods or limitations paragraph needs.

| paper item | ours | spirit | detail differences | consequence for the write-up |
|---|---|---|---|---|
| **E4.2 AR as verifier** — Opus 4.6 NLA + AR; Haiku 4.5 decomposes each explanation into ~11 atomic claims tagged THEME/ENTITY/DETAIL, judges SUPPORTED / NOT_IN_TEXT against the prefix; each claim is *removed by rewording the sentence* (`rewritten_text`); Δmse per claim; grouped true vs false, related vs unrelated; "FVE drop when removed" 0.09–0.37 pp; "noisy… weak per-claim verifier" | S2 (delete a whole bullet vs length-matched random span), S3 (one fact substituted vs paraphrase of the same bullet, paired), R2 (every bullet), off-topic swap, N3 (wrong / generic / omitted) | **faithful**: same question (does the AR's score track claim truth?), same instrument (AR score under an edited explanation, activation fixed) | (1) **unit**: our "claim" is a regex sentence split, median 31.5 words, 3.4 per explanation (**DESK**, `s2_claims.csv`) — a whole bullet holding several atomic claims; theirs is one proposition. (2) **edit**: S2 deletes the whole bullet; theirs removes one proposition and keeps the sentence — S3's within-sentence substitution is the closer analogue. (3) **labels**: theirs judged truth on natural claims; ours synthetic one-fact corruption (Qwen2.5-7B-Instruct editor, greedy) plus deterministic swaps, no truth judge (X3's Qwen judge left n=1 usable; human blind sheet pending). (4) **statistic**: theirs grouped means with unstated error bars; ours paired A−P with cluster CIs. (5) **model**: Opus NLA (4–5 snippets, ~500 tokens) vs released 7B (2–3 bullets, ~130 tokens) | "We ran the paper's verifier test as a paired, interventional design on the released 7B pair: the claim unit is a bullet, the manipulation is a one-fact substitution against a paraphrase of the same bullet, and truth is by construction rather than judged. The paper's per-claim deletion effects on Claude (0.1–0.4 FVE points) are not numerically comparable." Cite Dingeto for the number-comparable audit on this pair |
| **E4.1 claim taxonomy** (theme 64% true, entity 28%, detail 24%; false claims mostly related) | not run; N2 recut of the 490 corruptions by changed-word type is proposed, no model runs | n/a | we have no judged truth labels; a recut by *edit* type is not their *claim* type | Appendix only, labelled "type of the changed word", or omit |
| **E4.3 recurrence** (true claims recur at more of the last 10 positions) | not run | n/a | needs 10 positions per text and a match judge | Name as future work, not tested |
| **E3.3 factual accuracy** (judge lists claims about the prefix, counts false; Claude NLAs 27–51% grounded) | not run with a judge; `notes/quote_census.csv` is mechanical (quoted spans ≥3 words: 1.8% verbatim in the prefix; final token quoted right in 82%; "expecting" hits the target's top-1 in 44%) | partial | mechanical proxies, not a claim-level judge; Dingeto's counterfactual audit on this pair (≈2% of specific claims grounded) is the closest published number | Report the census as "mechanically verifiable content", never as a groundedness rate |
| **E2 steganography transforms** (six whole-explanation Claude rewrites; % FVE maintained: shuffle 93–98, light paraphrase 93–105, aggressive 76–89, French 81–90, coherence 45–73→5–15, summary 50–77→0–18) | S3 paraphrase of one bullet (cost 0.0049 cos), R2 paraphrase of every bullet (0.0141), S2 `shuffle_order` (−0.0147), R3 truncation curve, C1 reorder/reverse | **faithful for shuffle and paraphrase**; the other four transforms not run | transform by Qwen2.5-7B-Instruct per bullet, not Claude on the whole explanation; ratio convention unknown on their side. Approximate conversion of ours to their axis (**DESK**, cos→`fve_nrm` with the 0.7335 denominator, ratio to own): every-bullet paraphrase **0.94**, bullet reorder **0.94**, every-bullet corruption **0.97**, last bullet alone **0.76**, off-topic swap **0.54** | "Our paraphrase and reorder retain about 94% of FVE-equivalent, in the range the paper reports for its meaning-preserving transforms on Claude and close to Dingeto's 0.89 on this pair; the conversion uses the released training-set variance and is approximate." Do not claim to have run their transform suite |
| **E6.1 layer sensitivity** (⅔-depth NLA applied at other layers; RM-term rate; "less coherent") | X1 (verified entity/topic readout at blocks 16/20/24/27), X1b (fluency, quoted-token accuracy), N4 (target displacement by layer) | **faithful in design**, different readout | theirs string-matches a hidden concept on a model organism; ours measures independently verified readout with donor and no-injection controls | "Following the paper's off-layer application, we measure verified readout rather than surfaced content; both are transfer under distribution shift" |
| **C1 / C4 edit steering** (Δ = AR(edit) − AR(orig) added at one token; direct patching "does not lead to modified behavior on Opus 4.6") | RT route 4 (AR(desc) rescaled and patched; stopped at gate G2 11/16); T5 not run | partial (RT is their direct-patching variant, not the Δ-steering) | our gate failed before any route ran | Report RT as a gate failure; note the paper's own null for direct patching on Opus and Dingeto's "patching the tap barely moves behavior" as consistent context, not as our finding |
| **E7 / AO** ("ask the AV a question" by QA fine-tuning; phrasing sensitivity ±10%) | S5 (instruction variants, 0/200 followed), T2/T2a/T2c (prefilled likelihood), U1 (un-finetuned interpreter control), T2b (activation dependence) | same goal (targeted questions), **different route**: inference-only | theirs trains oracles; ours forces a prefix on the frozen AV and reads likelihoods; their held-out tasks (user modeling, classification) are not our topic/entity tasks | "The paper reaches targeted questions by training oracles; we test whether the frozen verbalizer can be read by prefilled likelihoods, with an un-finetuned-model control the paper does not have" |
| **E0 FVE** (released 0.752 on the training set) | S1 cos 0.882 → `fve_nrm` ≈ **0.68** (**DESK**, approximate) on wikitext eval positions | same quantity | held-out and off-distribution, so lower is expected (the setup doc says so) | One sentence: "cos 0.882, about 0.68 FVE-equivalent against the released training-set 0.752" |
| **E0a shuffled-pairing control**, **M3 base-model transfer**, **M4 pooled activations** | U1 is a *different* control (un-finetuned weights in the AV interface, not shuffled pairing); M3/M4 not run | n/a | — | Do not describe U1 as the paper's shuffled control |
| **E1 five prediction tasks, E3.1 SAE consistency, E3.2 writing quality, E5 eval awareness, E6.0/E6.2 auditing** | not run | n/a | training curves on Claude, proprietary transcripts, organisms | Never imply these were reproduced |

## 3. What is ours and has no paper counterpart (keep, label as additions)
Per-position decomposition with a reorder control (R3, C1); source-edit matched pairs C2/C3; the paraphrase null and
length-matched random-span control in the verifier test; the every-claim amplification (R2); the AV's own likelihood as a
readout with no-injection, donor-swap, held-out-prefix and un-finetuned-interpreter controls (T2a, T2c, U1); residual
steering of the AV (T3) and injected-direction sensitivity (T4); the frozen-scorer test of the paper's confabulation
hypothesis 2 (N3); the snippet-masking interaction (X3, inconclusive).

## 4. Sanity checks the setup doc lists (§6.5), applied to us
- Marker id / neighbours / suffix ids asserted against the live tokenizer — **yes**, every stage via `nla_lib`.
- Decode known positions against the authors' example — **yes** (`notes/nla_setup/README.md`, ±0.05 mse_nrm at four positions).
- `mse = 2(1 − cos)` — **yes**, stated in PLAN round 1; we report cos.
- FVE denominator — **not applicable**; we never report FVE. If the write-up gives an FVE-equivalent, say "training-set
  denominator 0.7335, approximate".
- Token-level diff of edits, reject edits larger than the target claim — **partial**: S3 acceptance is tags parsed, word
  count ±30%, ≥1 word changed; the desk audit found corruptions change a median of 1 word and paraphrases 14
  (`notes/diagnostics_round3b.md`); 6/490 corruptions are punctuation-only, one a non-edit. The human blind validity sheet
  (`notes/s3_edit_validity_BLIND.csv`) is the outstanding check; report its counts.
- Bootstrap by document — **yes**, everywhere.

## 5. Sentences for the methods / limitations paragraph (rewrite in your voice)
1. Extraction, injection, reconstructor and score follow the released pair's own code path, verified against the
   authors' example transcript; we report cosine, where the released MSE equals 2(1 − cos).
2. Stimuli are 200 wikitext-2 documents truncated to 512 tokens with one random position each; 17 of the 160 evaluation
   positions fall below the pair's training minimum of 50 and excluding them does not change the paired result.
3. Our verifier test is the paper's claim-deletion design made interventional: the unit is a bullet, the manipulation a
   one-fact substitution against a paraphrase of the same bullet, truth is by construction, and the reconstructor's
   response is a paired difference with cluster bootstrap intervals. The paper's grouped effects on Claude NLAs, and its
   atomic-claim unit, are not numerically comparable; Dingeto 2026 is the number-comparable audit on this pair.
4. Our paraphrase and reorder edits play the role of the paper's meaning-preserving transforms; we did not run its
   coherence or summary transforms, and the FVE-equivalent retention figures we quote use the released training-set
   variance and are approximate.
5. Cross-layer application follows the paper's appendix design but replaces surfaced content with a verified readout.
6. We did not run the paper's five prediction tasks, judge-based groundedness, claim taxonomy or recurrence analyses;
   the quote census is mechanical.

## 6. Open items the human should decide
- Whether to add the FVE-equivalent conversion (one sentence, §5 item 4) or stay in cosine only. Recommendation: one
  sentence, because it lets a reader place our retention numbers next to the paper's and Dingeto's.
- Whether to run the paper's exact E4.2 (atomic claims, judged truth, rewrite-deletion) as a future-work item. It is
  the cleanest "same test, same instrument" replication still open on this pair, and the setup doc ranks it first
  (§6.2). Not before submission.
