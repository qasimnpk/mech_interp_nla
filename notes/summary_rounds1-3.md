# Summary of rounds 1–3 (agent draft, 2026-09-06 23:00; T3 still running, MORNING3 not yet written)

Every number below is copied from a bench file: `overnight/*_summary.md`, `DISCONFIRMATION.md`
(rounds 1–2 in main, round 3 in `../mech_interp_nla-nightshift/overnight/`). Rewrite before use.

## Setup (fixed across all rounds)
- Target `Qwen/Qwen2.5-7B-Instruct`, block 20 (`hidden_states[21]`), bf16 on MPS.
- NLA pair `kitft/nla-qwen2.5-7b-L20-av` (verbalizer, full 28-layer fine-tune, injects the activation at
  marker `㈎` rescaled to norm 150) and `kitft/nla-qwen2.5-7b-L20-ar` (reconstructor, 21-layer truncated
  backbone + linear value head, last-token readout). Score = cosine between AR(text) and the true activation.
- Stimuli: 200 wikitext-2 train documents (≥300 tokens, seed 0), raw text, one position per document drawn
  uniformly from tokens 16..511, plus a second position per document for same-document controls. Pilot =
  stimuli 0–39, evaluation = 40–199 (n=160). Greedy decoding, 200 tokens; ~10 s per explanation.
- Explanation format the checkpoint produces: three claims, e.g. genre/format claim, a "the phrase X
  suggests …" claim, and a final `Final token "X" … strongly expecting "Y"` claim (the local snippet).
- Claims are split on newlines then sentence ends; 671 claims over 200 explanations.
- All CIs are 95% cluster bootstraps by source explanation (1000 draws, seed 0). Three outcomes per
  pre-registered kill test: MET / NOT MET / INCONCLUSIVE.

## Finding 1 — the pipeline reproduces and is position-specific (round 1, S1/S4)
| quantity (eval, n=160) | mean cos |
|---|---|
| own explanation vs own activation | 0.882 [0.875, 0.889] |
| same document, other position | 0.366 |
| other document | 0.320 |
| empty explanation (AR prior) | 0.347 |
| blind describer (sees context, not activation) | 0.429; raw context as text 0.473 |
| adjacent layers 19 / 21 | 0.835 / 0.836 |
Kill tests K1a, K1b, K4 NOT MET.

## Finding 2 — the score reads wording and relevance, not facts (rounds 1–2, S2/S3/R1/R2)
Setup: for each of 538 eval claims, an LLM (the target itself) wrote a one-fact contradiction c* and a
meaning-preserving paraphrase c~; 490 accepted after checks. Cost = cos(z) − cos(z with claim replaced).
| edit | cost |
|---|---|
| delete one claim vs random equal-length span (S2) | claim − span = 0.0058 [0.0022, 0.0096]; claims are units |
| one-fact corruption (S3) | 0.0031 [0.0016, 0.0048] |
| paraphrase (S3) | 0.0049 [0.0035, 0.0067]; corrupt − para = −0.0018 [−0.0028, −0.0008] → K3 MET |
| deterministic number/name swap | 0.0038; K3-det MET |
| corrupt EVERY claim vs paraphrase every claim (R2) | 0.0075 vs 0.0141 → R2 MET |
| swap in an off-topic claim | 0.114; AUROC 0.955 (one-fact corruption AUROC 0.53) |
R1: the target's own block-20 last-token encoding of the claim sentences moves 0.040 under corruption
and 0.134 under paraphrase (S_T = −0.094, MET). Caveat: c and c* share final tokens, c~ does not.

## Finding 3 — the final snippet carries the score, by content not position (round 2 R3, round 3 C1)
- Last claim alone recovers 88% of the lift over the empty floor (cos 0.822); first claim alone 23%.
- Deletion cost: last claim 0.125, first 0.010, middle 0.017.
- C1 (round 3): move the last claim to the front → its deletion cost 0.099 vs 0.125 in place (keeps 79%,
  paired diff −0.026 [−0.032, −0.021], threshold ≤ −0.05 → NOT MET). Reversed order: cost 0.132.
  So the snippet's weight is its content (token identity + next-token expectation), not its slot.
- Even corrupting the last claim costs 0.0048 vs paraphrase 0.0055: the snippet is read for wording too.

## Finding 4 — the verbalizer ignores instruction text (round 1, S5)
40 pilot activations × 6 prompt variants (one word, French, opposite, angry, POS-first). Mechanical
compliance 0/80, agent-judged 0/120; cos unchanged (±0.003). Outputs are not identical to default
(word-sequence similarity to default 0.55–0.59 vs 0.17 across stimuli): the text perturbs the greedy
stream like a sampling seed, content/format/length unchanged.

## Finding 5 — but semantics are still in the activation and readable (round 3, C2/T2/T4)
- **C2 (matched activation pairs).** 40 hand-templated context pairs differing in one entity 11–17
  tokens before a shared suffix (`… is Paris.` vs `… is Lyon.`), same final token. cos(h_a, h_b) = 0.966.
  Descriptions mention the own entity in 11/80, neither in 66/80. Four-way margin
  M = [cos(h_a,d_a) − cos(h_a,d_b)] + [cos(h_b,d_b) − cos(h_b,d_a)] = 0.019 [0.010, 0.034], 40/40 > 0
  → NOT MET. Text-side entity swap in the description (n=12): 0.0048 [−0.0001, 0.0080].
- **T2 (forced-prefix readout, AV forward only).** Prefill `<explanation>\nThe passage concerns` and
  compare log-prob of the document's true title vs a foreign title.
  | condition | AUROC (eval) |
  |---|---|
  | own activation | 0.752 [0.702, 0.798] → NOT MET |
  | no injection (prior) | 0.488 |
  | prior-corrected | 0.935 |
  | foreign activation injected, prefers foreign | 0.775 |
  | yes/no question format | 0.550 → MET (format useless; yes-bias ≈ +2.6 logits) |
  Claims: prefill the claim up to the corrupted word; lp(original) − lp(corrupt) = 9.78 injected vs
  1.39 with no injection, 97.3% prefer original (n=298 LLM edits, 393 deterministic: 15.4 vs 3.7).
  **Missing control:** same prefix under a foreign activation (the prefix is the AV's own greedy output).
- **T1 (AR as text probe).** cos(h, AR("This text is about {topic}")) AUROC 0.61 [0.59, 0.64],
  INCONCLUSIVE; RepE difference-of-means probe in the target 0.74–0.81. Claim-alone probe: true − corrupt
  0.015, true − paraphrase 0.036 (wording still dominates, but true > corrupt in 73%).
- **T4 (perturb the injected vector with a target concept direction).** Norm-preserving mix of h with a
  sports or French difference-of-means direction. At β = +0.25 (18° rotation) sports words appear in
  100% of descriptions (baseline 12.5%, random direction 17.5%); French at 72.5% (β=0.5: 95%).
  → NOT MET; replicates the LessWrong "NLAs read outside the J-space" result on this 7B pair.
- **T3 (steer the AV's own residual stream, running).** French/terse directions at blocks 8/14,
  α ∈ {1,2,4}; will be cut at the 85-min cap (~34/40 stimuli).

## One-paragraph reading (draft)
The reconstruction score is a wording-and-relevance score: it separates a claim about another
activation easily, treats a one-fact contradiction as cheaper than a paraphrase, and gets 88% of its
value from the local "final token … expecting …" snippet, whose weight is content not position. Yet the
fact is not gone: two activations differing only in an upstream entity are told apart by the score,
a forced-prefix likelihood reads the topic and the corrupted word back out of the activation, and an
injected concept direction surfaces in the description at an 18° rotation. So the verbalizer has the
semantics and the reconstructor is the wrong instrument for checking them; and the verbalizer cannot
be asked for them by prompt text, only by prefilling or by editing the vector.

## Round 3b candidates (see notes/round3b_candidates.md)
T2b foreign-activation swap on the claim readout (~10 min); T2c entity readout on the C2 pairs
(~5 min); C3 activation-side wording null for C2 (~20 min).
