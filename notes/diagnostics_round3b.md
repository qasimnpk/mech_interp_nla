# Diagnostics on round-3b outputs (desk, 2026-09-07; pandas over the committed CSVs, no model runs)

Every number here is a re-derivation from `overnight/t2c_pairs.csv`, `c3_cells.csv`, `t2a_scores.csv`, `t2b_claims.csv`, `t2_claims.csv`. Descriptive; no new thresholds.

## T2c — per pair (prefix p1)

- n pairs 40; donor effect D(h_a) − D(h_b): mean 1.738, median 0.695, frac > 0 0.775 (31/40)
- both correct (D(h_a) > 0 and D(h_b) < 0): 0.225 (9/40)
- same candidate wins under both activations: 0.750 (30/40); of these, a wins in 16, b wins in 14
- donor effect in wrong direction: 6; exactly zero: 3 (pairs [8, 9, 10])
- prior-centred both correct: 0.150
- concentration: top 5 pairs carry 0.58 of the summed donor effect; mean without template 5 = 1.113, median 0.543
- |D(h_0)| median 1.086 vs |donor| median 0.695

## C3 — transfer of the entity effect across wording

- donor effect at w1: mean 1.738, at w2: 1.772; paired (w2 − w1): mean 0.034 CI95 by template [-0.137,0.210]; median 0.047; frac |w2−w1| < 1 nat 0.950
- Spearman(w1 effect, w2 effect) across pairs: 0.894
- both-correct at w1 0.225, at w2 0.200; same verdict for the pair under both wordings: 0.925
- reconstruction margins per cell: M_fact mean 0.0175, M_wording mean 0.0097; frac cells fact > wording 0.625
- caution: an interval containing zero is not equivalence; report as 'no detectable wording effect at n=40'.

## T2a — raw and corrected side by side (eval n=160, held-out prefix p3)

| scoring | pooled AUROC | within-pair choice accuracy [CI by document] |
|---|---|---|
| p3 raw | 0.761 | 0.781 [0.719,0.844] |
| p3 per-token | 0.773 | 0.794 [0.725,0.856] |
| p3 prior-corrected | 0.943 | 0.944 [0.906,0.975] |
| p3 no injection | 0.486 | 0.475 [0.400,0.550] |
| p3 swap (foreign activation injected; accuracy of still choosing the TRUE title) | 0.214 | 0.200 [0.144,0.256] (so it follows the donor 80% of the time) |
- prior-corrected = lp(candidate | own activation) − lp(candidate | no injection); identical prefix and candidate strings (asserted in t2a_audit.py). The rule was introduced by the bench in round 3 after seeing round-3 T2 outputs: exploratory; p3 tests prefix transfer on the same 160 documents, not new documents.
- what the correction fixes: under no injection the longer or rarer title loses; the correction removes that length/frequency bias:

| true title length − foreign (tokens) | n | raw accuracy | prior-corrected accuracy |
|---|---|---|---|
| true shorter by >3 | 38.0 | 1.000 | 0.895 |
| true shorter by 1–3 or equal | 51.0 | 0.902 | 0.961 |
| true longer by 1–3 | 38.0 | 0.711 | 0.921 |
| true longer by >3 | 33.0 | 0.424 | 1.000 |

## Observation-count reconciliation (units)

| unit | count | where |
|---|---|---|
| documents / stimuli | 200 (160 evaluation) | stimuli.csv |
| explanations | 200 (one per stimulus) | explanations.jsonl |
| claims (split by the fixed splitter) | 671; 538 in evaluation explanations | s2_claims.csv |
| accepted LLM corruption/paraphrase triples | 490 (of 538); deterministic swaps 402 | s3_scores.csv |
| scored rows in the claim-word readout | 691 single-word rows (of 892 accepted pairs) = LLM 298 + deterministic 393; a claim can appear in both | t2_claims.csv (single_word=True) |
| explanations represented | 160 (bootstrap cluster = explanation) | |
| T2b rows | 691 (same rows; LLM 298, det 393); in_ctx True 192 | t2b_claims.csv |
- The round-3 headline '9.78 nats, 97.3%' is the 298 LLM single-word rows; T2b's 691-row table pools LLM and deterministic edits (deterministic rows are number/name swaps of the same claims). Report the two separately, as T2b does.
- `in_ctx` = the original word string occurs in the 64-token left context + current token. It is a string check, not factual support; a name present in the context does not validate the relation the claim asserts.

## Correction (2026-09-07 03:00): the activation saw the FULL prefix, not the 64-token window
`s0_smoke.py` runs the target on the document truncated to 512 tokens; the activation at `pos` has seen
tokens 0..pos (median 276 tokens on the labelling sheet, max 510). `context_left_64` is a display window only.
Re-running the bench's exact `in_ctx` rule (word stripped of edge punctuation, whole-word, case-insensitive)
over the full prefix + current token (`notes/t2b_in_full_prefix.csv`; bench in_ctx reproduced exactly):

| word_orig present in … | n | d_own | d_pos2 | d_foreign | d_noinj | d_own − d_pos2 | frac d_own > 0 |
|---|---|---|---|---|---|---|---|
| 64-token window (bench in_ctx) | 192 | 18.23 | 6.63 | 4.08 | 3.14 | 11.60 | 0.990 |
| full prefix, present | 257 | 16.69 | 6.74 | 3.56 | 3.01 | 9.95 | 0.988 |
| full prefix, absent | 434 | 10.80 | 4.99 | 2.48 | 2.56 | 5.81 | 0.963 |
| LLM edits only, full prefix present / absent | 83 / 215 | 10.32 / 9.57 | | | | 6.82 / 5.91 | |

Reading: the correct lexical statement is "434 of 691 original words do not occur anywhere in the prefix the
activation saw; the AV still prefers them over the corruption by 10.8 nats under its own activation, of which
5.8 nats are specific to the exact position". Absence of the word is not absence of support (a paraphrase or
inference may be supported); presence does not validate the relation the claim asserts. Only the human labels
settle that, and they must be made against the full prefix (the blinded sheet now carries `full_prefix_to_pos`).

## C3 — does the matching margin track activation distance? (descriptive, post hoc, 2026-09-07)
Across all 160 margins (40 cells × {fact w1, fact w2, wording a, wording b}) Spearman(M, 1−cos) = 0.768 (fact
edits alone 0.777, wording edits alone 0.735). In the 16 cells where the wording edit moved the activation more than
the entity edit, mean M_fact 0.005 vs M_wording 0.014; in the other 24, M_fact 0.028 vs M_wording 0.0065.
Reading: the margin follows activation displacement regardless of edit type. Not a mechanism test (no
distance-matched design); report as consistent-with, not as established.
