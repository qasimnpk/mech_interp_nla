# Desk session 2026-09-08 → 09: discussion summary and conclusions (agent draft for the write-up; rewrite in your own voice)

Every number below traces to `overnight/*_summary.md`, `overnight/DISCONFIRMATION.md`, `notes/evidence_table.md`, or
`notes/NLA_paper_experiment_setup.md`. Round 4 (planned this session) runs overnight 2026-09-09→10; its results are not here.

## 1. Where the project stands (one paragraph)
On the released Qwen2.5-7B layer-20 NLA pair, reconstruction is faithful and position-specific (cos 0.882 own vs 0.347 empty,
0.32–0.37 wrong position/document), but the reconstruction score is a relevance-and-wording detector anchored on the final-token
snippet, not a fact checker: a meaning-preserving paraphrase of one claim costs more than a one-fact corruption (0.0049 vs 0.0031,
paired −0.0018 [−0.0028, −0.0008]); a wrong specific costs the same as a generic placeholder (0.0025 vs 0.0022) while omitting the
claim costs 0.050; the last snippet alone recovers 88% of the lift and keeps 79% of its cost when moved to the front. A forced-prefix
likelihood readout of the same verbalizer recovers the document topic reliably (0.78 raw / 0.94 prior-corrected, learned not
injection artefact: base model 0.47) and an upstream entity only weakly (donor sensitivity 1.7 nats, choice accuracy ≈ 0.60).
Off-layer reading works from block 16 to 24 (entity readout best at 24) and collapses at 27. Round-trip patching stopped at its gate
(11/16). Finding 2 replicates Dingeto (arXiv 2607.20379) on the same checkpoint with a paired design; finding 3 (snippet dominance
and the final-token feature as the verifiably-about-the-model part: quoted token right 82%, forecast hits the target's top-1 44% vs
2.5% shuffled) is ours.

## 2. Ledger — what moves the reconstruction cosine and what does not
| manipulation | Δcos |
|---|---|
| whole explanation vs empty | +0.535 |
| explanation applied to another position / document | −0.52 / −0.56 |
| delete the final-token snippet | −0.125 |
| off-topic swap of one claim | −0.114 (AUROC 0.96) |
| omit one specific claim (N3) | −0.050 |
| read the adjacent layer with the same text | −0.047 |
| delete first / middle claim | −0.010 / −0.017 |
| move snippet to front | cost 0.125 → 0.099 |
| paraphrase every claim / one claim | −0.014 / −0.005 |
| corrupt one fact in every claim / one claim | −0.0075 / −0.0031 |
| wrong specific vs generic placeholder | −0.0025 vs −0.0022 |
| corrupt vs paraphrase the snippet itself | −0.0048 vs −0.0055 |
| reverse claim order | ≈ 0 |
No effect: instructions to the verbalizer (0/200); residual steering inside it (breaks format first); reconstruction error vs answer
correctness (M, uninformative). Conversion on this pair: ΔFVE ≈ 2.7 × Δcos.

## 3. Answers settled in discussion (for the write-up's framing)
- **Cross-layer application** is mechanically trivial (any vector, rescaled to 150). Adjacent layers are near-duplicates (the L20
  text reconstructs L19/L21 at 0.835 vs 0.882), so L±1 "belief change" is sampling noise unless multi-sample recurrence is used.
  Blocks 16–24 are readable, 27 is not (X1/X1b). Future work: emergence-layer test on fact recall with logit/tuned-lens as the
  independent grader and AR-verified new claims; a tuned-lens-style affine map before injection. Recurrence across layers has the
  same generic-claim confound as recurrence across positions.
- **Causal masking**: position t sees tokens ≤ t at every layer; depth is the only place a position can hold "more". Recurrence
  across the last 10 positions works because later positions have more context, not feedback. E4.3's confound: late-entering
  evidence is structurally low-recurrence; normalise by eligible positions.
- **Paper evaluations**: suffix/classification are saturated from the warm start (SFT on Sonnet-written summaries with the vector
  injected; the "final token … expecting" snippet is mandated by that prompt); CoT hints is the informative one but needs the
  hint-following gate. FVE = 1 − 2(1 − cos)/Var on unit vectors (Var ≈ 0.73 here); cross-model comparability is weak. Flat factual
  accuracy over RL is consistent with the deletion result because false claims have positive deletion cost and the per-claim truth
  premium (~0.0016 FVE) is tiny against the 0.3 FVE RL gain; our N3 shows the truth premium ≈ 0 at the single-fact level. The
  paper's true > related-false > unrelated-false ordering is carried by relatedness; holding relatedness fixed, truth contributes
  nothing detectable (S3/N3/X3). "False about the text" ≠ "false about the model": only causal tests separate them (RT blocked).
  Every paper eval except FVE grades text against the prefix; FVE is dominated by gist + snippet.
- **CoT-hints replication**: not for this deadline (three gates, no trajectory, human hours). Future-work sentence.
- **Claim prevalence** (`notes/claim_prevalence_sample_2026-09-08.md`, agent-labelled, 44 claims): 45% true, 52% false-on-topic, 2%
  off-topic; genre slot 4/9/1, middle "quoted sentence" slot 3/13/0, final-token slot 13/1/0. Almost every false claim is a true
  frame with an invented specific; the invented specifics never occur in the prefix (bench string check: key word in full prefix
  257/691 = 37%). No round has human truth labels; the blind sheets are unfilled.
- **Extension to 27B / Opus** (reasoned, untested): wording noise > truth signal should extend (the paper's own light paraphrase
  keeps 93–105% FVE vs a 0.16-point per-claim truth gap); the magnitude of the fact signal may grow with model size (Dingeto's
  ridge ceiling for specifics ≈ 6% here); snippet dominance is partly a 2–3-snippet format artefact; absolute per-claim costs scale
  with 1/(number of claims).

## 4. Dingeto (arXiv 2607.20379): overlap and the "2%" correction
- Overlap (verified against the text on file): claim flips with per-edit validity on the same pair; explanation-level paraphrase /
  masking transform control (paraphrase 0.89, content-word mask 0.04); flat across layers 16–27; append-and-rerank control (near
  our K1); synthetic template sandbox with exact ground truth (co-trained pairs, small models — not the released pair).
- Not in Dingeto: B1's crossed test (both meanings × both activations, preference reversal); A1's paraphrase-averaged per-meaning
  discrimination and natural-error correction; D1's AR-direction subtraction → AV persistence.
- **Correction**: "≈2% grounded" = fraction of salient specific claims whose flip moves reconstruction above threshold
  (4.2/2.1/1.6% at τ = 0.02/0.05/0.10), explicitly a sensitivity-limited lower bound (append-and-rerank recovers a topic the flip
  test rates at 28%). It is not a truth rate. Fix the wording in `human-plan.md` evidence table and anywhere else it reads as truth.
- Provenance paragraph (advisor): date of first contact (2026-09-07), which experiments were complete (rounds 1–3), what changed
  after (3c base-model control; round-4 paraphrase averaging and crossed design), what replicates vs extends. Short, no apology, no
  priority claim; dated plans and logs are the chronology.

## 5. Round 4 (overnight 2026-09-09→10) — what and why
Order V0 → B1 → A1 → K1 → D1 → T9 (`overnight/PLAN.md` "Round 4 stages", commit feac26d). Orchestrator (Claude) does every
editor/judge task via task files; TARGET never used as an LLM; labels provisional until the human relabels from blind sheets.
- **B1** (human, primary controlled): 40 paired contexts, four families, shared suffix, preamble so t ≥ 50; meanings A/B only;
  orchestrator verifies the fact slot and produces a fact-swapped version; μ over 4 English paraphrases;
  D = [μ_A(h_A) − μ_B(h_A)] − [μ_A(h_B) − μ_B(h_B)], cluster by pair.
- **A1** (human, primary natural): 60 fresh wikitext contexts at a sentence-final token in [127, 255]; ≤ 2 slots per explanation;
  entailment labels with evidence quotes; corrections for natural errors; G = μ_correct − mean μ_false; A1-nat on corrections.
- **K1** (desk): 8-way ranking of the AV's original word vs matched alternatives; measures preference for the AV's word, not truth;
  positive control = final-token snippet. **D1** (desk, exploratory): subtract the AR-attributed claim direction (γ = 0.3), re-verbalize
  greedy, persistence vs random-direction control; measures AV output change only.
- Three-way reading binding: CI ≤ 0 MET, > 0 NOT MET, straddles INCONCLUSIVE; never "information absent".
- Optional if slack, else future work: a 10-pair IOI arm as positive control (answer = next token; check Qwen's top-1 first).
  Not tonight: RAVEL, CounterFact.
- Morning: `overnight/DISCONFIRMATION.md` first, then `<stage>_review_blind.csv` before `<stage>_review_key.csv`, then rerun
  `b1_analyze.py` / `a1_analyze.py --labels`.

## 6. Ideas assessed (from the human's list) — keep for future work
Length forcing (low value; AR OOD past 150 tokens); claim repetition (characterises aggregation, not truth); AV perplexity of its own
claim (self-consistency: 13 nats own vs 2.9 foreign vs 2.7 none; contrastive own−foreign carries some grounding signal: in-prefix
words 16.7 vs absent 10.8); mean Δ over many edits (= claim weight; needs truth labels); verbal confidence spans (skip; use
contrastive likelihood); temperature recurrence (needs foreign-activation control and specificity stratification). Desk additions
not run: negation test, cross-position AR profile without new decodes, target-side corroboration of invented specifics (logit lens /
target log-probs), residual re-verbalization.

## 7. Write-up structure agreed
Exec summary by finding: (1) score = relevance + wording + snippet, not a fact checker [replicates Dingeto, paired design]; (2) the
final-token feature is the verifiable part and carries the score; (3) likelihood readout recovers topic reliably, entity weakly,
and is learned; (4) round-4 A1/B1: does controlling wording recover discrimination, and does it follow the source fact. Provenance
paragraph per §4. Verified-by-human section: which numbers were re-derived by hand (still `_fill_` in `notes/human_log.md`).
