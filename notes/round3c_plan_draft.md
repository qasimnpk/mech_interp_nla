# Round 3c — DRAFT for tonight's loop (desk, 2026-09-07 08:00; paste into PLAN.md on approval)

Purpose: one mandatory control the readout result cannot be published without, plus the two cheapest
extensions both advisors ranked highest. ≈1.5 h compute; hard stop 2.5 h; stage cap 45 min. Nothing here is a
dependency for the application; the human's review budget for the whole round is ≤ 45 min.
Execution order: **U1 → X3 → X1 → X1b (optional, dropped first) → T8.**

Why these and not the others: the NLA paper already applied a late-layer NLA to earlier activations and found
"more striking content, generally less coherent" (appendix, reward-sycophancy organism), so a cross-layer run is
only worth doing with an *independently verified* readout (X1). Dingeto 2026 already audited this pair's score
against claim flips, so the snippet-interaction test (X3) is the piece that is ours. The Solshine card shows
teacher-forced discrimination can appear without a trained adapter, so U1 is mandatory. Not tonight: the
error-monitoring extension (new dataset and labelling infrastructure, half a day), best-of-8 (53 min of generation
alone; the score's limits are already the central finding), generalize-vs-omit (N3), the target-side layer curve (N4).

**Reuse (read-only):** `t2a_scores.csv`, `t2c_pairs.csv`, `c2_pairs.csv`, `out/c2_acts.npz`, `t0_topics.csv`,
`stimuli.csv`, `s3_scores.csv`, `s3_edits.jsonl`, `s2_claims.csv`, `c1_expl.csv`, `t2_prefix.py` / `t2c_entity.py`
(scorers), `t2a_audit.py`, `nla_lib.py`. Shared readout definition as in Round 3b (summed log-prob of `" " + candidate`).

### U1 — artifact check + base-model-with-injection control + text-only reference (TARGET only, ≈20 min)
**Base-model-with-injection (kill).** Load `Qwen/Qwen2.5-7B-Instruct` weights into the AV injection code path
(same prompt template, marker id 149705, rescale to norm 150, marker row replaced and asserted; skip the
`nla_meta` role assert, log that it was skipped). No AV weights anywhere in this stage.
- Topic: the 160 evaluation items of T2a with prefix `p3` and with round-3 `PREFILL_CC`; own activation, foreign
  swap, no injection; candidates `" " + topic_true` / `" " + topic_foreign`. Report raw and prior-corrected AUROC and
  within-pair accuracy, CIs by document, side by side with the AV numbers from `t2a_scores.csv` on identical items.
- Entity: the 40 C2 pairs with prefix `p1`, `h_a`, `h_b`, `h_0`. Report donor sensitivity, both-correct, choice
  accuracy, CIs by template, next to `t2c_pairs.csv`.
- **Kill U1:** CI (by document) of [AV raw AUROC − base raw AUROC] on `p3` **≤ 0 → MET** (the likelihood readout is
  not attributable to NLA training; the injection alone carries it). Report the same difference for prior-corrected
  accuracy and for the entity donor sensitivity (not kills).
**Text-only reference (reported, no kill):** base model reads the full prefix (tokens 0..pos, no injection) followed
by `\nThe document is about`, scores the same two titles. Raw and prior-corrected (prior = same prompt with the
prefix removed). This is the "what does activation access buy over the text" comparison; a match does not prove
text inversion and is reported as such.
Outputs: `u1_base_topic.csv`, `u1_base_entity.csv`, `u1_text.csv`, `u1_summary.md`. ≈2,000 TARGET forwards.

### X3 — does the local snippet mask factual sensitivity? (AR only, ≈20 min)
For every accepted S3 triple (original c, corruption c*, paraphrase c~) whose claim is NOT the last claim
(exclude `claim_idx == n_claims − 1`; report the count), score three backgrounds:
- B0 full explanation (already in `s3_scores.csv`; recompute and assert equal within 1e-6);
- B1 snippet removed: the last claim deleted, remaining claims joined with a single space (as `c1_expl.csv` did);
- B2 matched removal: delete a random contiguous span of words equal to the snippet's word count from the other
  non-tested claims (seed 1000 + row), never touching the tested claim.
For each background score cos with c, c*, c~ inserted → A = cos(c) − cos(c*), P = cos(c) − cos(c~), and
AUROC(Δ corrupt vs Δ paraphrase) per background.
- **Kill X3:** CI (cluster by explanation) of [(A − P)_B1 − (A − P)_B0] **≤ 0 → MET** (removing the snippet does not
  unmask factual sensitivity). Report [(A − P)_B2 − (A − P)_B0] alongside, and the three AUROCs.
- Interpretation grid, pre-committed: B1 rises and B2 does not → competition with the snippet; both rise → generic
  length/context effect; neither → snippet dominance does not explain the insensitivity.
Also report absolute A and P per background and the background's mean cos, so relative and absolute are both visible.
≈330 rows × 3 backgrounds × 3 texts ≈ 3,000 AR forwards. Outputs `x3_scores.csv`, `x3_summary.md`, 5 verbatim rows.

### X1 — cross-layer readout with the fixed layer-20 AV (TARGET then AV forwards, ≈25 min)
Question: how does independently verified information recovery change when the layer-20 AV reads other layers?
- Layers (frozen): blocks **16, 20, 24, 27** (`hidden_states[17, 21, 25, 28]`). Same positions, injection at norm
  150 unchanged (a scalar before rescaling changes nothing; no whitening, no learned map).
- Activations: TARGET forward on the 80 C2 contexts and the 200 stimuli, all four layers saved to `out/x1_acts.npz`.
  Assert block-20 rows equal `c2_acts.npz` / `acts_L20.npz` to 1e-4.
- Entity: T2c protocol (`p1`, both entities, `h_a`, `h_b`, `h_0`) at each layer. Report **separately** per layer:
  donor sensitivity with CI by template, both-correct rate, choice accuracy raw and prior-centred.
- Topic: `p3` on the 160 evaluation items at each layer: raw and prior-corrected AUROC and accuracy, foreign swap.
- **Kill X1:** at every non-training layer, donor-sensitivity CI **≤ 0 → MET** (no readable transfer at any tested
  layer). Reported, not kills: which layer maximises accuracy; whether donor sensitivity and accuracy move together.
  Pre-committed readings: accuracy better elsewhere → the training layer is not the best extraction layer for this
  task; donor sensitivity up without accuracy → distribution shift changes the readout without making it useful;
  both down → a measurable transfer limit. Label the analysis exploratory (same examples as T2c).
≈480 TARGET forwards + ≈1,500 AV forwards. Outputs `x1_entity.csv`, `x1_topic.csv`, `x1_summary.md`.

### X1b — OPTIONAL, dropped first: cross-layer generations (AV, ≈15 min)
40 pilot stimuli, full greedy explanations from block-16 and block-27 activations (80 generations). Report parse_ok,
CJK rate, quoted-final-token accuracy, expecting-candidates hit on the target's top-1 (with the shuffled-pairing
floor, which is 0.029 [0.012, 0.056] at block 20 vs 0.444 own), word-overlap with the block-20 explanation, and
`cos(AR(desc), h_layer)` vs `cos(AR(desc), h_20)`. No kill; descriptive. The paper's "less coherent" observation is
the comparison point. Outputs `x1b_outputs.jsonl`, `x1b_summary.md`, 4 fixed examples (stimuli 0, 7, 19, 33).

### T8 — MORNING3c.md
Kill lines, the U1 side-by-side table (AV vs base vs text), the X3 background table, the X1 per-layer table,
X1b if run, verbatim examples, FOLLOWUPS, provenance, wall-clock. Commit. Stop.

## Thresholds (round 3c)
| K | stage | statistic | MET if |
|---|---|---|---|
| U1 | U1 | CI by document of [AV − base] raw AUROC, p3, eval | ≤ 0 |
| X3 | X3 | CI by explanation of [(A−P)_B1 − (A−P)_B0] | ≤ 0 |
| X1 | X1 | donor-sensitivity CI (by template) at every non-training layer | ≤ 0 at all of 16, 24, 27 |

## Human review after the run (≤ 45 min)
Re-derive U1's AV−base difference and X3's B1−B0 difference with one-liners; read 5 X3 verbatim rows and the 4 X1b
examples; decide which of X3 / X1 goes into the main text (the other to the appendix).
