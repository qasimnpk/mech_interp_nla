# Round 4 proposal — distributed concept edits and coordinated intervention (FOR HUMAN REVIEW, not in PLAN.md)

Source: the human's cross-position hunch + a second advisor's response (2026-09-06). Desk design
below. Nothing here runs until the human accepts, edits or rejects each block.

## The question, sharpened
**Does low reconstruction sensitivity conceal a distributed, behaviourally important concept?**
Two sub-questions, run in order:
- **D-score:** does scoring one fact across all the positions where the verbalizer mentions it
  discriminate a factual corruption from a paraphrase better than single-position scoring does?
  (Advisor's caveat, which we accept: per-position AR calls are independent, so the window sum is
  just a sum. The only way this helps is if some positions carry a large effect and we did not
  sample them, or if variance across positions is informative. Statistical unit = document.)
- **D-steer:** does a *coordinated* description-derived edit at several positions change the
  target's downstream answer selectively, even though reconstruction barely registers the edit?

## Why it fits our story
Rounds 1–2 say the reconstructor scores local wording. If description-derived edits still steer a
behaviour that depends on the edited concept, reconstruction importance and behavioural importance
dissociate — a sharper result than "the AR is a poor fact checker". If they do not steer while a
donor patch does, the AR interface is inadequate for semantic control, which also closes the
question cleanly. Prior art to cite either way: the NLA paper already builds steering vectors from
differences of reconstructions of edited descriptions (poetry plans, perceived reward); our
addition is distributed edits, budget-matched specificity, and the reconstruction-vs-behaviour
comparison.

## Task family (proposed): ownership transfer with varying output mappings
Context template (chat format, since the pair was trained 50% on chat data):
```
Mira gives her key to Leena. Tomas keeps his key. {question}
```
Counterfactual twin: `Mira gives her key to Tomas. Leena keeps her key.` (owner swapped; every
other token identical → matched donor activations at every position).
Questions (answer must vary with the mapping, so a single answer-token boost cannot explain success):
- Q1 `Who now holds Mira's key? Answer with a name.` → Leena / Tomas
- Q2 `Access codes: Leena=7, Tomas=4. Which code opens Mira's key's lock? Answer with a digit.` → 7 / 4
- Q3 `Labels: Leena=alpha, Tomas=beta. Which label is on the person holding Mira's key?` → alpha / beta
24 contexts by permuting 3 name triples × 2 orders × 4 object words (key, coin, ticket, letter);
8 development, 16 held-out. Mappings in Q2/Q3 re-randomised per context.

**Gate G0 (target competence):** target accuracy ≥ 0.9 on all three questions, else change task.
**Gate G1 (site controllable):** donor-patch the twin's block-20 activations into the original at
the 6 positions below; mean log-odds shift toward the twin's answer with CI > 0 on dev, else stop
D-steer and report D-score only.

## Positions (6 per context, chosen after the fact is available)
p1 end of "Leena" (transfer completes), p2 end of sentence 1, p3 end of "Tomas", p4 end of
sentence 2, p5 last token of the question, p6 the pre-answer token (assistant-turn prefix newline).
Earlier positions are excluded on purpose (cannot represent later facts).

## D-score procedure
1. Verbalize all 6 positions × 24 contexts (144 generations, ~25 min).
2. Claim table: split as in round 1; a claim "mentions the owner" if it contains the current-owner
   name (string match, plus the LLM editor's paraphrases of "holds/has/received the key").
   Report mention rate per position; **if the owner is mentioned at < 3 positions on average,
   D-score is INCONCLUSIVE** (nothing to edit) — check this on the 8 dev contexts first.
3. Edits, only where the claim exists (never add a claim where absent): corrupt (owner name →
   other name, everywhere in that claim), paraphrase (LLM, meaning-preserving), unrelated edit
   (object word → another object word, matched length), local snippet left untouched.
4. Score every edited description against its own h_t. Report: window mean Δ, edited-positions
   mean Δ, per-position Δ, recurrence count; corruption vs paraphrase vs unrelated, paired by
   document, cluster bootstrap by document.
5. **Kill D1:** CI of mean(edited-positions corruption cost − paraphrase cost) ≤ 0 → MET.
   Also report the same at the single best position, so "did more positions help" is answerable.

## D-steer procedure (only if G1 passes)
- For each position t with an owner claim: `u(d)=AR(d)/‖AR(d)‖`, `v_t = ‖h_t‖ (u(d*_t) − u(d_t))`,
  `h'_t = h_t + α v_t` at block 20 during the target forward.
- Conditions, all at **matched total perturbation budget** Σ‖α v_t‖ (chosen on dev, frozen):
  single position (each t), coordinated (all edited positions, α scaled by 1/√k), same vectors
  applied at control positions (shifted by +2 tokens), paraphrase-derived v, norm-matched random v,
  **context-encoding baseline** (difference of the target's own block-20 activations on the twin
  vs original context at the same positions, i.e. the donor difference direction, at the same
  budget), donor patch (positive control, full replacement).
- Measures: log-odds of twin answer vs original answer for Q1–Q3; collateral: KL on an unrelated
  question (`What object was given?`). Dose α from a 3-point grid on dev; held-out reported only at
  the frozen dose.
- **Kill D2:** coordinated AR-edit effect − paraphrase-derived effect, CI ≤ 0 → MET (no semantic
  specificity). **D3 (synergy, descriptive):** coordinated vs best single at matched budget.
  **D4:** AR-edit vs context-encoding baseline — if the baseline is as good, the AR adds nothing.

## Budget (laptop)
144 AV generations (~25 min) + ~300 editor generations (~40 min) + ~600 AR forwards (~4 min) +
~4,000 target forwards with hooks (~25 min). One night. TARGET+AR co-resident; AV separately.

## Risks the human should weigh
- The verbalizer was trained on wikitext-like and chat text; puzzle sentences may get generic
  descriptions that never name the owner. The dev-set mention-rate check is the guard.
- The local "expecting X" snippet at p6 will dominate reconstruction; the edit must not touch it,
  and the p6 result should be reported separately.
- The AR is direction-only; ‖AR(d)‖ is meaningless, hence the normalisation (advisor agrees).
- Novelty of the distributed-edit protocol is unverified; the NLA paper's steering section must be
  read in full before any claim (its text is in `notes/nla_paper_2026_text.txt`, grep "steer").

## Prior art in the NLA paper, read at primary source (2026-09-06)
- Poetry: "we edit the NLA explanation at the newline ... take the difference Δ = AR(AV_edit) − AR(AV_orig) as the edit direction. We then steer with this direction at the newline token only, at the layer the NLA is trained on ... h_orig → h_orig + α‖h_orig‖ Δ/‖Δ‖." Result: "steering is only successful roughly 50% of the time"; "fewer than 80% of completions actually end with 'mouse' or 'house' because they partially degenerate."
- Rewards: edit "reward"→"penalty" in five rollouts on one token, average the five Δ's, steer at that single token; more odd answers than a random vector; the edit word does not appear in the output, so not token-boosting.
- Their own framing: "We do not aim to outperform existing steering methods: the purpose ... is to demonstrate that NLA explanations bear a causal relationship to model outputs."
**Consequences for us:** single-token, single-edit, no budget-matched controls, no paraphrase null, no comparison with a context-encoding direction, no multi-position coordination, no link to reconstruction importance. Every one of those is what D-steer adds. Also adopt their rescaling convention (α‖h‖ Δ/‖Δ‖) so doses are comparable, and report degeneration rate as they do.

## What the human decides
1. Task family: ownership transfer as above, or a different intermediate variable?
2. Run D-score alone first (one night) and D-steer the next, or both in one night?
3. Accept the gates G0/G1 and kills D1/D2 as written?
4. Is this round 4 (after the round-3 promptability night) or does it replace round 3?
